code = """
import os
import sys
import json

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
 
from flask import Flask, g, request
from flask.ext.restful import Resource
from common import app, api, Base, Controller

{code}

def main():
    app.debug = app.config['DEBUG']
    app.run(host='0.0.0.0', threaded=True)

if __name__ == '__main__':
    main()

"""

#####################
# SQL ALCHEMY MODEL #
#####################

base_model = """
class {name}(Base):
    __tablename__ = '{table}'
    restful = '{rest}'
    allowed_in_create = [{allowed_in_create}]
    required_in_create = [{required_in_create}]
    {columns}
"""

######################
# SQL ALCHEMY COLUMN #
######################
primary_key = 'primary_key=True'
nullable    = 'nullable=False'
foreign_key = "ForeignKey('%s')"
column      = "%s = Column(%s)"
allowed_in_create = "allowed_in_create = [%s]"
required_in_create = "required_in_create = [%s]"

#########################
# RESOURCE & CONTROLLER #
#########################

single_resource = """
class Single{name}Resource(Resource):
    def get(self, id):
        return {name}Controller().get_one(g.db, id)
"""

multi_resource = """
class {name}Resource(Resource):
    def get(self):
        return {name}Controller().get_all(g.db)
    def post(self):
        payload = json.loads(request.data)
        return {name}Controller().create_from_dict(g.db, payload)
"""

controller = """
class {name}Controller(Controller):
    def __init__(self):
        super({name}Controller, self).__init__({name})
"""

