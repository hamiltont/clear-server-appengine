'''
Created on Jun 28, 2010

@author: Zach
'''
from django.utils import simplejson
from google.appengine.ext import db, webapp
import Utils

class Device(db.Model):
    sensors = db.ListProperty(int)
    created = db.DateTimeProperty(auto_now_add=True)

class RESTDevice(webapp.RequestHandler):
    def get(self, id=None):
        if id is None:
            # for "/device"
            devices = db.GqlQuery("SELECT __key__ FROM Device")
            self.response.out.write(Utils.GqlEncoder().encode(devices))
        else:
            # for "/device/abc123def456"
            device = Device.get_by_id(int(id), None)
            self.response.out.write(Utils.GqlEncoder().encode(device))

    def post(self, id=None):
        decoded = simplejson.JSONDecoder().decode(self.request.body)
            
        #Create a new device and save it
        device = Device()
        device.sensors = decoded.get('sensors')
        device.put()
        self.response.set_status(201)
        self.response.out.write(Utils.GqlEncoder().encode({"id":device.key()}))