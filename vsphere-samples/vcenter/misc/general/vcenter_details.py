#!/usr/bin/env python

# Copyright (c) 2008-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

"""
Python program for listing the VMs on an ESX / vCenter host
"""

from pyVmomi import vmodl
from pyVmomi import vim

from helpers import cli, service_instance, vm


def parse_service_instance(si):
    """
    Print some basic knowledge about your environment as a Hello World
    equivalent for pyVmomi
    """

    content = si.RetrieveContent()
    object_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                          [], True)
    for obj in object_view.view:
        print(obj)
        if isinstance(obj, vim.VirtualMachine):
            vm.print_vm_info(obj)

    object_view.Destroy()
    return 0


def main():
    """
    Simple command-line program for listing the virtual machines on a system.
    """

    parser = cli.Parser()
    args = parser.get_args()

    try:
        si = service_instance.connect(args)

        # ## Do the actual parsing of data ## #
        parse_service_instance(si)

    except vmodl.MethodFault as ex:
        print("Caught vmodl fault : {}".format(ex.msg))
        return -1

    return 0


# Start program
if __name__ == "__main__":
    main()
