#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

import argparse
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

import ssl
import sys

# This sample demonstrates how to collect all ClusterComputeResource objects in single datacenter
def main():
    parser = argparse.ArgumentParser(description='vCenter Cluster Collector - Collects all ClusterComputeResource objects in single Datacenter.')
    parser.add_argument("--vcip", help="vc ip address")
    parser.add_argument("--user", help="SSO domain user")
    parser.add_argument("--password", help="SSO domain user password")

    if len(sys.argv) < 3:
        parser.print_help()
        sys.exit(0)

    params = parser.parse_args()

    sslctx = ssl._create_unverified_context()
    si = SmartConnect(host=params.vcip, user=params.user, pwd=params.password, sslContext=sslctx);			

    content = si.RetrieveContent()

    # Let's assume we already know the datacenter name
    datacenter_name = "DataCenter"

    # Find the Datacenter object
    datacenter = next(
        (dc for dc in content.rootFolder.childEntity if isinstance(dc, vim.Datacenter) and dc.name == datacenter_name),
        None
    )

    if not datacenter:
        print(f"Datacenter '{datacenter_name}' not found.")
        return

    # Create a recursive container view starting from hostFolder
    container_view = content.viewManager.CreateContainerView(
        container=datacenter.hostFolder,
        type=[vim.ClusterComputeResource],
        recursive=True
    )

    clusters = container_view.view
    container_view.Destroy()

    print(f"Clusters in Datacenter '{datacenter.name}':")
    for cluster in clusters:
        print(f"  - {cluster.name}")

    Disconnect(si)

if __name__ == "__main__":
    main()