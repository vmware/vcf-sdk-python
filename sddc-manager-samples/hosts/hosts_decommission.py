#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

import argparse
from common.ssl_helper import get_unverified_session
from utils.client import create_sddc_manager_client
from common import helper
from vmware.sddc_manager.model_client import HostDecommissionSpec
import json
import time

parser = argparse.ArgumentParser()

parser.add_argument(
    '--server',
    required=True,
    help='SDDC Manager Instance Host Name')

parser.add_argument(
    '--user',
    required=True,
    help='SDDC Manager username')

parser.add_argument(
    '--password',
    required=True,
    help='SDDC Manager password')

args = parser.parse_args()
server = args.server
user = args.user
password = args.password
session = get_unverified_session()  # hack to skip server verification
sddc_client = create_sddc_manager_client(server=server,
                                         username=user, password=password)

"""
Description: Demonstrates de-commission of the hosts
Prerequisites: Prepare HostDecommissionSpec with host details to de-commission hosts.
"""

def create_host_decommission_spec_from_json(data):
    return HostDecommissionSpec(**data)

with open("hosts/hosts_decommission.json", "r") as hosts_to_decommission:
    # Fetch bringup network pool details
    hosts_to_decommission_json = json.load(hosts_to_decommission)
    hosts_to_decommission_spec_list = []
    for host in hosts_to_decommission_json['hosts_spec']:
        hosts_to_decommission_spec_list.append(create_host_decommission_spec_from_json(host))
    # Trigger host commission
    print("Trigger the host commission")
    print(hosts_to_decommission_spec_list)
    task = sddc_client.v1.Hosts.decommission_hosts(hosts_to_decommission_spec_list)
    # sleep before starting the polling
    time.sleep(20)
    print("Poll host decommission task status")
    helper.poll_task_status(sddc_client, task.id)
    print("Host decommission task response:")
    print(task.id)
