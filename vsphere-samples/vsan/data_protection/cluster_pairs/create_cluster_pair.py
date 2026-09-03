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

from com.vmware.snapservice_client import *


class CreateClusterPair(object):

    def __init__(self, snapservice_client, args):
        self._snapservice_client = snapservice_client
        self._spec = ClusterPairs.CreateSpec(
            local_cluster=ClusterPairs.LocalClusterMemberSpec(
                cluster=args.local_cluster_mo_id
            ),
            peer_cluster=ClusterPairs.PeerClusterMemberSpec(
                site=args.peer_site_id,
                cluster=args.peer_cluster_mo_id
            )
        )

    def create_task(self):
        return self._snapservice_client.ClusterPairs.create_task(self._spec)

    def create_precheck_task(self):
        return self._snapservice_client.ClusterPairs.create_precheck_task(self._spec)


def get_args():
    parser = sample_cli.build_arg_parser()
    required_args = parser.add_argument_group('snapservice required arguments')
    required_args.add_argument('--snapservice',
                               action='store',
                               required=True,
                               help='Snapservice IP/hostname to connect to')
    required_args.add_argument('--local_cluster_mo_id',
                               action='store',
                               required=True,
                               help='Local cluster MO ID to create cluster pair')
    required_args.add_argument('--peer_site_id',
                               action='store',
                               required=True,
                               help='Peer site ID to create cluster pair')
    required_args.add_argument('--peer_cluster_mo_id',
                               action='store',
                               required=True,
                               help='Peer cluster MO ID to create cluster pair')
    parser.add_argument('--precheck',
                        action='store_true',
                        help='Whether it is a precheck task')
    return sample_util.process_cli_args(parser.parse_args())


def main():
    args = get_args()
    clients = DataProtectionClients(args)

    create_cluster_pair = CreateClusterPair(clients.snapservice_client, args)
    if args.precheck is True:
        print('Is a precheck task')
        task = create_cluster_pair.create_precheck_task()
        print('Create cluster pair precheck task:', task.task_id)
    else:
        print('Is not a precheck task')
        task = create_cluster_pair.create_task()
        print('Create cluster pair task:', task.task_id)

    wait_for_snapservice_task(clients.snapservice_client, task.task_id)


if __name__ == '__main__':
    main()
