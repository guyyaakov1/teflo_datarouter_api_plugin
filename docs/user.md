# User Guide

### Install
To install the plugin you can use pip. 
```bash
$ pip install teflo_datarouter_plugin@git+https://github.com/RedHatQE/teflo_datarouter_api_plugin.git@<tagged_branch>
```

## Credentials
To report resources with datarouter API requires credentials. You can utilize them from teflo.cfg.


* The name section of report block should contain te name of the ".tar.gz" payload to send.
If the user point to a dir Teflo plugin will try to compose and send to API.
Learn more about payload structure on Confluence page.
* Provide Teflo the credentials in the `teflo.cfg` and reference that particular 
section using Teflo's `credential` parameter.
 
  ```yaml
  #Example teflo scenario referencing the credential in the teflo.cfg
  
   report:
    - name: test.tar.gz
      description: test report to Teflo datarouter plugin
      executes: testexe
      credential: datarouter-creds
      dr_metadata: user_input.json
      importer: datarouter

  ```    
### Configuring Credentials
Below are the provider specific options that can be specified in the `teflo.cfg` 

|key| Description | Required|
|  ---  |   ----  | ---  |
|dr_client_id|The DataRouter client id with permissions.| True|
|dr_client_secret|The DataRouter client secret.| True|
|auth_url|URL to Get Access token .| True|
|host_url|URL to handle user DataRouter API requests.| True|


```ini
# Example credentials in teflo.cfg
[credentials:datarouter-creds]
dr_client_id=dummy
dr_client_secret=ChangeMe123
auth_url=
host_url=
  ```
