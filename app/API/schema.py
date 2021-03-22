from drf_yasg2.app_settings import swagger_settings
from drf_yasg2.generators import OpenAPISchemaGenerator
from drf_yasg2.inspectors import FileFieldInspector, NotHandled, SwaggerAutoSchema



class TagOpenAPISchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, *args, **kwargs):
        schema = super().get_schema(*args, **kwargs)
        tags = [tag for path_key, path in schema.paths.items() for op in path.operations for tag in op[1].tags]
        schema.tags = [{'name': tag} for tag in tags]
        return schema



class AutoSchema(SwaggerAutoSchema):
    field_inspectors = swagger_settings.DEFAULT_FIELD_INSPECTORS

    def get_operation_id(self, operation_keys):
        operation_id = super().get_operation_id(operation_keys)
        return operation_id
        #return camelize(operation_id, uppercase_first_letter=False)
