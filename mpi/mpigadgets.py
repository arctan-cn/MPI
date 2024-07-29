class Version:
    def __init__(self, version:str):
        version = version.split('.')
        for i in range(len(version)):
            version[i] = int(version[i])
        self.__version = version
    @property
    def version(self): return self.__version
    def __le__(self, version): return not self.__ge__(version)
    def __ge__(self, version):
        isType(version, Version)
        if self.__version == version.__version: return True
        for i in range(len(self.__version)):
            if i > len(version.version) - 1: return True
            if self.__version[i] < version.version[i]: return False
        for i in range(len(version.version)-len(self.__version)):
            if version.version[len(self.__version)+i]: return False
        return True
    def __repr__(self):
        result = []
        for i in self.__version: result.append(str(i))
        return ".".join(result)
class Counter:
    def __init__(self, *args, **kwargs):
        for key in args: setattr(self, key, 0)
        for key in kwargs: setattr(self, key, kwargs[key])
def isType(value, requiredType):
    if type(value) != requiredType: raise TypeError("Argument must be %s, not %s." % (requiredType.__name__, type(value).__name__))
def requireArgument(key, args, allowEmpty:bool=True, typeRequired=None):
    if not key in args: raise TypeError(f"\"{key}\" is required")
    if (not args[key]) and (not allowEmpty): raise TypeError("\"{key}\" cannot be empty ")
    if typeRequired and type(args[key]) != typeRequired: raise TypeError("\"{key}\" must be %s (not %s)" % (typeRequired.__name__, type(args[key]).__name__))