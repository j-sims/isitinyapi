# Isi Tiny API

### Description
Sample code for serving config data not available through PAPI. Caching added to ensure the code doesn't impact services.


### Installation

#### Download
On the cluster run the following command:

```
cd /ifs/data/Isilon_Supoprt
curl -o isi_tiny_api.zip https://github.com/j-sims/isitinyapi/archive/refs/heads/main.zip
unzip isi_tiny_api.zip
cd isitinyapi
```

#### Edit the config.json
- edit the config.json and update with the keys and commands required
  - keep the list as short as possible and keep in mind the runtime that each command will take (total cannot exceed 2 min)

#### Add to mcp crontab
- edit the /etc/mcp/templates/crontab file and add the following lines to the end per this KB: https://www.dell.com/support/kbdoc/en-us/000190875/isilon-how-to-automate-weekly-cluster-log-uploads-isi-gather-info

```
# Every hour check to ensure isi_tiny_api is running
0       *       *       *       *       root    /bin/bash $INSTALLPATH/run.sh
```

Once the cron entry is in place the run.sh script will check hourly to see if the isi_tiny_api.py script is running and if not, will start the script.

#### Add to apache config file /usr/local/apache2/conf/webui_httpd.conf

Add these two modules line to the Modules Section near the top

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
