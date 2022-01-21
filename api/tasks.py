import logging
import subprocess
import time
from contextlib import contextmanager
from django.core.cache import cache
from hashlib import md5

from celery import shared_task
from django.conf import settings

from api.models import TestRunRequest, TestEnvironment

logger = logging.getLogger(__name__)
MAX_RETRY = 10

LOCK_EXPIRE = 60 * 10


@contextmanager
def cache_lock(lock_id, oid):
    timeout_at = time.monotonic() + LOCK_EXPIRE - 3
    status = cache.add(lock_id, oid, LOCK_EXPIRE)
    try:
        yield status
    finally:
        if time.monotonic() < timeout_at and status:
            cache.delete(lock_id)


def handle_task_retry(instance: TestRunRequest, retry: int) -> None:
    if retry < MAX_RETRY:
        countdown = 2 ** retry
        logger.warning(f'Test Environment is busy, Retrying in {countdown}')
        instance.save_logs(logs=f"Failed to run tests on env {instance.env.name} retrying in {countdown} seconds.")
        instance.mark_as_retrying()
        execute_test_run_request.s(instance.id, retry + 1).apply_async(countdown=countdown)
    else:
        logger.error(
            f"Failed to run tests(ID:{instance.id}) on env {instance.env.name} after retrying {MAX_RETRY} times."
        )
        instance.save_logs(logs=f"Failed to run tests on env {instance.env.name} after retrying {MAX_RETRY} times.")
        instance.mark_as_failed_to_start()


@shared_task
def execute_test_run_request(instance_id: int, retry: int = 0) -> None:
    instance = TestRunRequest.objects.get(id=instance_id)

    if instance.env.is_busy():
        handle_task_retry(instance, retry)
        return
    env_hexdigest = md5(instance.env.name.encode('utf-8')).hexdigest()
    lock_id = f"{instance_id}-lock-{env_hexdigest}"
    with cache_lock(lock_id, instance.env.id) as acquired:
        if acquired:
            env = TestEnvironment.objects.get(name=instance.env.name)
            env.lock()

            cmd = instance.get_command()
            logger.info(f'Running tests(ID:{instance_id}), CMD({" ".join(cmd)}) on env {instance.env.name}')

            instance.mark_as_running()

            run = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True)
            return_code = run.wait(timeout=settings.TEST_RUN_REQUEST_TIMEOUT_SECONDS)

            env.unlock()
            instance.save_logs(logs=run.stdout.read())
            if return_code == 0:
                instance.mark_as_success()
            else:
                instance.mark_as_failed()
            logger.info(
                f'tests(ID:{instance_id}), CMD({" ".join(cmd)}) on env {instance.env.name} Completed successfully.')
