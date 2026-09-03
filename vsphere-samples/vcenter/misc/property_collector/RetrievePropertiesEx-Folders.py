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


def main():
    parser = argparse.ArgumentParser(description='RetrieveProperties of all folder')
    parser.add_argument("--vcip", help="vc ip address")
    parser.add_argument("--user", help="SSO domain user")
    parser.add_argument("--password", help="SSO domain user password")

    if len(sys.argv) < 3:
        parser.print_help()
        sys.exit(0)

    params = parser.parse_args()

    # Disable SSL certificate verification
    sslctx = ssl._create_unverified_context()

    # Connect to the vCenter server
    si = SmartConnect(host=params.vcip, user=params.user, pwd=params.password, sslContext=sslctx)

    # Create recursive container view from the root, listing all folders.
    containerView = si.content.viewManager.CreateContainerView(
            container=si.content.rootFolder,
            type=[vim.Folder],
            recursive=True)

    #Specify that we will use container view for traversal
    traversalSpec = vmodl.query.PropertyCollector.TraversalSpec()
    traversalSpec.name = 'traverseEntries'
    traversalSpec.path = 'view'
    traversalSpec.skip = False
    traversalSpec.type = vim.ContainerView

    # Creating the object spec to be used for the filter
    # The object spec specifies the type of object and the traversal spec to be used
    objSpec = vmodl.query.PropertyCollector.ObjectSpec(obj=containerView, selectSet=[traversalSpec])

    properties = ["name", "childEntity"]

    # Creating the property spec to be used for the filter
    # The property spec specifies the type of object and the properties to be retrieved
    propSpec = vmodl.query.PropertyCollector.PropertySpec()
    propSpec.type = vim.Folder
    propSpec.pathSet = properties

    # Creating the filter spec to be used for the filter
    # The filter spec combines the object spec and the property spec
    filterSpec = vmodl.query.PropertyCollector.FilterSpec()
    filterSpec.objectSet = [objSpec]
    filterSpec.propSet = [propSpec]

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