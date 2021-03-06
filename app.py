import os
import boto3

from chalice import Chalice

from chalicelib.auth import get_jwt_token
from chalicelib.db import InMemoryTodoDB, DynamoDBTodo

app = Chalice(app_name='helloworld')
app.debug = True
_DB = None
_USER_DB = None


def get_app_db():
    global _DB
    if _DB is None:
        _DB = DynamoDBTodo(
            boto3.resource('dynamodb').Table(os.environ['APP_TABLE_NAME'])
        )
    return _DB


def get_users_db():
    global _USER_DB
    if _USER_DB is None:
        _USER_DB = boto3.resource('dynamodb').Table(
            os.environ['USERS_TABLE_NAME']
        )
    return _USER_DB


@app.route('/todos', methods=['GET'])
def get_todos():
    return get_app_db().list_items()


@app.route('/todos', methods=['POST'])
def add_new_todo():
    body = app.current_request.json_body
    return get_app_db().add_item(
        description=body['description'],
        metadata=body.get('metadata')
    )


@app.route('/todos/{uid}', methods=['GET'])
def get_todo(uid):
    return get_app_db().get_item(uid)


@app.route('/todos/{uid}', methods=['DELETE'])
def delete_todo(uid):
    return get_app_db().delete_item(uid)


@app.route('/todos/{uid}', methods=['PUT'])
def update_todo(uid):
    body = app.current_request.json_body
    get_app_db().update_item(
        uid,
        description=body.get("description"),
        state=body.get("state"),
        metadata=body.get("metadata"),
    )


@app.route('/login', methods=['POST'])
def test_db():
    body = app.current_request.json_body
    record = get_users_db().get_item(
        Key={'username': body['username']}
    )['Item']
    jwt_token = get_jwt_token(
        body['username'], body['password'], record
    )
    return {'token': jwt_token.decode()}
