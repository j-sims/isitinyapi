#! /bin/env python3
import os
import json
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import time

INSTALLPATH = "/ifs/data/Isilon_Support/tinyapi"

with open(f'{INSTALLPATH}/config.json', 'r') as f:
    config = json.load(f)

def is_cached(config):
    file_path = Path(config['main']['cache_file'])
    if not os.path.exists(file_path):
        return False
    mtime = file_path.stat().st_mtime
    current_time = time.time()
    if (current_time - mtime) > 3600:
        return False
    return True


def get_sysctl_data(config):
    sysctls ={}
    for key in config['sysctl']:
        pass


def run_command(command):
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    if result.returncode == 0:
        return result
    else:
        return result

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL path
        if self.path == '/':
            self.handle_root_path()
        else:
            self.handle_404()

    def handle_root_path(self):
        
        send_error_code = False
        if is_cached(config):
            with open(config['main']['cache_file'], 'r') as f:
                cache = json.load(f)
                cache['cache'] = True
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
        
                self.wfile.write(json.dumps(cache).encode('utf-8'))
        else:
            data = {} 
            data['cache'] =  False
            data['sysctl'] = {}
            data['commands'] = {}
            
            for key in config['sysctl']:
                result = run_command(f"sysctl -n {key}")

                if result.returncode != 0:
                    send_error_code = True
                    data['sysctl'][key] = result.stderr.rstrip()
                else:
                    data['sysctl'][key] = result.stdout.rstrip()

            for cmd in config['commands']:
                result = run_command(cmd)

                if result.returncode != 0:
                    send_error_code = True
                    data['commands'][cmd] = result.stderr.rstrip()
                else:
                    data['commands'][cmd] = result.stdout.rstrip()

            with open(config['main']['cache_file'], 'w') as f:
                json.dump(data, f)
                
            if send_error_code:
                self.send_response(422)
            else:
                self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            self.wfile.write(json.dumps(data).encode('utf-8'))



    def handle_404(self):
        self.send_response(404)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {"error": "Resource not found."}
        self.wfile.write(json.dumps(response).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler):
    server_address = (config['main']['address'], config['main']['port'])
    httpd = server_class(server_address, handler_class)
    print('Starting httpd...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()