'''
    This is just a simple script to run a local server, in case someone needs it, it uses the config file associated with the main script if present,
    and if not it defaults to 127.0.0.1:8080
'''
import os
import json

IP = '127.0.0.1'
PORT = 8080

# If the config file exists this will load its configuration, otherwise default is applied
if os.path.exists('config'):
    with open('config') as f:
        text = json.load(f)
        IP = text['SERVER_IP']
        PORT = int(text['SERVER_PORT'])        

os.system(f'python -m http.server -b {IP} {PORT}')