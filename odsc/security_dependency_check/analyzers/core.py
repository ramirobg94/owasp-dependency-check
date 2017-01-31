import requests

from typing import List
from flask import current_app

from security_dependency_check import celery, Project, Vulnerabilities
from .helpers import AVAILABLE_TASKS

try:
    import ujson as json
except ImportError:
    import json

REGEX_SEVERITY = r'''(severity[\s]*:[\s]*)([\w]+)(;)'''


def update_project_status(project_id: int, status: str):
    p = Project.query.get(project_id)
    p.status = status

    db = current_app.config["DB"]
    db.session.add(p)
    db.session.commit()


@celery.task(name="core_dispatch")
def core_dispatch(lang: str, repo: str, project_id: int):
    """
    This tasks do:

    - Clean the URL of repo
    - Check that repo is accessible
    - Clone remote repo and create a copy for each tool
    """
    # Clean repo URL
    repo = repo.strip().replace(" ", "")

    # Check if remote is accesible
    try:
        if requests.get(repo, timeout=5).status_code != 200:
            update_project_status(project_id, "non-accessible")
            return

        selected_tasks = AVAILABLE_TASKS[lang]

        # Add counter to the Redis
        current_app.config["REDIS"].setex("ODSC_{}_counter".format(project_id),
                                          value=len(selected_tasks),
                                          time=360000)  # 10 hours

        # Call all analyzers for each language
        for task_name in selected_tasks:
            celery.send_task(task_name, args=(repo, project_id))

        # Update the project status
        update_project_status(project_id, "running")
    except:
        # If any exception occurred mark the project as non-accessible
        update_project_status(project_id, "non-accessible")


@celery.task(name="core_partial_results_storage")
def core_partial_results_storage(project_id: int, partial_results: dict):
    """This tasks storage partial results of an analysis"""

    db = current_app.config["DB"]
    redis_db = current_app.config["REDIS"]

    redis_counter_key = "ODSC_{}_counter".format(project_id)
    redis_partial_result_key = "ODSC_{}_partial".format(project_id)

    # Storage the results in unique key in Redis
    if partial_results:
        redis_db.set(redis_partial_result_key, json.dumps(partial_results))

    # Update counter in Redis
    current_app.config["REDIS"].decr(redis_counter_key)

    # Only if counter is less than 0 -> all tasks were ended
    pending_tasks = int(current_app.config["REDIS"].get(redis_counter_key))

    # Update the project passed tests
    p = Project.query.get(project_id)
    p.passed_tests += 1

    db.session.add(p)
    db.session.commit()

    if not pending_tasks:
        # Get all partial and non-merged results from Redis
        redis_info = redis_db.get(redis_partial_result_key)

        if type(redis_info) is bytes:
            redis_info = redis_info.decode()

        unmerged_results = json.loads(redis_info)

        # Remove Partial results from Redis
        redis_db.delete(redis_partial_result_key)

        # Remove Redis project counter
        redis_db.delete(redis_counter_key)

        # Next step -> Merger
        celery.send_task("core_merger_task",
                         args=(project_id, unmerged_results))


# --------------------------------------------------------------------------
# Añadir: el contador de tests pasados
# --------------------------------------------------------------------------
@celery.task(name="core_merger_task")
def core_merger_task(project_id: int, unmerged_results: List[dict]):
    """this task join all the vulnerabilities"""

    db = current_app.config["DB"]

    cleaned_results = []
    for i, result in enumerate(unmerged_results):

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

    # Update project status
    p = Project.query.get(project_id)
    p.status = "finished"
    db.session.add(p)

    # Commit al changes
    db.session.commit()
