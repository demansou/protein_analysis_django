import hashlib


def file_hasher(file):
    hasher = hashlib.md5()
    with open(file, 'rb') as fs:
        buf = fs.read()
        hasher.update(buf)
    return hasher.hexdigest()


def large_file_hasher(file):
    hasher = hashlib.md5()
    BLOCKSIZE = 65536
    with open(file, 'rb') as fs:
        buf = fs.read(BLOCKSIZE)
        while buf:
            hasher.update(buf)
            buf = fs.read(BLOCKSIZE)
    return hasher.hexdigest()
