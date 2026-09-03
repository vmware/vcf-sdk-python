#!/usr/bin/env python

# Copyright (c) 2016-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0


import pyVim.task
from pyVmomi import vim
from helpers.common.vim.inventory import get_datastore_mo

from helpers.common.vim import datastore_file


def create_vmdk(service_instance, datacenter_mo, datastore_path):
    """Create vmdk in specific datacenter"""
    vdm = service_instance.content.virtualDiskManager
    task = vdm.CreateVirtualDisk(
        datastore_path, datacenter_mo,
        vim.VirtualDiskManager.SeSparseVirtualDiskSpec(
            diskType='seSparse', adapterType='lsiLogic',
            capacityKb=1024 * 1024 * 4))
    pyVim.task.WaitForTask(task)
    print("Created VMDK '{}' in Datacenter '{}'".
          format(datastore_path, datacenter_mo.name))
    return task.info.result


def delete_vmdk(service_instance, datacenter_mo, datastore_path):
    """Delete vmdk from specific datastore"""
    vdm = service_instance.content.virtualDiskManager
    task = vdm.DeleteVirtualDisk(datastore_path, datacenter_mo)
    pyVim.task.WaitForTask(task)


def detect_vmdk(client, soap_stub, datacenter_name, datastore_name,
                datastore_path):
    """Find vmdk in specific datastore"""
    datastore_mo = get_datastore_mo(client,
                                    soap_stub,
                                    datacenter_name,
                                    datastore_name)
    if not datastore_mo:
        return False

    dsfile = datastore_file.File(datastore_mo)
    if dsfile.exists(datastore_path):
        return True
    else:
        return False
