#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '8.0.3+'

from helpers.common import sample_cli
from helpers.common import sample_util
from vsan.data_protection.data_protection_clients import DataProtectionClients


class GetTask(object):
    def __init__(self, snapservice_client, task_id):
        self._snapservice_client = snapservice_client
        self._task_id = task_id

    def get_task(self):
        return self._snapservice_client.Tasks.get(self._task_id)


def get_args():
    parser = sample_cli.build_arg_parser()
    required_args = parser.add_argument_group('snapservice required arguments')
    required_args.add_argument('--snapservice',
                               action='store',
                               required=True,
                               help='Snapservice IP/hostname to connect to')
    required_args.add_argument('--task_id',
                               action='store',
                               required=True,
                               help='Task ID to query')
    return sample_util.process_cli_args(parser.parse_args())


def main():
    args = get_args()
    clients = DataProtectionClients(args)

    task = GetTask(clients.snapservice_client, args.task_id)
    print(task.get_task())


if __name__ == '__main__':
    main()
