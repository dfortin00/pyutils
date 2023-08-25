import copy
import json
from json import JSONEncoder

import sys, os

if 'pyutils' in sys.modules:
    from pyutils.objects.jsonobject import JSONObject
else:
    sys.path.insert(0,
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from objects.jsonobject import JSONObject

def to_json(obj:JSONObject, excludeNull:bool=False, nullIfEmpty:bool=False, indent:int=None) -> str:
    """
    Convert a JSONObject into a JSON string.

    Args:
        obj: The JSONObject to convert to string
        excludeNull: Remove all null fields from the JSON string
        nullIfEmpty: Sets fields to null if they contain empty array or object
        indent: The level of indentation used to output the JSON string

    Returns:
        A string in JSON format.
    """

    def isEmpty(o):
        if o == None: return True

        # Dictionaries
        if isinstance(o, dict):
            return all(x == None for x in o.values())

        # JSON Objects
        if issubclass(type(o), JSONObject):
            for k in o._json_properties.keys():
                if not isEmpty(getattr(o, k)): return False
            return True

        # Lists
        if isinstance(o, list):
            if not o: return True # Check for empty list
            for v in o:
                if not isEmpty(v): return False
            return True

        return False


    def noneIfEmpty(o):
        # Dictionaires
        if isinstance(o, dict):
            for k, v in o.items():
                o[k] = noneIfEmpty(v)
            if isEmpty(o): return None

        # JSON Objects
        if not o == None and issubclass(type(o), JSONObject):
            for k in o._json_properties.keys():
                setattr(o, k, noneIfEmpty(getattr(o, k)))
            if isEmpty(o): return None

        # Lists
        if isinstance(o, list):
            for i in range(len(o)):
                o[i] = noneIfEmpty(o[i])
            if excludeNull: o = [i for i in o if i is not None]
            if isEmpty(o): return None

        return o


    class Encoder(JSONEncoder):
        def default(self, o):
            if not excludeNull and not nullIfEmpty: return o.__dict__

            items = copy.deepcopy(o.__dict__)

            if nullIfEmpty:
                for k, v in items.items():
                    items[k] = noneIfEmpty(v)

            if excludeNull:
                filtered = {k: v for k, v in items.items() if v is not None}
                items.clear()
                items.update(filtered)

            return items

    return json.dumps(obj, indent=indent, cls=Encoder)


def from_json(jsonString:str, cls:JSONObject) -> JSONObject:
    """
    Convert a JSON string into a JSONObject class instance.

    Args:
        json_string: The JSON string that will populate the object
        cls: Name of the class used by the return object

    Returns:
        A populated JSONObject class instance.
    """

    if jsonString == "null": return None

    if not issubclass(cls, JSONObject):
        raise Exception('Unable to populate JSON object : classType is not child of JSONObject : class=' + cls.__name__)

    obj = cls()
    jsonDict = json.loads(jsonString)

    if not hasattr(obj, '_json_properties'):
        raise Exception('Unable to populate JSON object : Class definition missing _json_properties')

    for key in jsonDict.keys():
        if not hasattr(obj, key):
            raise Exception('Unable to populate JSON object : Missing class memeber : key=' + key)

        # JSON Object
        prop = obj.property_type(key)
        if issubclass(prop, JSONObject):
            setattr(obj, key, from_json(json.dumps(jsonDict[key]), prop))
            continue

        # JSON List
        if isinstance(jsonDict[key], list):
            listtype = obj.property_type(key, True)

            if not listtype == None and issubclass(listtype, JSONObject):
                setattr(obj, key, [])
                for i in range(len(jsonDict[key])):
                    getattr(obj, key).append(from_json(json.dumps(jsonDict[key][i]), listtype))
                continue

            setattr(obj, key, jsonDict[key])
            continue

        # Everything else
        setattr(obj, key, jsonDict[key])

    return obj

if __name__ == "__main__":

    from objects.jsonobject import JSONObject

    class ChildObject(JSONObject):
        _json_properties = {
            'childName'     : str,
            'childLast'     : str,
            'age'           : int
        }

        def __init__(self):
            super(ChildObject, self).__init__()

    class ParentObject(JSONObject):
        _json_properties = {
            'firstName'     : str,
            'lastName'      : str,
            'children'      : [ChildObject],
        }

        def __init__(self):
            super(ParentObject, self).__init__()

    parent = ParentObject()
    parent.firstName = "Sam"
    parent.lastName = "Maxwell"

    parent.children = [ChildObject(), ChildObject(), ChildObject()]
    children = parent.children

    children[0].childName = "Billy"
    children[0].childLast = "Maxwell"
    children[0].age = 10

    children[1].childName = "Sally"
    children[1].childLast = "Maxwell"


    parentString = to_json(parent, indent=4)
    print(parentString)

    print('\n----------------------------------\n')

    parentString = to_json(parent, indent=4, excludeNull=True, nullIfEmpty=True)
    print(parentString)

    print('\n----------------------------------\n')

    response = from_json(parentString, ParentObject)
    print(vars(response))
    print()


# TODO:
#   - Mixed array types
#   - Check for duplicate JSON properties in class
#   - Proper type conversion