#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '8.0.3+'

from helpers.common import sample_cli
from helpers.common import sample_util
from vsan.data_protection.data_protection_clients import DataProtectionClients


class Info(object):
    def __init__(self, snapservice_client):
        self._snapservice_client = snapservice_client

    def get_about(self):
        return self._snapservice_client.info.About.get()


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

    info = Info(clients.snapservice_client)
    print("----------------------------------------")
    print("About:")
    print(info.get_about())


if __name__ == '__main__':
    main()
