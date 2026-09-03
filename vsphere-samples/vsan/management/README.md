vSAN Samples
==================

This directory holds the vsan sample programs and utils. The sample scripts here
use the pyVmomi library. The vsanapisamples.py and vsaniscsisamples.py
depends on the vsanapiutils.py, which provides utility libraries to retrieve 
vSAN Managed Objects.

Sample code usage
==================

To run the sample program, you need to put pyVmomi to the same directory of the 
samples or paths where can be searched by Python.

```shell
python vsanapisamples.py -s <host-address> -u <username> -p <password> --cluster <cluster-name>
```

```shell
python vsaniscsisamples.py -s <host-address> -u <username> -p <password> --cluster <cluster-name>
```

Getting Help
============

* Use "-h" or "--help" to see parameter usage message.
* You can use the sample code to get vSAN Managed Objects on vCenter and
  ESXi servers. It will automatically identify the target server type.
