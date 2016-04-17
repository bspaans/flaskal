from hamcrest import *
from flaskal.model import Column
from flaskal.parser import ColumnParser
import unittest

class ColumnParserTest(unittest.TestCase):
    def test_parser_name_type(self):
        c = ColumnParser()
        result = c.parse("name=test type=integer")
        assert_that(result.name, equal_to("test"))
        assert_that(result.type, equal_to('integer'))

    def test_parser_primary_key(self):
        c = ColumnParser()
        result = c.parse("primary_key=True")
        assert_that(result.primary_key, equal_to(True))
        result = c.parse("primary_key=False")
        assert_that(result.primary_key, equal_to(False))
        with self.assertRaises(ValueError):
            c.parse('primary_key=')
        with self.assertRaises(ValueError):
            c.parse('primary_key=0')
        with self.assertRaises(ValueError):
            c.parse('primary_key=false')

    def test_parser_nullable(self):
        c = ColumnParser()
        result = c.parse("nullable=True")
        assert_that(result.nullable, equal_to(True))
        result = c.parse("nullable=False")
        assert_that(result.nullable, equal_to(False))
        with self.assertRaises(ValueError):
            c.parse('nullable=')
        with self.assertRaises(ValueError):
            c.parse('nullable=0')
        with self.assertRaises(ValueError):
            c.parse('nullable=false')

    def test_parser_allowed_in_create(self):
        c = ColumnParser()
        result = c.parse("allowed_in_create=True")
        assert_that(result.allowed_in_create, equal_to(True))
        result = c.parse("allowed_in_create=False")
        assert_that(result.allowed_in_create, equal_to(False))
        with self.assertRaises(ValueError):
            c.parse('allowed_in_create=')
        with self.assertRaises(ValueError):
            c.parse('allowed_in_create=0')
        with self.assertRaises(ValueError):
            c.parse('allowed_in_create=false')

    def test_parser_required(self):
        c = ColumnParser()
        result = c.parse("required=True")
        assert_that(result.required_in_create, equal_to(True))
        result = c.parse("required=False")
        assert_that(result.required_in_create, equal_to(False))
        with self.assertRaises(ValueError):
            c.parse('required=')
        with self.assertRaises(ValueError):
            c.parse('required=0')
        with self.assertRaises(ValueError):
            c.parse('required=false')

    def test_parser_fails_on_unknown_fields(self):
        c = ColumnParser()
        with self.assertRaises(ValueError):
            c.parse('unknown=false')

    def test_parser_default(self):
        c = ColumnParser()
        result = c.parse('default=10')
        assert_that(result.default, equal_to('10'))
