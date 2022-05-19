import logging

class JsonConverter:
  def __init__(self) -> None:
    self._accepted_tags = dict() # Will store all of the types used, so the dicts can be converted back to those types
  
  def addAcceptedTag(self, class_type: type):
    type_str = class_type.__name__
    self._accepted_tags[type_str] = class_type

  def addAcceptedTags(self, class_types: list[type]):
    for class_type in class_types:
      type_str = class_type.__name__
      self._accepted_tags[type_str] = class_type

  def objToJson(self, obj):
    obj_type = type(obj)
    type_str = obj_type.__name__
    if obj_type is list:
      new_list = list()
      for item in obj:
        new_list.append(self.objToJson(item))
      return new_list
    elif obj_type is set:
      new_set = set()
      for item in obj:
        new_set.add(self.objToJson(item))
      return new_set
    elif obj_type is dict:
      new_dict = dict()
      for key in obj:
        new_dict[key] = self.objToJson(obj[key])
      return new_dict
    elif (obj_type in [int,float,str,bool]) or (obj == None):
      return obj
    else:
      try:
        new_dict = vars(obj)
      except TypeError:
        logging.error(f'Object type: {obj_type.__name__}\nData:\n{obj}')
        exit()
      for key in new_dict:
        new_dict[key] = self.objToJson(new_dict[key])
      type_str = obj_type.__name__
      new_dict['type'] = type_str
      if type_str not in self._accepted_tags:
        self._accepted_tags[type_str] = obj_type
      return new_dict

  def jsonToObj(self, orig):
    orig_type = type(orig)

    if orig == None:
      return None
    elif orig_type is list:
      new_list = list()
      for item in orig:
        new_list.append(self.jsonToObj(item))
      return new_list
    elif orig_type is set:
      new_set = set()
      for item in orig:
        new_set.add(self.jsonToObj(item))
      return new_set
    elif orig_type is dict:
      if 'type' in orig:
        dict_type_str = orig.pop('type')
        # https://stackoverflow.com/questions/1176136/convert-string-to-python-class-object
        dict_type = self._accepted_tags[dict_type_str]
        new_obj = dict_type.__new__(dict_type)
        for key in orig:
          val = self.jsonToObj(orig[key])
          setattr(new_obj, key, val)
        return new_obj
      else:
        new_dict = dict()
        for key in orig:
          new_dict[key] = self.jsonToObj(orig[key])
        return new_dict
    elif orig_type in [int,float,str,bool]:
      return orig
    else:
      logging.info('Type error:')
      logging.info(f'Type: {orig_type}')
      logging.info(f'Data:\n{orig}')
      raise TypeError