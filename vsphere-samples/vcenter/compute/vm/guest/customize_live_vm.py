#!/usr/bin/env python

# Copyright (c) 2025-2026 Broadcom. All Rights Reserved.
# Broadcom Confidential. The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

"""
Demo how to customize a running virtual machine.

Sample Prerequisites:
- The sample needs an existing Linux VM with vmtools/open-vm-tools installed.
- The guest customization engine needs to be installed in a virtual machine
  before using the API. Details refer to [Installing the Guest Customization
  Engine](https://techdocs.broadcom.com/us/en/vmware-cis/vsphere/vsphere-sdks-tools/8-0/web-services-sdk-programming-guide/virtual-machine-guest-operations/guest-network-customization-for-instant-clone-virtual-machines/installing-the-guest-customization-engine.html).

How to run this script:
python3 customize_live_vm.py -s vCenterIP -u vCenterUserName -p vCenterPassword
-n vmName -v -vu vmUserName -vp vmPassword
"""

__vcenter_version__ = '9.0+'

import time
import ssl
import configparser
from os.path import dirname, realpath, join as pjoin
from pyVim.connect import SmartConnect
from pyVmomi import vim
from com.vmware.vcenter.vm_client import Power
from vmware.vapi.vsphere.client import create_vsphere_client
from com.vmware.vapi.std.errors_client import NotFound
from helpers.common.sample_cli import build_arg_parser
from helpers.common.ssl_helper import get_unverified_session
from helpers.common.vim.helpers.vim_utils import get_obj
from helpers.vm_helpers.vm_helper import get_vm
from customizationSpecs import CustomizationSpecManager


# New class inheriting from CustomizationSpecManager to create Linux
# customizations
class NewCustomizationSpecManager(CustomizationSpecManager):
    def __init__(self, client):
        self.client = client
        self.specs_svc = client.vcenter.guest.CustomizationSpecs
        self.config = configparser.ConfigParser()
        self.linCfgPath = pjoin(dirname(realpath(__file__)),
                                'resources/linSpec.cfg')
        self.specsAdded = []


class CustomizeVM(object):
    def __init__(self):
        parser = build_arg_parser()

        # Add command line arguments
        parser.add_argument('-n', '--vm_name',
                            action='store', required=True,
                            help='Name of the testing vm')
        parser.add_argument('-vu', '--vm_username',
                            action='store', required=True,
                            help='VM username')
        parser.add_argument('-vp', '--vm_password',
                            action='store', required=True,
                            help='VM password')

        self.args = parser.parse_args()

        self.vm_name = self.args.vm_name
        self.vm_username = self.args.vm_username
        self.vm_password = self.args.vm_password
        self.cleardata = self.args.cleardata

        if not all([self.vm_name, self.vm_username, self.vm_password]):
            raise Exception('Must specify an existing Linux VM and the'
                            + ' VM username and password for test with'
                            + ' "-n VM_NAME -vu VM_USERNAME'
                            + ' -vp VM_PASSWORD"')

        session = \
            get_unverified_session() if self.args.skipverification else None
        self.client = create_vsphere_client(server=self.args.server,
                                            username=self.args.username,
                                            password=self.args.password,
                                            session=session)

        sslContext = ssl._create_unverified_context()
        self.si = SmartConnect(host=self.args.server,
                               user=self.args.username,
                               pwd=self.args.password,
                               sslContext=sslContext)

        self.specs_svc = self.client.vcenter.guest.CustomizationSpecs
        self.vmcust_svc = self.client.vcenter.vm.guest.CustomizationLive
        self.custSpecMgr = NewCustomizationSpecManager(self.client)

        self.vm = get_vm(self.client, self.vm_name)
        if not self.vm:
            raise Exception('Need an existing Linux vm with name ({}).'
                            'Please create the vm first.'.format(self.vm_name))
        self.vmRef = self.getVmRef(vmName=self.vm_name)

    def getVmRef(self, vmName=None):
        """Retrieve the VM reference from vSphere."""

        content = self.si.RetrieveContent()
        return get_obj(content, [vim.VirtualMachine], vmName)

    def powerOnVm(self):
        """Ensure the VM is powered on."""

        print('Ensure the VM is powered-on.')
        status = self.client.vcenter.vm.Power.get(self.vm)
        print('vm.Power.get({})'.format(status))
        if status == Power.Info(state=Power.State.POWERED_OFF,
                                clean_power_off=True):
            print('Powering on VM: ({})'.format(self.vm))
            self.client.vcenter.vm.Power.start(self.vm)
            # Wait for the vm to fully power on
            time.sleep(30)

    def customizeLiveVM(self):
        """Customize the running VM by applying the customization spec."""

        print("Using VM '{}' ({}) for Customization test".
              format(self.vm_name, self.vm))
        # create a linux customizationSpec
        self.custSpecMgr.parseLinuxCfg()
        self.specName = self.custSpecMgr.specName
        print("Create a default Linux customizationSpec '{}'".
              format(self.specName))
        try:
            self.specs_svc.get(self.specName)
            print("Default customizationSpec '{}' exists. Skip creating".
                  format(self.specName))
        except NotFound:
            self.custSpecMgr.createLinuxSpec()

        print('Create the credentials.')
        vmCred = self.vmcust_svc.GuestAuthentication(self.vm_username,
                                                     self.vm_password)

        print('Set the specification.')
        self.setSpec = self.vmcust_svc.RunSpec(name=self.specName, spec=None,
                                               auth=vmCred)

        print('Run VM customization.')
        # Customize the running VM
        task_svc = self.vmcust_svc.run_task(vm=self.vm, spec=self.setSpec)

        if not self.waitForTaskToComplete(task_svc):
            return False

    def waitForTaskToComplete(self, task_svc):
        """Wait for the task to complete and return the result."""

        taskId = task_svc.get_task_id()
        print("TaskId is '{}'".format(taskId))
        taskInstance = task_svc.task_svc_instance
        print("TaskInstance is '{}'".format(taskInstance))

        while True:
            taskDetails = taskInstance.get(taskId)
            print("TaskDetails '{}'".format(taskDetails))
            if taskDetails.status == self.vmcust_svc.Info.Status.SUCCEEDED:
                print("Task '{}' Succeeded".format(taskId))
                return True
            if taskDetails.status == self.vmcust_svc.Info.Status.FAILED:
                print("Task '{}' Failed. Task Info '{}'".format(taskId,
                                                                taskDetails))
                return False
            time.sleep(5)

    def verifyStatus(self):
        """Verify the customization status on the VM."""

        print("Verify the status on the VM '{}'".format(self.vm_name))
        goscInfo = self.vmcust_svc.get(self.vm)
        print("Live customization status is '{}'".format(goscInfo.status))
        if goscInfo.status == self.vmcust_svc.Info.Status.SUCCEEDED:
            print("Test PASS!")

    def cleanUp(self):
        """
        Clean up the VM by deleting the customization spec and powering off.
        """

        vm = self.vm
        # clear customizationSpec
        self.custSpecMgr.deleteSpec()
        # Power off the vm if it is on
        status = self.client.vcenter.vm.Power.get(vm)
        if status == Power.Info(state=Power.State.POWERED_ON):
            print('VM is powered on, power it off')
            self.client.vcenter.vm.Power.stop(vm)
            print('vm.Power.stop({})'.format(vm))
        status = self.client.vcenter.vm.Power.get(vm)
        if status == Power.Info(state=Power.State.POWERED_OFF):
            self.client.vcenter.VM.delete(vm)
            print("Deleted VM -- '{}-({})".format(self.vm_name, vm))


def main():
    myCustomizeVM = CustomizeVM()
    myCustomizeVM.powerOnVm()
    myCustomizeVM.customizeLiveVM()
    myCustomizeVM.verifyStatus()
    if myCustomizeVM.cleardata:
        print("Clean up in progress...")
        myCustomizeVM.cleanUp()


if __name__ == '__main__':
    main()
