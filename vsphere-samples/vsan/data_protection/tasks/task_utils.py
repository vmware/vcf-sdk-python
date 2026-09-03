#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

import time

from com.vmware.snapservice.tasks_client import Status

from vsan.data_protection.tasks.get_task import GetTask


def wait_for_snapservice_task(snapservice_client, ss_task_id):
    """
    Wait for the snapservice task to complete.
    """
    task = GetTask(snapservice_client, ss_task_id)
    while True:
        task_info = task.get_task()

        if task_info.status == Status.SUCCEEDED:
            print("# Task {} succeeds.".format(task_info.description.id))
            return
        elif task_info.status == Status.FAILED:
            print("# Task {} fails.\nError:\n".format(task_info.description.id))
            print(task_info.error)
            return
        else:
            print("# Task {} progress: {}".format(task_info.description.id,
                                                  task_info.progress.completed))
            time.sleep(5)
