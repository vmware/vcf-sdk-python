#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

import argparse
from pyVmomi import vim, vmodl
from pyVim.connect import SmartConnect, Disconnect

import ssl
import sys

# This sample demonstrates how to retrieve properties of all folders
# It uses the PropertyCollector to retrieve properties of the specified type

# Helper function, printResult, to print the result of the RetrievePropertiesEx call
# The result is a list of objects, each object contains the properties of the object
# The token is used to identify the next set of properties
# The token is passed to the ContinueRetrievePropertiesEx method to retrieve the next set of properties
def printResult(result):
    print("Token: ", result.token)
    for obj in result.objects:
        folder = obj.obj
        propSet = obj.propSet
        print("Folder: ", folder)
        for prop in propSet:
            print("Property: ", prop.name, " Value: ", prop.val)
        print("===================================")


# Create a traversal spec to traverse the entire inventory
# This includes all resource pools, VMs, hosts, datastores, and folders
# The traversal spec is used to specify the path to traverse and the type of object to traverse
# The selection spec is used to specify the type of object to select

def build_full_traversal():
    traversal_spec = vmodl.query.PropertyCollector.TraversalSpec
    selection_spec = vmodl.query.PropertyCollector.SelectionSpec

    # Recurse through all resourcepools
    rp_to_rp = traversal_spec(name='rpToRp', type=vim.ResourcePool, path="resourcePool", skip=False)

    rp_to_rp.selectSet.extend(
        (
            selection_spec(name="rpToRp"),
            selection_spec(name="rpToVm"),
        )
    )

    rp_to_vm = traversal_spec(name='rpToVm', type=vim.ResourcePool, path="vm", skip=False)

    # Traversal through resourcepool branch
    cr_to_rp = traversal_spec(
        name='crToRp', type=vim.ComputeResource, path='resourcePool', skip=False)
    cr_to_rp.selectSet.extend(
        (
            selection_spec(name='rpToRp'),
            selection_spec(name='rpToVm'),
        )
    )

    # Traversal through host branch
    cr_to_h = traversal_spec(name='crToH', type=vim.ComputeResource, path='host', skip=False)

    # Traversal through hostFolder branch
    dc_to_hf = traversal_spec(name='dcToHf', type=vim.Datacenter, path='hostFolder', skip=False)
    dc_to_hf.selectSet.extend(
        (
            selection_spec(name='visitFolders'),
        )
    )

    # Traversal through vmFolder branch
    dc_to_vmf = traversal_spec(name='dcToVmf', type=vim.Datacenter, path='vmFolder', skip=False)
    dc_to_vmf.selectSet.extend(
        (
            selection_spec(name='visitFolders'),
        )
    )

    # Traversal through network folder branch
    dc_to_net = traversal_spec(
        name='dcToNet', type=vim.Datacenter, path='networkFolder', skip=False)
    dc_to_net.selectSet.extend(
        (
            selection_spec(name='visitFolders'),
        )
    )

    # Traversal through datastore branch
    dc_to_ds = traversal_spec(name='dcToDs', type=vim.Datacenter, path='datastore', skip=False)
    dc_to_ds.selectSet.extend(
        (
            selection_spec(name='visitFolders'),
        )
    )

    # Recurse through all hosts
    h_to_vm = traversal_spec(name='hToVm', type=vim.HostSystem, path='vm', skip=False)
    h_to_vm.selectSet.extend(
        (
            selection_spec(name='visitFolders'),
        )
    )

    # Recurse through the folders
    visit_folders = traversal_spec(
        name='visitFolders', type=vim.Folder, path='childEntity', skip=False)
    visit_folders.selectSet.extend(
        (
            selection_spec(name='visitFolders'),
            selection_spec(name='dcToHf'),
            selection_spec(name='dcToVmf'),
            selection_spec(name='dcToNet'),
            selection_spec(name='crToH'),
            selection_spec(name='crToRp'),
            selection_spec(name='dcToDs'),
            selection_spec(name='hToVm'),
            selection_spec(name='rpToVm'),
        )
    )

    full_traversal = selection_spec.Array(
        (visit_folders, dc_to_hf, dc_to_vmf, dc_to_net, cr_to_h, cr_to_rp, dc_to_ds, rp_to_rp,
         h_to_vm, rp_to_vm,))

    return full_traversal


def main():
    parser = argparse.ArgumentParser(description='RetrieveProperties of all folder')
    parser.add_argument("--vcip", help="vc ip address")
    parser.add_argument("--user", help="SSO domain user")
    parser.add_argument("--password", help="SSO domain user password")

    if len(sys.argv) < 3:
        parser.print_help()
        sys.exit(0)

    params = parser.parse_args()

    sslctx = ssl._create_unverified_context()
    si = SmartConnect(host=params.vcip, user=params.user, pwd=params.password, sslContext=sslctx);			

    #Specify that we will use traversal spec for traversal

    # Create a traversal spec to traverse the entire inventory
    # This includes all resource pools, VMs, hosts, datastores, and folders
    traversal  = build_full_traversal()
        
    # Specify the object spec to be used for the filter
    # The object spec specifies the type of object to retrieve properties for
    objSpec = vmodl.query.PropertyCollector.ObjectSpec(obj=si.content.rootFolder, selectSet=traversal)

    # Specify the property spec to be used for the filter
    # The property spec specifies the properties to retrieve and the type of object to retrieve properties for
    propSpec_folder = vmodl.query.PropertyCollector.PropertySpec()
    propSpec_folder.type = vim.Folder
    propSpec_folder.pathSet = ["name", "childEntity"]

    propSpec_vm = vmodl.query.PropertyCollector.PropertySpec()
    propSpec_vm.type = vim.VirtualMachine
    propSpec_vm.pathSet = ["name", "runtime.powerState", "runtime.host"]

    # Specify the filter spec to be used for the retrival 
    # It combines the object spec and property spec
    filterSpec = vmodl.query.PropertyCollector.FilterSpec()
    filterSpec.objectSet = [objSpec]
    filterSpec.propSet = [propSpec_folder, propSpec_vm]

    # The maxObjects property specifies the maximum number of objects to retrieve in single call
    resrieveOptions = vmodl.query.PropertyCollector.RetrieveOptions()
    resrieveOptions.maxObjects = 1 # 1 object per call

    token = None

    try:
        propertyCollector = si.content.propertyCollector

        # First call to RetrievePropertiesEx will return the first set of properties
        # The result will contain the properties of the first set of objects
        result = propertyCollector.RetrievePropertiesEx([filterSpec], resrieveOptions)
        
        # The token is used to identify the next set of properties
        # It must be passed to the ContinueRetrievePropertiesEx method to retrieve the next set of properties
        token = result.token
        
        # Print the properties of the first set of objects
        printResult(result)

        # If there are more properties to retrieve, continue retrieving
        # token != None means there are more properties to retrieve
        while token:
            # This will return the next set of properties
            # The token is used to identify the next set of properties
            result = propertyCollector.ContinueRetrievePropertiesEx(token)
            token = result.token
            printResult(result)

    except KeyboardInterrupt:
        print("\nInterrupted...")

    if token:
        # If token != None here, means there are more properties to retrieve, but we got interrupted
        # We need to cancel the retrieve
        result = propertyCollector.CancelRetrievePropertiesEx(token)

    # Disconnect from the vCenter server
    Disconnect(si)

if __name__ == "__main__":
    main()