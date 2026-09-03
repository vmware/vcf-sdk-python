#!/usr/bin/env python

# Copyright (c) 2016-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '6.5+'

from com.vmware.vcenter_client import Network

import helpers.vm_helpers.network_helper
import vcenter.compute.vm.hardware.main
import vcenter.compute.vm.placement
import vcenter.compute.vm.power
from helpers.common.sample_util import pp
from helpers.setup import testbed_setup
from helpers.setup import testbed
from vcenter.compute.vm.create.create_default_vm import CreateDefaultVM
from vcenter.compute.vm.create.create_basic_vm import CreateBasicVM
from vcenter.compute.vm.create.create_exhaustive_vm import \
    CreateExhaustiveVM


class VMSetup(object):
    def __init__(self, context=None):
        self.context = context
        self.basic_vm = None
        self.default_vm = None
        self.exhaustive_vm = None

    def setup(self, context):
        print('Setup Samples Started')

        self.context = context

        ###########################################################################
        # Getting a PlacementSpec
        ###########################################################################
        placement_spec = vcenter.compute.vm.placement.get_placement_spec_for_resource_pool(context)
        print('=' * 79)
        print('= Resource selection')
        print('=' * 79)
        print('placement_spec={}'.format(pp(placement_spec)))

        ###########################################################################
        # Getting a Network
        # Choose one of the following ways to get the PlacementSpec
        # 1. STANDARD_PORTGROUP on DATACENTER2
        # 2. DISTRIBUTED_PORTGROUP on DATACENTER2
        ###########################################################################
        standard_network = helpers.vm_helpers \
            .network_helper.get_network_backing(
            context.client,
            context.testbed.config['STDPORTGROUP_NAME'],
            context.testbed.config['VM_DATACENTER_NAME'],
            Network.Type.STANDARD_PORTGROUP)
        print('standard_network={}'.format(standard_network))

        distributed_network = helpers.vm_helpers \
            .network_helper.get_network_backing(
            context.client,
            context.testbed.config['VDPORTGROUP1_NAME'],
            context.testbed.config['VM_DATACENTER_NAME'],
            Network.Type.DISTRIBUTED_PORTGROUP)
        print('distributed_network={}'.format(distributed_network))

        print('=' * 79)

        self.default_vm = CreateDefaultVM(context.client,
                                          placement_spec)
        self.basic_vm = CreateBasicVM(context.client, placement_spec)
        self.exhaustive_vm = CreateExhaustiveVM(context.client,
                                                placement_spec,
                                                standard_network,
                                                distributed_network)

        print('Setup Samples Complete')

    def cleanup(self):

        print('Cleanup Samples Started')
        CreateDefaultVM(self.context.client).cleanup()
        CreateBasicVM(self.context.client).cleanup()
        CreateExhaustiveVM(self.context.client).cleanup()
        print('Cleanup Samples Complete\n')

    def validate(self):
        print('Validating and Detecting Resources in vcenter.vm Samples')
        r = testbed_setup.validate(self.context)
        if r:
            print('==> Samples Setup validated')
            return True
        else:
            print('==> Samples Setup has errors')
            return False

    def run(self):
        # Clean up in case of past failures
        self.cleanup()

        # Check that sample is ready to run
        if self.context.option['DO_SAMPLES']:
            if not self.validate():
                exit(0)

        ###########################################################################
        # Create VM samples
        #
        # Choose one of the following ways to create the VM
        # 1. Default
        # 2. Basic (2 disks, 1 nic)
        # 3. Exhaustive (3 disks, 2 nics, 2 vcpu, 2 GB memory, boot=BIOS, 1 cdrom,
        #                1 serial port, 1 parallel port, 1 floppy,
        #                boot_devices= [CDROM, DISK, ETHERNET])
        ###########################################################################
        self.default_vm.run()
        self.basic_vm.run()
        self.exhaustive_vm.run()

        ###########################################################################
        # Incremental device CRUDE + connect/disconnect samples
        #
        ###########################################################################
        if self.context.option['DO_SAMPLES_INCREMENTAL']:
            vcenter.compute.vm.hardware.main.setup(self.context)
            vcenter.compute.vm.hardware.main.validate(self.context)
            vcenter.compute.vm.hardware.main.run()
            if self.context.option['DO_SAMPLES_CLEANUP']:
                vcenter.compute.vm.hardware.main.cleanup()

        # Sample cleanup
        if self.context.option['DO_SAMPLES_CLEANUP']:
            self.cleanup()
