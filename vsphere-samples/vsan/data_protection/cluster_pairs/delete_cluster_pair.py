#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '8.0.3+'

from helpers.common import sample_cli
from helpers.common import sample_util
from vsan.data_protection.data_protection_clients import DataProtectionClients
from vsan.data_protection.tasks.task_utils import wait_for_snapservice_task


class DeleteClusterPair(object):

    def __init__(self, snapservice_client):
        self._snapservice_client = snapservice_client

    def delete_task(self, cluster_pair_id):
        return self._snapservice_client.ClusterPairs.delete_task(cluster_pair_id)


def get_args():
    parser = sample_cli.build_arg_parser()
    required_args = parser.add_argument_group('snapservice required arguments')
    required_args.add_argument('--snapservice',
                               action='store',
                               required=True,
                               help='Snapservice IP/hostname to connect to')
    required_args.add_argument('--cluster_pair_id',
                               action='store',
                               required=True,
                               help='Cluster pair ID to delete')
    return sample_util.process_cli_args(parser.parse_args())


def main():
    args = get_args()
    clients = DataProtectionClients(args)

    delete_cluster_pairs = DeleteClusterPair(clients.snapservice_client)
    delete_task = delete_cluster_pairs.delete_task(args.cluster_pair_id)

    print('Delete cluster pair task:', delete_task.task_id)
    wait_for_snapservice_task(clients.snapservice_client, delete_task.task_id)


if __name__ == '__main__':
    main()
