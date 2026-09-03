#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

import time

from vmware.vapi.vsphere.client import create_vsphere_client
from helpers.common import (sample_cli, sample_util)
from helpers.common.ssl_helper import get_unverified_session
from com.vmware.vcenter.deployment_client import Size, DeploymentSize
from com.vmware.vcenter.deployment.size_client import ResizeState, Status

class ScaleUp:
    """
    Demonstrates scale-up operation. Resize the current deployment size of a vCenter to a higher deployment size.
    Resize API is available from vCenter version 9.1.
    sample cmd:
    python ./vcenter/management/resize/scale_up.py --server "10.161.235.150" --username "administrator@vsphere.local"
    --password "E7}o21WvX-gb0_]T" -v

    """

    def __init__(self):
        parser = sample_cli.build_arg_parser()
        args = sample_util.process_cli_args(parser.parse_args())

        # Connect to vAPI services
        session = get_unverified_session() if args.skipverification else None
        """
        Initialize and connect to vCenter.
        :param server: vCenter FQDN or IP
        :param username: vCenter username
        :param password: vCenter password
        """
        self.server = args.server
        self.username = args.username
        self.password = args.password
        # Connect to vCenter
        self.client = create_vsphere_client(
            server=args.server,
            username=args.username,
            password=args.password,
            session=session
        )
        print(f"Connected to vCenter: {self.server}")

    # ---------------------------------------------------------------------
    # 1.Get vCenter deployment info
    # ---------------------------------------------------------------------
    def get_deployment_info(self):
        info = self.client.vcenter.deployment.Size.get()
        print(f"vCenter deployment Size info: {info}")
        return info

    def print_deployment_size_info(self, info):
        print("--------------------------------------------------")
        print(f"vCenter Current deployment size: {info.size}")
        print(f"vCenter CPU count: {info.cpu_count}")
        print(f"vCenter Memory: {info.memory}")
        print(f"vCenter Total disk space: {info.total_disk_space}")
        print("--------------------------------------------------")

    # -------------------------------------------------------------------------
    # 2. Resize vCenter (Scale Up)
    # -------------------------------------------------------------------------
    def resize_vc(self):
        spec = self.create_spec()
        print(f"vCenter resize spec: {spec}")
        self.client.vcenter.deployment.Size.update(spec)

    def create_spec(self):
        connection = Size.Connection(
            hostname=self.server,
            username=self.username,
            password=self.password
        )

        spec = Size.Spec(
            deployment_size=DeploymentSize.SMALL,
            connection=connection,
            defer_service_restart=True
        )
        return spec

    # -------------------------------------------------------------------------
    # 3. Poll and check resize status
    # -------------------------------------------------------------------------
    def get_resize_status(self):
        status_client = self.client.vcenter.deployment.size.Status
        current_state = None
        while True:
            status_info = status_client.get()
            if status_info:
                current_state = status_info.current_state
                print(f"vCenter Current resize state: {current_state}")
            else:
                print("No resize status info available yet.")
            if current_state in (ResizeState.PENDING_SERVICE_RESTART, ResizeState.RESIZING_FAILED):
                break
            print("Resize still in progress... waiting 10 seconds before next check.")
            time.sleep(100)
        print(f"Final resize status info: {status_info}")
        return status_info

    def print_resize_status(self, status_info):
        print("--------------------------------------------------")
        print("vCenter Resize Status:")
        print(f"Current state: {status_info.current_state}")
        if status_info.resize_info:
            print(f"Source deployment size is: {status_info.resize_info.source_deployment_size_name}")
            print(f"Desired deployment size is: {status_info.resize_info.desired_deployment_size_name}")
        print("--------------------------------------------------")

def main():
    scale_up = ScaleUp()

    print("Getting vCenter current deployment size before Scale Up...")
    info_before = scale_up.get_deployment_info()
    scale_up.print_deployment_size_info(info_before)

    print("Initiating vCenter Scale Up...")
    scale_up.resize_vc()

    print("Checking resize status...")
    status_info = scale_up.get_resize_status()
    scale_up.print_resize_status(status_info)

    print("Getting vCenter deployment size after Scale Up...")
    info_after = scale_up.get_deployment_info()
    scale_up.print_deployment_size_info(info_after)


if __name__ == '__main__':
    main()

