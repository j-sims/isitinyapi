# Isi Tiny API

## Description
This sample code enables polling of cluster state data that is unavailable via PAPI without the need to run shell scripts locally.

The code should be used to obtain outputs from `sysctl` and other commands for monitoring or dashboards.

All responses are returned in JSON format.

Currently, only a single endpoint ('/') is provided, which returns all `sysctl` keys and the outputs of all commands specified in the `config.json` file.
## Risks
Installing the Tiny API requires executing unix shell commands and hand editing the apache config file. Unless the user is experienced making changes such as these in a production environment they risk breaking the apache configuration and rendering the WebUI inaccessible.

Proceeding to install is to accept the risk to the environment. Such changes are not supported by Dell EMC.

## Requirements
OneFS version 9.5+ is required

## Installation
Installing the services requires changes to the apache config file and adding it to the crontab.

The apache config file change consists of adding two sections and an additional keyword to one line.

As the version of apache and the config file format can change between releases the steps here are provided as guidance and cannot be taken as an exact process.

### Install High Level Process
- Download the code to one node in /ifs/data/Isilon_Support
- Extract in place creating isitinyapi-main
- Edit the config.json file to define systl keys and commands
- Run installcron.sh on one or all nodes to monitor the service hourly and restart if needed
- Copy the webui config file, edit, and run deployhttpd.sh on one or all nodes
- Manually start the service the first time on one or all nodes OR wait until the next hour for the service to be started by cron

### Single Node or All Nodes?
If the data that is needed can be collected from a single node then the installation can be performed on one node. However, if the data needed is from each node then the installation will need to be performed on all nodes.

### Download
On one node of the cluster, run the following command to download:

```
cd /ifs/data/Isilon_Support
curl -k -L -o isi_tiny_api.zip https://github.com/j-sims/isitinyapi/archive/refs/heads/main.zip
unzip isi_tiny_api.zip
cd isitinyapi-main
```

### Edit the config.json
- edit the config.json and update with the keys and commands required
  - keep the list as short as possible and keep in mind the runtime that each command will take (total cannot exceed 2 min)

### Add to mcp crontab

**single node**
```
bash /ifs/data/Isilon_Support/isitinyapi-main/installcron.sh
```

**all nodes**
```
isi_for_array bash /ifs/data/Isilon_Support/isitinyapi-main/installcron.sh
```


Once the cron entry is in place the run.sh script will check hourly to see if the isi_tiny_api.py script is running and if not, will start the script.

### Configure Apache

### Copy /usr/local/apache2/conf/webui_httpd.conf and backup

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

### Edit /ifs/data/Isilon_Support/isitinyapi-main/webui_httpd.conf

Add these two sections

#### Add near top with other LoadModules

```

LoadModule proxy_module modules/mod_proxy.so
LoadModule proxy_http_module modules/mod_proxy_http.so
```

#### Add tinyapi to list of services
Change near line 358 from this:
```
         IsiAuthServices platform remote-service namespace
```
to this:
```
         IsiAuthServices platform remote-service namespace tinyapi
```


#### Add this immediately after the Platform API section
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

### Deploy apache config
**single node**
```
bash /ifs/data/Isilon_Support/isitinyapi-main/deployhttpdconf.sh
```

**all nodes**
```
isi_for_array bash /ifs/data/Isilon_Support/isitinyapi-main/deployhttpdconf.sh
```

### Start the Service

**single node**
```
bash /ifs/data/Isilon_Support/isitinyapi-main/run.sh && \
sleep 3 && \
ps -auxww | grep isi_tiny_api.py | grep -v grep > /dev/null && echo Running || echo "Not Running"
```

**all nodes**
```
isi_for_array bash /ifs/data/Isilon_Support/isitinyapi-main/run.sh
```


## Role Based Access
Access to the service requires both an authenticated user and 'r'ead access to the platform api. Refer to the administration guide for instructions on creating a role with platform access and adding a user to that role.

## Testing Tiny API

### Create local user or skip and use existing user.
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

## Limitations
This code is engineered to efficiently monitor a select set of sysctl parameters and execute a limited number of commands. By default, it employs a caching mechanism with a one-hour duration to minimize system load from frequent external command executions. Any reduction in the caching period or a significant increase in the number of commands could adversely affect cluster performance.

The application is configured to accept only GET requests and restricts access exclusively to the localhost. This design limits the potential for external attacks. Any modifications to these settings should be undertaken only after thorough evaluation and must be approved by the information security team.

The changes in these instructions may be lost during upgrades. After each upgrade check to see if the service is still operating and re-install if needed.

## Stop / Start

### Stop
```
ps -auxww | grep isi_tiny_api.py | grep -v grep | awk '{print$2}' | xargs kill -9
```

### Start
```
cd /ifs/data/Isilon_Support/isitinyapi-main
bash run.sh
```

## Upgrade or Config Changes
Updates are only recognized and implemented at startup. For an upgrade, simply download and install the latest version over the existing one. Then, restart the system to activate the upgrade.

The same procedure applies for configuration updates.


## Uninstall Tiny API
Remove the following two lines from the /etc/mcp/templates/crontab file and then restart isi_mcp:

### Remove these lines

```
# Every hour check to ensure isi_tiny_api is running
0       *       *       *       *       root    /bin/bash /ifs/data/Isilon_Support/isitinyapi-main/run.sh
```

### Restart mcp
```
isi services -a isi_mcp disable && isi services -a isi_mcp enable
``` 

#### Remove near top of /usr/local/apache2/conf/webui_httpd.conf

```

LoadModule proxy_module modules/mod_proxy.so
LoadModule proxy_http_module modules/mod_proxy_http.so
```

#### Remove tinyapi from list of auth services
Change near line 358 from this:
```
         IsiAuthServices platform remote-service namespace tinyapi
```
to this:
```
         IsiAuthServices platform remote-service namespace 
```

#### Remove near bottom of /usr/local/apache2/conf/webui_httpd.conf
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

### Restart webui
```isi services isi_webui disable && isi services isi_webui enable```

### Remove files from install location
```
rm -rf /ifs/data/Isilon_Support/isitinyapi-main && rm /ifs/data/Isilon_Support/isitinyapi.zip
```