#!/usr/bin/env python

# Copyright (c) 2019-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '7.0+'

from com.vmware.esx.hcl_client import CompatibilityData

from vcenter.management.host.hcl.utils import get_configuration
from helpers.common import sample_cli, sample_util


class CompatibilityDataStatusSample(object):
    """
     Sample demonstrating vCenter HCL Compatibility Data Status Check Operation
     Sample Prerequisites:
     vCenter on linux platform
     """

    def __init__(self):
        parser = sample_cli.build_arg_parser()
        args = sample_util.process_cli_args(parser.parse_args())

        config = get_configuration(args.server, args.username,
                                         args.password,
                                         args.skipverification)
        self.api_client = CompatibilityData(config)

    def run(self):
        """
        Invokes the HCL Compatibility Data Status GET API to get information
        about when the compatibility data was last updated
        """
        data_status_info = self.api_client.get()
        print("Compatibility Data Status : ", data_status_info)


def main():
    """
     Entry point for the CompatibilityDataStatusSample client
    """
    dataStatusSample = CompatibilityDataStatusSample()
    dataStatusSample.run()


if __name__ == '__main__':
    main()
