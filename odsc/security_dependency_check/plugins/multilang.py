import os
import xml.etree.ElementTree as ET

from cpe import CPE
from typing import List, Dict
from security_dependency_check import odsc_plugin


@odsc_plugin(lang="nodejs")
def owasp_dependency_checker_task(source_code_location: str) -> List[Dict]:
    """
    Run OWASP dependency-check and storage all vulnerabilities in
    an unified format in Redis
    """
    command = ['dependency-check --project "{loc}" --scan',
               ' "{loc}" -f "XML" -o {loc}',
               ' --enableExperimental']

    # Install dependencies is VERY important
    os.system("npm install")

    # We use os.system instead of subprocess.call because because the OWASP
    # Dependency check tool can take te CVE wordlist downloaded from the OS
    # context. Using subprocess.call this is not possible. This implies
    # that without the context no vulnerabilities was detected
    os.system("".join(command).format(loc=source_code_location))

    tree = ET.parse('{}/dependency-check-report.xml'. \
                    format(source_code_location))
    root = tree.getroot()

    SCHEME = "{https://jeremylong.github.io/DependencyCheck/dependency" \
             "-check.1.3.xsd}"

    results = []
    for dependency in root.iterfind(".//{}dependency".format(SCHEME)):
        # Get dep info

        vulnerabilities = dependency.findall(".//{}vulnerability".format(SCHEME))
        for vulnerability in vulnerabilities:
            advisory = getattr(
                vulnerability.find("{}name".format(SCHEME)),
                "text", "")
            severity = getattr(
                vulnerability.find("{}severity".format(SCHEME)),
                "text", "")
            summary = getattr(
                vulnerability.find("{}description".format(
                    SCHEME)),
                "text", "")

            for vulnerable_version in vulnerability.findall(
                    ".//{}vulnerableSoftware/{}software["
                    "@allPreviousVersion='true']".format(
                        SCHEME, SCHEME)):
                cpe = CPE(vulnerable_version.text)
                library = cpe.get_product()[0]
                version = cpe.get_version()[0]

                results.append(dict(library=library,
                                    version=version,
                                    severity=severity,
                                    summary=summary,
                                    advisory=advisory))

    return results
