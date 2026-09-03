#!/usr/bin/env python

# Copyright (c) 2016-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '6.5+'

from com.vmware.vcenter_client import Cluster

from helpers.vm_helpers import datacenter_helper


def get_cluster(client, datacenter_name, cluster_name):
    """
    Returns the identifier of a cluster
    Note: The method assumes only one cluster and datacenter
    with the mentioned name.
    """

    datacenter = datacenter_helper.get_datacenter(client, datacenter_name)
    if not datacenter:
        print("Datacenter '{}' not found".format(datacenter_name))
        return None

    filter_spec = Cluster.FilterSpec(names=set([cluster_name]),
                                     datacenters=set([datacenter]))

    cluster_summaries = client.vcenter.Cluster.list(filter_spec)
    if len(cluster_summaries) > 0:
        cluster = cluster_summaries[0].cluster
        print("Detected cluster '{}' as {}".format(cluster_name, cluster))
        return cluster
    else:
        print("Cluster '{}' not found".format(cluster_name))
        return None
