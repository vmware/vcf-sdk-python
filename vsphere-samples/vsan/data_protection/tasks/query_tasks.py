#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '8.0.3+'

from helpers.common import sample_cli
from helpers.common import sample_util
from vsan.data_protection.data_protection_clients import DataProtectionClients

from com.vmware.snapservice_client import Tasks


class QueryTasks(object):
    def __init__(self, snapservice_client):
        self._snapservice_client = snapservice_client

    def list(self):
        return self._snapservice_client.Tasks.list()

    def list_by_filter(self, filter_spec):
        return self._snapservice_client.Tasks.list(filter=filter_spec)


def get_args():
    parser = sample_cli.build_arg_parser()
    required_args = parser.add_argument_group('snapservice required arguments')
    required_args.add_argument('--snapservice',
                               action='store',
                               required=True,
                               help='Snapservice IP/hostname to connect to')
    return sample_util.process_cli_args(parser.parse_args())


def main():
    args = get_args()
    clients = DataProtectionClients(args)

    tasks = QueryTasks(clients.snapservice_client)

    # List all tasks
    list_tasks = tasks.list()
    print("List of tasks:")
    print("----------------------------------------")
    for task in list_tasks.items:
        print(task)
        print("----------------------------------------")

    # List filtered tasks
    print("List of filtered tasks:")
    print("----------------------------------------")
    # See the Tasks.FilterSpec class constructor for other filters
    filter_spec = Tasks.FilterSpec(operations={'create'})
    filtered_tasks = tasks.list_by_filter(filter_spec)
    for task in filtered_tasks.items:
        print(task)
        print("----------------------------------------")


if __name__ == '__main__':
    main()
