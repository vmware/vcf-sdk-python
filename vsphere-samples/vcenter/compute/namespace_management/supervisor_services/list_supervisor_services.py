#!/usr/bin/env python

# Copyright (c) 2022-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '7.0.2+'

from com.vmware.vcenter.namespace_management_client import SupervisorServices
from com.vmware.vcenter.namespace_management.supervisor_services_client import \
    Versions

from helpers.common import sample_cli
from helpers.common import sample_util
from helpers.common.ssl_helper import get_unverified_session
from vcenter.management.host.hcl.utils import get_configuration

separator = '-' * 40


class ListSupervisorServices(object):
    """
    Demonstrates looking up a list of Supervisor Services registered on vCenter.
    """
    def __init__(self):
        parser = sample_cli.build_arg_parser()
        args = sample_util.process_cli_args(parser.parse_args())
        session = get_unverified_session() if args.skipverification else None
        stub_config = get_configuration(
                args.server, args.username, args.password,
                session)
        self.supervisor_services = SupervisorServices(stub_config)
        self.versions = Versions(stub_config)

    def run(self):
        """
        List Supervisor Services registered on vCenter Server.
        """
        services = self.supervisor_services.list()
        print('{0}\nList of Supervisor Services\n{0}'.format(separator))
        for s in services:
            versions = self.versions.list(s.supervisor_service)
            version_summary = ', '.join([v.version for v in versions])
            print('Service:      {0}'.format(s.supervisor_service))
            print('Display Name: {0}'.format(s.display_name))
            print('Versions:     {0}'.format(version_summary))
            print('State:        {0}\n{1}'.format(s.state, separator))


def main():
    list_cl = ListSupervisorServices()
    list_cl.run()


if __name__ == '__main__':
    main()
