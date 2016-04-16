from hamcrest import *
from flaskal.model import Column
import unittest

class ColumnTest(unittest.TestCase):
    def test_to_alchemy(self):
        c = Column('test', 'integer')
        assert_that(c.to_alchemy(), equal_to('test = Column(Integer)'))

    def test_to_alchemy_string_type(self):
        c = Column('test', 'string(250)')
        assert_that(c.to_alchemy(), equal_to('test = Column(String(250))'))

    def test_primary_key_to_alchemy(self):
        c = Column('test', 'integer')
        c.primary_key=False
        assert_that(c.to_alchemy(), not_(contains_string("primary_key")))
        c.primary_key=True
        assert_that(c.to_alchemy(), contains_string("primary_key=True"))

    def test_not_nullable_to_alchemy(self):
        c = Column('test', 'integer')
        c.nullable=True
        assert_that(c.to_alchemy(), not_(contains_string("nullable")))
        c.nullable=False
        assert_that(c.to_alchemy(), contains_string("nullable=False"))

    def test_foreign_key_to_alchemy(self):
        c = Column('test', 'integer')
        c.foreign_key = None
        assert_that(c.to_alchemy(), not_(contains_string("ForeignKey")))
        c.foreign_key = 'tbl.id'
        assert_that(c.to_alchemy(), contains_string("ForeignKey('tbl.id')"))

    def test_to_alchemy_fails_if_name_is_missing(self):
        c = Column(typ='integer')
        with self.assertRaises(ValueError):
            c.to_alchemy()

    def test_to_alchemy_fails_if_type_is_missing(self):
        c = Column(name='test')
        with self.assertRaises(ValueError):
            c.to_alchemy()

