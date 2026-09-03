#!/usr/bin/env python

# Copyright (c) 2017-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '6.5+'

from vmware.vapi.vsphere.client import create_vsphere_client

from com.vmware.vcenter.vm_client import Power

from helpers.common import sample_cli
from helpers.common import sample_util
from helpers.vm_helpers.vm_helper import get_vm
from helpers.common.ssl_helper import get_unverified_session


class DeleteVM(object):
    """
    Demonstrates Deleting User specified Virtual Machine (VM)
    Sample Prerequisites:
    vCenter/ESX
    """

    def __init__(self):
        parser = sample_cli.build_arg_parser()
        parser.add_argument('-n', '--vm_name',
                            action='store',
                            default='Sample_Default_VM_for_Simple_Testbed',
                            help='Name of the testing vm')
        args = sample_util.process_cli_args(parser.parse_args())
        self.vm_name = args.vm_name

        session = get_unverified_session() if args.skipverification else None

        # Connect to vSphere client
        self.client = create_vsphere_client(server=args.server,
                                            username=args.username,
                                            password=args.password,
                                            session=session)

    def run(self):
        """
        Delete User specified VM from Server
        """
        vm = get_vm(self.client, self.vm_name)
        if not vm:
            raise Exception('Sample requires an existing vm with name ({}).'
                            'Please create the vm first.'.format(self.vm_name))
        print("Deleting VM -- '{}-({})')".format(self.vm_name, vm))
        state = self.client.vcenter.vm.Power.get(vm)
        if state == Power.Info(state=Power.State.POWERED_ON):
            self.client.vcenter.vm.Power.stop(vm)
        elif state == Power.Info(state=Power.State.SUSPENDED):
            self.client.vcenter.vm.Power.start(vm)
            self.client.vcenter.vm.Power.stop(vm)
        self.client.vcenter.VM.delete(vm)
        print("Deleted VM -- '{}-({})".format(self.vm_name, vm))


def main():
    delete_vm = DeleteVM()
    delete_vm.run()


if __name__ == '__main__':
    main()
