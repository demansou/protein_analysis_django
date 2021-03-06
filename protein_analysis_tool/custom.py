import hashlib

"""
class Singleton(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance
"""


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def file_hasher(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as fs:
        buf = fs.read()
        hasher.update(buf)
    return hasher.hexdigest()


def large_file_hasher(file_path):
    hasher = hashlib.md5()
    BLOCKSIZE = 65536
    with open(file_path, 'rb') as fs:
        buf = fs.read(BLOCKSIZE)
        while buf:
            hasher.update(buf)
            buf = fs.read(BLOCKSIZE)
    return hasher.hexdigest()
