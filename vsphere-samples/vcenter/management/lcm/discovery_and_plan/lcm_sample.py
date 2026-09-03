#!/usr/bin/env python
#
# Copyright (c) 2019-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '7.0+'

from com.vmware.vcenter.lcm_client import Reports

from helpers.common import sample_cli, sample_util
from helpers.common.ssl_helper import get_unverified_session
from vcenter.management.host.hcl.utils import get_configuration


class SampleLcm(object):
    """
     Sample demonstrating vCenter LCM Update APIs
     Sample Prerequisites:
     vCenter on linux platform
     """

    def __init__(self):
        parser = sample_cli.build_arg_parser()
        parser.add_argument('-f', '--file_name',
                        help='Provide csv report file name.')
        args = sample_util.process_cli_args(parser.parse_args())
        self.csv_report = args.file_name
        session = get_unverified_session() if args.skipverification else None
        stub_config = get_configuration(
                args.server, args.username, args.password,
                session)
        self.report_client = Reports(stub_config)

    def run(self):
        """
        Access to download the interop report APIs by providing csv_report name
        """
        report_details = self.report_client.get(self.csv_report)
        print("Report Details - ", report_details)


def main():
    """
     Entry point for the sample client
    """
    lcm = SampleLcm()
    lcm.run()


if __name__ == '__main__':
    main()
