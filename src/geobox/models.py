#!/usr/bin/env python
#
# Copyright 2008 Brett Slatkin
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Models for Mutiny backend.

In San Francisco, the degrees of latitude and longitude roughly translate into
these distances on the ground:

0.00001 = 1 meters = 3.2 feet
0.0001 = 10 meters = 32 feet
0.0002 = 20 meters = 65 feet
0.0005 = 50 meters = 165 feet
0.001 = 100 meters = 330 feet
0.002 = 200 meters = 660 feet = 0.125 miles
0.005 = 500 meters = 1,640 feet = 0.3 miles
0.008 = 800 meters = 2,625 feet = 0.5 miles
0.016 = 1600 meters = 5,250 feet = 1.0 miles
0.05 = 5000 meters = 16,400 feet = 3.1 miles

We'll use all of these various resolutions to allow for scanning for bus stops
at different levels of resolution.
"""

__author__ = "bslatkin@gmail.com (Brett Slatkin)"

import logging
import math
from google.appengine.ext import db

import geobox


# List of resolutions and slices. Should be in increasing order of size/scope.
GEOBOX_CONFIGS = (
  (4, 5, True),
  (3, 2, True),
  (3, 8, False),
  (3, 16, False),
  (2, 5, False),
)

# Radius of the earth in miles.
RADIUS = 3963.1676


def _earth_distance(lat1, lon1, lat2, lon2):
  lat1, lon1 = math.radians(float(lat1)), math.radians(float(lon1))
  lat2, lon2 = math.radians(float(lat2)), math.radians(float(lon2))
  return RADIUS * math.acos(math.sin(lat1) * math.sin(lat2) +
      math.cos(lat1) * math.cos(lat2) * math.cos(lon2 - lon1))


class MuniStop(db.Model):
  """Represents a single Muni stop."""

  system = db.StringProperty(required=True)  # Just "sf-muni" for now.
  stop_id = db.StringProperty(required=True)
  location = db.GeoPtProperty(required=True)
  in_routes = db.StringListProperty()
  out_routes = db.StringListProperty()
  has_inbound_routes = db.BooleanProperty(required=True)
  has_outbound_routes = db.BooleanProperty(required=True)
  geoboxes = db.StringListProperty()
  title = db.StringProperty(required=True)

  @classmethod
  def create(cls, **kwargs):
    """Insert a new Muni stop entry with all corresponding geoboxes.
    
    Args:
      system: The muni system to use. Always "sf-muni" right now.
      lat, lon: Coordinates of stop.
      stop_id: The stop ID of the stop.
      in_routes: List of inbound routes.
      out_routes: List of outbound routes.
    """
    all_boxes = []
    lat = kwargs.pop("lat")
    lon = kwargs.pop("lon")
    for (resolution, slice, use_set) in GEOBOX_CONFIGS:
      if use_set:
        all_boxes.extend(geobox.compute_set(lat, lon, resolution, slice))
      else:
        all_boxes.append(geobox.compute(lat, lon, resolution, slice))
    kwargs["stop_id"] = str(kwargs["stop_id"])
    kwargs["location"] = db.GeoPt(lat, lon)
    kwargs["key_name"] = "stop:%s:%s" % (kwargs["system"], kwargs["stop_id"])
    kwargs["geoboxes"] = all_boxes
    kwargs["has_inbound_routes"] = bool(len(kwargs["in_routes"]) > 0)
    kwargs["has_outbound_routes"] = bool(len(kwargs["out_routes"]) > 0)
    return cls(**kwargs)

  @classmethod
  def query(cls, system, lat, lon, inbound, max_results, min_params):
    """Queries for Muni stops repeatedly until max results or scope is reached.
    Args:
      system: The transit system to query.
      lat, lon: Coordinates of the agent querying.
      inbound: If the routes we're interested in are inbound.
      max_results: Maximum number of stops to find.
      min_params: Tuple (resolution, slice) of the minimum resolution to allow.
    
    Returns:
      List of (distance, MuniStop) tuples, ordered by minimum distance first.
      There will be no duplicates in these results. Distance is in meters.
    """
    # Maps stop_ids to MuniStop instances.
    found_stops = {}
    
    # Do concentric queries until the max number of results is reached.
    # Use only the first three geoboxes for search to reduce query overhead.
    for params in GEOBOX_CONFIGS[:3]:
      if len(found_stops) >= max_results:
        break
      if params < min_params:
        break

      resolution, slice, unused = params
      box = geobox.compute(lat, lon, resolution, slice)
      logging.debug("Searching for box=%s at resolution=%s, slice=%s",
                    box, resolution, slice)
      query = cls.all()
      query.filter("geoboxes =", box)
      query.filter("system =", system)
      if inbound:
        query.filter("has_inbound_routes =", True)
      else:
        query.filter("has_outbound_routes =", True)
      results = query.fetch(50)
      logging.debug("Found %d results", len(results))
      
      # De-dupe results.
      for result in results:
        if result.stop_id not in found_stops:
          found_stops[result.stop_id] = result

    # Now compute distances and sort by distance.
    stops_by_distance = []
    for stop in found_stops.itervalues():
      distance = _earth_distance(lat, lon, stop.location.lat, stop.location.lon)
      stops_by_distance.append((distance, stop))
    stops_by_distance.sort()

    return stops_by_distance[:max_results]
