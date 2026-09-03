#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

"""
An example of the lifecycle of Direct Path Profile operations, such as
creating, listing, delete and querying direct path profile capacity related
to the host and cluster.
Run this script on a setup which has ESXi host that have vGPU devices.

Usage
direct_path_profiles.py -s <vc-server> -u <user> -p <password> -v <vmName>
   --datacenter-name <datacenterName> --datastore-name <datastoreName>
   --esx-ip <esx-host-ip> -nossl

Explanation of arguments.
vc-server : IP address of vCenter server.
user : User name to login to vCenter server.
password : Password of user to login to vCenter server.
vmName : Name of the new VM that will be created.
esx-ip : IP address of the esxi host on which VM will be registered.
datacenter-name : Name of the datacenter on which the VM will be created.
datastore-name : Name of the datastore on which the VM will be stored.
                 Provide the name of datastore which is connected to the host.

Sample Output
Number of Direct Path Profiles : 1
List of Direct Path Profiles:
Direct Path Profile Name: dpp-mockup-vmiop ID: Yj/5Cgur/wPz5l4tH9yw/gz
VM created: abcd

Number of Direct Path Profiles after vGPU VM power on : 2
List of Direct Path Profiles:
Direct Path Profile Name: unnamed-Nvidia-mockup-vmiop-2c ID: wb6Hy099PPz+8n
Direct Path Profile Name: dpp-mockup-vmiop ID: Yj/5Cgur/wPz5l4tH9yw/gz

Capacity of Direct Path Profiles on Host 'host10':
Direct Path Profile ID : wb6Hy099PPz+8n
Direct Path Profile Name: unnamed-Nvidia-mockup-vmiop-2c
Consumed 1
remaining 15
max 16
unusedReservation 0
Direct Path Profile ID : Yj/5Cgur/wPz5l4tH9yw/gz
Direct Path Profile Name: dpp-mockup-vmiop
Consumed 0
remaining 16
max 32
unusedReservation 0

Capacity of Direct Path Profiles on Cluster 'cls':
Direct Path Profile ID : wb6Hy099PPz+8n
Direct Path Profile Name: unnamed-Nvidia-mockup-vmiop-2c
Consumed 1
remaining 63
max 64
unusedReservation 0
Direct Path Profile ID : Yj/5Cgur/wPz5l4tH9yw/gz
Direct Path Profile Name: dpp-mockup-vmiop
Consumed 0
remaining 112
max 128
unusedReservation 0
Destroying VM abcd
"""

import sys
from pyVim.task import WaitForTask
from pyVmomi import vim
from helpers import cli, pchelper, service_instance


def create_direct_path_profiles_for_vGPU(dppManager, vgpuProfile):
    """
    Creates a Direct path profile for the given vGPU profile.
    """
    dppName = 'dpp-%s' % vgpuProfile
    filterSpec = vim.DirectPathProfileManager.FilterSpec(names=[dppName])
    dppList = dppManager.DirectPathProfileManagerList(filterSpec)
    for dpp in dppList:
        print(f"Found Direct Path Profiles: {dpp.id}")
        dppId = dpp.id
    if len(dppList) == 0:
        sp = vim.DirectPathProfileManager.CreateSpec(name=dppName)
        sp.deviceConfig = vim.DirectPathProfileManager.VmiopDirectPathConfig()
        sp.deviceConfig.vgpuProfile = vgpuProfile
        dppId = dppManager.DirectPathProfileManagerCreate(sp)
    return dppId


def list_direct_path_profiles(dppManager):
    """
    Lists all the direct path profile in the vcenter and prints
    the Direct path profile name and ID.
    """
    filterSpec = vim.DirectPathProfileManager.FilterSpec()
    dppList = dppManager.DirectPathProfileManagerList(filterSpec)
    print()
    print(f"The number of Direct Path Profiles : {len(dppList)}")
    print("List of Direct Path Profiles:")
    for dpp in dppList:
        print(f"Direct Path Profile Name: {dpp.name} ID: {dpp.id}")


def query_direct_path_profile_capacity_on_host(dppManager, host):
    """
    Queries the Direct path profile capacity for the given host
    and print the relevant details.
    """
    targetHost = vim.DirectPathProfileManager.TargetHost()
    targetHost.host = host
    entity = targetHost
    capacityResults = dppManager.DirectPathProfileManagerQueryCapacity(entity)
    print()
    print(f"Capacity of Direct Path Profiles on the Host '{host.name}':")
    for capacityInfo in capacityResults:
        print(f"Direct Path Profile ID : {capacityInfo.profile.id}")
        print(f"Direct Path Profile Name: {capacityInfo.profile.name}")
        print(f"Consumed {capacityInfo.consumed}")
        print(f"remaining {capacityInfo.remaining}")
        print(f"max {capacityInfo.max}")
        print(f"unusedReservation {capacityInfo.unusedReservation}")


def query_direct_path_profile_capacity_on_cluster(dppManager, cluster):
    """
    Queries the Direct path profile capacity for the given cluster
    and print the relevant details.
    """
    targetCluster = vim.DirectPathProfileManager.TargetCluster()
    targetCluster.cluster = cluster
    entity = targetCluster
    capacityResults = dppManager.DirectPathProfileManagerQueryCapacity(entity)
    print()
    print(f"Capacity of Direct Path Profiles on the Cluster '{cluster.name}':")
    for capacityInfo in capacityResults:
        print(f"Direct Path Profile ID : {capacityInfo.profile.id}")
        print(f"Direct Path Profile Name: {capacityInfo.profile.name}")
        print(f"Consumed {capacityInfo.consumed}")
        print(f"remaining {capacityInfo.remaining}")
        print(f"max {capacityInfo.max}")
        print(f"unusedReservation {capacityInfo.unusedReservation}")


def create_vm(si, host, args):
    """
    Creates a VM with the given name on the given datastore and datacenter
    Returns reference to the create VM.
    """
    vm_name = args.vm_name
    datacenter_name = args.datacenter_name
    datastore_name = args.datastore_name
    content = si.RetrieveContent()
    source_pool = host.parent.resourcePool
    if datastore_name is None:
        datastore_name = host.datastore[0].name
    config = create_config_spec(datastore_name=datastore_name, name=vm_name)
    for child in content.rootFolder.childEntity:
        if child.name == datacenter_name:
            vm_folder = child.vmFolder  # child is a datacenter
            break
    else:
        print("Datacenter %s not found!" % datacenter_name)
        sys.exit(1)
    try:
        WaitForTask(vm_folder.CreateVm(config, pool=source_pool, host=host))
        vm = pchelper.get_obj(si.content, [vim.VirtualMachine], vm_name)
        print("VM created: %s" % vm_name)
        return vm
    except vim.fault.DuplicateName:
        print("VM duplicate name: %s" % vm_name, file=sys.stderr)
    except vim.fault.AlreadyExists:
        print("VM name %s already exists." % vm_name, file=sys.stderr)


def create_config_spec(datastore_name, name, memory=4, guest="otherGuest",
                       cpus=1):
    """
    Prepares a config spec to create a VM with the given specifications.
    Returns reference to the VM config spec.
    """
    config = vim.vm.ConfigSpec()
    config.memoryMB = int(memory)
    config.memoryReservationLockedToMax = True
    config.guestId = guest
    config.name = name
    config.numCPUs = cpus
    files = vim.vm.FileInfo()
    files.vmPathName = "[" + datastore_name + "]"
    config.files = files
    return config


def add_vGPU_to_vm(testvm, vgpu='mockup-vmiop'):
    """
    Add given vgpu to given VM by reconfiguring the VM.
    """
    device = vim.vm.device.VirtualPCIPassthrough()
    backing = vim.vm.device.VirtualPCIPassthrough.VmiopBackingInfo()
    backing.SetVgpu(vgpu)
    device.SetBacking(backing)
    configspec = vim.vm.ConfigSpec()
    configspec.memoryReservationLockedToMax = True
    """ Add a device to the given spec """
    devSpec = vim.vm.device.VirtualDeviceSpec()
    devSpec.SetOperation(vim.vm.device.VirtualDeviceSpec.Operation.add)
    devSpec.SetDevice(device)
    configspec.SetDeviceChange([])
    deviceChange = configspec.GetDeviceChange()
    deviceChange.append(devSpec)
    configspec.SetDeviceChange(deviceChange)
    testvm.ReconfigVM_Task(spec=configspec)


def main():
    """
    Sample Python program for creating direct path profile, listing
    all the direct path profiles, deleting the direct path profiles
    and querying the capacity for a given direct path profile on host
    and cluster.
    """
    parser = cli.Parser()
    parser.add_required_arguments(cli.Argument.VM_NAME,
                                  cli.Argument.DATACENTER_NAME,
                                  cli.Argument.DATASTORE_NAME,
                                  cli.Argument.ESX_IP)
    args = parser.get_args()
    si = service_instance.connect(args)
    content = si.RetrieveContent()
    dppManager = content.directPathProfileManager
    if dppManager is not None:
        # mockup-vmiop is the name of vGpu device.
        profile = 'mockup-vmiop'
        dppId = create_direct_path_profiles_for_vGPU(dppManager, profile)
        # Expect number of Direct Path profiles to be 1.
        list_direct_path_profiles(dppManager)
        host = pchelper.get_obj(content, [vim.HostSystem], args.esx_ip)
        vm = create_vm(si, host, args)
        # mockup-vmiop-2c is the name of vGpu device.
        add_vGPU_to_vm(vm, 'mockup-vmiop-2c')
        WaitForTask(vm.PowerOn())
        """
        Powering on a VM with vGPU device might result in auto generating
        a unnamed direct path profile if there is no corresponding user
        generated direct path profile.
        """
        list_direct_path_profiles(dppManager)
        query_direct_path_profile_capacity_on_host(dppManager, host)
        query_direct_path_profile_capacity_on_cluster(dppManager, host.parent)
        dppManager.DirectPathProfileManagerDelete(dppId)
        WaitForTask(vm.PowerOff())
        print("Destroying VM %s" % args.vm_name)
        WaitForTask(vm.Destroy())
    else:
        print("Cannot get reference to Direct Path Profile Manager.")


if __name__ == "__main__":
    main()
