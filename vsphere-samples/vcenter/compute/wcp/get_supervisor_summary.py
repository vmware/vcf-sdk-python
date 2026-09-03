#!/usr/bin/env python

# Copyright (c) 2022-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '8.0.0+'

from com.vmware.vcenter.namespace_management.supervisors_client import Summary
from helpers.common import sample_cli
from helpers.common import sample_util
from helpers.common.ssl_helper import get_unverified_session
from vcenter.management.host.hcl.utils import get_configuration


class GetSupervisorsSummary(object):
    """
    Demonstrates looking up a Supervisor Summary on a given Supervisor Cluster.
    """

    def __init__(self):
        parser = sample_cli.build_arg_parser()
        parser.add_argument('--supervisor',
                            required=True,
                            help='The MoID of the Supervisor to query.')

        args = sample_util.process_cli_args(parser.parse_args())
        session = get_unverified_session() if args.skipverification else None
        stub_config = get_configuration(
            args.server, args.username, args.password,
            session)
        self.supervisor_summary = Summary(stub_config)
        self.supervisor = args.supervisor

    def run(self):
        """
        Get Supervisor Summary on vCenter Server.
        """
        summary = self.supervisor_summary.get(self.supervisor)
        print('name: {0}'.format(summary.name))
        print('config_status: {0}'.format(summary.config_status))
        print('kubernetes_status: {0}'.format(summary.kubernetes_status))
        print('stats: {0}\n'.format(summary.stats))


def main():
    list_cl = GetSupervisorsSummary()
    list_cl.run()


if __name__ == '__main__':
    main()
