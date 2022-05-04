def objToJson(obj):
  obj_type = type(obj)
  if obj_type is list:
    new_list = list()
    for item in obj:
      new_list.append(objToJson(item))
    return new_list
  elif obj_type is set:
    new_set = set()
    for item in obj:
      new_set.add(objToJson(item))
    return new_set
  elif obj_type is dict:
    new_dict = dict()
    for key in obj:
      new_dict[key] = objToJson(obj[key])
    return new_dict
  elif obj_type in [int,float,str]:
    return obj
  else:
    new_dict = vars(obj)
    for key in new_dict:
      new_dict[key] = objToJson(new_dict[key])
    new_dict['type'] = obj_type.__name__
    return new_dict

def jsonToObj(orig):
  orig_type = type(orig)
  if orig_type is list:
    print('Item is a list')
    new_list = list()
    for item in orig:
      new_list.append(jsonToObj(item))
    return new_list
  elif orig_type is set:
    new_set = set()
    for item in orig:
      new_set.add(jsonToObj(item))
    return new_set
  elif orig_type is dict:
    if 'type' in orig:
      dict_type = orig.pop('type')
      # https://stackoverflow.com/questions/1176136/convert-string-to-python-class-object
      new_obj = globals()[dict_type]()
      for key in orig:
        val = jsonToObj(orig[key])
        setattr(new_obj, key, val)
      return new_obj
    else:
      new_dict = dict()
      for key in orig:
        new_dict[key] = jsonToObj(orig[key])
      return new_dict
  elif orig_type in [int,float,str]:
    return orig
  else:
    raise TypeError