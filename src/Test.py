'''
Created on Jun 28, 2010

@author: Zach
'''
from google.appengine.ext import db
from google.appengine.ext import webapp
from django.utils import simplejson
import Utils
from SerializableProperty import SerializableProperty

class Test(db.Model):
    name = db.StringProperty()
    details = db.StringProperty()
    requests = SerializableProperty()
    lat = db.FloatProperty()
    lon = db.FloatProperty()
    radius = db.IntegerProperty()
    
    @classmethod
    def query(self, mylat, mylon):
        query = Test.all()
        results = query.fetch(limit=50)
        tests=[]
        for test in results:
            testlat = test.lat
            testlon = test.lon
            dist = Utils.Haversine.distance((testlat, testlon), (mylat, mylon))
            if dist < test.radius:
                tests.append(test)
        return tests
    

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
        
        test = Test()
        test.lat = decoded.get('lat')
        test.lon = decoded.get('lon')
        test.radius = decoded.get('radius')
        test.name = decoded.get('name')
        test.details = decoded.get('details')
        test.requests = decoded.get('requests')
        test.put()
        
        self.response.set_status(201)
        self.response.out.write(Utils.GqlEncoder().encode({"id":test.key()}))
