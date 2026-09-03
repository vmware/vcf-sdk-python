#!/usr/bin/env python

# Copyright (c) 2016-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '7.0.1+'

from com.vmware.vcenter.namespace_management_client import Clusters

from helpers.common import sample_cli
from helpers.common import sample_util
from helpers.common.ssl_helper import get_unverified_session
from vcenter.management.host.hcl.utils import get_configuration
from pprint import pprint


class ListCluster(object):
    """
    Demonstrates getting list of WCP enabled clusters
    Sample Prerequisites:
    vCenter/ESX with wcp enable"
    """
    def __init__(self):
        parser = sample_cli.build_arg_parser()
        args = sample_util.process_cli_args(parser.parse_args())
        session = get_unverified_session() if args.skipverification else None
        stub_config = get_configuration(
                args.server, args.username, args.password,
                session)
        self.list_cluster = Clusters(stub_config)

    def run(self):
        """
        List cluster present in server
        """
        clusters = self.list_cluster
        list_of_cl = clusters.list()
        print("----------------------------")
        print("List Of clusters")
        print("----------------------------")
        pprint(list_of_cl)
        print("----------------------------")


def main():
    list_cl = ListCluster()
    list_cl.run()


if __name__ == '__main__':
    main()
