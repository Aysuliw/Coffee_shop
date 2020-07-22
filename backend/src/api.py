import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

# ROUTES
'''
Endpoint :  GET /drinks
Permission :  public endpoint
Success Status Code : 200
Returns: List of drinks.
    It contains drink.short() data representation.
'''


@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()

    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    }),200


'''
Endpoint:  GET /drinks-detail
Permission:  'get:drinks-detail'
Success Status Code: 200
Returns: List of drinks.
    It contains drink.long() data representation.
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drinks = Drink.query.all()

    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in drinks]
    }), 200


'''
Endpoint: POST /drinks
Permission:  'post:drinks'
Success Status Code: 200
Returns: newly created drink.
    It contains drink.long() data representation.
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    body = request.get_json()

    new_title = body.get('title', None)
    new_recipe = body.get('recipe', None)

    try:
        drink = Drink(
            title=new_title,
            recipe=json.dumps(new_recipe)
        )
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200
    except BaseException:
        abort(422)


'''
Endpoint: PATCH /drinks/<id>
Permission: 'patch:drinks'
Success Status Code: 200
Returns: Updated drink.
    It contains drink.long() data representation.
'''


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    try:
        drink = Drink.query.get(id)
        if drink is None:
            abort(404)
        body = request.get_json()

        drink.title = body.get('title')
        drink.recipe = json.dumps(body.get('recipe'))
        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200
    except BaseException:
        abort(422)


'''
Endpoint: DELETE /drinks/<id>
Permission: 'delete:drinks'
Success Status Code: 200
Returns: id of deleted drink
'''


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()

        if drink is None:
            abort(404)
        drink.delete()

        return jsonify({
            'success': True,
            'delete': id
        }), 200
    except BaseException:
        abort(422)


# Error Handling

'''
Bad request(400)
'''


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


'''
Resource not found(404)
'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
Method not allowed(405)
'''


@app.errorhandler(405)
def not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
    }), 405


'''
Unprocessable entity(422)
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
Internal server error(500)
'''


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
    }), 500


'''
Error handler for AuthError
'''


@app.errorhandler(AuthError)
def auth_error(e):
    return jsonify(e.error), e.status_code
