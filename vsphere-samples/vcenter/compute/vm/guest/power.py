#!/usr/bin/env python

# Copyright (c) 2019-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '6.7+'

import logging

from com.vmware.vcenter.vm_client import Power as HardPower
from com.vmware.vapi.std.errors_client import (NotFound, ServiceUnavailable)
from com.vmware.vcenter.vm.guest_client import Power
from com.vmware.vcenter.vm.guest_client import Identity
from vmware.vapi.vsphere.client import create_vsphere_client
from helpers.common.sample_util import parse_cli_args_vm
from helpers.common.sample_util import pp
from helpers.setup import testbed
from helpers.vm_helpers.vm_helper import get_vm
from helpers.common.ssl_helper import get_unverified_session
from helpers.vm_helpers.guest_helper import \
    (wait_for_guest_info_ready, wait_for_guest_power_state,
        wait_for_power_operations_state)

"""
Demonstrates the virtual machine soft power operations.

Sample Prerequisites:
The sample needs an existing VM with VMware Tools.
"""
STATE_TIMEOUT = 300


class SoftPower(object):
    """
    Demonstrates soft power APIs
    Sample Prerequisites:
    vCenter/ESX
    """
    def __init__(self):
        server, username, password, self.cleardata, \
                   skip_verification, self.vm_name = \
            parse_cli_args_vm(testbed.config['VM_NAME_DEFAULT'])

        session = get_unverified_session() if skip_verification else None
        self.vsphere_client = create_vsphere_client(server=server,
                                                    username=username,
                                                    password=password,
                                                    session=session)

        # Increase the logging level for more detailed output.
        # logging.basicConfig(level=logging.DEBUG)

    def run(self):
        self.vm = get_vm(self.vsphere_client, self.vm_name)
        if not self.vm:
            raise Exception('Sample requires an existing vm with name ({}).'
                            'Please create the vm first.'.format(self.vm_name))
        print("Using VM '{}' ({}) for Guest Power Sample".format(self.vm_name,
                                                                 self.vm))

        # power on the VM if necessary
        status = self.vsphere_client.vcenter.vm.Power.get(self.vm)
        if status != HardPower.Info(state=HardPower.State.POWERED_ON):
            print("Powering on VM {}.".format(self.vm_name))
            self.vsphere_client.vcenter.vm.Power.start(self.vm)
            print('vm.Power.start({})'.format(self.vm))

        # reboot the guest
        wait_for_power_operations_state(self.vsphere_client, self.vm,
                                        True, STATE_TIMEOUT)
        print('\n# Example: Reboot the vm')
        identity = self.vsphere_client.vcenter.vm.guest.Power.reboot(self.vm)
        wait_for_power_operations_state(self.vsphere_client, self.vm,
                                        False, STATE_TIMEOUT)
        print('Tools have stopped.')
        wait_for_guest_power_state(self.vsphere_client, self.vm,
                                   Power.State.RUNNING, STATE_TIMEOUT)
        wait_for_power_operations_state(self.vsphere_client, self.vm,
                                        True, STATE_TIMEOUT)
        print('vm.guest.Power.reboot({})'.format(self.vm))

        # Standby the guest -- already running from previous step
        print('\n# Example: Standby the vm')
        self.vsphere_client.vcenter.vm.guest.Power.standby(self.vm)
        wait_for_guest_power_state(self.vsphere_client, self.vm,
                                   Power.State.NOT_RUNNING, STATE_TIMEOUT)
        print('vm.guest.Power.standby({})'.format(self.vm))

        # shutdown the guest
        # power back on from previous standby
        self.vsphere_client.vcenter.vm.Power.start(self.vm)
        wait_for_power_operations_state(self.vsphere_client, self.vm,
                                        True, STATE_TIMEOUT)
        print("Shutting down VM {}.".format(self.vm_name))
        self.vsphere_client.vcenter.vm.guest.Power.shutdown(self.vm)
        wait_for_guest_power_state(self.vsphere_client, self.vm,
                                   Power.State.NOT_RUNNING, STATE_TIMEOUT)
        print('vm.guest.Power.shutdown({})'.format(self.vm))

    def cleanup(self):
        # no-op, sample leaves VM off
        return


def main():
    soft_power = SoftPower()
    soft_power.run()
    soft_power.cleanup()


if __name__ == '__main__':
    main()
