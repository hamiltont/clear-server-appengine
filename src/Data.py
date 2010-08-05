'''
Created on Jun 28, 2010

@author: Zach
'''
from django.utils import simplejson
from google.appengine.ext import db
from google.appengine.ext import webapp
from SerializableProperty import SerializableProperty
from Utils import GqlEncoder

class Data(db.Model):
    test_id = db.IntegerProperty()
    device_id = db.IntegerProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    content = SerializableProperty()

class RESTData(webapp.RequestHandler):
    def get(self, id=None):
        if id is None:
            # for "/result"
            data = db.GqlQuery("SELECT __key__ FROM Data")
            self.response.out.write(GqlEncoder().encode(data))
        else:
            # for "/result/abc123def456"
            datum = Data.get_by_id(int(id), None)
            self.response.out.write(GqlEncoder().encode(datum))
    def post(self):
            decoded = simplejson.JSONDecoder().decode(self.request.body)
            
            data = Data()
            data.test_id = decoded.get('test_id')
            data.device_id = decoded.get('device_id')
            data.content = decoded.get('content')
            data.put()
            
            self.response.set_status(201)
            self.response.out.write(simplejson.JSONEncoder().encode({"id":data.key().id()}))
    