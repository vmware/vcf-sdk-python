#!/usr/bin/env python

# Copyright (c) 2008-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

"""
Python program for powering on VMs
"""

from pyVmomi import vim, vmodl
from helpers import cli, service_instance
from helpers.tasks import wait_for_tasks


def main():
    """
    Simple command-line program for powering on virtual machines on a system.
    """

    parser = cli.Parser()
    parser.add_custom_argument('-v', '--vm-name', required=True, action='append',
                               help='Names of the Virtual Machines to power on')
    args = parser.get_args()
    # form a connection...
    si = service_instance.connect(args)

    try:
        vmnames = args.vm_name
        if not vmnames:
            print("No virtual machine specified for poweron")

        # Retreive the list of Virtual Machines from the inventory objects
        # under the rootFolder
        content = si.content
        obj_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                           [vim.VirtualMachine],
                                                           True)
        vm_list = obj_view.view
        obj_view.Destroy()

        # Find the vm and power it on
        tasks = [vm.PowerOn() for vm in vm_list if vm.name in vmnames]

        # Wait for power on to complete
        wait_for_tasks(si, tasks)

        print("Virtual Machine(s) have been powered on successfully")
    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)
    except Exception as error:
        print("Caught Exception : " + str(error))


# Start program
if __name__ == "__main__":
    main()
