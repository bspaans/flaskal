import yaml
import sys
from flaskal.model import Column, Model
from flaskal.parser import ColumnParser, ModelParser

template = """
import os
import sys
import json

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
 
from flask import Flask, g, request
from flask.ext.restful import Resource
from common import app, api, Base, Controller

{code}

if __name__ == '__main__':
    app.debug = app.config['DEBUG']
    app.run(host='0.0.0.0', threaded=True)

"""


def load_yaml(definition):
    return ModelParser().parse_multiple(definition)

def print_code(models):
    result = ""
    apis = []
    for m in models:
        result += m.generate_code_in_single_string() + "\n"
        apis.append(m.get_endpoints())
    for d in apis:
        for resource, endpoint in d.iteritems():
            result += "api.add_resource(%s, %s)" % (resource, endpoint) + "\n"
    print template.format(code=result)


if __name__ == '__main__':
    definition = yaml.load(open(sys.argv[1]))
    print_code(load_yaml(definition))
