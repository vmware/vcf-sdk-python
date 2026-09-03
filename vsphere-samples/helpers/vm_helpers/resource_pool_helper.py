#!/usr/bin/env python

# Copyright (c) 2016-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '6.5+'

from com.vmware.vcenter_client import ResourcePool

from helpers.vm_helpers import datacenter_helper


def get_resource_pool(client, datacenter_name, resource_pool_name=None):
    """
    Returns the identifier of the resource pool with the given name or the
    first resource pool in the datacenter if the name is not provided.
    """
    datacenter = datacenter_helper.get_datacenter(client, datacenter_name)
    if not datacenter:
        print("Datacenter '{}' not found".format(datacenter_name))
        return None

    names = set([resource_pool_name]) if resource_pool_name else None
    filter_spec = ResourcePool.FilterSpec(datacenters=set([datacenter]),
                                          names=names)

    resource_pool_summaries = client.vcenter.ResourcePool.list(filter_spec)
    if len(resource_pool_summaries) > 0:
        resource_pool = resource_pool_summaries[0].resource_pool
        print("Selecting ResourcePool '{}'".format(resource_pool))
        return resource_pool
    else:
        print("ResourcePool not found in Datacenter '{}'".
              format(datacenter_name))
        return None
