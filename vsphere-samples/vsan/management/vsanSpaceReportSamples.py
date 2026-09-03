#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

"""
This file includes sample code for vCenter side vSAN space reporting
API QuerySpaceUsage accessing.

To provide an example of vSAN space reporting API access, it shows how to get
vSAN space usage result, including following types:
- vSAN Effective Capacity Overview
- vSAN Effective Space Usage Breakdown
- vSAN Data Reduction (Deduplication / Compression) is Enabled
- vSAN Standard Space Usage Overview
- vSAN Standard Usage Breakdown View
...

"""


import sys
import ssl
import atexit
import argparse
import getpass
if sys.version[0] < '3':
   input = raw_input
sys.path.append("/usr/lib64/vmware-vpx/vsan-health/")
sys.path.append("/usr/lib/vmware/site-packages/")
from pyVim.connect import SmartConnect, Disconnect

import pyVmomi
from vsanapiutils import GetLatestVmodlVersion, GetVsanVcMos, \
   IsEsaAutoRaidEnabledInCluster, ConnectToSpbm, GetVsanStorageProfile, \
   IsAutoManagedRAIDEnabledInProfile, GetLocalVsanDatastore

def GetArgs():
   """
   Supports the command-line arguments listed below.
   """
   parser = argparse.ArgumentParser(
       description=
       'vSAN SDK sample application for vSAN space reporting API usage. '
       'It queries the space usage information for the specific cluster '
       'and print out the current space usage information, including total '
       'capacity usage overview, space efficiency status and capacity usage '
       'breakdown, etc.')
   parser.add_argument('-v', '--vc', required=True, action='store',
                       help='Remote vCenter Server to connect to')
   parser.add_argument('-o', '--port', type=int, default=443, action='store',
                       help='Port to connect on, default is 443')
   parser.add_argument('-u', '--user', required=True, action='store',
                       help='User name to use when connecting to '
                            'vCenter Server')
   parser.add_argument('-p', '--password', required=False, action='store',
                       help='Password to use when connecting to vCenter '
                            'Server. If not provided, it will prompt to '
                            'ask for manually inputting the password')
   parser.add_argument('--cluster', dest='clusterName', metavar="CLUSTER",
                      default='VSAN-Cluster',
                      help='The name of the vSAN cluster which the space usage '
                           'query is going to perform on')
   args = parser.parse_args()
   return args

def GetClusterInstance(clusterName, serviceInstance):
   content = serviceInstance.RetrieveContent()
   searchIndex = content.searchIndex
   datacenters = content.rootFolder.childEntity
   for datacenter in datacenters:
      cluster = searchIndex.FindChild(datacenter.hostFolder, clusterName)
      if cluster is not None:
         return cluster
   return None

def ConnectToServers(args, sslContext):
   """
   Creates connections to the vCenter, vSAN and vSAN space reporting system
   @param args
   @return vc service instance, cluster, vSAN space reporting system
   """
   if args.password:
      password = args.password
   else:
      password = getpass.getpass(prompt='Enter password for vc %s and '
                                        'user %s: ' % (args.vc, args.user))

   # Connect to vCenter, get vc service instance
   si = SmartConnect(host=args.vc,
                     user=args.user,
                     pwd=password,
                     port=int(args.port),
                     sslContext=sslContext)

   atexit.register(Disconnect, si)

   # Get vSAN service instance stub
   apiVersion = GetLatestVmodlVersion(args.vc, int(args.port))
   aboutInfo = si.content.about
   if aboutInfo.apiType != 'VirtualCenter':
      raise Exception("The sample script should be run against vc.")

   vsanStub = GetVsanVcMos(si._stub,
                           context = sslContext,
                           version = apiVersion)

   # Get vSAN cluster config system and vsan cluster health system
   vss = vsanStub['vsan-cluster-space-report-system']
   vccs = vsanStub['vsan-cluster-config-system']

   # Get cluster
   cluster = GetClusterInstance(args.clusterName, si)

   return (si, cluster, vss, vccs)

def BytesToTibBytes(byteSize):
   tibSize = byteSize / (2**40)
   return round(tibSize, 4)

def CheckIfEffectiveCapacityEnabled(cluster, si, sslContext, clusterConfigs):
   """
   Check if the effective capacity is enabled in the vSAN cluster configuration
   @param cluster: vSAN cluster object
   @param si: service instance
   @param sslContext: SSL context for secure connection
   @param clusterConfigs: vSAN cluster configurations
   @return: True if effective capacity is enabled, False otherwise
   """
   # Check if "Apply Auto-RAID to all objects" is enabled in the cluster configuration
   isEffectiveCapacityEnabled = IsEsaAutoRaidEnabledInCluster(clusterConfigs)
   # If "Apply Auto-RAID to all objects" is not enabled,
   # check if the auto RAID policy is enabled on the default vSAN datastore storage policy
   if not isEffectiveCapacityEnabled:
      print("Checking if the effective capacity is enabled in the vSAN storage profile")
      pbmSi = ConnectToSpbm(stub=si._stub, context=sslContext)
      vsanDs = GetLocalVsanDatastore(cluster)
      vsanProfile = GetVsanStorageProfile(pbmSi, vsanDs[0])
      isEffectiveCapacityEnabled = IsAutoManagedRAIDEnabledInProfile(vsanProfile)
   return isEffectiveCapacityEnabled

def main():
   args = GetArgs()

   # For python 2.7.9 and later, the default SSL context has stricter
   # connection handshaking rule, hence we are turning off the hostname checking
   # and client side cert verification.
   sslContext = None
   if sys.version_info[:3] > (2,7,8):
      sslContext = ssl.create_default_context()
      sslContext.check_hostname = False
      sslContext.verify_mode = ssl.CERT_NONE

   (si, cluster, vss, vccs) = ConnectToServers(args, sslContext)

   if cluster is None:
      print("Cluster %s is not found for %s" % (args.clusterName, args.vc))
      return -1
   else:
      # Here is an example of how to get space reporting results
      # by vSAN space reporting API.
      spaceResult = \
         vss.QuerySpaceUsage(cluster=cluster)

      if not spaceResult:
         print("Space result is None for the given cluster %s" % \
            args.clusterName)
         return -1

      # The effective capacity will be reported with the any of following prerequisites satisfied on 90U1 or higher version:
      # 1. The "Apply Auto-RAID to all objects" is enabled in ESA cluster configuration.
      # 2. The auto RAID policy is enabled on the default vSAN datastore storage policy.

      # It shows an example of how to check the prerequisites,
      # NOTE: This sample can help check the cluster configuration for an initial troubleshooting if the
      # effective capacity is not enabled as expected or the effectiveSpaceUsage is not reported
      # in the QuerySpaceUsage API for 9.1U1 or higher version, but the precheck is not required
      # if the effectiveSpaceUsage is reported.
      # Same for other features like global deduplication and compression, if the related fields
      # are not reported in the QuerySpaceUsage API, please refer to the sample code below
      # to check the feature enabled status.

      # Get the vSAN cluster configuration
      clusterConfigs = vccs.GetConfigInfoEx(cluster)
      if not clusterConfigs:
         raise Exception("Failed to get cluster configs for %s" % args.clusterName)

      # Get vSAN ESA enabled status
      vsanEsaEnabled = clusterConfigs.vsanEsaEnabled

      # Get ESA global deduplication and compression enabled status
      globalDedupEnabled = False
      compressionEnabled = False
      dataEfficiencyConfig = clusterConfigs.dataEfficiencyConfig
      if dataEfficiencyConfig is not None:
         globalDedupEnabled = vsanEsaEnabled and dataEfficiencyConfig.dedupEnabled
         compressionEnabled = dataEfficiencyConfig.compressionEnabled

      # Check if effective capacity is enabled in the vSAN cluster configuration
      isEffectiveCapacityEnabled = CheckIfEffectiveCapacityEnabled(
         cluster, si, sslContext, clusterConfigs)

      print("Checking vSAN cluster configuration for %s" % args.clusterName)
      print("vSAN ESA Enabled: %s" % vsanEsaEnabled)
      print("vSAN ESA Effective Capacity Enabled: %s" % isEffectiveCapacityEnabled)
      print("vSAN ESA Global Deduplication Enabled: %s" % globalDedupEnabled)
      print("vSAN ESA Compression Enabled: %s" % compressionEnabled)
      # End of vSAN cluster configuration precheck

      if isEffectiveCapacityEnabled:
         if not hasattr(spaceResult, "effectiveSpaceUsage") or \
               not spaceResult.effectiveSpaceUsage:
            print("Effective space usage is not available for the given cluster %s" % \
               args.clusterName)
         else:
            print("\nvSAN Effective Capacity Overview")
            usage = spaceResult.effectiveSpaceUsage
            fields = [
               ("vSAN Effective Total Usable Capacity", usage.totalUsableB),
               ("vSAN Effective Used Capacity", usage.totalUsableB - usage.freeUsableB),
               ("vSAN Effective Free Usable Capacity", usage.freeUsableB),
               ("Actual Written Capacity", usage.actualWrittenB),
               ("Over Reserved Capacity", usage.overReservedB),
               ("Total Provisioning Capacity", usage.totalProvisionB),
            ]
            for label, value in fields:
               print(f"{label}: {BytesToTibBytes(value)} TiB")

            snapshotSpace = getattr(usage, 'snapshotSpace', None)
            if snapshotSpace:
               print(f"Total Snapshot Count: {snapshotSpace.snapshotCount}")
               print(f"Actual Snapshot Usage: {BytesToTibBytes(snapshotSpace.actualSnapshotUsedB)} TiB")
               print(f"Fully Inflated Snapshot Usage: {BytesToTibBytes(snapshotSpace.fullyInflatedSnapshotUsedB)} TiB")

               print("\nvSAN Effective Space Usage Breakdown")
               objectTypes = [
                 'vdisk',
                 'vmswap',
                 'fileShare',
                 'namespace',
                 'aggregatedSystemObjects'
               ]
               spaceUsageByObjectType = spaceResult.spaceDetail.spaceUsageByObjectType
               for objType in objectTypes:
                 total = sum(
                   getattr(obj, 'primaryCapacityB', 0)
                   for obj in spaceUsageByObjectType
                   if obj.objType == objType
                 )
                 print(f"{objType}: {BytesToTibBytes(total)} TiB")
      if any([vsanEsaEnabled, compressionEnabled, globalDedupEnabled]):
         efficientCapacityState = getattr(spaceResult, 'efficientCapacity', None)
         if isEffectiveCapacityEnabled:
            savings = (efficientCapacityState.esaCompressionSpaceSaving +
                       efficientCapacityState.esaDedupSpaceSaving)
         else:
            savings = (efficientCapacityState.logicalCapacityUsed -
                       efficientCapacityState.physicalCapacityUsed)
         print("\nvSAN Data Reduction (Deduplication / Compression) is Enabled")
         print(f"Data Reduction Savings: {BytesToTibBytes(savings)} TiB")

         ratio = getattr(spaceResult, 'spaceEfficiencyRatio', None)
         if ratio:
            print(f"Data Reduction Ratio: {ratio.overallRatio}x")
         if globalDedupEnabled:
            print(f"Overall Global Deduplication Ratio: {ratio.dedupRatio}x")
            if (isEffectiveCapacityEnabled and
                  hasattr(ratio, "dedupEnabledRatio")):
               print(f"Global Deduplication Enabled Ratio: {ratio.dedupEnabledRatio}x")
         if vsanEsaEnabled or compressionEnabled:
            print(f"Compression Ratio: {ratio.compressionRatio}x")
         if (isEffectiveCapacityEnabled and
               hasattr(ratio, "thinProvisionRatio") and
               hasattr(ratio, "snapshotSavingRatio")):
            print("\nOverall Space Efficiency")
            print(f"Thin-provisioning Saving Ratio: {ratio.thinProvisionRatio}x")
            print(f"Snapshot Saving Ratio: {ratio.snapshotSavingRatio}x")

      print("\nvSAN Standard Space Usage Overview")
      totalCapacity = spaceResult.totalCapacityB
      freeCapacity = spaceResult.freeCapacityB
      usedCapacity = spaceResult.spaceOverview.usedB

      print(f"Total vSAN Capacity: {BytesToTibBytes(totalCapacity)} TiB")
      print(f"Used vSAN Capacity: {BytesToTibBytes(usedCapacity)} TiB")
      print(f"Free vSAN Capacity: {BytesToTibBytes(freeCapacity)} TiB")

      print("\nvSAN Standard Usage Breakdown View")
      objectTypes = [
         'vdisk',
         'vmswap',
         'statsdb',
         'namespace',
         'traceobject',
         'esaObjectOverhead',
         'fileSystemOverhead'
      ]
      usageByType = spaceResult.spaceDetail.spaceUsageByObjectType
      for objType in objectTypes:
         total = sum(getattr(obj, 'usedB', 0) for obj in usageByType if obj.objType == objType)
         print(f"{objType}: {BytesToTibBytes(total)} TiB")

if __name__ == "__main__":
   main()
