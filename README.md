# Isi Tiny API

### Description
This sample code enables polling of cluster state data that is unavailable via PAPI without the need to run shell scripts locally.

The code should be used to obtain outputs from `sysctl` and other commands for monitoring or dashboards.

All responses are returned in JSON format.

Currently, only a single endpoint ('/') is provided, which returns all `sysctl` keys and the outputs of all commands specified in the `config.json` file.

### Installation

#### Download
On the cluster, run the following command to download and set up the API:

```
cd /ifs/data/Isilon_Support
curl -o isi_tiny_api.zip https://github.com/j-sims/isitinyapi/archive/refs/heads/main.zip
unzip isi_tiny_api.zip
cd isitinyapi
```

#### Edit the config.json
- edit the config.json and update with the keys and commands required
  - keep the list as short as possible and keep in mind the runtime that each command will take (total cannot exceed 2 min)

#### Add to mcp crontab
- edit the /etc/mcp/templates/crontab file and add the following lines to the end: see [this KB](https://www.dell.com/support/kbdoc/en-us/000190875/isilon-how-to-automate-weekly-cluster-log-uploads-isi-gather-info)

```
# Every hour check to ensure isi_tiny_api is running
0       *       *       *       *       root    /bin/bash /ifs/data/Isilon_Support/isitinyapi/run.sh
```

Once the cron entry is in place the run.sh script will check hourly to see if the isi_tiny_api.py script is running and if not, will start the script.

#### Add to apache config file /usr/local/apache2/conf/webui_httpd.conf


```

LoadModule proxy_module modules/mod_proxy.so
LoadModule proxy_http_module modules/mod_proxy_http.so
```

Add this location section near the bottom after the last Location section
```
    # =================================================
    # Tiny API
    # =================================================
    <Location /tinyapi>
        AuthType Isilon
        IsiAuthName "namespace"
        IsiAuthTypeBasic On
        IsiAuthTypeSessionCookie On
        Require valid-user
        ProxyPass "http://localhost:8000/"
        ProxyPassReverse "http://localhost:8000/"
        SetHandler fastcgi-script
        Options +ExecCGI
        ErrorDocument 401 /json/401.json
    </Location>
```

### Limitations
This code is engineered to efficiently monitor a select set of sysctl parameters and execute a limited number of commands. By default, it employs a caching mechanism with a one-hour duration to minimize system load from frequent external command executions. Any reduction in the caching period or a significant increase in the number of commands could adversely affect cluster performance.

The application is configured to accept only GET requests and restricts access exclusively to the localhost. This design limits the potential for external attacks. Any modifications to these settings should be undertaken only after thorough evaluation and must be approved by the information security team.

The changes in these instructions may be lost during upgrades. After each upgrade check to see if the service is still operating and re-install if needed.
