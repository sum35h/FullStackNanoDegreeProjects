import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app, resources={r"*": {"origins": "*"}})

'''
@TODO uncomment the following line to initialize the database
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES
'''
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks',methods=['GET'])
def fetch_drinks():
    try:
        drinks = Drink.query.all()
        print('len:',len(drinks))
        return jsonify({'success':True,
                        'drinks': [drink.short() for drink in drinks]}),200
    except Exception as e:
        print(e)
        abort(404)



'''
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def fetch_drinks_detail(payload):
    try:
        drinks = Drink.query.all()
    except:
        abort(404)
    return jsonify({'success':True, 'drinks':[drink.long() for drink in drinks]}),200


'''
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks',methods=['POST'])
@requires_auth('post:drinks')
def add_drink(payload):
    try:
        data = request.get_json()
        recipe=data.get('recipe')
        print(recipe,type(recipe))
        drink = Drink(title=data.get('title'),recipe=json.dumps(recipe))
        drink.insert()
        return jsonify({'success':True,'drinks' : [drink.long()]}),200
    except Exception as e:
        print(e)
        abort(400)

    


'''
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:id>',methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload,id):
    print(Drink.query.all())
    data=request.get_json()
    try:
        drink=None
        drink = Drink.query.filter(Drink.id==id).first()
        if drink is None:
                abort(404)
        if data.get('title'):
            title = data['title']
            drink.title = title
        if data.get('recipe'):
            getrecipe = data['recipe']
            recipe = [getrecipe]
            recipe = json.dumps(getrecipe)
            drink.recipe = recipe
        drink.update()
        drinks = [drink.long()]
        return jsonify({
            'success':True,
            'drinks':drinks
        })
    except Exception as e:
        print('error',e)
        abort(500)


'''
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:id>',methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload,id):
    try:
        drink = Drink.query.get(id)
        drink.delete()
        return jsonify({"success":True,"delete":id}),200
    except Exception as e:
        print('delete failed:',e)
        abort(404)

## Error Handling
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


@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({"success":False,
                    "error":404,
                    "message":"Resource Not Found"}),404

@app.errorhandler(AuthError)
def not_authenticated(auth_error):
    return jsonify({
        "success": False,
        "error": auth_error.status_code,
        "message": auth_error.error
    }), 401
