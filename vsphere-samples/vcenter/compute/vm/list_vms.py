#!/usr/bin/env python

# Copyright (c) 2016-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '6.5+'

from pprint import pprint

from vmware.vapi.vsphere.client import create_vsphere_client

from helpers.common import sample_cli
from helpers.common import sample_util
from helpers.common.ssl_helper import get_unverified_session


class ListVM(object):
    """
    Demonstrates getting list of VMs present in vCenter
    Sample Prerequisites:
    vCenter/ESX
    """
    def __init__(self):
        parser = sample_cli.build_arg_parser()
        args = sample_util.process_cli_args(parser.parse_args())
        session = get_unverified_session() if args.skipverification else None
        self.client = create_vsphere_client(server=args.server,
                                            username=args.username,
                                            password=args.password,
                                            session=session)

    def run(self):
        """
        List VMs present in server
        """
        list_of_vms = self.client.vcenter.VM.list()
        print("----------------------------")
        print("List Of VMs")
        print("----------------------------")
        pprint(list_of_vms)
        print("----------------------------")


def main():
    list_vm = ListVM()
    list_vm.run()


if __name__ == '__main__':
    main()
