from marshmallow import Schema, fields


class UserSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)


class ToDoSchema(Schema):
    todo_id = fields.Integer(required=False)
    title = fields.String(required=True)
    description = fields.String()
    done = fields.Boolean(load_only=True)


class ToDoIdSchema(Schema):
    title = fields.Integer(required=True)
