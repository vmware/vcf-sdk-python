#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

import json
import argparse
from common.ssl_helper import get_unverified_session
from common import helper
from vmware.sddc_manager.model_client import DomainCreationSpec, \
    DomainUpdateSpec
from utils.client import create_sddc_manager_client
import time

"""
Description: 
Create a workload domain with VLCM clusters. Monitor the creation of the domain, and upon successful creation, proceed with its deletion.
Prerequisites to create workload domain,
    1. Create the Network pool 
    2. Commission the hosts
    3. Make sure at least three hosts are available in SDDC inventory pool
    4. Make sure license keys for the product types(ESX, VSAN and NSXT) are present in SDDC license inventory
    5. In the add_domain.json file used for creating a request payload replace the vCenter root password and NSX Admin password
"""


def create_domain_creation_spec_from_json(data):
    json_dictionary = json.loads(data)
    return DomainCreationSpec(**json_dictionary)


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
    '--nsx_manager_admin_password',
    required=True,
    help='NSX Admin Password')

parser.add_argument(
    '--vcenter_root_password',
    required=True,
    help='vCenter Root Password')

args = parser.parse_args()
server = args.server
user = args.user
password = args.password
nsx_manager_admin_password=args.nsx_manager_admin_password
vcenter_root_password=args.vcenter_root_password
session = get_unverified_session()  # hack to skip server verification
sddc_client = create_sddc_manager_client(server=server,
                                         username=user, password=password)


def populate_the_prerequisite_in_request_payload(domain_creation_spec):
    domain_creation_spec.compute_spec["cluster_specs"][0]["cluster_image_id"] = helper.get_cluster_image_id(sddc_client)
    unassigned_hosts = helper.get_hosts_based_on_status(
        sddc_client, "UNASSIGNED_USEABLE")
    if len(unassigned_hosts) < 3:
        raise AssertionError("Not enough unassigned hosts to create a domain")
    for index in range(3):
        domain_creation_spec.compute_spec["cluster_specs"][0]["host_specs"][index]["id"] = unassigned_hosts[index].id


with open("domains/add_domain.json", "r") as json_data:
    domain_json = json_data.read()
    domain_creation_spec = create_domain_creation_spec_from_json(domain_json)
    domain_creation_spec.vcenter_spec['root_password'] = vcenter_root_password
    domain_creation_spec.nsxt_spec['nsxManager_admin_password'] = nsx_manager_admin_password
    populate_the_prerequisite_in_request_payload(domain_creation_spec)
    # Validating the request
    print("Validating the create domain request")
    helper.validate_domain_request(sddc_client, domain_creation_spec)
    # Trigger create domain
    print("Trigger the create domain")
    task = sddc_client.v1.Domains.create_domain(domain_creation_spec)
    #sleep before starting the polling
    time.sleep(20)
    # poll the task status
    print("Poll Create domain task status")
    helper.poll_task_status(sddc_client, task.id)
    print("Create domain response:")
    print(task.id)
    # perform cleanup on successful creation
    domain_id = helper.get_domain_id(
        sddc_client, "VI", domain_creation_spec.domain_name)
    helper.poll_domain_status(sddc_client, domain_id)
    domain_update_json_data = '{"mark_for_deletion":true}'
    json_dictionary = json.loads(domain_update_json_data)
    domain_update_spec = DomainUpdateSpec(**json_dictionary)
    print("Mark the domain for deletion")
    sddc_client.v1.Domains.update_domain(domain_id, domain_update_spec)
    print("Trigger domain deletion")
    task = sddc_client.v1.Domains.delete_domain(domain_id)
    print("Poll Delete domain task status")
    helper.poll_task_status(sddc_client, task.id)
    print("Deleted domain task response")
    print(task.id)
