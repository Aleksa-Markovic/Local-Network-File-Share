import os
import json

IP = 'localhost'
PORT = 8080

if os.path.exists('config'):
    with open('config') as f:
        text = json.load(f)
        IP = text['SERVER_IP']
        PORT = int(text['SERVER_PORT'])        

os.system(f'python -m http.server -b {IP} {PORT}')