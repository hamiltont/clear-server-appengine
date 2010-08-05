'''
Created on Jul 1, 2010

@author: Zach
'''
from Test import Test
from google.appengine.ext import webapp
import Utils

class Poll(webapp.RequestHandler):
    def get(self):
        lat = float(self.request.get('lat'))
        lon = float(self.request.get('lon'))
        newtests = Test.query(lat, lon)
        self.response.out.write(Utils.GqlEncoder().encode(newtests))