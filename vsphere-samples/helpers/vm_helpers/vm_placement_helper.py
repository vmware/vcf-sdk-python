#!/usr/bin/env python

# Copyright (c) 2016-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '6.5+'

from com.vmware.vcenter_client import VM

from helpers.vm_helpers import datastore_helper
from helpers.vm_helpers import folder_helper
from helpers.vm_helpers import resource_pool_helper


def get_placement_spec_for_resource_pool(client,
                                         datacenter_name,
                                         vm_folder_name,
                                         datastore_name):
    """
    Returns a VM placement spec for a resourcepool. Ensures that the
    vm folder and datastore are all in the same datacenter which is specified.
    """
    resource_pool = resource_pool_helper.get_resource_pool(client,
                                                           datacenter_name)

    folder = folder_helper.get_folder(client,
                                      datacenter_name,
                                      vm_folder_name)

    datastore = datastore_helper.get_datastore(client,
                                               datacenter_name,
                                               datastore_name)

    # Create the vm placement spec with the datastore, resource pool and vm
    # folder
    placement_spec = VM.PlacementSpec(folder=folder,
                                      resource_pool=resource_pool,
                                      datastore=datastore)

    print("get_placement_spec_for_resource_pool: Result is '{}'".
          format(placement_spec))
    return placement_spec
