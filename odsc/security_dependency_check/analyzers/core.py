import os
import uuid
import shutil
import logging
import requests
import tempfile

from typing import List, Dict
from flask import current_app

from security_dependency_check import celery, Project, Vulnerabilities

from .helpers import has_valid_format

try:
    import ujson as json
except ImportError:
    import json

log = logging.getLogger("celery")

REGEX_SEVERITY = r'''(severity[\s]*:[\s]*)([\w]+)(;)'''


def update_project_status(project_id: int, status: str):
    p = Project.query.get(project_id)
    p.status = status

    db = current_app.config["DB"]
    db.session.add(p)
    db.session.commit()


@celery.task(name="meta_task_runner")
def meta_task_runner(task_name: str,
                     module: str,
                     repo: str,
                     project_id: int):
    manager = celery.ODSC_PLUGINS_MANAGER

    task_obj = vars(manager.load_plugin(module))[task_name]

    # Create the temporal directory
    curr_dir = tempfile.TemporaryDirectory()

    # Prepare to run the task
    os.environ["PATH"] = os.environ.get("PATH") + \
                         current_app.config["ADDITIONAL_BINARY_PATHS"]

    # Clone remote dir
    clone_dir = os.path.join(curr_dir.name, uuid.uuid4().hex)
    os.system('git clone {} {}'.format(repo, clone_dir))

    # Passionate to cloned dir
    os.chdir(clone_dir)

    # Call the function
    try:
        results = task_obj(clone_dir)
    except Exception as e:
        results = None
        log.error("Plugin '{}' was generated an exception for project '{}': "
                  "{}".format(task_name, project_id, e))

    # Check plugin result format
    if not has_valid_format(results):
        log.error("Plugin '{}' was generated results with invalid format "
                  "for project '{}'".format(task_name, project_id))

    celery.send_task("core_partial_results_storage", args=(project_id,
                                                           results))

    # Cleanup and remote the temporal directory
    curr_dir.cleanup()
    shutil.rmtree(curr_dir.name, ignore_errors=True)


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
        if requests.get(repo, timeout=20).status_code != 200:
            update_project_status(project_id, "non-accessible")
            return

        selected_tasks = celery.ODSC_PLUGINS[lang]

        # Add counter to the Redis
        current_app.config["REDIS"].setex("ODSC_{}_counter".format(project_id),
                                          value=len(selected_tasks),
                                          time=360000)  # 10 hours

        # Call all analyzers for each language
        for plugin_name, module in selected_tasks:
            celery.send_task("meta_task_runner", args=(plugin_name,
                                                       module,
                                                       repo,
                                                       project_id))

        # Update the project status
        update_project_status(project_id, "running")
    except:
        # If any exception occurred mark the project as non-accessible
        update_project_status(project_id, "non-accessible")


@celery.task(name="core_partial_results_storage")
def core_partial_results_storage(project_id: int, partial_results: List[Dict]):
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

        if not redis_info:
            redis_info = "[]"

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
