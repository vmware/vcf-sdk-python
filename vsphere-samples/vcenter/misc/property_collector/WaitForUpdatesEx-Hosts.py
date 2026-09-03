#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

import argparse
from datetime import datetime

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl

import ssl
import sys

# This sample demonstrates how to watch for property changes on a host system
# It uses the PropertyCollector to watch for changes to the properties 
# specified in the property spec. The sample will run for predefined number
# of iterations or until interrupted. The sample will print the changes to 
# the properties specified in the property spec, the kind of change (enter,
# modify, leave), the moref of the object, time of the change and value of
# the changed properties.

def main():
    parser = argparse.ArgumentParser(
        description='Watch host property change: name and summary.quickStats ' \
        'properties with waitForUpdatesEx') 

    parser.add_argument("--vcip", help="vc ip address")
    parser.add_argument("--user", help="SSO domain user")
    parser.add_argument("--password", help="SSO domain user password")

    if len(sys.argv) < 3:
        parser.print_help()
        sys.exit(0)

    # Parse the command line arguments
    params = parser.parse_args()

    # Disable SSL certificate verification
    sslctx = ssl._create_unverified_context()

    # Connect to the vCenter server
    # The SmartConnect function will return a service instance object
    si = SmartConnect(host=params.vcip, user=params.user, pwd=params.password, sslContext=sslctx);		

    # Create recursive container view from the root, listing all Hosts.
    containerView = si.content.viewManager.CreateContainerView(
            container=si.content.rootFolder,
            type=[vim.HostSystem],
            recursive=True)

    #Specify that we will use container viewfor traversal
    traversalSpec = vmodl.query.PropertyCollector.TraversalSpec()
    traversalSpec.name = 'traverseEntries'
    traversalSpec.path = 'view'
    traversalSpec.skip = False
    traversalSpec.type = vim.ContainerView
        
    #Specify the object spec to be used for the filter
    objSpec = vmodl.query.PropertyCollector.ObjectSpec(obj=containerView, selectSet=[traversalSpec])

    #List which properties we need.
    properties = ["name", "summary.quickStats"]

    #Specify the property spec to be used for the filter 
    propSpec = vmodl.query.PropertyCollector.PropertySpec()
    propSpec.type = vim.HostSystem
    propSpec.pathSet = properties

    #Specify the filter spec to be used for the filter
    filterSpec = vmodl.query.PropertyCollector.FilterSpec()
    filterSpec.objectSet = [objSpec]
    filterSpec.propSet = [propSpec]

    #Create the filter
    #The filter will be used to watch for changes to the properties specified in the property spec
    propertyCollector = si.content.propertyCollector
    filter = propertyCollector.CreateFilter(filterSpec, True)

    #Create wait options
    #The wait options specify how long to wait for updates and how many updates to return
    #The maxWaitSeconds specifies the maximum time to wait for updates in seconds
    #The maxObjectUpdates specifies the maximum number of updates to return
    waitopts = vmodl.query.PropertyCollector.WaitOptions()
    waitopts.maxWaitSeconds = 1     # Intentually low to demostrate the waitForUpdatsEx timeout
    waitopts.maxObjectUpdates = 1   # Intentually low to demostrate the waitForUpdatsEx updates pagination

    #Define max number of iterations for the sample to run
    #If None, the sample will run indefinitely
    iterations = 10

    # Version is used to track the version of the updates
    # The version is passed to the WaitForUpdatesEx method to retrieve the next set of updates
    # and is updated with the version of the updates returned by the WaitForUpdatesEx method
    # Initial version is set to empty string
    version = ""

    try:
        while True:
            if iterations is not None:
                if iterations <= 0:
                    print('Iteration limit reached, monitoring stopped')
                    break
            
            # Call WaitForUpdatesEx to wait for updates to the properties specified in the property spec
            result = propertyCollector.WaitForUpdatesEx(version, waitopts)

            # Timeout, call again
            if result:
                # Process results    
                for filter_set in result.filterSet:
                    for object_set in filter_set.objectSet:
                        moref = object_set.obj
                        kind = object_set.kind
                        
                        if kind in ('enter', 'modify'):
                            change_set = object_set.changeSet
                            
                            print("== %s: %s %s ==" % (datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"), kind, moref))
                            for change in change_set:
                                print('%s: %s' % (change.name,  change.val))

                            print('\n')
                        elif kind == 'leave':
                            print("== %s: %s %s ==" % (datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"), kind, moref))
                            print('(removed)\n')

                # Update the version with the version of the updates returned by the WaitForUpdatesEx method
                version = result.version
            else:
                print("== %s: No updates ==" % datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"))
                print('(timeout)\n')
        
            if (result is None) and (iterations is not None):
                iterations -= 1
                print('Iterations left: %s \n' % iterations)

    except KeyboardInterrupt:
        # Cleanup
        print("\nInterrupted...")

    filter.Destroy()
    Disconnect(si)

if __name__ == "__main__":
    main()