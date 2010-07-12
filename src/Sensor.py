'''
Created on Jun 29, 2010

@author: Zach
'''
from google.appengine.ext import db, webapp
from SensorType import SensorType
from django.utils import simplejson
import Utils

class Sensor(db.Model):
    type = db.IntegerProperty()
    name = db.StringProperty()
    vendor = db.StringProperty()
    version = db.IntegerProperty()

class RESTSensor(webapp.RequestHandler):
    def get(self, id=None):
        if id is None:
            # for "/sensor"
            sensors = db.GqlQuery("SELECT __key__ FROM Sensor")
            self.response.out.write(Utils.GqlEncoder().encode(sensors))
        else:
            # for "/sensor/abc123def456"
            sensor = Sensor.get_by_id(int(id), None)
            self.response.out.write(Utils.GqlEncoder().encode(sensor))
    def post(self):
        decoded = simplejson.JSONDecoder().decode(self.request.body)
        mySensor = db.GqlQuery("SELECT __key__ FROM Sensor WHERE name=:1 AND vendor=:2 AND version=:3", decoded.get('name'), decoded.get('vendor'), decoded.get('version')).get()
        if mySensor == None:
            newSensor = Sensor()
            type = decoded.get('type')
            testsensortype = db.GqlQuery("SELECT __key__ FROM SensorType WHERE type=:1", type).get()
            if testsensortype == None:
                sensortype = SensorType()
                sensortype.type = type
                sensortype.put()
                newSensor.type = sensortype.key().id()
            else:
                newSensor.type = testsensortype.id()
            newSensor.name = decoded.get('name')
            newSensor.vendor = decoded.get('vendor')
            newSensor.version = decoded.get('version')
            newSensor.put()
            self.response.set_status(201)
            self.response.out.write(simplejson.JSONEncoder().encode({"id":newSensor.key().id()}))
        else:
            self.response.set_status(200)
            self.response.out.write(simplejson.JSONEncoder().encode({"id":mySensor.id()}))