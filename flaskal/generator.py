import templates

class CodeGenerator(object):
    def output_code(self, models):
        result = ""
        apis = []
        for m in models:
            result += m.generate_code_in_single_string() + "\n"
            apis.append(m.get_endpoints())
        for d in apis:
            for resource, endpoint in d.iteritems():
                result += "api.add_resource(%s, %s)" % \
                        (resource, endpoint) + "\n"
        return templates.code.format(code=result)
