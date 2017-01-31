from typing import List

from flask import current_app

from security_dependency_check import celery, Project, Vulnerabilities

REGEX_SEVERITY = r'''(severity[\s]*:[\s]*)([\w]+)(;)'''

try:
    import ujson as json
except ImportError:
    import json


@celery.task(name="core_partial_results_storage")
def core_partial_results_storage(project_id: int, partial_results: dict):
    """This tasks storage partial results of an analysis"""

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

    p = Project.query.get(project_id)
    p.passedTests = p.numberTests

    db.session.add(p)
    db.session.commit()
