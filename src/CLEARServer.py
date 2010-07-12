'''
Created on Jun 27, 2010

@author: Zach
'''
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from Device import RESTDevice
from Test import RESTTest
from SensorType import RESTSensorType
from Sensor import RESTSensor
from Data import RESTData
from Poll import Poll

application = webapp.WSGIApplication([('/poll', Poll),
                                      ('/device', RESTDevice),
                                      ('/device/(.*)', RESTDevice),
                                      ('/sensortype', RESTSensorType),
                                      ('/sensortype/(.*)', RESTSensorType),
                                      ('/sensor', RESTSensor),
                                      ('/sensor/(.*)', RESTSensor),
                                      ('/data', RESTData),
                                      ('/data/(.*)', RESTData),
                                      ('/test', RESTTest),
                                      ('/test/(.*)', RESTTest),
                                     ],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()


    