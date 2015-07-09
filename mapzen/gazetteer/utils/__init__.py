# https://pythonhosted.org/setuptools/setuptools.html#namespace-packages
__import__('pkg_resources').declare_namespace(__name__)

import shapely.geometry
import requests
import geojson
import json
import os
import os.path
import logging
import re

def id2fqpath(root, id):

    fname = id2fname(id)
    parent = id2path(id)

    root = os.path.join(root, parent)
    path = os.path.join(root, fname)

    return path

def id2fname(id):
    return "%s.geojson" % id

def id2path(id):

    tmp = str(id)
    parts = []
    
    while len(tmp) > 3:
        parts.append(tmp[0:3])
        tmp = tmp[3:]

    if len(tmp):
        parts.append(tmp)

    return "/".join(parts)

def generate_id():

    url = 'http://api.brooklynintegers.com/rest/'
    params = {'method':'brooklyn.integers.create'}

    try :
        rsp = requests.post(url, params=params)    
        data = rsp.content
    except Exception, e:
        logging.error(e)
        return 0

    # Note: this is because I am lazy and can't
    # remember to update the damn code to account
    # for PHP now issuing warnings for the weird
    # way it does regular expressions in the first
    # place... (20150623/thisisaaronland)
    
    try:
        data = re.sub(r"^[^\{]+", "", data)
        data = json.loads(data)
    except Exception, e:
        logging.error(e)
        return 0
    
    return data.get('integer', 0)

def ensure_bbox(f):

    if not f.get('bbox', False):
        geom = f['geometry']
        shp = shapely.geometry.asShape(geom)
        f['bbox'] = list(shp.bounds)

def crawl(root, **kwargs):

    validate = kwargs.get('validate', False)

    for (root, dirs, files) in os.walk(root):

        for f in files:
            path = os.path.join(root, f)
            path = os.path.abspath(path)

            if not path.endswith('geojson'):
                continue

            if validate:
                try:
                    fh = open(path, 'r')
                    data = geojson.load(fh)
                except Exception, e:
                    logging.error("failed to load %s, because %s" % (path, e))
                    continue

            yield path
    