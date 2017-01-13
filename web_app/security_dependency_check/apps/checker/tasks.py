import os
import uuid
import tempfile

import subprocess
from cpe import CPE
from flask import current_app
import xml.etree.ElementTree as ET

from security_dependency_check import celery, Project, Vulnerabilities, VulnerabilitySharedObj


@celery.task(name="mytask")
def add(x, y):
    """Testing task"""
    print(x)
    return x + y


@celery.task(name="joiner_task")
def joiner_task(project_id: int, other):
    """this task join all the vulnerabilities"""
    db = current_app.config["DB"]
    redis_db = current_app.config["REDIS"]
    
    p = Project.query.get(project_id)

    passed = p.passedTests + 1


    
    if passed == p.numberTests:
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
                    if result['library'] == vul_r['library'] and result['advisory'] == vul_r['advisory']:
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
            db.session.commit()

    p.passedTests += 1
    db.session.commit()

    return "joiner TODO"


# --------------------------------------------------------------------------
# Custom checker test
# --------------------------------------------------------------------------

@celery.task(name="owasp_dependency_checker_task")
def owasp_dependency_checker_task(lang: str, repo: str, type: str, project_id: int):
    """Run OWASP dependency-check and storage all vulnerabilities in an unified format in Redis"""
    
    redis_db = current_app.config["REDIS"]
    
    with tempfile.TemporaryDirectory() as f:
        curr_dir = str(f)
    
        os.system('git clone {} {}'.format(repo, curr_dir))
        os.system('/usr/local/bin/dependency-check --project "{}" --scan "{}" -f "XML" -o  "{}" --enableExperimental'.format(repo,
                                                                                                              curr_dir,
                                                                                                              curr_dir))
        
        tree = ET.parse('{}/dependency-check-report.xml'.format(curr_dir))
        root = tree.getroot()
        cleared_results = {}
    
        for neighbor in root[2]:
            for elemts in neighbor:
                if 'vulnerabilities' in elemts.tag:
                    for vulnerability in elemts:
                        for vulnerabilityTags in vulnerability:
                            severity = ""
                            advisory = ""
                            description = ""
                            
                            if 'severity' in vulnerabilityTags.tag:
                                severity = vulnerabilityTags.text
                            if 'description' in vulnerabilityTags.tag:
                                description = vulnerabilityTags.text
                            if 'name' in vulnerabilityTags.tag:
                                advisory = vulnerabilityTags.text
                            if 'vulnerableSoftware' in vulnerabilityTags.tag:
                                for software in vulnerabilityTags:
                                    if 'allPreviousVersion' in software.attrib:
                                        cpe = CPE(software.text)
                                        product = cpe.get_product()[0]
                                        version = cpe.get_version()[0]
                                        
                                        vulnerability = VulnerabilitySharedObj(product,
                                                                               version,
                                                                               severity,
                                                                               description,
                                                                               advisory)
                                        
                                        cleared_results[str(uuid.uuid1())] = vulnerability.__dict__
        
        redis_db.hmset(project_id, cleared_results)
    
    celery.send_task("joiner_task", args=(project_id, 1))


# Task que pasa retire que es el comprado de nodejs devulve las vulnerabilidades al redis
@celery.task(name="retire_task")
def retire_task(lang: str, repo: str, type: str, project_id: int):
    redis_db = current_app.config["REDIS"]

    with tempfile.TemporaryDirectory() as f:
        curr_dir = str(f)
        #curr_dir = "/tmp/fuckyou/"
    
        os.system('git clone {} {}'.format(repo, curr_dir))

        os.environ["PATH"] = os.environ.get("PATH") + ":/usr/local/bin"

        os.chdir(curr_dir)
        out_path = os.path.join(curr_dir, 'checkba.txt')
        subprocess.call('npm install', shell=True)

        os.system('/usr/local/bin/retire --outputformat text --outputpath {}'.format(out_path))

        f = open(out_path, "r").readlines()

        to_store = {}
        
        for x in f:
            if "has known vulnerabilities" in x:
                #library, version, _, _, _, _, _, severity = x.split(" ")

                # ese caracter es la flechita
                x = x.strip("\r\n \u21B3")
                a = x.replace("  ", " ")
                a = x.split(" ")

                #library, version, _, _, _, _, _, severity = x.split(" ")
                library = a[0]
                version = a[1]
                severity = a[6]
                
                if "severity" in x:
                    severity = severity
                else:
                    severity = ''
                
                summary = x[x.find("summary"):].replace("\n", '')
                if not summary:
                    summary = x[x.find("advisory"):].replace("\n", '')
                
                vulnerability = VulnerabilitySharedObj(library, version, severity, summary, '')
                
                to_store[str(uuid.uuid4())] = vulnerability.__dict__
                
        redis_db.hmset(project_id, to_store)
    
    celery.send_task("joiner_task", args=(project_id, 1))
    
    return 2
