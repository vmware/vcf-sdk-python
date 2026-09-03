#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '8.0.3+'

from helpers.common import sample_cli
from helpers.common import sample_util
from vsan.data_protection.data_protection_clients import DataProtectionClients


class ClusterPairs(object):

    def __init__(self, snapservice_client):
        self._snapservice_client = snapservice_client

    def list(self):
        return self._snapservice_client.ClusterPairs.list()

    def get(self, cluster_pair_id):
        return self._snapservice_client.ClusterPairs.get(cluster_pair_id)


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

    cluster_pairs = ClusterPairs(clients.snapservice_client)
    cps = cluster_pairs.list()

    print("List of cluster pairs:")
    print("----------------------------------------")
    cluster_pair_id = None
    for cp in cps.items:
        print(cp)
        print("----------------------------------------")
        cluster_pair_id = cp.cluster_pair

    print('\nGet cluster pair for id: {}'.format(cluster_pair_id))
    print("----------------------------------------")
    if cluster_pair_id is not None:
        cp = cluster_pairs.get(cluster_pair_id)
        print(cp)


if __name__ == '__main__':
    main()
