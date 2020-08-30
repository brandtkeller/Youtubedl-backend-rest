from configparser import ConfigParser
import sys


def config(filename='database.ini', section='postgresql'):
    db = {}

    # Need to add error checking logic here
    # We already exit if the length of sys.argv isn't >=5 
    db["host"] = sys.argv[1]
    db["database"] = sys.argv[2]
    db["user"] = sys.argv[3]
    db["password"] = sys.argv[4]

    return db