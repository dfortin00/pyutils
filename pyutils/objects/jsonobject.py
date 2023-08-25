
class JSONObject():
    _json_properties = {}

    def __init__(self):
        for k in self._json_properties.keys():
            setattr(self, k, None)

    def property_type(self, key, listType=False):
        if isinstance(self._json_properties[key], list):
            if listType:
                return None if (len(self._json_properties[key]) == 0) else self._json_properties[key][0]
            return type([])
        return self._json_properties[key]

    def is_instance(self, key, cls):
        if isinstance(self._json_properties[key], list):
            return type(self._json_properties[key]) == cls
        return self._json_properties[key] == cls
