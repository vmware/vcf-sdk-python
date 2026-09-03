#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '9.0.0'

import time
import logging

from com.vmware.cis_client import Tasks
from com.vmware.cis.task_client import Status as TaskStatus
from com.vmware.vcenter.lcm.deployment_client import MigrationUpgrade
from vmware.vapi.stdlib.client.task import Task

NUM_RETRIES = 10
DELAY = 30

logger = logging.getLogger(__name__)


class Prechecks:
    def __init__(self, migration_client: MigrationUpgrade, task_client: Tasks):
        """
        Class demonstrating how to call RDU's pre-check API. It can be called before the upgrade or during it.
        A requirement before executing this API is to have the vCenter lifecycle plugin upgraded to you desired
        target version.
        :param migration_client: MigrationUpgrade client for the source vCenter
        :param task_client: Tasks client for the source vCenter
        """
        self.migration_client = migration_client
        self.task_client = task_client

    @staticmethod
    def _wait_for_result(task: Task, num_retries: int, delay: int):
        """
        Methods waits for the completion of a task. Throws an error if the task times out or fails.
        :param task: The task object.
        :param num_retries: Number of times the status of the task is fetched.
        :param delay: The delay between the retries in seconds.
        :return: The task result
        """
        for _ in range(0, num_retries):
            task_status = task.get_info()

            if task_status.status == TaskStatus.SUCCEEDED:
                logger.info("Task has completed successfully.")
                return task.get_result()

            if task_status.status == TaskStatus.FAILED:
                error_msg_list = [msg.default_message for msg in task_status.error.messages]
                logger.error("Task has failed with error: %s", '\n'.join(error_msg_list))
                try:
                    task_result = task.get_result()
                except AttributeError:
                    logger.error("No result was returned from the upgrade prechecks. "
                                 "Most probably the checks didn't start.")
                    raise Exception("No result was returned from the upgrade prechecks.")

                return task_result

            logger.info("The upgrade precheck is still running. Current progress %s", task_status.progress)
            time.sleep(delay)

        logger.error("The upgrade precheck execution has timed out after %d seconds", NUM_RETRIES * DELAY)
        raise Exception("The upgrade precheck execution has timed-out")

    def run_prechecks(self, init_spec: MigrationUpgrade.InitSpec = None):
        """
        Run the prechecks.
        :param init_spec: Init spec which will be used for the upgrade. If an upgrade has already been initialized
        this parameter should be skipped, the pre-checks will use the init spec from the initialized upgrade.
        :return:
        """
        logger.info("Run the upgrade checks.")
        task = self.migration_client.check_task(spec=init_spec)

        logger.info("Running task with ID %s", task.get_task_id())

        logger.info("Verify if the checks have passed successfully.")
        return self._wait_for_result(task=task, num_retries=NUM_RETRIES, delay=DELAY)
