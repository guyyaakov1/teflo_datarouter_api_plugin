# User Guide

### Install
To install the plugin you can use pip. 
```bash
 pip install teflo_datarouter_plugin@git+https://github.com/RedHatQE/teflo_datarouter_api_plugin.git@<tagged_branch>
```

## scenario descriptor

To report resources with datarouter API, we need to define some keys in the scenario descriptor.


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
|name|The Name of DataRouter payload to send. This is used as a regex string by Teflo to find payload within the the current workspace or the results directory.| True|
|executes|Point to which executes block collect logs from.| False|
|credential|DataRouter auth credentials.(referring to teflo.cfg)| True|
|dr_metadata|DataRouter json file that contain configuration.(a path relative to workspace)| True|
|importer|Which importer to use.| False|


  * If using the execute block to collect artifacts/payload to be sent via the teflo_datarouter_api_plugin, the artifacts/payload will be searched in the artifacts director under Teflo's results directory or if artifact_locations is used, then the payload will be searched in the locations mentioned there.
  * DataRouter Plugin output files can be found under .data_folder/.results/datarouter
  * More information about where the artifacts can be stored can be found [Here](https://teflo.readthedocs.io/en/latest/users/definitions/report.html#finding-the-right-artifacts).

## Credentials
To report resources with datarouter API requires credentials. You can initialize them from teflo.cfg.

Below are the importer specific options that can be specified in the `teflo.cfg` 

```ini
# Example credentials in teflo.cfg
[credentials:datarouter-creds]
DR_CLIENT_ID=dummy
DR_CLIENT_SECRET=ChangeMe123
AUTH_URL=
HOST_URL=
  ```
> **Note**  
>  > **When using host_url and auth_url with https protocol, user would need to install/export proper public RH certificates**

|key| Description | Required|
|  ---  |   ----  | ---  |
|DR_CLIENT_ID|The DataRouter client id with permissions.| True|
|DR_CLIENT_SECRET|The DataRouter client secret.| True|
|AUTH_URL|URL used for acquiring temporary auth token.| True|
|HOST_URL|URL for Data router service.| True|

> **Note**  
>  > **Please reach out to Teflo team to get more information on the auth_url.**


## Request Status

When payload is sent to DR API, Teflo DR Plugin will wait 5min for response with status "OK/FAILURE".
All results can be found in results.yml

```yaml
# Example of output in results.yml
    request_results:
      request_id: 0000-0000-0000-0000-00000000
      status: OK
      targets:
        reportportal:
          status: OK
  ```
