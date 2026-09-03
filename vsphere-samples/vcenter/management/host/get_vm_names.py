#!/usr/bin/env python

# Copyright (c) 2017-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

"""
Python program for flat text listing the VMs on an
ESX / vCenter, host one per line.
"""
from helpers import cli, service_instance

MAX_DEPTH = 10


def print_vminfo(vm, depth=1):
    """
    Print information for a particular virtual machine or recurse into a folder
    with depth protection
    """

    # if this is a group it will have children. if it does, recurse into them
    # and then return
    if hasattr(vm, 'childEntity'):
        if depth > MAX_DEPTH:
            return
        vmlist = vm.childEntity
        for child in vmlist:
            print_vminfo(child, depth+1)
        return

    summary = vm.summary
    print(summary.config.name)


def main():
    """
    Simple command-line program for listing the virtual machines on a host.
    """

    parser = cli.Parser()
    args = parser.get_args()
    si = service_instance.connect(args)

    content = si.RetrieveContent()
    for child in content.rootFolder.childEntity:
        if hasattr(child, 'vmFolder'):
            datacenter = child
            vmfolder = datacenter.vmFolder
            vmlist = vmfolder.childEntity
            for vm in vmlist:
                print_vminfo(vm)


# Start program
if __name__ == "__main__":
    main()
