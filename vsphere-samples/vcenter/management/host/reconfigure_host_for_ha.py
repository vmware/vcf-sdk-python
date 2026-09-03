#!/usr/bin/env python

# Copyright (c) 2016-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

"""
Written by Juan Manuel Rey
Github: https://github.com/jreypo
Blog: http://blog.jreypo.io/

vSphere Python SDK script to force the HA reconfiguration in an ESXi host
Tested with vSphere 6.0 U1
"""

from pyVmomi import vim
from helpers import tasks, cli, service_instance


def main():
    parser = cli.Parser()
    parser.add_required_arguments(cli.Argument.ESX_IP)
    args = parser.get_args()
    si = service_instance.connect(args)

    content = si.RetrieveContent()
    object_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                          [vim.HostSystem],
                                                          True)

    host_list = object_view.view
    object_view.Destroy()

    for host in host_list:
        if host.name == args.esx_ip:
            esx = host

    print("Proceeding to execute operation 'Reconfigure for HA' in host %s" % esx.name)
    reconf_ha = esx.ReconfigureHostForDAS_Task()
    task = reconf_ha
    tasks.wait_for_tasks(si, [task])
    print("Operation complete")

    return 0


# Main execution
if __name__ == "__main__":
    main()
