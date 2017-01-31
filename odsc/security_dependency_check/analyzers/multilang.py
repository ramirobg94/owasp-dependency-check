import os
import tempfile
import uuid
import xml.etree.ElementTree as ET

from cpe import CPE
from flask import current_app

from security_dependency_check import celery, VulnerabilitySharedObj


@celery.task(name="owasp_dependency_checker_task")
def owasp_dependency_checker_task(repo: str,
                                  project_id: int):
    """
    Run OWASP dependency-check and storage all vulnerabilities in
    an unified format in Redis
    """

    with tempfile.TemporaryDirectory() as curr_dir:
        os.environ["PATH"] = os.environ.get("PATH") + \
                             current_app.config["ADDITIONAL_BINARY_PATHS"]

        os.system('git clone {} {}'.format(repo, curr_dir))
        os.system('dependency-check -n --project "{}" --scan '
                  '"{}" -f "XML" -o  "{}" --enableExperimental'.format(repo,
                                                                       curr_dir,
                                                                       curr_dir))

        tree = ET.parse('{}/dependency-check-report.xml'.format(curr_dir))
        root = tree.getroot()
        cleared_results = {}

        SCHEME = "{https://jeremylong.github.io/DependencyCheck/dependency" \
                 "-check.1.3.xsd}"

        for neighbor in root[2]:
            for elemts in neighbor:
                if 'vulnerabilities' in elemts.tag:
                    for vulnerability in elemts:
                        advisory = getattr(
                            vulnerability.find("{}name".format(SCHEME)),
                            "text", "")
                        severity = getattr(
                            vulnerability.find("{}severity".format(SCHEME)),
                            "text", "")
                        description = getattr(
                            vulnerability.find("{}description".format(SCHEME)),
                            "text", "")

                        for vulnerable_version in vulnerability.findall(
                                ".//{}vulnerableSoftware/{}software["
                                "@allPreviousVersion='true']".format(
                                    SCHEME, SCHEME)):
                            cpe = CPE(vulnerable_version.text)
                            product = cpe.get_product()[0]
                            version = cpe.get_version()[0]

                            vulnerability = VulnerabilitySharedObj(product,
                                                                   version,
                                                                   severity,
                                                                   description,
                                                                   advisory)

                            cleared_results[str(uuid.uuid1())] = \
                                vulnerability.__dict__

    # Call the joiner
    celery.send_task("core_partial_results_storage", args=(project_id,
                                                           cleared_results))


__all__ = ("owasp_dependency_checker_task", )
