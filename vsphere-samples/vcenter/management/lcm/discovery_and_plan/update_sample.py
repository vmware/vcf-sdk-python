#!/usr/bin/env python

# Copyright (c) 2019-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '7.0+'

from com.vmware.vcenter.lcm.update_client import Pending, PrecheckReport

from helpers.common import sample_cli, sample_util
from helpers.common.ssl_helper import get_unverified_session
from vcenter.management.host.hcl.utils import get_configuration


class SampleUpdate(object):
    """
     Sample demonstrating vCenter LCM Update APIs
     Sample Prerequisites:
     vCenter on linux platform
     """
    def __init__(self):
        parser = sample_cli.build_arg_parser()
        args = sample_util.process_cli_args(parser.parse_args())
        session = get_unverified_session() if args.skipverification else None
        stub_config = get_configuration(
                args.server, args.username, args.password,
                args.skipverification)
        self.pending_client = Pending(stub_config)
        self.precheck_client = PrecheckReport(stub_config)

    def run(self):
        """
        Access the Update APIs to list available patches and details
        """
        available_updates = self.pending_client.list()
        print("vCenter available updates - ", available_updates)
        if available_updates.updates:
            target_version = available_updates.updates[0].version
            update_details = self.pending_client.get(target_version)
            print("vCenter available update details - ", update_details)

            # precheck API's
            precheck_result = self.precheck_client.create_task(target_version)
            print("Pre upgrade checks task id started with: \n{0}".format(precheck_result.get_task_id()))


def main():
    """
     Entry point for the sample client
    """
    update = SampleUpdate()
    update.run()


if __name__ == '__main__':
    main()
