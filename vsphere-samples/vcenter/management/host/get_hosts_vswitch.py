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

from pyVmomi import vim
from helpers import cli, service_instance
import sys


def get_vm_hosts(content):
    host_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                        [vim.HostSystem],
                                                        True)
    hosts = list(host_view.view)
    host_view.Destroy()
    return hosts


def get_hosts_switches(hosts):
    host_switches_dict = {}
    for host in hosts:
        switches = host.config.network.vswitch
        host_switches_dict[host] = switches
    return host_switches_dict


def main():
    parser = cli.Parser()
    args = parser.get_args()
    si = service_instance.connect(args)
    content = si.RetrieveContent()

    hosts = get_vm_hosts(content)
    host_switches_dict = get_hosts_switches(hosts)
    if host_switches_dict is not None:
        print("The vSwitches are:\n")
    for host, vswithes in host_switches_dict.items():
        for vswitch in vswithes:
            print(vswitch.name)


# Main section
if __name__ == "__main__":
    sys.exit(main())
