import yaml
import sys

template = """
import os
import sys
import json

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from flask import Flask, g, Blueprint, request
from flask.ext.restful import Resource, Api
from common import app, api, Base, Controller

{code}
 
@app.before_request
def before_request():
    # Create an engine that stores data in the local directory's
    # sqlalchemy_example.db file.
    engine = create_engine('sqlite:///sqlalchemy_example.db')
     
    # Create all tables in the engine. This is equivalent to "Create Table"
    # statements in raw SQL.
    Base.metadata.create_all(engine)

    Base.metadata.bind = engine

    DBSession = sessionmaker(bind=engine)
    # A DBSession() instance establishes all conversations with the database
    # and represents a "staging zone" for all the objects loaded into the
    # database session object. Any change made against the objects in the
    # session won't be persisted into the database until you call
    # session.commit(). If you're not happy about the changes, you can
    # revert all of them back to the last commit by calling
    # session.rollback()
    session = DBSession()

    # Insert a Person in the person table
    new_person = Person(name='new person')
    session.add(new_person)
    session.commit()

    # Insert an Address in the address table
    new_address = Address(post_code='00000', person=new_person)
    session.add(new_address)
    g.db = session

    new_person.name = 'dick head'
    session.commit()
    print new_person.to_json()
    print new_address.to_json()

@app.teardown_request
def teardown_request(exception):
    pass

if __name__ == '__main__':
    app.debug = app.config['DEBUG']
    app.run(host='0.0.0.0', threaded=True)

"""

class Column(object):
    def __init__(self):
        self.name = None
        self.type = None
        self.primary_key = False
        self.foreign_key = None
        self.nullable = True
        self.allowed_in_create = True 
        self.required_in_create = False

    def to_alchemy(self):
        args = [self.type.capitalize()]
        if self.primary_key:
            args.append("primary_key=True")
        if not self.nullable:
            args.append("nullable=False")
        if self.foreign_key is not None:
            args.append("ForeignKey('%s')" % self.foreign_key)
        return "%s = Column(%s)" % (self.name, ", ".join(args))

    def __repr__(self):
        return self.to_alchemy()


class Model(object):
    def __init__(self, name):
        self.name = name
        self.rest = None
        self.table = None
        self.columns = []
        self.relationships = []

    def verify(self):
        return self.rest is not None and self.table is not None

    def add_columns(self, columns):
        self.columns += columns

    def add_relationships(self, relationships):
        self.relationships += relationships

    def to_alchemy_model(self):
        lines = ['__tablename__ = \'%s\'' % self.table,
                'restful = \'%s\'' % self.rest]
        allowed_in_create = []
        required_in_create = []
        for c in self.columns:
            lines.append(c.to_alchemy())
            if c.allowed_in_create:
                allowed_in_create.append("'%s'" % c.name)
            if c.required_in_create: 
                required_in_create.append("'%s'" % c.name)
        lines.append('allowed_in_create = [%s]' % ", ".join(allowed_in_create))
        lines.append('required_in_create = [%s]' % ", ".join(required_in_create))
        for r in self.relationships:
            lines.append("%s = relationship(%s)" % (r.lower(), r))
        return 'class %s(Base):\n    %s\n' % \
                (self.name, "\n    ".join(lines))

    def to_controller(self):
        model = self.name.capitalize()
        result = "class %sController(Controller):\n" % model
        result += "    def __init__(self):\n"
        result += "        super(%sController, self).__init__(%s)\n" % (model, model)
        return result

    def to_resources(self):
        model = self.name.capitalize()
        result = "class %sResource(Resource):\n" % model
        result += "    def get(self):\n"
        result += "        return %sController().get_all(g.db)\n" % model
        result += "    def post(self):\n"
        result += "        payload = json.loads(request.data)\n"
        result += "        return %sController().create_from_dict(g.db, payload)\n" % model
        result += "\nclass Single%sResource(Resource):\n" % model
        result += "    def get(self, id):\n"
        result += "        return %sController().get_one(g.db, id)\n" % model
        return result

    def generate_code_in_single_string(self):
        return self.to_alchemy_model() + "\n" + self.to_controller() + "\n" + self.to_resources()

    def get_endpoints(self):
        model = self.name.capitalize()
        return {"%sResource" % model: "%s.restful" % model, 
                "Single%sResource" % model:
                "%s.restful + \"<int:id>\"" % model}

    def __repr__(self):
        return self.generate_code_in_single_string()
        return '<%s %s %s: [%s]' % (self.name, self.rest, self.table, ", ".join(map(lambda s: str(s), self.columns)))


def load_columns(column_definitions):
    cols = []
    for c in column_definitions:
        column = Column()
        for part in c.split():
            key, val = part.split("=")
            if key in ['name', 'type', 'foreign_key']:
                setattr(column, key, val)
            if key in ['primary_key', 'allowed_in_create', 'nullable']:
                if val == 'True' or val == 'False':
                    setattr(column, key, val == 'True')
                else:
                    print "not a valid bool"
                    sys.exit(1)
            if key == 'required':
                if val == 'True' or val == 'False':
                    column.required_in_create = val == 'True'
                else:
                    print "not a valid bool"
                    sys.exit(1)
        cols.append(column)
    return cols

def load_yaml(definition):
    models = []
    for name, dict in definition.iteritems():
        model = Model(name)
        for key, value in dict.iteritems():
            if key in ['rest', 'table']:
                setattr(model, key, value)
            if key == 'columns':
                model.add_columns(load_columns(value))
            if key == 'relationships':
                model.add_relationships(value)
        models.append(model)
    return models

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


definition = yaml.load(open(sys.argv[1]))
print_code(load_yaml(definition))
