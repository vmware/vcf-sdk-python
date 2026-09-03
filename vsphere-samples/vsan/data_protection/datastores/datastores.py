#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '8.0.3+'

from helpers.common import sample_cli
from helpers.common import sample_util
from vsan.data_protection.data_protection_clients import DataProtectionClients


class Datastores(object):

    def __init__(self, snapservice_client):
        self._snapservice_client = snapservice_client

    def list(self, site_id):
        return self._snapservice_client.sites.Datastores.list(site_id)


def get_args():
    parser = sample_cli.build_arg_parser()
    required_args = parser.add_argument_group('snapservice required arguments')
    required_args.add_argument('--snapservice',
                               action='store',
                               required=True,
                               help='Snapservice IP/hostname to connect to')
    required_args.add_argument('--site_id',
                               action='store',
                               required=True,
                               help='Site id where datastores locate')
    return sample_util.process_cli_args(parser.parse_args())


def main():
    args = get_args()
    clients = DataProtectionClients(args)

    datastores = Datastores(clients.snapservice_client)


    print('\nList datastores for : {}'.format(args.site_id))
    print("----------------------------------------")

    dsList = datastores.list(args.site_id)
    print(dsList)


if __name__ == '__main__':
    main()
