from hamcrest import *
from flaskal.model import Model, Column
import unittest

test_controller = """
class TestController(Controller):
    def __init__(self):
        super(TestController, self).__init__(Test)
"""

test_single_resource = """
class SingleTestResource(Resource):
    def get(self, id):
        return TestController().get_one(g.db, id)
"""

test_multi_resource = """
class TestResource(Resource):
    def get(self):
        return TestController().get_all(g.db)
    def post(self):
        payload = json.loads(request.data)
        return TestController().create_from_dict(g.db, payload)
"""

test_alchemy_model = """
class Test(Base):
    __tablename__ = 'tbl'
    restful = '/api/test/'
    allowed_in_create = []
    required_in_create = []
    
"""

test_alchemy_model2 = """
class Test(Base):
    __tablename__ = 'tbl'
    restful = '/api/test/'
    allowed_in_create = ['test']
    required_in_create = []
    test = Column(Integer)
"""

test_alchemy_model3 = """
class Test(Base):
    __tablename__ = 'tbl'
    restful = '/api/test/'
    allowed_in_create = ['test']
    required_in_create = ['test']
    test = Column(Integer)
"""

test_alchemy_model4 = """
class Test(Base):
    __tablename__ = 'tbl'
    restful = '/api/test/'
    allowed_in_create = []
    required_in_create = []
    person = relationship(Person)
"""

test_alchemy_model5 = """
class Test(Base):
    __tablename__ = 'tbl'
    restful = '/api/test/'
    allowed_in_create = ['test']
    required_in_create = ['test']
    test = Column(Integer)
    person = relationship(Person)
"""

class ModelTest(unittest.TestCase):

    def test_model_to_alchemy(self):
        m = Model('test')
        m.table = 'tbl'
        m.rest = '/api/test/'
        assert_that(m.to_alchemy(), equal_to(test_alchemy_model))

    def test_model_with_column_to_alchemy(self):
        m = Model('test')
        m.table = 'tbl'
        m.rest = '/api/test/'
        column = Column('test', 'integer')
        m.columns = [column]
        assert_that(m.to_alchemy(), equal_to(test_alchemy_model2))

    def test_model_with_required_column_to_alchemy(self):
        m = Model('test')
        m.table = 'tbl'
        m.rest = '/api/test/'
        column = Column('test', 'integer')
        column.required_in_create = True
        m.columns = [column]
        assert_that(m.to_alchemy(), equal_to(test_alchemy_model3))

    def test_model_with_relationship(self):
        m = Model('test')
        m.table = 'tbl'
        m.rest = '/api/test/'
        m.relationships = ['Person']
        assert_that(m.to_alchemy(), equal_to(test_alchemy_model4))

    def test_model_with_column_and_relationship(self):
        m = Model('test')
        m.table = 'tbl'
        m.rest = '/api/test/'
        m.relationships = ['Person']
        column = Column('test', 'integer')
        column.required_in_create = True
        m.columns = [column]
        assert_that(m.to_alchemy(), equal_to(test_alchemy_model5))

    def test_model_to_controller(self):
        assert_that(Model('test').to_controller(),
                    equal_to(test_controller))

    def test_model_to_multi_resource(self):
        assert_that(Model('test').to_multi_resource(), 
                    equal_to(test_multi_resource))

    def test_model_to_single_resource(self):
        assert_that(Model('test').to_single_resource(), 
                    equal_to(test_single_resource))

    def test_model_get_endpoints(self):
        m = Model('test')
        endpoints = m.get_endpoints()
        assert_that(endpoints, has_entry('TestResource',
                                         'Test.restful'))
        assert_that(endpoints, has_entry('SingleTestResource',
                                         'Test.restful + "<int:id>"'))
