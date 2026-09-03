#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '8.0.3+'

from helpers.common import sample_cli
from helpers.common import sample_util
from vsan.data_protection.data_protection_clients import DataProtectionClients


class Sites(object):
    def __init__(self, snapservice_client):
        self._snapservice_client = snapservice_client

    def list(self):
        return self._snapservice_client.Sites.list()

    def get(self, site_id):
        return self._snapservice_client.Sites.get(site_id)


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

    sites = Sites(clients.snapservice_client)
    list_sites = sites.list()

    print("List of sites:")
    print("----------------------------------------")
    local_site_id = None
    for site in list_sites.items:
        print(site)
        print("----------------------------------------")
        if site.summary.local is True:
            local_site_id = site.site

    if local_site_id is not None:
        local_site = sites.get(local_site_id)
        print("\nLocal site:")
        print("----------------------------------------")
        print(local_site)
        print("----------------------------------------")


if __name__ == '__main__':
    main()
