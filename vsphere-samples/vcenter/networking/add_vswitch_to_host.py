#!/usr/bin/env python

# Copyright (c) 2016-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

"""
Written by nickcooper-zhangtonghao
Github: https://github.com/nickcooper-zhangtonghao
Email: nickcooper-zhangtonghao@opencloud.tech
Note: Example code For testing purposes only
"""
import sys
from pyVmomi import vim
from helpers import cli, service_instance


def get_vm_hosts(content):
    host_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                        [vim.HostSystem],
                                                        True)
    hosts = list(host_view.view)
    host_view.Destroy()
    return hosts


def add_hosts_switch(hosts, vswitch_name):
    for host in hosts:
        add_host_switch(host, vswitch_name)
    return True


def add_host_switch(host, vswitch_name):
    vswitch_spec = vim.host.VirtualSwitch.Specification()
    vswitch_spec.numPorts = 1024
    vswitch_spec.mtu = 1450
    host.configManager.networkSystem.AddVirtualSwitch(vswitch_name, vswitch_spec)


def main():
    """
    Sample for adding a virtual switch to host
    """
    parser = cli.Parser()
    parser.add_required_arguments(cli.Argument.VSWITCH_NAME)
    args = parser.get_args()
    si = service_instance.connect(args)
    content = si.RetrieveContent()

    hosts = get_vm_hosts(content)
    if add_hosts_switch(hosts, args.vswitch_name):
        print("vSwitch Added")


# Main section
if __name__ == "__main__":
    sys.exit(main())
