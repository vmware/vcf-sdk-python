This directory contains helper utilities for using VCF Installer API.
It helps establish and maintain authentication, task polling, etc.

client.py:
Defines a VcfInstallerClient to handle authentication and ease stub
creation for API invocations. Also handles automatic token refresh.

download_bundles_util.py:
Defines reusable functions for bundle management, such as connecting a depot,
forcing bundle sync, bundle download, download status polling.

misc_util.py:
Defines reusable common functions that can be used by other utils.
Also provides utility functions that call the VCF Installer API to
collect env specific details.

sddc_spec_util.py:
Defines reusable functions to aid spec creation for various spec objects.
Has some volume of hard-coded values to ease spec creation.

sddc_task_util.py:
Defines reusable functions for monitoring of various tasks, waiting
for them to complete.

ssl_helper.py:
Defines common functions for SSL cert validation and extraction.
