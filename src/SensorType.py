'''
Created on Jun 29, 2010

@author: Zach
'''
from google.appengine.ext import db, webapp
from django.utils import simplejson
import Utils

class SensorType(db.Model):
    type = db.StringProperty()

class RESTSensorType(webapp.RequestHandler):
    def get(self, id=None):
        if id is None:
            # for "/sensortype"
            sensortypes = db.GqlQuery("SELECT __key__ FROM SensorType")
            self.response.out.write(Utils.GqlEncoder().encode(sensortypes))
        else:
            # for "/sensortype/abc123def456"
            sensortype = SensorType.get_by_id(int(id), None)
            self.response.out.write(Utils.GqlEncoder().encode(sensortype))
    def post(self):
        decoded = simplejson.JSONDecoder().decode(self.request.body)
        
        sensortype = SensorType()
        sensortype.type = decoded.get('type')
        sensortype.put()
        
        self.response.out.write(sensortype.key().id())