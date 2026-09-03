#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '9.0.0'

from com.vmware.vcenter.lcm_client import Notifications
from com.vmware.cis.task_client import Progress
from com.vmware.vcenter.lcm.deployment.common_client import Status
from com.vmware.vcenter.lcm.deployment.migration_upgrade_client import Status as UpgradeStatus

"""
    File contains helper methods for displaying all parts of the upgrade status.
"""


def notifications_to_str(notifications: Notifications, indentation: int = 0):
    if not notifications:
        return "No available notifications"

    indentations = indentation * ' '
    error_str = ""
    warnings_str = ""
    info_str = ""
    msg_pattern = "{0}Message: {1}\n{0}Resolution: {2}\n"
    if notifications.errors:
        for error in notifications.errors:
            error_str = msg_pattern.format(indentations,
                                           error.message.default_message,
                                           (error.resolution.default_message if error.resolution else "None"))

    if notifications.warnings:
        for warning in notifications.warnings:
            warnings_str = msg_pattern.format(indentations,
                                              warning.message.default_message,
                                              (warning.resolution.default_message if warning.resolution else "None"))

    if notifications.info:
        for info in notifications.info:
            info_str = msg_pattern.format(indentations,
                                          info.message.default_message,
                                          (info.resolution.default_message if info.resolution else "None"))

    return (f"{indentations}- Error: \n{error_str}\n"
            f"{indentations}- Warning: \n{warnings_str}\n"
            f"{indentations}- Info: \n{info_str}\n")


def messages_to_str(messages, indentation: int = 0):
    indentations = indentation * ' '
    loc_msgs = ['\n' + indentations + "- " + msg.default_message for msg in messages]
    return ''.join(loc_msgs)


def upgrade_info_to_str(upgrade_info: UpgradeStatus.UpgradeInfo, indentation: int = 0):
    indentations = indentation * ' '
    return (f"{indentations}- Upgrading to version: {upgrade_info.upgrade_to}\n"
            f"{indentations}- Configured pause point: {upgrade_info.pause if upgrade_info.pause else 'None'}\n"
            f"{indentations}- Switchover scheduled at: {upgrade_info.start_switchover if upgrade_info.start_switchover else 'None'}\n"
            f"{indentations}- Remaining data to replicate to the new machine: {str(upgrade_info.remaining_replication_data)}\n"
            f"{indentations}- Upgrade errors: {messages_to_str(upgrade_info.error.messages, 4) if upgrade_info.error else 'None'}\n")


def progress_to_str(progress: Progress, indentation: int = 0):
    if not progress:
        return "None"

    indentations = indentation * ' '
    return (f"{indentations}- Total: {str(progress.total)}\n"
            f"{indentations}- Completed: {str(progress.completed)}\n"
            f"{indentations}- Message: {progress.message.default_message}\n")


def status_to_str(upgrade_status: UpgradeStatus.Info):
    status = "\n1. Result: " + upgrade_status.status
    status += "\n2. Current state: " + (upgrade_status.current_state if upgrade_status.current_state else "None")

    status += "\n3. Upgrade information:\n"
    status += upgrade_info_to_str(upgrade_info=upgrade_status.upgrade_info, indentation=1)

    status += "\n4. Progress:\n"
    status += progress_to_str(progress=upgrade_status.progress, indentation=1)

    status += "\n5. Notifications:\n"
    status += notifications_to_str(notifications=upgrade_status.notifications, indentation=1)

    if upgrade_status.status == Status.PENDING:
        status += "\nUpgrade has not yet been initialized."

    if upgrade_status.status == Status.FAILED:
        status += "\n6. Upgrade has failed. You can find the issue which caused the fail in the errors bellow. \n"
        status += " - Errors: " + messages_to_str(upgrade_status.error.messages, 4) + '\n'

    if upgrade_status.status == Status.CANCELED:
        status += ("\n6. Upgrade has been successfully canceled."
                   "You can find the issue which triggered cancellation in the errors below.\n")
        status += " - Errors: " + messages_to_str(upgrade_status.error.messages, 4) + '\n'

    return status
