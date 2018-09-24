from flask import Flask, request
from flask_restplus import Resource, Api, fields
from .models import DBSession, User, ToDo
from sqlalchemy.exc import SQLAlchemyError
from .marshmallow import UserSchema, ToDoSchema
from marshmallow import ValidationError
from .config import config

app = Flask(__name__)
api = Api(app)

app.config.from_object(config['default'])

# Swagger fields
register_post = api.model('Create New User', {
    'username': fields.String(example='user'),
    'password': fields.String(example='pass'),
})

login_post =  api.model('Login', {
    'username': fields.String(example='user'),
    'password': fields.String(example='pass'),
})

todo_post = api.model('Create New Task', {
    'title': fields.String(example='To do something...'),
    'description': fields.String(example='Some description'),
    'done': fields.Boolean(example=False),
})


@api.errorhandler
def default_error_handler(error):
    '''Default error handler'''
    return {'message': str(error)}, getattr(error, 'code', 500)


@api.route('/register')
class RegisterPost(Resource):
    @api.expect(register_post)
    def post(self):
        json_data = request.get_json()
        if not json_data or not isinstance(json_data, dict):
            return {'message': 'No input data provided'}, 400  # Bad Request

        # Validate and deserialize input
        try:
            data = UserSchema().load(json_data)
        except ValidationError as err:
            return {'error': err.messages}, 422  # Unprocessable Entity

        db_session = DBSession()
        try:
            current_user = User.filter_by_username(data['username'], db_session)
            if current_user:
                return {'message': f'USER ALREADY EXISTS'}, 200  # OK
            else:
                new_user = User(data)
                db_session.add(new_user)
                db_session.commit()
                return {'message': f'USER ADDED'}, 200  # OK
        except SQLAlchemyError as err:
            return {'error': str(err)}, 500  # Internal Server Error
        finally:
            db_session.close()


@api.route('/login')
class LoginPost(Resource):
    @api.expect(login_post)
    def post(self):
        json_data = request.get_json()
        if not json_data or not isinstance(json_data, dict):
            return {'message': 'No input data provided'}, 400  # Bad Request

        # Validate and deserialize input
        try:
            data = UserSchema().load(json_data)
        except ValidationError as err:
            return {'error': err.messages}, 422  # Unprocessable Entity

        db_session = DBSession()
        try:
            current_user = User.filter_by_username(data['username'], db_session)
            if current_user:
                return {'message': f'You are LOGGED IN as {data["username"]}'}, 200, \
                       {'Set-Cookie': f'token={data["username"]}'}
        except SQLAlchemyError as err:
            return {'error': str(err)}, 500
        finally:
            db_session.close()
        return {'message': 'Could not verify your login!'}, 401


@api.route('/logout')
class Logout(Resource):
    def get(self):
        return {'message': 'logout'}, 200, {'Set-Cookie': 'token=None'}  # OK


@api.route('/users')
class UsersGet(Resource):
    def get(self):
        """Get all users by list for Admin."""
        db_session = DBSession()
        try:
            users = db_session.query(User).all()
        except SQLAlchemyError as err:
            return {'error': str(err)}, 500  # Internal Server Error
        finally:
            db_session.close()
        return {'users': UserSchema(many=True).dump(users)}, 200  # OK


@api.route('/todo')
class Todo(Resource):
    @api.expect(todo_post)
    def post(self):
        """Post task."""
        json_data = request.get_json()
        if not json_data or not isinstance(json_data, dict):
            return {'message': 'No input data provided'}, 400  # Bad Request

        # Validate and deserialize input
        try:
            data = ToDoSchema().load(json_data)
        except ValidationError as err:
            return {'error': err.messages}, 422  # Unprocessable Entity

        db_session = DBSession()
        try:
            current_user = User.filter_by_username(request.cookies.get('token'), db_session)
            if current_user:
                new_todo = ToDo(current_user.id, data)
                db_session.add(new_todo)
                db_session.commit()
            else:
                return {'message': 'You need logged in'}, 403  # FORBIDDEN
        except SQLAlchemyError as err:
            return {'error': str(err)}, 500  # Internal Server Error
        finally:
            db_session.close()
        return {'message': f'TODO ADDED'}, 200  # OK

    def get(self):
        """Get tasks."""
        db_session = DBSession()
        try:
            current_user = User.filter_by_username(request.cookies.get('token'), db_session)
            if current_user:
                todo = db_session.query(ToDo).all()
                return {'todo': ToDoSchema(many=True).dump(todo)}, 200  # OK
            else:
                return {'message': 'You need logged in'}, 403  # FORBIDDEN
        except SQLAlchemyError as err:
            return {'error': str(err)}, 500  # Internal Server Error
        finally:
            db_session.close()


@api.route('/todo/<int:todo_id>')
class Todoid(Resource):
    def delete(self, todo_id):
        """Delete task."""
        db_session = DBSession()
        try:
            current_user = User.filter_by_username(request.cookies.get('token'), db_session)
            if current_user:
                db_session.query(ToDo).filter(ToDo.user_id == current_user.id).filter(ToDo.todo_id == todo_id).delete()
                db_session.commit()
                return {'message': f'TODO DELETED'}, 200  # OK
            else:
                return {'message': 'You need logged in'}, 403  # FORBIDDEN
        except SQLAlchemyError as err:
            return {'error': str(err)}, 500  # Internal Server Error
        finally:
            db_session.close()

    @api.expect(todo_post)
    def put(self, todo_id):
        """Modify task."""
        json_data = request.get_json()
        if not json_data or not isinstance(json_data, dict):
            return {'message': 'No input data provided'}, 400  # Bad Request

        # Validate and deserialize input
        try:
            data = ToDoSchema().load(json_data)
        except ValidationError as err:
            return {'error': err.messages}, 422  # Unprocessable Entity

        db_session = DBSession()
        try:
            current_user = User.filter_by_username(request.cookies.get('token'), db_session)
            if current_user:
                current_todo = ToDo.filter_by_id(todo_id, db_session)
                for key in data.keys():
                    current_todo.__setattr__(key, data[key])
                    print(key, data[key])
                db_session.add(current_todo)
                db_session.commit()
                return {'message': f'TODO UPDATED'}, 200  # OK
            else:
                return {'message': 'You need logged in'}, 403  # FORBIDDEN
        except SQLAlchemyError as err:
            return {'error': str(err)}, 500  # Internal Server Error
        finally:
            db_session.close()
