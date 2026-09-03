This directory contains below samples for inventory APIs:

1. Bulk Transition

   | Sample                              | Description                                                                 |
   |-------------------------------------|-----------------------------------------------------------------------------|
   | customize_vm.py                     | Demonstrates customizing a Linux virtual machine.                           |
   | customize_vm_with_cloudinit_data.py | Demonstrates customizing a Linux virtual machine with cloud-init data       |
   | customize_live_vm.py                | Demonstrates customizing a running Linux virtual machine and start the network service in the guest. |
   | customizationSpecs.py               | Demonstrates create/list/get/set/delete customizationSpecs in vCenter       |
   | customizationSpecs_import_export.py | Demonstrates import/export customizationSpecs in vCenter                    |
   | cloudinitDataCustomizationSpecs.py  | Demonstrates create/list/get/set/delete cloud-init data customizationSpecs in vCenter |


### Running the samples:
Run the commands below to customize a virtual machine and manage customization specifications.

    # customize a Linux virtual machine
    python <sample-dir>/customize_vm.py -s "<vcenter_ip>" -u "<vcenter_user>" -p "<vcenter_password>" -n "<vm_name>" -v

    # customize a Linux virtual machine with cloud-init data
    python <sample-dir>/customize_vm_with_cloudinit_data.py -s "<vcenter_ip>" -u "<vcenter_user>" -p "<vcenter_password>" -n "<vm_name>" -v

    # customize a running Linux virtual machine
    python <sample-dir>/customize_live_vm.py -s "<vcenter_ip>" -u "<vcenter_user>" -p "<vcenter_password>" -n "<vm_name>" -v -vu "<vm_username>" -vp "<vm_password>" -c

    # create/list/get/set/delete customizationSpecs in a vCenter
    python <sample-dir>/customizationSpecs.py -s "<vcenter_ip>" -u "<vcenter_user>" -p "<vcenter_password>" -v

    # import/export customizationSpecs in a vCenter
    python <sample-dir>/customizationSpecs_import_export.py -s "<vcenter_ip>" -u "<vcenter_user>" -p "<vcenter_password>" -v

    # create/list/get/set/delete cloud-init data customizationSpecs in a vCenter
    python <sample-dir>/cloudinitDataCustomizationSpecs.py -s "<vcenter_ip>" -u "<vcenter_user>" -p "<vcenter_password>" -v

### Testbed Requirement:

    - 1 x vCenter Server
    - 1 x ESX host
    - The target virtual machine must have VMTools installed
    - Some samples require the target virtual machine with cloud-init or the customization engine pre-installed
