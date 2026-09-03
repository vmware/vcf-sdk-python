#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

import json
import argparse

from common.ssl_helper import get_unverified_session
from vmware.sddc_manager.model_client import ClusterCreationSpec, \
    ClusterUpdateSpec
from utils.client import create_sddc_manager_client
from common import helper
import time

"""
Description: 
Demonstrate adding a cluster to the domain. Monitor the creation of the cluster, and upon successful creation, proceed with its deletion.
Prerequisites to add cluster to domain,
   1. Create the Network pool
   2. Commission the hosts
   3. Make sure given domain is present in SDDC inventory
   4. Make sure at least three hosts are available in SDDC inventory pool
   5. Make sure license keys for the product types(ESX and VSAN) are present in SDDC license inventory
Prerequisite before executing the sample:
   1. In this sample script, wherever the helper.get_domain_id method is called, replace the second argument with the type of 
      domain (in this case, 'MANAGEMENT') and the third argument with the domain name.
"""

def create_cluster_creation_spec_from_json(data):
    json_dictionary = json.loads(data)
    return ClusterCreationSpec(**json_dictionary)


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


def populate_the_prerequisite_in_request_payload(cluster_creation_spec):
    cluster_creation_spec.domain_id = helper.get_domain_id(
        sddc_client, "MANAGEMENT", "sddcId-1001")
    unassigned_hosts = helper.get_hosts_based_on_status(
        sddc_client, "UNASSIGNED_USEABLE")
    cluster_creation_spec.compute_spec["cluster_specs"][0]["cluster_image_id"] = helper.get_cluster_image_id(sddc_client)
    if len(unassigned_hosts) < 3:
        raise AssertionError("Not enough unassigned hosts to add a cluster")
    for index in range(3):
        cluster_creation_spec.compute_spec["cluster_specs"][0]["host_specs"][index]["id"] = unassigned_hosts[index].id


with open("clusters/add_cluster.json", "r") as json_data:
    cluster_json = json_data.read()
    cluster_creation_spec = create_cluster_creation_spec_from_json(
        cluster_json)
    populate_the_prerequisite_in_request_payload(cluster_creation_spec)
    # Validating the request
    print("Validate add Cluster request")
    helper.validate_cluster_request(sddc_client, cluster_creation_spec)
    # Trigger add cluster
    print("Trigger add Cluster")
    task = sddc_client.v1.Clusters.create_cluster(cluster_creation_spec)

    #sleep before starting the polling
    time.sleep(20)
    # poll the task status
    print("Poll Create Cluster task status")
    helper.poll_task_status(sddc_client, task.id)
    print("Add Cluster response:")
    print(task.id)
    # Delete cluster
    domain_id = helper.get_domain_id(sddc_client, "MANAGEMENT", "sddcId-1001")
    cluster = helper.get_management_clusters_by_name(
        sddc_client, domain_id, cluster_creation_spec.compute_spec["cluster_specs"][0]["name"])
    print("Mark the Cluster for deletion")
    cluster_update_json_data = '{"mark_for_deletion":true}'
    json_dictionary = json.loads(cluster_update_json_data)
    cluster_update_spec = ClusterUpdateSpec(**json_dictionary)
    sddc_client.v1.Clusters.update_cluster(cluster.id, cluster_update_spec)
    print("Trigger Cluster deletion")
    task = sddc_client.v1.Clusters.delete_cluster(cluster.id)
    print("Poll Delete Cluster task status")
    helper.poll_task_status(sddc_client, task.id)
    print("Deleted Cluster task response")
    print(task.id)
