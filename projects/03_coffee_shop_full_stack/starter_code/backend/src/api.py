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
uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
    implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks")
def get_drinks():
    drinks = Drink.query.all()
    drinks = [drink.short() for drink in drinks]

    return jsonify({
        'success': True,
        "drinks": drinks
    })

'''
    implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks-detail")
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drinks = Drink.query.all()
    drinks = [drink.long() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': drinks
    })

'''
    implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    body = request.get_json()
    if body is None:
      abort(400)

    title = body.get('title', None)
    recipe = body.get('recipe', None)

    if title is None or recipe is None:
        abort(400)

    recipe = json.dumps(recipe)
    drink = Drink(title=title, recipe=recipe)
    try:
        drink.insert()
        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    except:
        abort(422)


'''
    implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if drink is None:
        abort(404)

    body = request.get_json()
    if body is None:
      abort(400)

    title = body.get('title', None)
    if title is None:
        abort(400)

    drink.title = title

    try:
        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    except:
        abort(422)


'''
    implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if drink is None:
        abort(404)

    try:
        drink.delete()

        return jsonify({
            'success': True,
            'delete': drink_id
        })
    except:
        abort(422)

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
    implement error handler for 400
'''

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False, 
        "error": 400,
        "message": "bad request"
        }), 400

'''
    implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "resource not found"
        }), 404

'''
    implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
