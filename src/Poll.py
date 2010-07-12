'''
Created on Jul 1, 2010

@author: Zach
'''
from Device import Device
from Sensor import Sensor
from Test import Test
from google.appengine.ext import webapp
import Utils

class Poll(webapp.RequestHandler):
    def get(self):
        id = self.request.get('id')
        lat = self.request.get('lat')
        lon = self.request.get('lon')
        device = Device.get_by_id(int(id), None)
        sensors = device.sensors
        sensorlist = []
        for sensor in sensors:
            currentSensor = Sensor.get_by_id(sensor, None)
            sensorlist.append(currentSensor.type)
        newtests = Test.query(lat, lon, 50)
        self.response.out.write(Utils.GqlEncoder().encode(newtests))