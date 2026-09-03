#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

from utils.misc_util import poll

_VALIDATION_STATUS_COMPLETED = "COMPLETED"
_VALIDATION_STATUS_IN_PROGRESS = "IN_PROGRESS"
_VALIDATION_STATUS_UNKNOWN = "UNKNOWN"
_VALIDATION_STATUS_FAILED = "FAILED"
_DEPLOYMENT_STATUS_COMPLETED_WITH_SUCCESS = "COMPLETED_WITH_SUCCESS"
_DEPLOYMENT_STATUS_COMPLETED_WITH_FAILURE = "COMPLETED_WITH_FAILURE"

_DEFAULT_POLL_INTERVAL = 60

def poll_sddc_validation_status(client, validation_id, timeout):
    """
    Poll the validation status.

    :type: client: :class:`utils.client.VcfInstallerClient`
    :param client: VCF Installer Client
    :param validation_id: id of validation
    :param timeout: time to poll before giving up (in hours)
    :return: retrieved validation if it is successful or `None` if still in progress
    :rtype: :class:`vmware.vcf_installer.model_client.Validation`
    :raises AssertionError: If validation fails or a timeout is hit.
    """
    def poller():
        validation = client.v1.sddcs.Validations.get_sddc_spec_validation(validation_id)

        if not validation:
            raise AssertionError("Unable to poll validation")
        elif validation.execution_status == _VALIDATION_STATUS_COMPLETED:
            print ("Validation with id:{0} completed successfully!".format(validation_id))
            return validation
        elif validation.execution_status != _VALIDATION_STATUS_IN_PROGRESS:
            log_validation_result(validation)
            raise AssertionError("Failed to perform validation with id ",
                                 validation_id, validation.execution_status)
        else:
            print ("Validation with id:{0} has status {1}.".format(validation_id,
                                                                   validation.execution_status))
            return None

    return poll(poller, timeout, _DEFAULT_POLL_INTERVAL)

def log_validation_result(validation):
    failed_validations = []
    for val_check in validation.validation_checks:
        if _VALIDATION_STATUS_UNKNOWN == val_check.result_status:
            print("Validation check {0} result is {1}".format(val_check.description,
                                                              val_check.result_status))
        if _VALIDATION_STATUS_FAILED == val_check.result_status:
            failed_validations.append(val_check)

    print("A total of {0} number of validation checks failed.\n".format(len(failed_validations)))
    for failed_check in failed_validations:
        print("Failed validation check {0}\n".format(failed_check))


def poll_sddc_deployment_status(client, sddc_task_id, timeout):
    """
    Poll the SDDC deployment task status.

    :type: client: :class:`utils.client.VcfInstallerClient`
    :param client: VCF Installer Client
    :param sddc_task_id: id of sddc deployment task
    :param timeout: time to poll before giving up (in hours)
    :return: the retrieved task if it is successful or `None` if still in progress
    :rtype: :class:`vmware.vcf_installer.model_client.SddcTask`
    :raises AssertionError: If validation fails or a timeout is hit.
    """
    def poller():
        task = client.v1.Sddcs.get_sddc_task_by_id(sddc_task_id)
        if not task:
            raise AssertionError("Unable to poll sddc deployment task")
        elif task.status == _DEPLOYMENT_STATUS_COMPLETED_WITH_SUCCESS:
            return task
        elif task.status == _DEPLOYMENT_STATUS_COMPLETED_WITH_FAILURE:
            raise AssertionError("Failed deployment with id {}".format(sddc_task_id))
        else:
            return None

    return poll(poller, timeout, _DEFAULT_POLL_INTERVAL)
