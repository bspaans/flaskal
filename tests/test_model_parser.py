from hamcrest import *
from flaskal.parser import ModelParser
import unittest

class ModelParserTest(unittest.TestCase):
    def test_parser_name_type(self):
        c = ModelParser()
        model = {}
        result = c.parse('test', model)
        assert_that(result.name, equal_to("test"))

    def test_parser_rest(self):
        c = ModelParser()
        model = {'rest': '/api/test/'}
        result = c.parse('test', model)
        assert_that(result.rest, equal_to("/api/test/"))

    def test_parser_table(self):
        c = ModelParser()
        model = {'table': 'tbl'}
        result = c.parse('test', model)
        assert_that(result.table, equal_to("tbl"))

    def test_parser_relationships(self):
        c = ModelParser()
        model = {'relationships': ['Person']}
        result = c.parse('test', model)
        assert_that(result.relationships, equal_to(["Person"]))

    def test_parser_columns(self):
        c = ModelParser()
        model = {'columns': ['name=test type=integer default=50']}
        result = c.parse('test', model)
        assert_that(result.columns[0].name, equal_to('test'))
        assert_that(result.columns[0].type, equal_to('integer'))
        assert_that(result.columns[0].default, equal_to('50'))

