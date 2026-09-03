#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

from datetime import datetime, timedelta
import time


def get_license_keys(product_type, license_key_status, sddc_client):
    """
       Get license key information. Use to auto-populate the json required while triggering APIs
       @return: the license key for the mentioned product_type
       """
    try:
        response = sddc_client.v1.LicenseKeys.get_license_keys(
            product_type, license_key_status)
        if len(response.elements) == 0:
            raise AssertionError("Unable to retrieve the license key")
        return response.elements[0].key
    except Exception as ex:
        raise AssertionError("Failed to get the license keys information", ex)


def get_hosts_based_on_status(sddc_client, status):
    """
          Get  hosts. Use to auto-populate the json required while triggering APIs
          @return: the list of unassigned hosts that can be used to create domain, clusters
    """
    try:
        response = sddc_client.v1.Hosts.get_hosts(status=status)
        if len(response.elements) == 0:
            raise AssertionError("Unable to retrieve the unassigned hosts")
        return response.elements
    except Exception as ex:
        raise AssertionError("Unable to retrieve the unassigned hosts", ex)

def get_cluster_image_id(sddc_client):
    """
          Get cluster Image Id. Use to auto-populate the json required while triggering APIs
          @return: the cluster Image Id that can be used to create domain, clusters
    """
    try:
        response = sddc_client.v1.Personalities.get_personalities()
        if response and len(response.elements) == 0:
            raise AssertionError("Unable to retrieve the personalities")
        return response.elements[0].personality_id
    except Exception as ex:
        raise AssertionError("Unable to retrieve the personalities", ex)


def get_host_based_on_cluster_id_for_removal(sddc_client, cluster_id):
    """
          Get  hosts. Use to auto-populate the json required while triggering APIs
          @return: one of the host belongs to the cluster
    """
    try:
        response = sddc_client.v1.Hosts.get_hosts(cluster_id=cluster_id)
        if len(response.elements) <= 6:
            raise AssertionError(
                "Insufficient hosts to remove a host from the cluster")
        return response.elements[6]
    except Exception as ex:
        raise AssertionError(
            "Unable to retrieve the hosts for the mentioned cluster", ex)


def get_domain_id(sddc_client, type, domain_name):
    """
       Get domain_id.
       Use to auto-populate the json required while triggering apis
       @return: domain_id
     """
    try:
        response = sddc_client.v1.Domains.get_domains(type)
        if len(response.elements) == 0:
            raise AssertionError("Unable to retrieve the domain information")
        is_found = False
        for domain in response.elements:
            if domain.name == domain_name:
                return domain.id
        if not is_found:
            raise AssertionError(
                "Failed to get the domain information for specific domain")
    except Exception as ex:
        raise AssertionError(
            "Failed to get the domain information", ex)


def get_management_clusters(sddc_client, domain_id):
    """
       Get a management cluster id.
       Use to pass the management cluster id as parameter for adding host to cluster
       @return: the clusters of management domain
     """
    try:
        response = sddc_client.v1.Clusters.get_clusters(domain_id=domain_id)
        if len(response.elements) == 0:
            raise AssertionError(
                "Unable to retrieve the management domain clusters information")
        return response.elements
    except Exception as ex:
        raise AssertionError(
            "Failed to get the management domain clusters information", ex)


def get_management_clusters_by_name(sddc_client, domain_id, cluster_name):
    """
           Get a management cluster id.
           Use to pass the management cluster id as parameter for adding host to cluster
           @return: the cluster id of management
         """
    try:
        clusters = get_management_clusters(sddc_client, domain_id)
        is_found = False
        for cluster in clusters:
            if cluster.name == cluster_name:
                return cluster
        if not is_found:
            raise AssertionError(
                "Failed to find the cluster information for specific domain")
        return
    except Exception as ex:
        raise AssertionError(
            "Failed to get the management domain information", ex)


def get_cluster_vds(sddc_client, cluster_id):
    """
       Get a Vds name for the  cluster id.
        Use to auto-populate the json required while triggering apis
       @return: vds name
     """
    try:
        response = sddc_client.v1.clusters.Vdses.get_vdses(cluster_id)
        if len(response) == 0:
            raise AssertionError("Unable to retrieve the vdses information")
        return response[0].name
    except Exception as ex:
        raise AssertionError("Failed to get the vdses information", ex)


def get_task_status(sddc_client, task_id):
    """
       Returns the status for a given task id.
       Used to check status of the task
       @return: task
     """
    try:
        return sddc_client.v1.Tasks.get_task(task_id)
    except Exception as ex:
        raise AssertionError("Failed to get the task status information", ex)


def retry_task(sddc_client, task_id):
    """
       Retry a failed Task by ID, if it exists
     """
    try:
            time.sleep(300)
            sddc_client.v1.Tasks.retry_task(task_id)
            return
    except Exception as ex:
        raise AssertionError("Failed to retry the task status information", ex)


def validate_domain_request(sddc_client, domain_creation_spec):
    """
       Validate the domain create request payload.
       Use to verify the request payload for create domain
     """
    try:
        response = sddc_client.v1.domains.Validations.validate_domain_creation_spec(
            domain_creation_spec)
        if response.result_status == "FAILED":
            raise AssertionError("Failed to validate the request payload")
        return
    except Exception as ex:
        raise AssertionError("Failed to validate the request payload", ex)


def validate_cluster_request(sddc_client, cluster_creation_spec):
    """
       Validate the cluster create request payload.
       Use to verify the request payload for create cluster
     """
    try:
        response = sddc_client.v1.clusters.Validations.validate_cluster_creation_spec(
            cluster_creation_spec)
        if response.result_status == "FAILED":
            raise AssertionError("Failed to validate the request payload")
        return
    except Exception as ex:
        raise AssertionError("Failed to validate the request payload", ex)

def poll_domain_status(sddc_client, domain_id):
    """
           poll the domain status.
           Use to poll the status of the domain
         """
    try:
        domains_info = sddc_client.v1.Domains.get_domain(domain_id)
        while domains_info.status == "ACTIVATING":
            time.sleep(30)
            domains_info = sddc_client.v1.Domains.get_domain(domain_id)

        if domains_info.status == "ACTIVE":
            print("The domain status is changed to ACTIVE", domain_id)
            return
        
        raise AssertionError(
            "Cannot perform operation on the domain as the status is set to {}", domains_info.status , domain_id)

    except Exception as ex:
        raise AssertionError(
            "Failed to poll the domain status for the domain id", domain_id, ex)

def poll_task_status(sddc_client, task_id):
    """
       poll the task status.
       Use to poll the status of the task and perform cleanup once done successfully
       Included the logic for retrying a failed task. A maximum of five retries will be attempted if the
       workflow fails due to a genuine issue or testbed instability.
     """
    try:
        task = get_task_status(sddc_client, task_id)
        start_time = datetime.now()
        retry_count = 1
        print("task {}".format(task.id))
        while task.status == "Pending" or task.status == "In Progress":
            time.sleep(900)
            task = get_task_status(sddc_client, task_id)
            if task.status == "Failed":
                if retry_count < 5:
                    print("Retry the task count: {}".format(retry_count))
                    retry_task(sddc_client,task_id)
                    time.sleep(600)
                    task = get_task_status(sddc_client, task_id)
                    retry_count =+ 1
                else:
                    raise AssertionError(
                        "Failed to perform the operation with task_id ", task_id)
        if task.status != "Successful":
            raise AssertionError(
                "Failed to perform the operation with task_id ", task_id)
        overall_time = (datetime.now() - start_time).total_seconds()/60.0
        print("Overall Time Taken in mins: {}".format(overall_time))
        return
    except Exception as ex:
        raise AssertionError(
            "Failed to poll the task status for the task id", task_id, ex)
