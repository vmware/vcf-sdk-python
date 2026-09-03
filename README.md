# VMware Cloud Foundation SDK for Python
## Table of Contents
- [Abstract](#abstract)
- [SDK Compatibility](#sdk-compatibility)
    - [Python Compatibility](#python-compatibility)
    - [VCF Component Compatibility](#vcf-component-compatibility)
- [Quick Start Guide](#quick-start-guide)
    - [Prepare a Python Development Environment](#prepare-a-python-development-environment)
    - [Install Required Python Packages](#install-required-python-packages)
    - [SDK Installation](#sdk-installation)
    - [Using the SDK Samples](#using-the-sdk-samples)
    - [Run SDK Samples](#run-sdk-samples)
        - [Run SDDC Manager Samples](#run-sddc-manager-samples)
        - [Run vSphere Samples](#run-vsphere-samples)
        - [Run VCF Installer Samples](#run-vcf-installer-samples)
        - [Run VCF Operations samples](#run-vcf-operations-samples)
            - [Operations samples](#operations-samples)
            - [Log Management samples](#log-management-samples)
            - [Operations for Networks samples](#operations-for-networks-samples)
    - [IDE Support](#ide-support)
- [API Documentation](#api-documentation)
- [SDK Support](#sdk-support)

## Abstract
This document describes the VMware Cloud Foundation Python SDK samples that use the [VMware Cloud Foundation python](https://pypi.org/project/vcf-sdk/) client libraries

## SDK Compatibility
### Python Compatibility

All modules of the VCF SDK for Python are compatible and verified with the supported versions of Python at the time of their release.
Once a Python version reaches EOL (End-Of-Life), it no longer receives security patches. VCF SDK releases which happen after this moment will not provide compatibility guarantees for the EOL-ed Python version. As a generally good practice and for best security posture, it is recommended to use the VCF SDK with an actively maintained version of Python and keeping your environment on the latest patch provided by the Python Software Foundation (PSF).

For release 9.1, the compatible Python versions are [3.10](https://www.python.org/downloads/release/python-3100/), [3.11](https://www.python.org/downloads/release/python-3110/), [3.12](https://www.python.org/downloads/release/python-3120/) and [3.13](https://www.python.org/downloads/release/python-3130/) and [3.14](https://www.python.org/downloads/release/python-3142/).

### VCF Component Compatibility
The SDK is compatible with following VMware Cloud Foundation components

- VMware Cloud Foundation
    - pyVmomi (includes vSAN) 8.0, 9.0 and 9.1
    - vCenter 8.0, 9.0 and 9.1
    - VMware vSAN Data Protection 8.0, 9.0 and 9.1
    - SDDC Manager 9.0 and 9.1
    - VCF Installer 9.0 and 9.1
    - NSX 9.1
    - VCF Operations 9.1
    - VCF Operations for Networks 9.1
    - Log Management 9.1
    - Fleet Lifecycle 9.1
    - SDDC Lifecycle 9.1

Kindly refer to README.md under each sample package and the [DocStrings](https://peps.python.org/pep-0257/#what-is-a-docstring) in the sample for detailed product compatibility information.

# Quick Start Guide
## Prepare a Python Development Environment
We recommend to install a [Python](http://docs.python-guide.org/en/latest/starting/installation/) supported version ([3.10](https://www.python.org/downloads/release/python-3100/) to [3.14](https://www.python.org/downloads/release/python-3142/)) and a compatible [pip](https://pypi.python.org/pypi/pip/) on your system.

***NOTE:*** [pip version 25.3](https://pypi.org/project/pip/25.3/) is compatible with all the Python versions supported by the SDK.

A Python virtual environment is also highly recommended.
* [Install a virtual env for Python 3](https://docs.python.org/3/tutorial/venv.html)

## Install Required Python Packages
The SDK package installation commands vary depending on the component being installed and the installation environment.

### Prerequisites
- The SDK requires OpenSSL 3.0+ in order to support TLS 1.2 & 1.3.
- *pip* and *setuptools* are common requirements for all installation types. It is recommended to upgrade *pip* to version [25.3](https://pypi.org/project/pip/25.3/) and *setuptools* to the latest version.

Install/Update compatible pip from PyPI.
```shell
pip install --upgrade pip
```
Install/Update setuptools
```shell
pip install --upgrade setuptools
```
## SDK Installation
The SDK installation options provided below are for Linux and Windows environments

### 1. Typical Installation of VCF SDK
This is the recommended way to install the SDK. The installation gets the SDK libraries and dependencies from [PyPI](https://pypi.org/).

```shell
pip install vcf-sdk
```

### 2. Install an Individual VCF SDK Component package from PyPI.
Individual VCF SDK components like SDDC Manager, VCF Installer etc, can be installed directly.
```shell
pip install <COMPONENT_PACKAGE_NAME>
# e.g. To install SDDC Manager
pip install sddc-manager
```
To get list of other VCF SDK packages, refer to [requirements.txt](./requirements.txt)

### 2. Download and Install SDK from Broadcom Portal
VCF SDK for Python is published to the [Broadcom Developer Portal](https://developer.broadcom.com/sdks/vcf-python-sdk/latest).
The SDK zip file follows the naming convention `vcf-sdk-python-<VERSION>-<BUILD_NUMBER>.zip`.

where 

`VERSION`      : The released version of the VCF SDK Python

`BUILD_NUMBER` : The build number of the released VCF SDK Python

e.g. ``` vcf-sdk-python-9.1.0.0-24798170.zip```

The SDK zip bundles the SDK libraries, samples, and documentation. However, third-party dependency packages are not bundled; they are listed in the `requirements-third-party.txt` file included in [vcf-sdk-python-<VERSION>-<BUILD_NUMBER>.zip](https://developer.broadcom.com/sdks/vcf-python-sdk/latest)

To install the VCF SDK Python from the zip, follow these steps. 
- Download the SDK zip from the trusted source [Broadcom Developer Portal](https://developer.broadcom.com/sdks/vcf-python-sdk/latest)
- Install the third party dependencies. 
    - Either `pip install` them using the `requirements-third-party.txt` or 
    - download the dependencies from [PyPI](https://pypi.org/) and install them from the download location.
- Install the SDK packages bundled in the zip.

e.g.
#### Unzip the SDK
```shell
# unzip the SDK to vcf-sdk-python directory
unzip vcf-sdk-python-9.1.0.0-24798170.zip -d vcf-sdk-python
cd vcf-sdk-python
```
#### Install Third Party dependencies
```shell
# Install the third party dependencies from PyPI
pip install -r requirements-third-party.txt
```
or

```shell
# Download third party dependencies from PyPI and install
pip download -r requirements-third-party.txt -d third-party_libs/
pip install --no-index -U third-party_libs/**/*.whl
```
#### Install vcf sdk python packages
```shell
# Install vcf sdk libraries from deflated sdk zip 
pip install --no-index -U pypi/**/*.whl
```

### 3. Install SDK in an air-gapped environment
To install VCF SDK in an air-gapped environment, first download the required SDK packages as "wheels" (pre-built package files) from a trusted source ([Broadcom Developer Portal](https://developer.broadcom.com/sdks/vcf-python-sdk/latest) or [PyPI](https://pypi.org/)) outside the airgap, then transfer them to the air-gapped system and install them using the `pip install` command with the local wheel file path; essentially, you cannot directly use online python package repositories in an air-gapped environment.

The required SDK packages are listed in the [requirements.txt](./requirements.txt) and [requirements-third-party.txt](./requirements-third-party.txt) files. Also, present in the [vcf-sdk-python.zip](https://developer.broadcom.com/sdks/vcf-python-sdk/latest).
- [requirements.txt](./requirements.txt) : Lists all the SDK packages, including the third party dependency packages.
- [requirements-third-party.txt](./requirements-third-party.txt) : Lists only the third party dependency packages.
#### 3.1 Download and Install SDK from Broadcom Portal
- In an environment which is outside of air gap.
    - Download the SDK zip from [Broadcom Developer Portal](https://developer.broadcom.com/sdks/vcf-python-sdk/latest), it contains requirements.txt, requirements-third-party.txt, samples, readme and SDK libraries.
    - Third Party dependencies are not bundled in this zip, download the dependencies from PyPI in an environment which has PyPI access, then copy and install them in the air-gapped environment.

    e.g.
    ```shell
    # Unzip the VCF SDK zip
    unzip vcf-sdk-python-9.1.0.0-24798170.zip -d vcf-sdk-python
    cd vcf-sdk-python
    # Download third party dependencies from PyPI
    pip download -r requirements-third-party.txt -d pypi/
    cd ..
    # zip the vcf-sdk-python with downloaded third party libraries
    zip -r vcf-sdk-python.zip vcf-sdk-python/
    ```

    The VCF SDK python packages as well as the third party libraries are present under `pypi` directory inside the `vcf-sdk-python.zip`.

- Transfer `vcf-sdk-python.zip` to the air-gapped system
    - Unzip `vcf-sdk-python.zip` and install vcf-sdk-python packages and dependencies.
    e.g.
    ```shell
    unzip vcf-sdk-python.zip -d vcf-sdk-python
    cd vcf-sdk-python/
    pip install --no-index -U pypi/**/*.whl
    ```
#### 3.2 Download SDK zip from GitHub Release and install
- In an environment which is outside of airgap
    - Download the SDK from [vcf-sdk-python github repository](https://github.com/vmware/vcf-sdk-python/tags), the zip contains requirements.txt, requirements-third-party.txt, samples and readme. The zip does not contain any SDK libraries or dependencies.

    e.g.
    ```shell
    wget https://github.com/vmware/vcf-sdk-python/archive/refs/tags/v9.1.0.0.zip
    unzip v9.1.0.0.zip -d vcf-sdk-python
    cd vcf-sdk-python
    pip download -r requirements.txt -d pypi/
    cd ..
    zip -r vcf-sdk-python.zip vcf-sdk-python/
    ```
    The VCF SDK python packages as well as the third party libraries are present under `pypi` directory inside the `vcf-sdk-python.zip`.
- Transfer `vcf-sdk-python.zip` to the air-gapped system
    - Unzip and install the vcf-sdk-python packages and dependencies.

    e.g.
    ```shell
    unzip pypi.zip -d pypi
    pip install --no-index -U pypi/**/*.whl
    ```

#### 3.3 Clone the SDK GitHub Repository and install
- In an environment which is outside of airgap
    - Clone the SDK from the [vcf-sdk-python GitHub repository]((https://github.com/vmware/vcf-sdk-python)). 
    - Downloaded SDK and third-party dependency packages from PyPI: The repository includes `requirements.txt`, `requirements-third-party.txt`, sample code, and README files. However, it does not include the SDK packages or third-party dependencies; these need to be downloaded from PyPI.

    e.g.
    ```shell
    git clone https://github.com/vmware/vcf-sdk-python.git
    cd vcf-sdk-python
    pip download -r requirements.txt -d pypi/
    cd ..
    zip -r vcf-sdk-python.zip vcf-sdk-python/
    ```
    The VCF SDK python packages as well as the third party libraries are present under `pypi` directory inside the `vcf-sdk-python.zip`.
- Transfer `vcf-sdk-python.zip` to the air-gapped system:
    - Unzip and install the vcf-sdk-python packages and its dependencies.

    e.g.
    ```shell
    unzip libs_pypi.zip -d libs_pypi
    pip install -U libs_pypi/**/*.whl
    ```

## Using the SDK Samples

### 1. Clone the SDK to get the samples
```shell
git clone https://github.com/vmware/vcf-sdk-python.git
cd vcf-sdk-python
```

### 2. Install the SDK libraries to run the samples
To run the samples install the SDK libraries using [requirements.txt](./requirements.txt), it lists all the SDK packages required for running the samples.

```shell
pip install -r requirements.txt
```
Refer to [SDK Installation](#sdk-installation) to explore other installation options.


### 3. Update PYTHONPATH to use SDK samples and utilities
Samples and utilities are organized as Python modules under each component's samples directory. The directory name follows the format:`<COMPONENT-NAME>-samples`.
Where `<COMPONENT-NAME>` is the name of the VCF component e.g sddc-manager, vsphere etc.
These directories are regular python packages. However, they are not installed via pip. Python will not be able to resolve the modules imported by the python samples under `<COMPONENT-NAME>-samples` directory, if run as is.

In order to make the modules discoverable by Python, update the environment variable `PYTHONPATH` with the location of `<COMPONENT-NAME>-samples` package.

Linux/Mac:
```shell
cd vcf-sdk-python
export PYTHONPATH=${PWD}/<COMPONENT-NAME>-samples:$PYTHONPATH

e.g. For SDDC Manager Samples
export PYTHONPATH=${PWD}/sddc-manager-samples:$PYTHONPATH
```
Windows:
```shell
cd vcf-sdk-python
set PYTHONPATH=%cd%\<COMPONENT-NAME>-samples;%PYTHONPATH%

e.g. For SDDC Manager Samples
set PYTHONPATH=%cd%\sddc-manager-samples;%PYTHONPATH%
```
#### 3.1 Update PYTHONPATH for vSphere Samples

Update the environment variable `PYTHONPATH` with the location of `vsphere-samples` package for Python to discover the vSphere modules.

Linux/Mac:
```shell
cd vcf-sdk-python
export PYTHONPATH=${PWD}/vsphere-samples:$PYTHONPATH
```
Windows:
```shell
set PYTHONPATH=%cd%\vsphere-samples;%PYTHONPATH%
```

### 4. Using the VCF SDK repository for connecting to the Server and samples execution
##### Connect to a SDDC Manager Server
```python
import requests
import urllib3
from vmware.vapi.sddc_manager.client import create_sddc_manager_client

session = requests.session()
# Disable cert verification for demo purpose.
# This is not recommended in a production environment.
session.verify = False
# Connect to a SDDC Manager Server using username and password
sddc_client = create_sddc_manager_client(server='<sddc_manager_ip>', username='<username>', password='<password>', session=session)
# Get Domains
sddc_client.v1.Domains.get_domains()
```

Output in a Python Interpreter:

```shell
(venv)[vsphere-samples]$ python
Python 3.12.8 (main, Nov 10 2025, 06:03:50)
[GCC 4.2.1 (Apple Inc. build 5666) (dot 3)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import requests
>>> import urllib3
>>> from vmware.vapi.sddc_manager.client import create_sddc_manager_client
>>> session = requests.session()
>>> session.verify = False
>>> urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
>>> sddc_client = create_sddc_manager_client(server='<sddc_manager_ip>', username='<username>', password='<password>', session=session)
>>> sddc_client.v1.Domains.get_domains()
Domains Info :
{elements : [Domain(id='7277ed7e-3239-438b-b7c7-a735f1293c08', name='sddcId-1001', org_name='COM', status='ACTIVE', upgrade_state='AVAILABLE', upgrade_status=UpgradeStatus(status='UP_TO_DATE', completed_resources=None, total_resources=None), type='MANAGEMENT', vra_integration_status=None, vrops_integration_status=None
...}
```

##### Connect to a vCenter Server
```python
import requests
import urllib3
from vmware.vapi.vsphere.client import create_vsphere_client
session = requests.session()

# Disable cert verification for demo purpose.
# This is not recommended in a production environment.
session.verify = False

# Disable the secure connection warning for demo purpose.
# This is not recommended in a production environment.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Connect to a vCenter Server using username and password
vsphere_client = create_vsphere_client(server='<vc_ip>', username='<vc_username>', password='<vc_password>', session=session)

# List all VMs inside the vCenter Server
vsphere_client.vcenter.VM.list()
```

Output in a Python Interpreter:

```shell
(venv)[vsphere-samples]$ python
Python 3.12.8 (main, Nov 10 2025, 06:03:50)
[GCC 4.2.1 (Apple Inc. build 5666) (dot 3)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import requests
>>> import urllib3
>>> from vmware.vapi.vsphere.client import create_vsphere_client
>>> session = requests.session()
>>> session.verify = False
>>> urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
>>> vsphere_client = create_vsphere_client(server='<vc_ip>', username='<vc_username>', password='<vc_password>', session=session)
>>> vsphere_client.vcenter.VM.list()
[Summary(vm='vm-58', name='standalone-20e4bd3af-esx.0-vm.0', power_state=State(string='POWERED_OFF'), cpu_count=1, memory_size_mib=256),
...]
```

##### Connect to a VCF Installer Server
```python
from utils.client import create_vcf_installer_client

# never use ca_certs=False in production! This is used in dev environments to avoid self-signed certificate validations
client = create_vcf_installer_client(server=<vcf_installer_ip>, password=<vcf_installer_admin_password>, ca_certs=False)
client.v1.system.ApplianceInfo.get_appliance_info()
```

Output in a Python Interpreter:


```shell
(.venv) [vcf-installer-samples]$ python
Python 3.12.5 (main, Aug  9 2024, 08:20:41) [GCC 14.2.1 20240805] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from utils.client import create_vcf_installer_client
>>> client = create_vcf_installer_client(server=<vcf_installer_ip>, password=<vcf_installer_admin_password>, ca_certs=False)
>>> client.v1.system.ApplianceInfo.get_appliance_info()
ApplianceInfo(role='VcfInstaller', version='9.1.0.0.24541873')
```

## Run SDK Samples
In this section we will walk you through the steps to run the sample code for few VCF Components like vSphere, SDDC Manager etc.

### Run SDDC Manager Samples
A VCF test environment is required with the following configuration:

```shell
$ python create_domains.py --server <SDDC_MANAGER IP> --user <username> --password <password>
```

### Run vSphere Samples

```shell
$ python vcenter/compute/vm/list_vms.py -v
```

### Run VCF Installer samples

```cmd
$ python get_appliance_info.py --vcf_installer_server_address <VCF_INSTALLER_IP> --vcf_installer_admin_password <VCF_INSTALLER_ADMIN_PASSWORD>
```

### Run VCF Operations samples

#### Operations samples
Before executing any operations samples, update the [client-config.json](./vcf-operations-samples/operations/json-config/client-config.json) file. Additionally, remember to update the configuration files specific to each sample; for example, update symptom-and-alert-definition-config.json for the symptoms_and_alert_definitions.py sample.

```cmd
$ python operations/symptomdefinitions/symptoms_and_alert_definitions.py operations/json-config/client-config.json operations/json-config/symptom-and-alert-definition-config.json
```

#### Log Management samples
Update the [client-config.properties](./vcf-operations-samples/log_management/resources/client-config.properties) before executing the python sample

```cmd
$ python log_management/advanced_search/advanced_search_example.py
```

#### Operations for Networks samples

```cmd
$ python operations_networks/groups/applications.py --server <OPS_NETWORKS_IP>  --user <OPS_NETWORKS_USERNAME> --password <OPS_NETWORKS_PASSWORD>
```


## IDE Support
This project contains python samples from VCF products which can be imported to the supported IDEs. Some specifics of PyCharm and Visual Studio Code, two popular IDEs for Python are discussed in the following subsections.

To work with the IDEs, either Clone the repository or download the SDK zip from Broadcom.com

### PyCharm
Open the project in [PyCharm IDE](https://www.jetbrains.com/help/pycharm/open-projects.html#open), create a virtual environment using a supported python version, and install `dependencies` to the project referring `requirements.txt` and `requirements-third-party.txt`.

To `Run` the sample from the PyCharm Editor, set the `PYTHONPATH` in `Edit Configuration Settings -> Environment -> Environment Variables`.
For more details regarding the `PYTHONPATH`, kindly refer the sample section, [Using the SDK Samples](#using-the-sdk-samples)

### Visual Studio Code
It is recommended to install [Python extension for VS Code](https://marketplace.visualstudio.com/items?itemName=ms-python.python).
Open the project in VS Code IDE, create and activate a virtual environment using a supported python version, refer to [Creating Environments in VS Code](https://code.visualstudio.com/docs/python/environments#_creating-environments).

Install SDK `dependencies` to the project referring `requirements.txt` and `requirements-third-party.txt`.

To `Run` the sample from the VS Code Editor, first set the `PYTHONPATH` environment variable, refer [setting environment variables in VS Code](https://code.visualstudio.com/docs/python/environments#_environment-variables).

You can run the sample from VS Code using two ways
1. Select the sample and click on `[Run and Debug]` button
2. Open the VS Code integrated terminal and run the sample

## API Documentation
### VCF
* [SDDC Manager](https://developer.broadcom.com/xapis/sddc-manager-api/latest/)
* [VCF Installer](https://developer.broadcom.com/xapis/vcf-installer-api/latest/)
* [VMware vSphere REST API Reference documentation](https://developer.broadcom.com/xapis/vsphere-automation-api/latest/)
* [vSphere Web Services API](https://developer.broadcom.com/xapis/vsphere-web-services-api/latest/)
* [vSAN](https://developer.broadcom.com/xapis/vsan-management-api/latest/)
* [SDDC Manager](#)
* [VCF NSX](#)
* [VCF Operations](#)
* [VCF Operations Networks](#)
* [VCF Log Management](#)
* [VCF Fleet LCM](#)
* [VCF SDDC LCM](#)

## SDK Support

Support details can be referenced under the **SDK and API Support for Commercial and Enterprise Organizations** section at [Broadcom Developer Portal](https://developer.broadcom.com/support).

For community support, please open a [Github issue](https://github.com/vmware/vcf-sdk-python/issues) or start a [Discussion](https://github.com/vmware/vcf-sdk-python/discussions).
