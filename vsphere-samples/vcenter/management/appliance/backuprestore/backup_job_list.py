#!/usr/bin/env python

# Copyright (c) 2017-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '6.7+'

from helpers.common import sample_cli
from helpers.common import sample_util
from helpers.common import vapiconnect
from com.vmware.appliance.recovery.backup.job_client import Details


class BackupJobList(object):
    """
    Demonstrates backup job list operation

    Retrieves backup job details from vCenter and prints the data

    Prerequisites:
        - vCenter
        - Backup operation is performed on the vCenter either manually or
          by scheduled backups
    """

    def __init__(self):
        self.stub_config = None

    def setup(self):
        parser = sample_cli.build_arg_parser()
        args = sample_util.process_cli_args(parser.parse_args())

        # Connect to vAPI services
        self.stub_config = vapiconnect.connect(
            host=args.server,
            user=args.username,
            pwd=args.password,
            skip_verification=args.skipverification)

    def run(self):
        details_client = Details(self.stub_config)
        job_list = details_client.list()

        for info in job_list.values():
            print(
                'Start time: {}, Duration: {}, Type: {}, Status: {}, Location: {}'
                .format(
                    info.start_time.strftime("%b %d %Y %H:%M"), info.duration,
                    info.type, info.status, info.location))


def main():
    backup_job_list = BackupJobList()
    backup_job_list.setup()
    backup_job_list.run()


if __name__ == '__main__':
    main()
