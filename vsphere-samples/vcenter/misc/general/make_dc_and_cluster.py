#!/usr/bin/env python

# Copyright (c) 2014-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

"""
Written by Michael Rice
Github: https://github.com/michaelrice
Website: https://michaelrice.github.io/
Blog: http://www.errr-online.com/
"""

from helpers import cluster, service_instance, datacenter, cli, pchelper
from pyVmomi import vim


parser = cli.Parser()
parser.add_required_arguments(cli.Argument.DATACENTER_NAME, cli.Argument.CLUSTER_NAME)
args = parser.get_args()
si = service_instance.connect(args)

content = si.RetrieveContent()
if pchelper.search_for_obj(content, [vim.Datacenter], args.datacenter_name):
    print("Datacenter '%s' already exists" % args.datacenter_name)
else:
    dc = datacenter.create_datacenter(dc_name=args.datacenter_name, service_instance=si)
    cluster.create_cluster(datacenter=dc, name=args.cluster_name)
    print("created DC and cluster")
