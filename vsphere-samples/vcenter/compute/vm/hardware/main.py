#!/usr/bin/env python

# Copyright (c) 2016-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

__vcenter_version__ = '6.5+'

import vcenter.compute.vm.hardware.adapter.sata
import vcenter.compute.vm.hardware.adapter.scsi
import vcenter.compute.vm.hardware.boot
import vcenter.compute.vm.hardware.boot_device
import vcenter.compute.vm.hardware.cdrom
import vcenter.compute.vm.hardware.cpu
import vcenter.compute.vm.hardware.disk
import vcenter.compute.vm.hardware.ethernet
import vcenter.compute.vm.hardware.floppy
import vcenter.compute.vm.hardware.memory
import vcenter.compute.vm.hardware.parallel
import vcenter.compute.vm.hardware.serial
from helpers.setup import testbed

from helpers.vm_helpers.vm_helper import get_vm


def setup(context):
    print('Setup vcenter.vm.hardware Samples Started')
    vcenter.compute.vm.hardware.cpu.setup(context)
    vcenter.compute.vm.hardware.memory.setup(context)
    vcenter.compute.vm.hardware.disk.setup(context)
    vcenter.compute.vm.hardware.adapter.sata.setup(context)
    vcenter.compute.vm.hardware.adapter.scsi.setup(context)
    vcenter.compute.vm.hardware.boot.setup(context)
    vcenter.compute.vm.hardware.boot_device.setup(context)
    vcenter.compute.vm.hardware.cdrom.setup(context)
    vcenter.compute.vm.hardware.ethernet.setup(context)
    vcenter.compute.vm.hardware.floppy.setup(context)
    vcenter.compute.vm.hardware.serial.setup(context)
    vcenter.compute.vm.hardware.parallel.setup(context)
    print('Setup vcenter.vm.hardware Samples Complete\n')


def cleanup():
    print('Cleanup vcenter.vm.hardware Samples Started')
    vcenter.compute.vm.hardware.cpu.cleanup()
    vcenter.compute.vm.hardware.memory.cleanup()
    vcenter.compute.vm.hardware.disk.cleanup()
    vcenter.compute.vm.hardware.adapter.sata.cleanup()
    vcenter.compute.vm.hardware.adapter.scsi.cleanup()
    vcenter.compute.vm.hardware.boot.cleanup()
    vcenter.compute.vm.hardware.boot_device.cleanup()
    vcenter.compute.vm.hardware.cdrom.cleanup()
    vcenter.compute.vm.hardware.ethernet.cleanup()
    vcenter.compute.vm.hardware.floppy.cleanup()
    vcenter.compute.vm.hardware.serial.cleanup()
    vcenter.compute.vm.hardware.parallel.cleanup()
    print('Cleanup vcenter.vm.hardware Samples Complete\n')


def validate(context):
    print('Validating and Detecting Resources in vcenter.vm.hardware Samples')
    names = set([testbed.config['VM_NAME_DEFAULT'],
                 testbed.config['VM_NAME_BASIC'],
                 testbed.config['VM_NAME_EXHAUSTIVE']])
    valid = True
    for name in names:
        if not get_vm(context.client, name):
            valid = False
    if not valid:
        raise Exception('==> Samples Setup validation failed: '
                        'Missing VMs required to run hardware samples')
    print('==> Samples Setup validated')


def run():
    ###########################################################################
    # Incremental device CRUDE + connect/disconnect samples
    #
    # Choose any combination of the following incremental hardware examples.
    # Each one will return the VM to its original configuration.
    #
    # * CPU update sample
    # * Memory update sample
    # * Disk CRUD sample
    # * Ethernet CRUD sample
    # * CDROM CRUD sample
    # * SCSI adapter sample
    # * SATA adapter sample
    # * Serial Port CRUD sample
    # * Parallel Port CRUD sample
    # * Floppy CRUD sample
    # * Boot configuration sample
    # * Boot Device configuration sample
    ###########################################################################
    print('#' * 79)
    print('# vcenter.vm.hardware Samples')
    print('#' * 79)
    vcenter.compute.vm.hardware.cpu.run()
    vcenter.compute.vm.hardware.memory.run()
    vcenter.compute.vm.hardware.disk.run()
    vcenter.compute.vm.hardware.adapter.sata.run()
    vcenter.compute.vm.hardware.adapter.scsi.run()
    vcenter.compute.vm.hardware.boot.run()
    vcenter.compute.vm.hardware.boot_device.run()
    vcenter.compute.vm.hardware.cdrom.run()
    vcenter.compute.vm.hardware.ethernet.run()
    vcenter.compute.vm.hardware.floppy.run()
    vcenter.compute.vm.hardware.serial.run()
    vcenter.compute.vm.hardware.parallel.run()

    ###########################################################################
    # Virtual Hardware Upgrade Sample
    #
    # TODO Not implemented
    ###########################################################################

    ###########################################################################
    # Hot Add Samples
    # * Hot add disk
    # * Hot add cdrom
    # * ...
    # TODO Not implemented
    ###########################################################################
