#!/usr/bin/env python

# Copyright (c) 2019-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '6.7+'

import sys
from vmware.vapi.vsphere.client import create_vsphere_client

from helpers.common import (sample_cli, sample_util)
from helpers.common.ssl_helper import get_unverified_session


"""
Description: Demonstrates services api workflow
1.Stop a running service
2.Get details of stopped service
3.Start the service stopped in step 2
4.Get details of service
5.Restart the service
6.Get details of service

"""


parser = sample_cli.build_arg_parser()
parser.add_argument(
    '--service_name',
    action='store',
    required=True,
    help='Specify servicename for all stop/start/restart operations')
args = sample_util.process_cli_args(parser.parse_args())
service_name = args.service_name
session = get_unverified_session() if args.skipverification else None
client = create_vsphere_client(server=args.server,
                               username=args.username,
                               password=args.password,
                               session=session)

appliance_service = client.appliance.Services
service_list = appliance_service.list()


def ouput_display(info, service_name):
    print("Service : {}".format(service_name))
    print("Description : {}".format(info.description))
    print("state : {}".format(info.state))
    print("-----------------------------------")


if service_name not in service_list:
    raise ValueError('Service with service name {} does not exists'.format(service_name))

print("Example: Stopping service : {}\n".format(service_name))
appliance_service.stop(service_name)
service_state = appliance_service.get(service_name)
ouput_display(service_state, service_name)
print("Example: Starting service : {}\n".format(service_name))
appliance_service.start(service_name)
service_state = appliance_service.get(service_name)
ouput_display(service_state, service_name)
print("Example: Restarting service : {}\n" .format(service_name))
appliance_service.restart(service_name)
print("Example: Getting service : {}\n".format(service_name))
service_state = appliance_service.get(service_name)
ouput_display(service_state, service_name)
