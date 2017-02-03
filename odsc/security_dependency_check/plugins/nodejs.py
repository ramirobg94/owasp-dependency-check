import os
import re
import subprocess
from typing import List, Dict

from security_dependency_check import odsc_plugin

REGEX_SEVERITY = r'''(severity[\s]*:[\s]*)([\w]+)(;)'''


@odsc_plugin("nodejs")
def nodejs_retire_task(source_code_location: str) -> List[Dict]:

    # Install their dependencies
    subprocess.call('npm install', shell=True)

    # Fix output results file
    out_path = os.path.join(source_code_location, 'retire_results.txt')

    os.system('retire -c --outputformat text --outputpath {}'. \
              format(out_path))

    f = open(out_path, "r").readlines()

    results = []

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

            if "summary:" in x:
                start = x.find("summary") + len("summary:")
            elif "advisory:":
                start = x.find("advisory") + len("advisory:")
            else:
                start = 0
            summary = x[start:].replace("\n", '').strip()
            if not summary:
                summary = "Unknown"

            results.append(dict(library=library,
                                version=version,
                                severity=severity,
                                summary=summary,
                                advisory=''))
    return results
