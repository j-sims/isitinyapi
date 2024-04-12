cp /ifs/data/Isilon_Support/isitinyapi-main/webui_httpd.conf /usr/local/apache2/conf/webui_httpd.conf && \
isi services -a isi_webui disable && isi services -a isi_webui && enable && \
echo Success