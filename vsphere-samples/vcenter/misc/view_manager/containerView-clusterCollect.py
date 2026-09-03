#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

import argparse
import ssl
import sys
from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect

# This sample demonstrates how to collect all ClusterComputeResource objects in a vCenter
# and map them to their respective Datacenter objects.

# Get the Datacenter for a given ClusterComputeResource
# This function traverses the parent chain of the cluster until it finds a Datacenter object.
def get_datacenter_for_cluster(cluster):
    parent = cluster.parent
    while parent:
        if isinstance(parent, vim.Datacenter):
            return parent
        parent = parent.parent
    return None

def main():
    parser = argparse.ArgumentParser(description='vCenter Cluster Collector - Collects all ClusterComputeResource objects and maps them to their respective Datacenter objects.')
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

    # Create a recursive view of all ClusterComputeResource objects
    # in the vCenter server.
    # This will include all clusters across all datacenters.
    cluster_view = content.viewManager.CreateContainerView(
        container=content.rootFolder,
        type=[vim.ClusterComputeResource],
        recursive=True
    )

    # Get all ClusterComputeResource objects
    clusters = cluster_view.view

    # Collect and map clusters to datacenters
    datacenter_clusters = {}

    for cluster in clusters:
        datacenter = get_datacenter_for_cluster(cluster)
        if datacenter:
            dc_name = datacenter.name
            if dc_name not in datacenter_clusters:
                datacenter_clusters[dc_name] = []
            datacenter_clusters[dc_name].append(cluster.name)

    # Print the mapping
    for dc_name, cluster_list in datacenter_clusters.items():
        print(f"Datacenter: {dc_name}")
        for cluster_name in cluster_list:
            print(f"  Cluster: {cluster_name}")

    # Cleanup
    cluster_view.Destroy()
    Disconnect(si)

if __name__ == "__main__":
    main()