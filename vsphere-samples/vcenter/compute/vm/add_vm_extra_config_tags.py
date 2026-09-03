#!/usr/bin/env python

# Copyright (c) 2014-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# Copyright 2014 Michael Rice
# SPDX-License-Identifier: Apache-2.0

"""
Sample for adding extra config tags to a VM
"""

import requests
from pyVmomi import vim
from helpers import cli, service_instance, pchelper, tasks

requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning)

parser = cli.Parser()
parser.add_optional_arguments(cli.Argument.UUID, cli.Argument.VM_NAME)
args = parser.get_args()
si = service_instance.connect(args)

vm = None
if args.uuid:
    vm = si.content.searchIndex.FindByUuid(None, args.uuid, True)
elif args.vm_name:
    vm = pchelper.get_obj(si.RetrieveContent(), [vim.VirtualMachine], args.vm_name)
if not vm:
    raise SystemExit("Unable to locate VirtualMachine.")

print("Found: {0}".format(vm.name))

spec = vim.vm.ConfigSpec()
opt = vim.option.OptionValue()
spec.extraConfig = []

options_values = {
    "custom_key1": "Ive tested very large xml and json, and base64 values here"
                   " and they work",
    "custom_key2": "Ive tested very large xml and json, and base64 values here"
                   " and they work",
    "custom_key3": "Ive tested very large xml and json, and base64 values here"
                   " and they work",
    "custom_key4": "Ive tested very large xml and json, and base64 values here"
                   " and they work"
}

for k, v in options_values.items():
    opt.key = k
    opt.value = v
    spec.extraConfig.append(opt)
    opt = vim.option.OptionValue()

task = vm.ReconfigVM_Task(spec)
tasks.wait_for_tasks(si, [task])
print("Done setting values.")
print("time to get them")
keys_and_vals = vm.config.extraConfig
for opts in keys_and_vals:
    print("key: {0} => {1}".format(opts.key, opts.value))
print("done.")
