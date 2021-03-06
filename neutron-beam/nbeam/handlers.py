import os
import json
import time
import types
import base64
import hashlib
import requests

import jwt
from cryptography.fernet import Fernet

from tornado.web import RequestHandler, StaticFileHandler, HTTPError
from tornado.escape import json_encode, json_decode

import nbeam.version

EKEYS = {}

class NeutronHandler (RequestHandler):
  def __init__ (self, *args, **kwargs):
    self.config = args[0].config
    self.ekey = None
    super(NeutronHandler, self).__init__(*args, **kwargs)
    
  def options (self):
    self.set_header('Access-Control-Allow-Origin', '*')
    self.set_header('Access-Control-Allow-Headers', 'Content-Type')
    
    methods = ['OPTIONS']
    for m in ('post', 'get', 'put', 'delete'):
      if hasattr(self, m):
        methods.append(m.upper())
        
    self.set_header('Access-Control-Allow-Methods', ", ".join(methods))
    
  def start_request (self):
    self.set_header('Content-Type', 'application/json')
    self.set_header('Access-Control-Allow-Origin', '*')
    self.set_header('Neutron-Beam-Version', nbeam.version.__version__)
    
    self.data = {'status': 'invalid-request'}
    
  def get_headers (self):
    self.set_header('Cache-Control', 'no-cache, no-store, must-revalidate')
    self.set_header('Pragma', 'no-cache')
    self.set_header('Expires', '0')
    
  def finish_request (self):
    if self.get_status() == 409:
      return None
      
    if self.config['encrypt']:
      j = self.encrypt(self.data)
      
    else:
      j = json_encode(self.data)
      
    self.write(j)
    self.finish()
    
  def valid_request (self):
    body = self.request.body
    if self.config['encrypt']:
      body = self.decrypt(body)
      
    if self.get_status() == 409:
      return False
      
    try:
      self.json = json.loads(body)
      
    except ValueError:
      self.json = {}
      
    self.get_path()
    if self.path.startswith(self.config['code_dir']):
      return True
      
    else:
      self.data = {'status': 'invalid-path'}
      return False
      
    return False
    
  def encrypt (self, body):
    body = json_encode(body)
    
    f = Fernet(self.ekey)
    return f.encrypt(body)
    
  def decrypt (self, body):
    global EKEYS
    
    now = time.time()
    for ts in EKEYS.keys():
      if now - ts > 1800:
        del EKEYS[ts]
        
    for ts, ekey in EKEYS.items():
      try:
        f = Fernet(ekey)
        data = f.decrypt(body)
        
      except:
        pass
        
      else:
        self.ekey = ekey
        return data
        
    self.set_status(409)
    self.write(json_encode({'status': 'invalid-encryption'}))
    self.finish()
    
  def hashstr (self, path):
    return 'nbeam-' + hashlib.sha256(path).hexdigest()
    
  def get_path (self):
    if 'path' in self.json:
      path = os.path.normpath(os.path.join(self.config['code_dir'], self.json['path']))
      basedir = self.json['path']
      
    else:
      path = os.path.normpath(self.config['code_dir'])
      basedir = ''
      
    self.path = path
    self.basedir = basedir
    
class PostMixin (object):
  def post (self):
    self.start_request()
    if self.valid_request():
      self.post_request()
      
    self.finish_request()
    
class SetupHandler (NeutronHandler):
  def url (self):
    url = 'http'
    if self.config['ssl']:
      url += 's'
      
    url += '://' + self.config['server'] + '/editor/get-ekey'
    
    return url
    
  def post (self):
    global EKEYS
    self.start_request()
    
    api_keys = self.config['api_key']
    if type(api_keys) not in (types.TupleType, types.ListType):
      api_keys = [api_keys]
      
    for api_key in api_keys:
      try:
        payload = jwt.decode(self.request.body, api_key)
        
      except:
        pass
        
      else:
        if payload['user'].lower() == self.config['username'].lower():
          r = requests.post(self.url(), data={'beam': payload['id'], 'akey': api_key})
          
          if r.status_code == 200:
            EKEYS[time.time()] = str(r.json()['key'])
            
            j = json_encode({'status': 'OK'})
            self.write(j)
            self.finish()
            return None
            
    self.clear()
    self.set_status(401)
    self.finish("Unauthorized")
    