from drf_yasg2.generators import OpenAPISchemaGenerator



class TagOpenAPISchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, *args, **kwargs):
        schema = super().get_schema(*args, **kwargs)
        tags = [tag for path_key, path in schema.paths.items() for op in path.operations for tag in op[1].tags]
        schema.tags = [{'name': tag} for tag in tags]
        return schema
