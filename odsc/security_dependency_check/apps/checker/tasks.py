import re
import os
import uuid
import tempfile
import subprocess
import xml.etree.ElementTree as ET

from cpe import CPE
from flask import current_app

from security_dependency_check import celery, Project, Vulnerabilities, \
    VulnerabilitySharedObj


REGEX_SEVERITY = r'''(severity[\s]*:[\s]*)([\w]+)(;)'''


@celery.task(name="joiner_task")
def joiner_task(project_id: int):
    """this task join all the vulnerabilities"""

    db = current_app.config["DB"]
    redis_db = current_app.config["REDIS"]

    if not int(current_app.config["REDIS"].get("ODSC_{}_counter".format(project_id))):
        r = redis_db.hgetall(project_id)

        results = []
        for x in r.values():
            results.append(eval(x.decode()))

        cleaned_results = []

        for i, result in enumerate(results):

            if not result['library']:
                continue

            if not cleaned_results:
                cleaned_results.append(result)
            else:
                _temp_add = {}
                for vul_r in cleaned_results:
                    if result['library'] == vul_r['library'] and \
                                    result['advisory'] == vul_r['advisory']:
                        break
                else:
                    _temp_add = result

                if _temp_add:
                    cleaned_results.append(_temp_add)

        for vul in cleaned_results:
            vul = Vulnerabilities(vul['library'],
                                  vul['version'],
                                  vul['severity'],
                                  vul['summary'],
                                  vul['advisory'],
                                  project_id)

            db.session.add(vul)

        p = Project.query.get(project_id)
        p.passedTests = p.numberTests

        db.session.add(p)
        db.session.commit()


# --------------------------------------------------------------------------
# Custom checker test
# --------------------------------------------------------------------------

@celery.task(name="owasp_dependency_checker_task")
def owasp_dependency_checker_task(lang: str,
                                  repo: str,
                                  type: str,
                                  project_id: int):
    """
    Run OWASP dependency-check and storage all vulnerabilities in
    an unified format in Redis
    """

    redis_db = current_app.config["REDIS"]

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
        if cleared_results:
            redis_db.hmset(project_id, cleared_results)

    current_app.config["REDIS"]. \
        decr("ODSC_{}_counter".format(project_id))

    # Call the joiner
    celery.send_task("joiner_task", args=(project_id, ))


# Task que pasa retire que es el comprado de nodejs devulve las
# vulnerabilidades al redis
@celery.task(name="retire_task")
def retire_task(lang: str, repo: str, type: str, project_id: int):
    redis_db = current_app.config["REDIS"]

    with tempfile.TemporaryDirectory() as curr_dir:
        os.environ["PATH"] = os.environ.get("PATH") + \
                             current_app.config["ADDITIONAL_BINARY_PATHS"]
        os.system('git clone {} {}'.format(repo, curr_dir))

        # Change to downloaded code directory and install their dependencies
        os.chdir(curr_dir)
        subprocess.call('npm install', shell=True)

        # Fix output results file
        out_path = os.path.join(curr_dir, 'checkba.txt')

        os.system('retire --outputformat text --outputpath {}'. \
                  format(out_path))

        f = open(out_path, "r").readlines()

        to_store = {}

        for x in f:
            if "has known vulnerabilities" in x:
                # Find the start of string
                for i, y in enumerate(x):
                    if y.isalnum():
                        break

                line = x[i:]

                library, version, _ = line.split(" ", maxsplit=2)
                try:
                    severity = re.search(REGEX_SEVERITY, line).group(2)
                except AttributeError:
                    severity = "unknown"

                summary = x[x.find("summary"):].replace("\n", '')
                if not summary:
                    summary = x[x.find("advisory"):].replace("\n", '')
                if not summary:
                    summary = "unknown"

                vulnerability = VulnerabilitySharedObj(library,
                                                       version,
                                                       severity,
                                                       summary,
                                                       '')

                to_store[str(uuid.uuid4())] = vulnerability.__dict__

        redis_db.hmset(project_id, to_store)

    current_app.config["REDIS"]. \
        decr("ODSC_{}_counter".format(project_id))

    # Call the joiner
    celery.send_task("joiner_task", args=(project_id, ))

__all__ = ("joiner_task", "owasp_dependency_checker_task", "retire_task")
