# Reduced downtime upgrade

This directory contains examples of running the RDU (reduced downtime upgrade) on a vCenter. 

## Prerequisites
1. **vCenter** - A vCenter on version 8.0 GA or higher. It can be either a vCenter that manages the ESXi host 
it is on (**self-managed**) or a vCenter on an ESXi host managed by another vCenter (**uber-managed**).
2. **Upgrade repository** - a server hosting the necessary resources for the plug-in update and the RDU. To set this up:
   1. Mount the target version .iso file on a machine which is reachable from the vCenter. 
   2. Start a file server or http server which will serve the `./repos` and `./vcsa` directories from the iso.
   3. Make sure that the server's certificate is trusted by the vCenter's certificate authority. You can either get a certificate from the vCenter 
CA or add the server's certificate to the vCenter's trusted certificates.
3. **Target OVA** - In addition to the files in the upgrade repository, the ova for the target version also needs to be added to the upgrade repository.
   The ova file is located in the `vcsa` directory of the iso.


## Complete Scenarios
The repository contains several ready scenarios to run RDU. 


### How to run them
The scenarios are located under `./scenarios/` directory. They include:

#### 1. Upgrade readiness
- This scenario checks if the environment is ready for upgrade without actually
running the upgrade. The sample is expected to be executed against a self-managed vCenter.


- It executes the following steps:
     1. Update lifecycle plugin
     2. Create init spec
     3. Run prechecks


- Command to run the scenario:
```
python upgrade_readiness.py 
   --server <vcenter_ip> 
   --username <username> 
   --password <password> 
   --skipverification 
   --target-upgrade-repo <target-upgrade-repo>
   --target-version <target-version>
   --target-ova <target-ova>
   --target-temp-password <target-temp-password>
```

- Where:
  - `<vcenter_ip>` - The IP or the hostname of the vCenter.
  - `<username>` - Username to authenticate with the vCenter. You can either use root or a SSO user with enough permissions
  - `<password>` - Password for the provided username.
  - `<target-upgrade-repo>` - The URL to the prepared update repository in the format https://{}/repos/patcher_repo
  - `<target-version>` - The target version to which the vCenter will be upgraded
  - `<target-ova>` - The URL to the prepared ova file.
  - `<target-temp-password>` - A temporary root password to deploy the target machine in the format https://{}/vcsa/VMware-vCenter-Appliance-{}_OVF10.ova


- Example command:

```
python upgrade_readiness.py \
   --server 10.10.10.10 \
   --username root \
   --password <password> \ 
   --skipverification \
   --target-upgrade-repo https://localhost:443/repos/patcher_repo \ 
   --target-version 9.0.0.0000 \
   --target-ova https://localhost:443/repos/VMware-vCenter-Server-Appliance-9.0.0.0000-24284692_OVF10.ova \
   --target-temp-password <temp-password>
```

#### 2. Full upgrade
- This scenario demonstrates how to run the full upgrade on a self-managed vCenter.

- It executes the following steps:
  1. Update lifecycle plugin
  2. Create init spec
  3. Run prechecks before the upgrade.
  4. Configure the upgrade with the init spec
  5. Run prechecks against the configured upgrade
  6. Create apply spec
  7. Run upgrade with the apply spec
  8. Monitor the upgrade.
  

- Command to run the full upgrade:
```
python full_upgrade.py 
   --server <vcenter_ip> \
   --username <username> \
   --password <password> \
   --skipverification \ 
   --target-upgrade-repo <target-upgrade-repo> \
   --target-version <target-version> \
   --target-ova <target-ova> \
   --target-temp-password <target-temp-password> \
   [--autocancellation ]
   [--preserve-original-name] 
   [--start-switchover <switchover-time>]
```
Where:
- `--autocancellation` - Whether to automatically cancel the upgrade on error.
- `--preserve-original-name` - Whether the upgraded vCenter vm should preserve the name of the original vCenter vm.
- `<switchover-time>` - After how many hours to schedule the downtime of the upgrade.
- all other parameters are the same as in the above scenario


#### 3. Upgrade with cancellation
- This scenario shows how to cancel a running upgrade. Executing against a self-managed vCenter.


- It executes the following steps:
  1. Update lifecycle plugin
  2. Create init spec
  3. Configure upgrade with the init spec
  4. Run prechecks
  5. Run the upgrade
  6. Trigger the cancellation after some time.
  7. Monitor for the cancellation completion


- Command to run it:
```
python upgrade_with_cancelation.py <same_parameters as above>
```
- The parameters are the same as in the above scenarios.


#### 4. Two phase upgrade
- This scenario shows how to pause the upgrade right before it goes into downtime and how to complete it.

- It includes the following steps:
    1. Update the lifecycle plugin. If the plugin has already been upgraded, this script won't fail
  and will continue with the upgrade
     2. Create the init spec for configuring the RDU upgrade. You can further customize by hand the init spec if needed.
     3. Configure the upgrade with the init spec.
     4. Create the apply spec with a pause point before the switchover/downtime.
     5. Run the apply API.
     6. Monitor the upgrade state till it reaches the pause point before the switchover.
     7. Change the apply spec to not include a pause point.
     8. Run the apply API again. It will start the upgrade and enter the switchover phase directly.
     9. Monitor till the upgrade is completed.

- Command to run it:
```
python two_phase_upgrade.py <same_parameters as above>
```
  

#### 5. Upgrade uber-managed vCenter
- This scenario demonstrates how to run the upgrade on an uber-managed vCenter. There isn't a difference in the 
upgrade flow, but the information about the managing vCenter should also be set in the init spec.


- It executes the following steps:
  1. Update lifecycle plugin
  2. Create init spec with uber vCenter details.
  3. Configure the upgrade with the init spec
  4. Run upgrade
  5. Monitor the upgrade


- Command to run it:
```
python uber_vc_upgrade.py <same_parameters_as_above> \
  --uber-vc-hostname <managing_vcenter_ip> \
  --uber-vc-username <managing_vcenter_username> \
  --uber-vc-password <managing-vcenter-pasword> 
```

#### 6. Check planned maintenance of vCenter
- This scenario demonstrates how to continuously check for vCenter planned maintenance before starting
a long-running workload operation.

- Command to run it:
```
python check_planned_maintenance.py \
  -s $VC -u $VCUSER -p $VCPASS \
  --minutes 10
```

#### 7. Wait and retry a workload operation when vCenter responds with HTTP 503 'Service unavailable' during upgrade
- This scenario demonstrates how to parse the response during service upgrade and wait to retry the operation.
- You would need to run Upgrade separately, and during the Switchover phase, start this sample.

- Command to run it:
```
python check_service_upgrade_in_progress.py \
  -s $VC -u $VCUSER -p $VCPASS
```


## Run singular steps

This sample also contains scripts to run each of the individual upgrade steps on its own.

### Update vCenter lifecycle manager plugin

- To run the plugin update execute the following command:
```
python update_vcenter_lifecycle_manager.py 
  --server <vcenter_ip> 
  --username <username> 
  --password <password> 
  --skipverification 
  --plugin-repo <plugin_repo>
```

Where:  
- `<vcenter_ip` - The IP or the hostname of the vCenter.  
- `<username>` - Username to authenticate with the vCenter. You can either use root or a SSO user with enough permissions
- `<password>` - Password for the provided username.  
- `<plugin_repo>` - the URL to the prepared upgrade repository.


### RDU

! **Plugin update** - To execute any of the RDU steps, first update the lifecycle manager plug-in to the desired target version.

#### Parameters

The parameters that are needed to run any of the upgrade steps are the following:

```
python rdu_steps.py <action> 
  --server <vcenter-ip> 
  --username <username> 
  --password <password> 
  --skipverification 
  --target-upgrade-repo <upgrade-repo> 
  --target-version <target-version> 
  --target-ova <target-ova> 
  --target-temp-password <target-temp-password>
  [--autocancellation ]
  [--preserve-original-name] 
  [--start-switchover <downtime>] 
  [--planned-maintenance-minutes <minutes>]
```
Where:
- `<action>` - possible actions are described in the following points
- `<vcenter_ip>` - The IP or the hostname of the vCenter.
- `<username>` - Username to authenticate with the vCenter. You can either use root or a SSO user with enough permissions
- `<password>`  - The password for the specified user. 
- `<upgrade-repo>` - URL to the prepared upgrade repository
- `<target-version>` - The target version in format A.B.C.DDDD
- `<target-ova>` - URL to the ova file
- `<target-temp-password>` - A temporary root password to deploy the target machine.
- `--autocancellation` - Whether to automatically cancel the upgrade on error.
- `--preserve-original-name` - Whether the upgraded vCenter vm should preserve the name of the original vCenter vm.
- `<start-switchover>` - After how many hours to schedule the downtime of the upgrade.
- `<planned-maintenance-minutes>` - How many minutes to check for planned maintenance, ahead of current time.

For a vCenter that is on an ESXi host managed by another vCenter (uber-managed) add the following parameters:
```
pyhton rdu_steps.py <action> ... --uber-vc-hostname <uber-hostname> --uber-vc-username <uber-username> --uber-vc-password <uber-password> 
```

#### 1. Set target repository 
! Needs to be executed before any other RDU API call. !  
Sets the repository containing the target version's packages.
```
python rdu_steps.py set-repository <params>
```

#### 2. Run sanity checks
You can run the upgrade sanity checks which will check if the environment can be upgraded. These checks can be run before starting an upgrade or during one.
If they are run after an upgrade has been configured, they will use the init spec with which the upgrade was configured.
```
python rdu_steps.py precheck <params>
```

#### 3. Set init spec
Configuring an upgrade will set the init spec which will be used.
```
python rdu_steps.py configure <params>
```

#### 4. Run upgrade

```
python rdu_steps.py apply <params>
```

#### 5. Cancel an ongoing upgrade

```
python rdu_steps.py cancel <params>
```

#### 6. Get the status of an ongoing upgrade
During the execution of the upgrade, the status can give more information on the state of the upgrade.
On failure or cancellation, the status will contain information about the error and how to fix it.
```
python rdu_steps.py status <params>
```
#### 7. Monitor an ongoing upgrade
This operation will check the status of the upgrade till it completes successfully, fails or is cancelled.

```
python rdu_steps.py monitor-upgrade <params>
```

#### 8. Check for Planned Maintenance of the vCenter
This operation checks if there are X minutes available before a planned maintenance of the vCenter starts.

Example with 5 minutes:
```
python rdu_steps.py planned-maintenance --planned-maintenance-minutes 5 <params>
```


