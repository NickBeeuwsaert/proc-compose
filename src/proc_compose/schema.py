from colander import Boolean, Mapping, MappingSchema, SchemaNode

from .datatypes import ProcComposeConfig


class CommandsSchema(MappingSchema):
    def schema_type(self):
        return Mapping(unknown="preserve")


class ProcComposeSchema(MappingSchema):
    commands = CommandsSchema()
    # Should probably make colorama optional if this is going to be
    # an option
    colorize = SchemaNode(Boolean())

    def schema_type(self):
        return Mapping(unknown="raise")

    def deserialize(self, cstruct):
        appstruct = super().deserialize(cstruct)
        return ProcComposeConfig(**appstruct)


class PyProjectToolSchema(MappingSchema):
    # We only care about our data
    proc_compose = ProcComposeSchema(name="proc-compose")

    def deserialize(self, cstruct):
        appstruct = super().deserialize(cstruct)

        return appstruct["proc-compose"]


class PyProjectSchema(MappingSchema):
    tool = PyProjectToolSchema()

    def deserialize(self, cstruct):
        appstruct = super().deserialize(cstruct)

        return appstruct["tool"]
