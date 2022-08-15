# User Guide

### Install
To install the plugin you can use pip. 
```bash
 pip install teflo_datarouter_plugin@git+https://github.com/RedHatQE/teflo_datarouter_api_plugin.git@<tagged_branch>
```

## scenario descriptor
To report resources with datarouter API, we need to define some keys to the scenario descriptor.

  ```yaml
  #Example teflo scenario referencing the credential in the teflo.cfg
  
   report:
    - name: example.tar.gz
      description: test report to Teflo datarouter plugin
      executes: testexe
      credential: datarouter-creds
      dr_metadata: user_input.json
      importer: datarouter

  ```    


|key| Description | Required|
|  ---  |   ----  | ---  |
|name|The Name of DataRouter payload to send.| True|
|executes|Point to which executes block collect logs from.| False|
|credential|DataRouter auth credentials.(referring to teflo.cfg)| True|
|dr_metadata|DataRouter json file that contain configuration.| True|
|importer|Which importer to use.| False|

  * The name section of report block should contain the name of the payload to send.
If the user point to a dir Teflo DR API Plugin will check if data is valid compose and send to API.
Learn more about payload structure on Confluence page.
  * When using execute block DR API Plugin will look for payload under collected artifacts dir.
    If user wants to send predifine payload(Without calling execute block) Payload Should be put under .resualts/ dir
  * More information about where the artifacts can be stored can be found [Here](https://teflo.readthedocs.io/en/latest/users/definitions/report.html#finding-the-right-artifacts).

## Credentials
To report resources with datarouter API requires credentials. You can initialize them from teflo.cfg.

Below are the provider specific options that can be specified in the `teflo.cfg` 

```ini
# Example credentials in teflo.cfg
[credentials:datarouter-creds]
dr_client_id=dummy
dr_client_secret=ChangeMe123
auth_url=
host_url=
  ```

|key| Description | Required|
|  ---  |   ----  | ---  |
|dr_client_id|The DataRouter client id with permissions.| True|
|dr_client_secret|The DataRouter client secret.| True|
|auth_url|URL used for acquiring temporary auth token.| True|
|host_url|URL for Data router service.| True|

> **Note**  
>  > **Please reach out to Teflo team to get more information on the auth_url.**
