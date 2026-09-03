#!/usr/bin/env python

# Copyright (c) 2019-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '7.0+'

from com.vmware.esx.hcl_client import CompatibilityData

from vcenter.management.host.hcl.utils import get_configuration
from helpers.common import sample_cli, sample_util


class CompatibilityDataUpdateSample(object):
    """
     Sample demonstrating vCenter HCL Compatibility Data Update Operation
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
        Calls the HCL Compatibility Data Update POST API to update the HCL Datastore on the vCenter
        """
        data_update_info = self.api_client.update_task()
        print("Compatibility Data Update Task ID : ", data_update_info.get_task_id())


def main():
    """
     Entry point for the CompatibilityDataUpdateSample client
    """
    dataUpdateSample = CompatibilityDataUpdateSample()
    dataUpdateSample.run()


if __name__ == '__main__':
    main()
