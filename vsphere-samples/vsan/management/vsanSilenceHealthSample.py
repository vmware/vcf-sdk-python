#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

"""
This sample demonstrates how to silence the vSAN cluster health checks and
unsilence it.
"""


from pyVim.connect import SmartConnect, Disconnect
import sys
import ssl
import atexit
import argparse
import getpass
if sys.version[0] < '3':
    input = raw_input
import vsanapiutils


def GetArgs():
    """
    Supports the command-line arguments listed below.
    """
    parser = argparse.ArgumentParser(
        description='Process args for vSAN sample application')
    parser.add_argument('-s', '--host', required=True,
                        action='store', help='Remote host to connect to')
    parser.add_argument('-o', '--port', type=int, default=443,
                        action='store', help='Port to connect on')
    parser.add_argument('-u', '--user', required=True,
                        action='store',
                        help='User name to use when connecting to host')
    parser.add_argument('-p', '--password', required=False,
                        action='store',
                        help='Password to use when connecting to host')
    parser.add_argument('--cluster', dest='clusterName',
                        metavar="CLUSTER", default='VSAN-Cluster')
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


def silenceClusterHealthCheck(cluster, checks, vcMos):
    vhs = vcMos['vsan-cluster-health-system']
    vhs.SetVsanClusterSilentChecks(
        cluster=cluster, addSilentChecks=checks, removeSilentChecks=[])
    print("Successfully silenced the '%s'" % checks)


def unsilenceClusterHealthCheck(cluster, checks, vcMos):
    vhs = vcMos['vsan-cluster-health-system']
    vhs.SetVsanClusterSilentChecks(
        cluster=cluster, addSilentChecks=[], removeSilentChecks=checks)
    print("Successfully unsilenced the '%s'" % checks)


def main():
    args = GetArgs()
    if args.password:
        password = args.password
    else:
        password = getpass.getpass(prompt='Enter password for host %s and '
                                          'user %s: ' % (args.host, args.user))

    # For python 2.7.9 and later, the default SSL context has more strict
    # connection handshaking rule. We may need turn off the hostname checking
    # and client side cert verification.
    context = None
    if sys.version_info[:3] > (2, 7, 8):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

    si = SmartConnect(host=args.host, user=args.user, pwd=password,
                      port=int(args.port), sslContext=context)
    atexit.register(Disconnect, si)

    # Detecting whether the host is vCenter or ESXi.
    aboutInfo = si.content.about
    apiVersion = vsanapiutils.GetLatestVmodlVersion(args.host, int(args.port))

    if aboutInfo.apiType == 'VirtualCenter':
        # Get vSAN health system from the vCenter Managed Object references.
        vcMos = vsanapiutils.GetVsanVcMos(
            si._stub, context=context, version=apiVersion)
        vhs = vcMos['vsan-cluster-health-system']

        cluster = getClusterInstance(args.clusterName, si)
        if cluster is None:
            print("Cluster %s not found for %s" % (args.clusterName, args.host))
            return -1

        print("Check for cluster %s" % cluster.name)

        # Query vSAN health summary
        healthSummary = vhs.QueryClusterHealthSummary(cluster)
        print("Overall health for cluster %s : %s" %
              (cluster.name, healthSummary.overallHealth))
        if healthSummary.overallHealth not in ['yellow', 'red']:
            print("Cluster health not yellow or red, exiting.")
            exit(0)

        # Find out the non-green health
        group_id = None
        checks = []
        for group in healthSummary.groups:
            if group.groupHealth not in ['yellow', 'red']:
                continue
            group_id = group.groupId
            for test in group.groupTests:
                if test.testHealth in ['yellow', 'red']:
                    test_id = test.testId
                    if test_id is not None:
                        checks.append(test_id.split('.')[-1])

        if group_id is None:
            print("All health checks are green!")
            exit(0)

        # Silence the health check
        silenceClusterHealthCheck(cluster, checks, vcMos)

        # Query health summary again and verify the health status
        healthSummary = vhs.QueryClusterHealthSummary(cluster)
        print("Overall health for cluster %s is %s after silencing" %
              (cluster.name, healthSummary.overallHealth))

        # Unsilence the health check
        unsilenceClusterHealthCheck(cluster, checks, vcMos)

        # Query health summary again after removing the silent check
        healthSummary = vhs.QueryClusterHealthSummary(cluster)
        print("Overall health for cluster %s is %s after unsilencing" %
              (cluster.name, healthSummary.overallHealth))
    else:
        print("Host %s is not a VC host. Please run on VC", args.host)


if __name__ == "__main__":
    main()
