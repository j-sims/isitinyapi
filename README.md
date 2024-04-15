# Isi Tiny API Readme

## Overview
The Isi Tiny API enables polling of cluster state data that is not accessible via PAPI, eliminating the need for local shell scripts. This API fetches and returns system information for specified sysctl keys and commands pre-defined in a JSON config file. 

It is particularly useful for monitoring systems and creating dashboards.

## Features

- **Single Endpoint**: The API has a single endpoint (`/`) which outputs all sysctl keys and command outputs defined in the `config.json` file.
- **Output Format**: All responses are in JSON.
- **Builtin caching** to prevent impacts to performance from abusive or misconfigured applications


## Risks
Running Unix shell commands and modifying the Apache configuration files can potentially disrupunzip isi_tiny_api.zip
cd isitinyapi-mainhese risks are significant unless managed by experienced personnel in production environments. Dell EMC does not support modifications to the apache configuration file.

## Requirements

- OneFS version 9.5 or higher is required for installation.

## Installation Options

There are two main installation options: modifying Apache or running the server on a alternate port independently. There are separate steps outlines below for each.

### General Setup

1. **Download and Extract**:
    One a single node of the cluster download and extract:

    ``` 
    cd /ifs/data/Isilon_Support
    curl -k -L -o isi_tiny_api.zip https://github.com/j-sims/isitinyapi/archive/refs/heads/main.zip
    unzip isi_tiny_api.zip
    cd isitinyapi-main

    ```

2. **Edit Configuration**:
   - Modify `config.json` to specify the sysctl keys and commands needed. Ensure the total runtime of these commands does not exceed two minutes. Test thoroughly before implementing in production.

3. **Cron Setup**:
   - Install the cron job on either a single node or all nodes by running one of the following:

   **single node**

       ```
       bash /ifs/data/Isilon_Support/isitinyapi-main/installcron.sh
       grep sitinyapi-main /etc/crontab
       ```

   **all nodes**

       ```
       isi_for_array bash /ifs/data/Isilon_Support/isitinyapi-main/installcron.sh
       isi_for_array grep sitinyapi-main /etc/crontab
       ```
4. **Configure**
    - **Independent Server Configuration (Option 1, Simple)**

        By deploying separately from Apache and serving on a separate port we avoid the need to alter the configuration of Apache and the associated risks.

        To run the server on its own port by edit the `config.json` and specify a port and an address of "0.0.0.0". Note that this method is less secure as there is no authentication and the python webserver is exposed directly.


    - **Apache Configuration (Option 2, More Secure, Not Supported by Dell)**

        By using the WebUI apache server to proxy requests to the Tiny API server the requests will inheirit the same security features as the platform API (Users must valid, authnticated, have rbac role).

        - Modify Apache Config:
        - Backup and copy `webui_httpd.conf` into install dir
        - Modify `webui_httpd.conf` in the install dir to include Tiny API
        - Deploy the updated config file
        - Test the WebUI to ensure remains functional
          - If not, check /var/log/apache2 log files, fix and redeploy

        1. Copy /usr/local/apache2/conf/webui_httpd.conf and backup

            **single node**

            ```
            cp  /usr/local/apache2/conf/webui_httpd.conf /ifs/data/Isilon_Support/isitinyapi-main
            cp  /usr/local/apache2/conf/webui_httpd.conf /usr/local/apache2/conf/webui_httpd.conf.orig.`date "+%Y%m%d%H%M%S"`
            ```

            **all nodes**

            ```
            isi_for_array cp  /usr/local/apache2/conf/webui_httpd.conf /ifs/data/Isilon_Support/isitinyapi-main
            isi_for_array cp  /usr/local/apache2/conf/webui_httpd.conf /usr/local/apache2/conf/webui_httpd.conf.orig.`date "+%Y%m%d%H%M%S"`
            ```

        2. Edit /ifs/data/Isilon_Support/isitinyapi-main/webui_httpd.conf
            Add these two sections:

            - Add near top with other LoadModules

            ```

            LoadModule proxy_module modules/mod_proxy.so
            LoadModule proxy_http_module modules/mod_proxy_http.so
            ```

            - Add tinyapi to list of services
            Change near line 358 from this:

            ```
                    IsiAuthServices platform remote-service namespace
            ```

            to this:

            ```
                    IsiAuthServices platform remote-service namespace tinyapi
            ```

            - Add this immediately after the Platform API section

            ```
                # =================================================
                # Tiny API
                # =================================================
                <Location /tinyapi>
                    AuthType Isilon
                    IsiAuthName "tinyapi"
                    IsiAuthTypeBasic On
                    IsiAuthTypeSessionCookie On
                    IsiDisabledZoneAllow Off
                    IsiMultiZoneAllow On
                    IsiCsrfCheck On
                    ProxyPass "http://localhost:8000/"
                    ProxyPassReverse "http://localhost:8000/"
                    Require valid-user
                    ErrorDocument 401 /json/401.json
                    Header set Content-Security-Policy "default-src 'none'"
                </Location>
            ```

        3. Deploy apache config
                **single node**

                ```
                bash /ifs/data/Isilon_Support/isitinyapi-main/deployhttpdconf.sh
                ```
                
                **all nodes**
                
                ```
                isi_for_array bash /ifs/data/Isilon_Support/isitinyapi-main/deployhttpdconf.sh
                ```

5. **Startup**
   - The easiest way to star the service is to wait for cron job to start the service which will happen at the top of the next hour (ex. 10:00a, 11:00a, 12:00p)

   - Alternatively, the impatient can start manually by running the `run.sh` script as root
   `bash /ifs/data/Isilon_Support/isitinyapi-main/run.sh`

## Updates / Configuration Changes

Changes to the config.json are applied at runtime. Code updates or config.json changes should be followed by terminating the service and then allowing it to start again.

```
ps-auxww | grep -i isi_tiny_api.py | grep -v grep | xargs kill -9 
```

## Uninstallation

To uninstall:

- Remove  lines from the crontab from mcp templates crontab
- Remove changes to webui-httpd.conf and deploy
- Terminate the service: ```ps-auxww | grep -i isi_tiny_api.py | grep -v grep | xargs kill -9```
- Delete the installation files from the system.
Error loading webview: Error: Could not register service worker: InvalidStateError: Failed to register a ServiceWorker: The document is in an invalid state..
## Limitations and Security

The API is designed to minimize system load by caching responses and limiting the frequency of command executions. It accepts only GET requests and restricts access to localhost for enhanced security using the Apache install to proxy requests isolating the python http server. Any deviations from this setup should be carefully evaluated in light of security considerations.

## Testing

Configure `test.py` with the appropriate cluster IP, username, and password and then run: ```python3 test.py```

## Role Based Access

Access to the service requires both an authenticated user and 'r'ead access to the platform api. Refer to the administration guide for instructions on creating a role with platform access and adding a user to that role.
Error loading webview: Error: Could not register service worker: InvalidStateError: Failed to register a ServiceWorker: The document is in an invalid state..
### Create local user or skip to use existing user

```
isi auth users create --set-password --enabled=True --provider LOCAL:System test
```

### Create role and assign user

```
isi auth roles create TinyAPI
isi auth roles modify --add-user test --add-priv-read ISI_PRIV_LOGIN_PAPI TinyAPI
```

### edit test.py and replace clusterip, username and password, then run

```
python3 test.py
````
