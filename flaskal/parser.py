from model import Column, Model

class ColumnParser(object):
    def __init__(self):
        self.simple_kv = ['name', 'type', 'foreign_key']
        self.bool_kv = ['primary_key', 'allowed_in_create', 'nullable']
        self.bool_values = ['True', 'False']
        self.kv_separator = '='

    def set_bool(self, column, field, val):
        if val not in self.bool_values:
            raise ValueError("not a valid bool: %s" % val)
        setattr(column, field, val == 'True')

    def parse(self, string):
        column = Column()
        for part in string.split():
            key, val = part.split(self.kv_separator)
            if key in self.simple_kv:
                setattr(column, key, val)
            elif key in self.bool_kv:
                self.set_bool(column, key, val)
            elif key == 'required':
                self.set_bool(column, 'required_in_create', val)
            else:
                raise ValueError("Unknown field: %s" % key)
        return column

    def parse_multiple(self, strings):
        return [ self.parse(string) for string in strings ] 

class ModelParser(object):
    def __init__(self):
        self.column_parser = ColumnParser()

    def parse(self, name, dict):
        model = Model(name)
        for key, value in dict.iteritems():
            if key in ['rest', 'table', 'relationships']:
                setattr(model, key, value)
            if key == 'columns':
                model.columns = self.column_parser.parse_multiple(value)
        return model

    def parse_multiple(self, dictionary):
        return [ self.parse(name, dict) for name, dict in 
                dictionary.iteritems()]
