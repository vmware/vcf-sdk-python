#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

import json
import argparse

from common.ssl_helper import get_unverified_session
from vmware.sddc_manager.model_client import ClusterUpdateSpec
from utils.client import create_sddc_manager_client
from common import helper
import time

"""
Description:
Demonstrates adding a host to the cluster and monitors the task for successful completion
Prerequisites to add host to cluster,
    1. Create the Network pool
    2. Commission the host
    3. Make sure given cluster and domain are present in SDDC inventory
    4. Make sure at least one host is available in SDDC inventory pool
    5. Make sure license keys for the product type(ESX) are present in SDDC license inventory
Prerequisite to execute the sample: 
    1.In this sample script, wherever the helper.get_domain_id method is called, replace the second argument with the domain type (e.g., 'MANAGEMENT')
     and the third argument with the domain name. This will fetch the relevant domain ID, which is needed for further computation to retrieve the 
     cluster details where the host needs to be added.
    2. In the sample script, wherever the get_management_clusters_by_name method is called, replace the third argument with the name of the cluster
      where the host needs to be added."
"""


def create_cluster_update_spec_from_json(data):
    json_dictionary = json.loads(data)
    return ClusterUpdateSpec(**json_dictionary)


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


def populate_the_prerequisite_in_request_payload(cluster_updation_spec):
    domain_id = helper.get_domain_id(sddc_client, "MANAGEMENT", "sddcId-1001")
    cluster = helper.get_management_clusters_by_name(
        sddc_client, domain_id, "SDDC-Cluster1")
    vds_name = helper.get_cluster_vds(sddc_client, cluster.id)
    vmnics = cluster_updation_spec. \
        cluster_expansion_spec["host_specs"][0]["host_network_spec"]["vm_nics"]
    for vmnic in vmnics:
        vmnic["vds_name"] = vds_name
    unassigned_hosts = helper.get_hosts_based_on_status(
        sddc_client, "UNASSIGNED_USEABLE")
    cluster_updation_spec.cluster_expansion_spec["host_specs"][0]["id"] = \
        unassigned_hosts[0].id
    return cluster.id


with open("clusters/add_host_to_cluster.json", "r") as json_data:
    cluster_updation_json = json_data.read()
    cluster_updation_spec = create_cluster_update_spec_from_json(
        cluster_updation_json)
    cluster_id = populate_the_prerequisite_in_request_payload(
        cluster_updation_spec)
    print("Add host to cluster")
    task = sddc_client.v1.Clusters.update_cluster(
        cluster_id, cluster_updation_spec)
    #sleep before starting the polling
    time.sleep(20)
    # poll the task status
    helper.poll_task_status(sddc_client, task.id)
    print("Add host task response")
    print(task.id)
