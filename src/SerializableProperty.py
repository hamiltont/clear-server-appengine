'''
Created on Jul 1, 2010

@author: thesweeheng
from: http://thesweeheng.wordpress.com/2009/11/16/gae-storing-serializable-objects-in-datastore/
'''
from google.appengine.ext import db
import cPickle as pickle
import zlib

class SerializableProperty(db.Property):
  """
  A SerializableProperty will be pickled and compressed before it is
  saved as a Blob in the datastore. On fetch, it would be decompressed
  and unpickled. It allows us to save serializable objects (e.g. dicts)
  in the datastore.

  The sequence of transformations applied can be customized by calling
  the set_transforms() method.
  """

  data_type = db.Blob
  _tfm = [lambda x: pickle.dumps(x, 2), zlib.compress]
  _itfm = [zlib.decompress, pickle.loads]

  def set_transforms(self, tfm, itfm):
    self._tfm = tfm
    self._itfm = itfm

  def get_value_for_datastore(self, model_instance):
    value = super(SerializableProperty,
        self).get_value_for_datastore(model_instance)
    if value is not None:
      value = self.data_type(reduce(lambda x, f: f(x), self._tfm, value))
    return value

  def make_value_from_datastore(self, value):
    if value is not None:
      value = reduce(lambda x, f: f(x), self._itfm, value)
    return value
