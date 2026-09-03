#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

import argparse
from common.ssl_helper import get_unverified_session
from utils.client import create_sddc_manager_client
from common import helper
from vmware.sddc_manager.model_client import HostCommissionSpec
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

parser.add_argument(
    '--esxi_password',
    required=True,
    help='ESXI password')

args = parser.parse_args()
server = args.server
user = args.user
password = args.password
esxi_password = args.esxi_password
session = get_unverified_session()  # hack to skip server verification
sddc_client = create_sddc_manager_client(server=server,
                                         username=user, password=password)

"""
Description: Commission Host 
Prerequisite to commission hosts: In the host_commission.json file -
    1. In each entry for the host to commission replace the network_pool_name and network_pool_id with appropriate value
    2. In each entry for the host to commission replace the esxi password
"""

def create_host_commission_spec_from_json(data):
    return HostCommissionSpec(**data)

def get_network_pool():
    network_pool_name = "bringup-networkpool"
    page_of_network_pool = sddc_client.v1.NetworkPools.get_network_pool()
    print(page_of_network_pool)
    network_pools = page_of_network_pool.elements
    for network_pool in network_pools:
        if network_pool_name == network_pool.name:
            return network_pool
    return None

with open("hosts/hosts_commission.json", "r") as hosts_to_commission:
    # Fetch bringup network pool details
    network_pool = get_network_pool()
    hosts_to_commission_json = json.load(hosts_to_commission)
    hosts_to_commission_spec_list = []
    for host in hosts_to_commission_json['hosts_spec']:
        host['network_pool_name'] = network_pool.name
        host['network_pool_id'] = network_pool.id
        host['password'] = esxi_password
        hosts_to_commission_spec_list.append(create_host_commission_spec_from_json(host))
    # Trigger host commission
    print("Trigger the host commission")
    task = sddc_client.v1.Hosts.commission_hosts(hosts_to_commission_spec_list)
    # sleep before starting the polling
    time.sleep(20)
    print("Poll host commission task status")
    helper.poll_task_status(sddc_client, task.id)
    print("Host Commission task response:")
    print(task.id)

