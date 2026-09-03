#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

import re
import time
from datetime import datetime, timedelta


def get_version_without_build_number(client):
    """
    Retrieves VCF Installer version without the build number suffix ".12345"
    :type: client: :class:`utils.client.VcfInstallerClient`
    :param client: VCF Installer Client
    :return: version
    """
    appliance_info = client.v1.system.ApplianceInfo.get_appliance_info()
    appliance_info_version = appliance_info.version
    version_regex = re.compile("(\\d+[.]\\d+[.]\\d+[.]\\d+)[.]\\d+")
    version_match = version_regex.match(appliance_info_version)
    if version_match:
        version_without_build = version_match.group(1)
    else:
        raise AssertionError("Cannot parse version {}".format(appliance_info_version))
    return version_without_build


def poll(poll_func, max_timeout, poll_interval):
    """
    Generic polling function to wait a condition to be met
    :param poll_func: function that calls the respective API to evaluate if polling should complete.
                    Returns a result when done. Returns None while not ready.
                    Throws an Exception in case the expected resource failed.
    :param max_timeout: maximum time to wait the respective condition (in hours)
    :param poll_interval: how often to call poll_func (in seconds)
    :return: the result of poll_func if polled successfully
    """
    start_time = datetime.now()
    timeout_time = start_time + timedelta(hours=max_timeout)
    timed_out = False
    try:
        while not timed_out:
            result = poll_func()
            if result:
                overall_time = (datetime.now() - start_time).total_seconds()/60.0
                print("Overall Time Taken in mins: {:.2f}".format(overall_time))
                return result
            time.sleep(poll_interval)
            timed_out = datetime.now() > timeout_time
    except Exception as e:
        raise AssertionError("Polling failed due to error.", e)

    raise AssertionError("Polling timed out")


def parse_bool_or_str(value):
    """
    Parse boolean value from bool|str.
    :param value: value to parse to bool
    :type: `bool`|`str`
    :return: boolean value if parsed, otherwise value is returned as is
    """
    if isinstance(value, str) and value.lower() in ('true', 'false'):
        return value.lower() == 'true'
    return value
