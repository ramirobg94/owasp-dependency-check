import os
import re
import tempfile
import subprocess

from flask import current_app

from security_dependency_check import celery, VulnerabilitySharedObj

REGEX_SEVERITY = r'''(severity[\s]*:[\s]*)([\w]+)(;)'''


@celery.task(name="nodejs_retire_task")
def nodejs_retire_task(repo: str,
                       project_id: int):

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

                vulnerability = VulnerabilitySharedObj(library,
                                                       version,
                                                       severity,
                                                       summary,
                                                       '')

                results.append(vulnerability.__dict__)

    celery.send_task("core_partial_results_storage", args=(project_id,
                                                           results))