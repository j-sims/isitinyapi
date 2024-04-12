echo '# Every hour check to ensure isi_tiny_api is running
0       *       *       *       *       root    /bin/bash /ifs/data/Isilon_Support/isitinyapi-main/run.sh' >> /etc/mcp/template/crontab && \
isi services -a isi_mcp disable && \
isi services -a isi_mcp enable && \
echo Success || echo Error
