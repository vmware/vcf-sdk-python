#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

"""
This file includes sample codes for VC and ESXi sides vSAN iSCSI API accessing.

To provide an example of vSAN iSCSI API access, it shows how to enable vSAN
iSCSI service, create targets and LUNs, together with disable iSCSI service.

NOTE: using vSAN iSCSI target service API requires a minimal
vim.version.version11 Stub.

"""


from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import pbm, VmomiSupport, SoapStubAdapter, vim
import sys
import ssl
import atexit
import argparse
import getpass
from distutils.version import StrictVersion

import pyVmomi
import vsanmgmtObjects
import vsanapiutils

def GetArgs():
   """
   Supports the command-line arguments listed below.
   """
   parser = argparse.ArgumentParser(
       description='Process args for vSAN iSCSI SDK sample application')
   parser.add_argument('-s', '--host', required=True, action='store',
                       help='Remote host to connect to')
   parser.add_argument('-o', '--port', type=int, default=443, action='store',
                       help='Port to connect on')
   parser.add_argument('-u', '--user', required=True, action='store',
                       help='User name to use when connecting to host')
   parser.add_argument('-p', '--password', required=False, action='store',
                       help='Password to use when connecting to host')
   parser.add_argument('--cluster', dest='clusterName', metavar="CLUSTER",
                      default='VSAN-Cluster')
   parser.add_argument('--enableVip', required=False, default=False, help=
                       'Whether enable virtual IP or not, default value is '
                       'False')
   parser.add_argument('--vSwitchName', required=False, default='vSwitch0',
                       help='vSwitch name used to enable vSAN iSCSI virtual IP')
   parser.add_argument('--vlanId', required=False, default=0, help='VLAN ID '
      'for the Virtual IP vmkernel adapter. Default 0 if not specified')
   parser.add_argument('--dvPortGroupId', required=False, help='Distributed '
                       'virtual port group MO ID used to enable vSAN iSCSI '
                       'virtual IP')
   parser.add_argument('--dvsUuid', required=False, help='Distributed virtual '
                       'switch uuid to enable vSAN iSCSI virtual IP')
   parser.add_argument('--vipV4Address', required=False,
                       help='Virtual IP V4 address')
   parser.add_argument('--vipV4Subnet', required=False, help='virtual IP V4 '
                       'subnet')
   parser.add_argument('--vipV4Gateway', required=False,
                       help='Virtual IP V4 gateway, default V4 gateway will be '
                       'used if it is not provided')
   parser.add_argument('--vipV6Address', required=False,
                       help='Virtual IP V6 address')
   parser.add_argument('--vipV6Subnet', required=False, help='virtual IP V6 '
                       'subnet')
   parser.add_argument('--vipV6Gateway', required=False,
                       help='Virtual IP V6 gateway, default V6 gateway will be '
                       'used if it is not provided')
   args = parser.parse_args()
   return args

def getClusterInstance(clusterName, serviceInstance):
   content = serviceInstance.RetrieveContent()
   searchIndex = content.searchIndex
   datacenters = content.rootFolder.childEntity
   for datacenter in datacenters:
      cluster = searchIndex.FindChild(datacenter.hostFolder, clusterName)
      if cluster is not None:
         return cluster
   return None

def connectToSpbm(stub, context):
   sessionCookie = stub.cookie.split('"')[1]
   VmomiSupport.GetRequestContext()["vcSessionCookie"] = sessionCookie
   pbmStub = vsanapiutils._GetVsanStub(stub, endpoint="/pbm/sdk", context=context,
                                       version="pbm.version.version2")
   pbmStub.cookie = stub.cookie
   pbmSi = pbm.ServiceInstance("ServiceInstance", pbmStub)
   return pbmSi

def getVsanStoragePolicy(pbmSi):
   resourceType = pbm.profile.ResourceType(
      resourceType=pbm.profile.ResourceTypeEnum.STORAGE
   )

   profileManager = pbmSi.RetrieveContent().profileManager
   profileIds = profileManager.PbmQueryProfile(resourceType)
   profiles = profileManager.PbmRetrieveContent(profileIds)
   for profile in profiles:
      # vSAN default storage profile possesses a unique profile ID of
      # 'aa6d5a82-1c88-45da-85d3-3d74b91a5bad' across different releases.
      # Other profiles may also be looked up when needed to apply to vSAN
      # iSCSI services.
      profileId = profile.profileId.uniqueId
      if (isinstance(profile, pbm.profile.CapabilityBasedProfile) and
            profileId == 'aa6d5a82-1c88-45da-85d3-3d74b91a5bad'):
         return vim.VirtualMachineDefinedProfileSpec(profileId=profileId)
   return None

def main():
   args = GetArgs()
   if args.password:
      password = args.password
   else:
      password = getpass.getpass(prompt='Enter password for host %s and '
                                        'user %s: ' % (args.host,args.user))

   # For python 2.7.9 and later, the default SSL context has more strict
   # connection handshaking rule. We may need turn of the hostname checking
   # and client side cert verification.
   context = None
   if sys.version_info[:3] > (2,7,8):
      context = ssl.create_default_context()
      context.check_hostname = False
      context.verify_mode = ssl.CERT_NONE

   si = SmartConnect(host=args.host,
                     user=args.user,
                     pwd=password,
                     port=int(args.port),
                     sslContext=context)

   atexit.register(Disconnect, si)

   aboutInfo = si.content.about
   apiVersion = vsanapiutils.GetLatestVmodlVersion(args.host, int(args.port))

   cluster = getClusterInstance(args.clusterName, si)
   if cluster is None:
      print("Cluster %s is not found for %s" % (args.clusterName, args.host))
      return -1

   vcMos = vsanapiutils.GetVsanVcMos(si._stub, context=context,
                                     version=apiVersion)
   vits = vcMos['vsan-cluster-iscsi-target-system']
   vccs = vcMos['vsan-cluster-config-system']

   # Fetch the storage policy ID for enable vSAN iSCSI service and
   # create the iSCSI home object.
   pbmSi = connectToSpbm(si._stub, context)
   vsanStoragePolicy = getVsanStoragePolicy(pbmSi)
   if vsanStoragePolicy is None:
      print('Cannot find the vSAN Storage Policy from the Virtual ' +
            'Center server.')
      return -1

   # Enable iSCSI service through vSAN Cluster Reconfiguration API on VC, and
   # the config port defaults to 3260 and can be customized.
   defaultVsanConfigSpec = vim.cluster.VsanIscsiTargetServiceDefaultConfigSpec(
                                 networkInterface="vmk0",
                                 port=2300)
   vitEnableSpec = vim.cluster.VsanIscsiTargetServiceSpec(
                         homeObjectStoragePolicy=vsanStoragePolicy,
                         defaultConfig=defaultVsanConfigSpec,
                         enabled=True)

   clusterReconfigSpec = vim.vsan.ReconfigSpec(iscsiSpec=vitEnableSpec,
                                               modify=True)
   vitEnableVsanTask = vccs.ReconfigureEx(cluster, clusterReconfigSpec)
   vitEnableVcTask = vsanapiutils.ConvertVsanTaskToVcTask(
                           vitEnableVsanTask, si._stub)
   vsanapiutils.WaitForTasks([vitEnableVcTask], si)
   print('Enable vSAN iSCSI service task finished with status: %s' %
         vitEnableVcTask.info.state)

   # Create vSAN iSCSI targets and an associated LUN with the size of 1GB.
   targetAlias = "sampleTarget"
   targetSpec = vim.cluster.VsanIscsiTargetSpec(
                      alias=targetAlias,
                      iqn='iqn.2015-08.com.vmware:vit.target1')
   vsanTask = vits.AddIscsiTarget(cluster, targetSpec)
   vcTask = vsanapiutils.ConvertVsanTaskToVcTask(vsanTask, si._stub)
   vsanapiutils.WaitForTasks([vcTask], si)
   print('Create vSAN iSCSI target task finished with status: %s' %
         vcTask.info.state)

   lunSize = 1 * 1024 * 1024 * 1024 # 1GB
   lunSpec = vim.cluster.VsanIscsiLUNSpec(
                                          lunId=0,
                                          lunSize=lunSize,
                                          storagePolicy=vsanStoragePolicy)
   vsanTask = vits.AddIscsiLUN(cluster, targetAlias, lunSpec)
   vcTask = vsanapiutils.ConvertVsanTaskToVcTask(vsanTask, si._stub)
   vsanapiutils.WaitForTasks([vcTask], si)
   print('Create vSAN iSCSI LUN task finished with status: %s' %
         vcTask.info.state)

   targetList = vits.GetIscsiTargets(cluster)
   print('Get vSAN iSCSI Targets: %s' % targetList)

   target = vits.GetIscsiTarget(cluster, targetAlias)
   print('Get vSAN iSCSI Target: %s' % target)

   lunList = vits.GetIscsiLUNs(cluster, targetAlias)
   print('Get vSAN iSCSI LUNs: %s' % lunList)

   lun = vits.GetIscsiLUN(cluster, targetAlias, 0)
   print('Get vSAN iSCSI LUN: %s' % lun)

   if args.enableVip:
      # Enable vSAN iSCSI virtual IP bound to given DV port group
      if args.dvPortGroupId:
         enableDvsVip(vccs, cluster, si, args.vipV4Address, args.vipV4Subnet,
                      args.vipV4Gateway, args.vipV6Address, args.vipV6Subnet,
                      args.vipV6Gateway, args.dvPortGroupId, args.dvsUuid)
      else:
      # Enable vSAN iSCSI VIP binding to standard switch
         enableVSwitchVip(vccs, cluster, si, args.vipV4Address,
                          args.vipV4Subnet, args.vipV4Gateway,
                          args.vipV6Address, args.vipV6Subnet,
                          args.vipV6Gateway, args.vSwitchName,
                          int(args.vlanId))

      # Get vSAN iSCSI VIP
      logVsanIscsiVipConfigs(vccs, cluster)

   # Remove vSAN iSCSI targets and LUN associated with the targets.
   vsanTask = vits.RemoveIscsiLUN(cluster, targetAlias, 0)
   vcTask = vsanapiutils.ConvertVsanTaskToVcTask(vsanTask, si._stub)
   vsanapiutils.WaitForTasks([vcTask], si)
   print("Remove vSAN iSCSI LUN task finished with status:%s" %
         vcTask.info.state)

   vsanTask = vits.RemoveIscsiTarget(cluster, targetAlias)
   vcTask = vsanapiutils.ConvertVsanTaskToVcTask(vsanTask, si._stub)
   vsanapiutils.WaitForTasks([vcTask], si)
   print("Remove vSAN iSCSI target task finished with status:%s" %
        vcTask.info.state)

   if args.enableVip:
      # Disable vSAN iSCSI VIP
      disableVip(vccs, cluster, si)

   # Disable iSCSI service through vSAN iSCSI API on vCenter.
   vitDisableSpec = vim.cluster.VsanIscsiTargetServiceSpec(enabled=False)
   clusterReconfigSpec = vim.vsan.ReconfigSpec(iscsiSpec=vitDisableSpec,
                                               modify=True)
   vitDisableVsanTask = vccs.ReconfigureEx(cluster, clusterReconfigSpec)
   vitDisableVcTask = vsanapiutils.ConvertVsanTaskToVcTask(
                           vitDisableVsanTask, si._stub)
   vsanapiutils.WaitForTasks([vitDisableVcTask], si)
   print('Disable vSAN iSCSI service task finished with status: %s' %
         vitDisableVcTask.info.state)

def enableVSwitchVip(vccs, cluster, si, ipv4Address, ipv4Subnet, ipv4Gateway,
                     ipv6Address, ipv6Subnet, ipv6Gateway,
                     vSwitchName, vlanId):
   v4NetworkConfig = None
   v6NetworkConfig = None
   if ipv4Address and ipv4Subnet:
      v4NetworkConfig = vim.vsan.VipNetworkConfig(ipAddress=ipv4Address,
                                            subnet=ipv4Subnet,
                                            gateway=ipv4Gateway)
   if ipv6Address and ipv6Subnet:
      v6NetworkConfig = vim.vsan.VipNetworkConfig(ipAddress=ipv6Address,
                                               subnet=ipv6Subnet,
                                               gateway=ipv6Gateway)
   vswitchConfig = vim.vsan.VipVswitchConfig(vswitchName=vSwitchName,
                                             vlanId=vlanId)
   vipConfigSpec = vim.vsan.VipConfigSpec(vswitchConfig=vswitchConfig,
                                          enabled=True,
                                          v4NetworkConfig=v4NetworkConfig,
                                          v6NetworkConfig=v6NetworkConfig)
   vipEnableSpec = vim.cluster.VsanIscsiTargetServiceSpec(
      vipConfigs=[vipConfigSpec])
   clusterReconfigSpec = vim.vsan.ReconfigSpec(iscsiSpec=vipEnableSpec,
                                               modify=True)
   vitEnableVsanTask = vccs.ReconfigureEx(cluster, clusterReconfigSpec)
   vitEnableVcTask = vsanapiutils.ConvertVsanTaskToVcTask(vitEnableVsanTask,
                                                          si._stub)
   vsanapiutils.WaitForTasks([vitEnableVcTask], si)
   print('Enable vSAN iSCSI virtual IP task finished with status: %s' %
         vitEnableVcTask.info.state)

def enableDvsVip(vccs, cluster, si, ipv4Address, ipv4Subnet, ipv4Gateway,
                 ipv6Address, ipv6Subnet, ipv6Gateway,
                 dvPortGroupId, dvsUuid):
   portGroup = vim.dvs.DistributedVirtualPortgroup(dvPortGroupId)
   dvSwitchConfig = vim.vsan.VipDVswitchConfig(portGroup=portGroup,
                                               dvsUuid=dvsUuid)
   v4NetworkConfig = None
   v6NetworkConfig = None
   if ipv4Address and ipv4Subnet:
      v4NetworkConfig = vim.vsan.VipNetworkConfig(ipAddress=ipv4Address,
                                            subnet=ipv4Subnet,
                                            gateway=ipv4Gateway)
   if ipv6Address and ipv6Subnet:
      v6NetworkConfig = vim.vsan.VipNetworkConfig(ipAddress=ipv6Address,
                                               subnet=ipv6Subnet,
                                               gateway=ipv6Gateway)
   vipConfigSpec = vim.vsan.VipConfig(distributedSwitchConfig=dvSwitchConfig,
                                      enabled=True,
                                      v4NetworkConfig=v4NetworkConfig,
                                      v6NetworkConfig=v6NetworkConfig)
   vipConfigs = [vipConfigSpec]

   vipEnableSpec = vim.cluster.VsanIscsiTargetServiceSpec(
      vipConfigs=vipConfigs
   )
   clusterReconfigSpec = vim.vsan.ReconfigSpec(iscsiSpec=vipEnableSpec,
                                               modify=True)
   vitEnableVsanTask = vccs.ReconfigureEx(cluster, clusterReconfigSpec)
   vitEnableVcTask = vsanapiutils.ConvertVsanTaskToVcTask(vitEnableVsanTask,
                                                          si._stub)
   vsanapiutils.WaitForTasks([vitEnableVcTask], si)
   print('Enable vSAN iSCSI virtual IP task finished with status: %s' %
         vitEnableVcTask.info.state)

def logVsanIscsiVipConfigs(vccs, cluster):
   iscsiTargetServiceConfig = getIscsiTargetServiceConfig(vccs, cluster)
   print('Get vSAN iSCSI virtual IP as: %s'
      % iscsiTargetServiceConfig.vipConfigs)

def disableVip(vccs, cluster, si):
   vipConfigSpec = vim.vsan.VipConfigSpec(enabled=False)
   vipDisableSpec = vim.cluster.VsanIscsiTargetServiceSpec(
      vipConfigs=[vipConfigSpec])
   clusterReconfigSpec = vim.vsan.ReconfigSpec(iscsiSpec=vipDisableSpec,
                                               modify=True)
   vitDisableVsanTask = vccs.ReconfigureEx(cluster, clusterReconfigSpec)
   vitDisableVcTask = vsanapiutils.ConvertVsanTaskToVcTask(vitDisableVsanTask,
                                                           si._stub)
   vsanapiutils.WaitForTasks([vitDisableVcTask], si)
   print('Disable vSAN iSCSI virtual IP task finished with status: %s' %
         vitDisableVcTask.info.state)

def getIscsiTargetServiceConfig(vccs, cluster):
   clusterConfig = vccs.GetConfigInfoEx(cluster)
   return clusterConfig.iscsiConfig

if __name__ == "__main__":
   main()
