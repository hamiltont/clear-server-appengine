'''
Created on Jun 28, 2010

@author: Zach
'''
from google.appengine.ext import db
from google.appengine.ext import webapp
from django.utils import simplejson
import Utils
import math
import geobox
from google.appengine.ext.db import GeoPt

# Radius of the earth in miles.
RADIUS = 3963.1676
def _earth_distance(lat1, lon1, lat2, lon2):
    lat1, lon1 = math.radians(float(lat1)), math.radians(float(lon1))
    lat2, lon2 = math.radians(float(lat2)), math.radians(float(lon2))
    return RADIUS * math.acos(math.sin(lat1) * math.sin(lat2) + math.cos(lat1) * math.cos(lat2) * math.cos(lon2 - lon1))

GEOBOX_CONFIGS = (
  (4, 5, True),
  (3, 2, True),
  (3, 8, False),
  (3, 16, False),
  (2, 5, False),
)

class Test(db.Model):
    name = db.StringProperty()
    details = db.StringProperty()
    sensor_types = db.ListProperty(int)
    questions = db.StringListProperty()
    location = db.GeoPtProperty()
    geoboxes = db.StringListProperty()
    
    @classmethod
    def query(self, lat, lon, max_results):
        found_tests = {}
        
        # Do concentric queries until the max number of results is reached.
        # Use only the first three geoboxes for search to reduce query overhead.
        for params in GEOBOX_CONFIGS[:3]:
            if len(found_tests) >= max_results:
                break

            resolution, slice, unused = params
            box = geobox.compute(lat, lon, resolution, slice)
            query = Test.all()
            query.filter("geoboxes =", box)
            results = query.fetch(50)
      
            # De-dupe results.
            for result in results:
                if result.name not in found_tests:
                    found_tests[result.name] = result

            # Now compute distances and sort by distance.
            tests_by_distance = []
            for test in found_tests.itervalues():
                #distance = _earth_distance(lat, lon, test.location.lat, test.location.lon)
                #tests_by_distance.append((distance, test))
                tests_by_distance.append((test.key().id(), test))
            #tests_by_distance.sort()

            return tests_by_distance[:max_results]
    

class RESTTest(webapp.RequestHandler):
    def get(self, id=None):
        if id is None:
            # for "/test"
            tests = db.GqlQuery("SELECT __key__ FROM Test")
            self.response.out.write(Utils.GqlEncoder().encode(tests))
        else:
            # for "/test/abc123def456"
            test = Test.get_by_id(int(id), None)
            self.response.out.write(Utils.GqlEncoder().encode(test))
    def post(self, id=None):
        # for "/test"
        decoded = simplejson.JSONDecoder().decode(self.request.body)
        
        all_boxes = []
        test = Test()
        lat= decoded.get('lat')
        lon = decoded.get('lon')
        test.name = decoded.get('name')
        test.details = decoded.get('details')
        test.sensor_types = decoded.get('sensor_types')
        test.questions = decoded.get('questions')
        for (resolution, slice, use_set) in GEOBOX_CONFIGS:
            if use_set:
                all_boxes.extend(geobox.compute_set(lat, lon, resolution, slice))
            else:
                all_boxes.append(geobox.compute(lat, lon, resolution, slice))
        test.location = GeoPt(lat, lon)
        test.geoboxes = all_boxes
        
        
        test.put()
        
        self.response.set_status(201)
        self.response.out.write(Utils.GqlEncoder().encode({"id":test.key()}))
