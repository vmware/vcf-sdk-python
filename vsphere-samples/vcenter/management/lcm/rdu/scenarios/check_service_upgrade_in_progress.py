#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '9.1.0'

import dataclasses
import logging
import sys
import time

from datetime import datetime

import requests
import dateutil
from dateutil import tz

from vmware.vapi.vsphere.client import create_vsphere_client

from helpers.common import sample_cli
from helpers.common import sample_util
from helpers.common.ssl_helper import get_unverified_session


logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

"""
Demonstrates calling a vCenter API during service upgrade. The vCenter would then respond
with HTTP 503 and 2 additional HTTP headers to notify the client when to retry.
Sample Prerequisites:
vCenter with RDU initiated, and currently in Switchover state
"""

@dataclasses.dataclass
class ListVM():
    """
    Class to perform some vCenter operation during RDU Switchover.
    """

    def __init__(self):
        parser = sample_cli.build_arg_parser()
        args = sample_util.process_cli_args(parser.parse_args())
        session = get_unverified_session() if args.skipverification else None
        self.client = create_vsphere_client(server=args.server,
                                            username=args.username,
                                            password=args.password,
                                            session=session)

    def run(self):
        """
        Example of calling a vCenter API - list VMs
        """
        list_of_vms = self.client.vcenter.VM.list()
        logger.info("----------------------------")
        logger.info("List Of VMs")
        logger.info("----------------------------")
        logger.info(list_of_vms)
        logger.info("----------------------------")


def wait_before_retry(upgrade_in_progress: bool, retry_after: datetime):
    """
    compare retry_after with current time and wait if necessary
    """

    # add here any time zone you may need
    tz_infos = {"CDT": tz.gettz('US/Central'),
                "PST": tz.gettz('US/Pacific'),
                "EST": tz.gettz("US/East"),
                "CET": tz.gettz('Europe/Central')}

    logger.info("service-upgrade-in-progress: %s", upgrade_in_progress)
    logger.info("retry-after: %s", retry_after)

    # parse the time in RFC1123 format and wait to retry after it...
    parsed_time = dateutil.parser.parse(retry_after, tzinfos=tz_infos)
    local_parsed_time = parsed_time.astimezone(tz=None)
    now_time = datetime.now().astimezone(tz=None)

    if local_parsed_time > now_time:
        seconds_to_wait = (local_parsed_time - now_time).total_seconds()
        logger.info("waiting for %d seconds until %s...", seconds_to_wait, local_parsed_time)
        time.sleep(seconds_to_wait)

    logger.info("done waiting")


def main():
    """
    main function
    """

    try:
        list_vm = ListVM()
        list_vm.run()
    except requests.exceptions.HTTPError as e:
        # During service upgrades, the vCenter (9.1 and above) responds with
        # HTTP Code 503 'Service unavailable' and 2 additional headers:
        # service-upgrade-in-progress: true / false
        # retry-after: datetime in rfc1123 format; the expected time when upgrade should finish
        # The operation should be retried after this time.
        logger.info("HTTP Code: %d", e.response.status_code)
        if e.response.status_code == 503:
            if ('service-upgrade-in-progress' in e.response.headers
                    and 'retry-after' in e.response.headers):
                wait_before_retry(e.response.headers["service-upgrade-in-progress"],
                                  e.response.headers["retry-after"])
                logger.info("Now retry the operation:")
                list_vm = ListVM()
                list_vm.run()
            else:
                # probably not an upgrade, instead some other unexpected problem
                logger.error(e.response.text)

if __name__ == '__main__':
    main()
