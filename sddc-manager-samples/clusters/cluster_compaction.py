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
Demonstrates how to remove a Host from a cluster.
Prerequisites to remove a host from a cluster:
    1. Ensure that Host with the given name exists inside the chosen cluster.
    2. Ensure that you have enough hosts remaining to facilitate the configured vSAN availability.
    3. Failure to do so might result in the datastore being marked as read-only or in data loss.
Prerequisite before executing the sample -
   1.In this sample, wherever the helper.get_domain_id method is called, replace the second argument with the domain type (e.g., 'MANAGEMENT' or 'VI')
     and the third argument with the domain name. This will fetch the relevant domain ID, which is needed for further computation to retrieve the 
     cluster details where the host needs to be added.
   2. In the sample, wherever the get_management_clusters_by_name method is called, replace the third argument with the name of the cluster
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
    host = helper.get_host_based_on_cluster_id_for_removal(sddc_client, cluster.id)
    cluster_updation_spec.cluster_compaction_spec["hosts"][0]["fqdn"] = host.fqdn
    cluster_updation_spec.cluster_compaction_spec["hosts"][0]["id"] = host.id
    return cluster.id


with open("clusters/cluster_compaction.json", "r") as json_data:
    cluster_compaction_json = json_data.read()
    cluster_updation_spec = create_cluster_update_spec_from_json(
        cluster_compaction_json)
    cluster_id = populate_the_prerequisite_in_request_payload(
        cluster_updation_spec)
    print("Delete host from management cluster")
    task = sddc_client.v1.Clusters.update_cluster(
        cluster_id, cluster_updation_spec)
    #sleep before starting the polling
    time.sleep(20)
    # poll the task status
    helper.poll_task_status(sddc_client, task.id)
    print("Cluster Compaction task response")
    print(task.id)
