from flask import Flask, g, url_for, request
from flask.ext.restful import Api, Resource
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json


DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
api = Api(app)


class NewBase(object):
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    def to_json(self):
        return json.dumps(self.to_dict())

class Controller(object):
    def __init__(self, cls):
        self.cls = cls
        self.allowed_in_create = []
        self.required_in_create = []

    def get_one(self, db, id):
        try:
            d = {"id": id}
            r = db.query(self.cls).filter_by(**d).one()
        except Exception, e:
            return "Not found", 404
        return r.to_dict(), 200

    def delete_one(self, db, id):
        try:
            r = db.query(self.cls).filter(self.cls.id == id).first()
        except Exception, e:
            return "Not found", 404
        db.delete(r)
        db.commit()
        return "OK", 200

    def delete_all(self, db, args):
        filter = self.build_filter(args)
        db.query(self.cls).filter_by(**filter).delete()
        db.commit()
        return "OK", 200

    def build_filter(self, multi_dict):
        queryable_columns = [ c.name for c in self.cls.__table__.columns ]
        filter = {}
        for key, val in multi_dict.iteritems():
            if key in queryable_columns:
                filter[key] = val
        return filter

    def get_all(self, db, args):
        filter = self.build_filter(args)
        return map(lambda s: s.to_dict(), 
                   db.query(self.cls).filter_by(**filter).all())

    def create_from_dict(self, db, payload):
        resource = self.cls()
        for key, v in payload.iteritems():
            if key in self.cls.allowed_in_create:
                setattr(resource, key, v)
        for key in self.cls.required_in_create:
            if key not in payload or payload[key] is None:
                return "Missing argument: " + key, 400
        return self.post_successful(db, resource)

    def post_successful(self, db, resource):
        try:
            db.add(resource)
            db.commit()
            return resource.to_dict(), 200
        except Exception, e:
            print e
            return 'No way', 400

 
@app.before_request
def before_request():
    # Create an engine that stores data in the local directory's
    # sqlalchemy_example.db file.
    engine = create_engine('sqlite:////tmp/flaskal.db')
     
    # Create all tables in the engine. This is equivalent to "Create Table"
    # statements in raw SQL.
    #Base.metadata.create_all(engine)

    Base.metadata.bind = engine

    DBSession = sessionmaker(bind=engine)
    g.db = DBSession()

@app.teardown_request
def teardown_request(exception):
    pass

class SitemapResource(Resource):
    def get(self):
        ignored_rules = ['/', '/static/<path:filename>']
        links = []
        for rule in app.url_map.iter_rules():
            if rule.rule not in ignored_rules:
                links.append(rule.rule)
        return {'links': links}

api.add_resource(SitemapResource, '/')
Base = declarative_base(cls=NewBase)
