#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__author__ = "Broadcom, Inc."
__vcenter_version__ = '9.1+'

from vmware.vapi.vsphere.client import create_vsphere_client

from helpers.common import (sample_cli, sample_util)
from helpers.common.ssl_helper import get_unverified_session

class CapacityUsage:
    """
    Demonstrates getting vCenter Capacity Usage.
    vCenter deployment size should at least be medium

    Running the sample:
    python ./vcenter/monitoring/capacity/usage.py --server <vc ip> --username <username> --password <password> --skipverification

    """

    def __init__(self):
        parser = sample_cli.build_arg_parser()
        args = sample_util.process_cli_args(parser.parse_args())
        session = get_unverified_session() if args.skipverification else None
        self.client = create_vsphere_client(server=args.server,
                                            username=args.username,
                                            password=args.password,
                                            session=session)

    def run(self):
        """
        Get vCenter capacity usage
        """
        print("Getting vCenter Capacity Usage")
        info = self.client.vcenter.capacity.Usage.get()
        print("vCenter Capacity Usage Report is: " + str(info))
        print("vCenter deployment size is : " + info.deployment_size)
        print("vCenter version is : " + info.version)
        print("vCenter Capacity Usage configurations are : " + str(info.configurations))
        print("vCenter Capacity Usage report location is : " + str(info.csv_report_location))


def main():
    capacity_usage = CapacityUsage()
    capacity_usage.run()

if __name__ == '__main__':
    main()
