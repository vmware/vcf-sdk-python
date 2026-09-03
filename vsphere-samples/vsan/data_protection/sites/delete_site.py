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


class DeleteSite(object):
    def __init__(self, snapservice_client, args):
        self._snapservice_client = snapservice_client
        self._args = args

    def delete_task(self):
        spec = Sites.DeleteSpec(
            vcenter_creds=Sites.UserCredentials(user=self._args.remote_vc_user, password=self._args.remote_vc_password))
        options = Sites.DeleteOptions(exclude_hms=False)
        return self._snapservice_client.Sites.delete_task(self._args.remote_site_id, spec, options=options)


def get_args():
    parser = sample_cli.build_arg_parser()
    required_args = parser.add_argument_group('snapservice required arguments')
    required_args.add_argument('--snapservice',
                               action='store',
                               required=True,
                               help='Snapservice IP/hostname to connect to')
    required_args.add_argument('--remote_vc_user',
                               action='store',
                               required=True,
                               help='Remote VC username for site pairing')
    required_args.add_argument('--remote_vc_password',
                               action='store',
                               required=True,
                               help='Remote VC password for site pairing')
    required_args.add_argument('--remote_site_id',
                               action='store',
                               required=True,
                               help='Remote site ID to delete')
    return sample_util.process_cli_args(parser.parse_args())


def main():
    args = get_args()
    clients = DataProtectionClients(args)

    delete_site = DeleteSite(clients.snapservice_client, args)
    delete_task = delete_site.delete_task()

    print('Delete site task:')
    print('----------------------------------------')
    print(delete_task.task_id)
    print('----------------------------------------')

    wait_for_snapservice_task(clients.snapservice_client, delete_task.task_id)


if __name__ == '__main__':
    main()
