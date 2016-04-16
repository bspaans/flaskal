import templates


class Column(object):
    def __init__(self, name = None, typ = None):
        self.name = name
        self.type = typ
        self.primary_key = False
        self.foreign_key = None
        self.nullable = True
        self.allowed_in_create = True 
        self.required_in_create = False

    def to_alchemy(self):
        if self.name is None or self.type is None:
            raise ValueError('Missing name and/or type in Column')
        args = [self.type.capitalize()]
        if self.primary_key:
            args.append(templates.primary_key)
        if not self.nullable:
            args.append(templates.nullable)
        if self.foreign_key is not None:
            args.append(templates.foreign_key % self.foreign_key)
        return templates.column % (self.name, ','.join(args))

    def __repr__(self):
        return self.to_alchemy()

class Model(object):
    def __init__(self, name):
        self.name = name
        self.rest = None
        self.table = None
        self.columns = []
        self.relationships = []

    def to_alchemy(self):
        lines = []
        allowed_in_create = []
        required_in_create = []
        for c in self.columns:
            lines.append(c.to_alchemy())
            if c.allowed_in_create:
                allowed_in_create.append("'%s'" % c.name)
            if c.required_in_create: 
                required_in_create.append("'%s'" % c.name)
        for r in self.relationships:
            lines.append("%s = relationship(%s)" % (r.lower(), r))
        return templates.base_model.format(
            name = self.name.capitalize(),
            table = self.table,
            rest = self.rest,
            allowed_in_create = ", ".join(allowed_in_create),
            required_in_create = ", ".join(required_in_create),
            columns = "\n    ".join(lines))

    def to_controller(self):
        return templates.controller.format(name = self.name.capitalize())

    def to_resources(self):
        return self.to_multi_resource() + self.to_single_resource()

    def to_multi_resource(self):
        return templates.multi_resource.format(name = self.name.capitalize())

    def to_single_resource(self):
        return templates.single_resource.format(name = self.name.capitalize())

    def generate_code_in_single_string(self):
        return self.to_alchemy() + "\n" + self.to_controller() + "\n" + self.to_resources()

    def get_endpoints(self):
        model = self.name.capitalize()
        return {"%sResource" % model: "%s.restful" % model, 
                "Single%sResource" % model:
                "%s.restful + \"<int:id>/\"" % model}

    def __repr__(self):
        return self.generate_code_in_single_string()
