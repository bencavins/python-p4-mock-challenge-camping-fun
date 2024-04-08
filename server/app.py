#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.get('/campers')
def get_all_campers():
    campers = Camper.query.all()
    return [camper.to_dict(rules=['-signups']) for camper in campers], 200

@app.post('/campers')
def post_camper():
    json_data = request.get_json()

    try:
        new_camper = Camper(
            name=json_data.get('name'),
            age=json_data.get('age')
        )
    except ValueError as e:
        return {"errors": ["validation errors"]}, 400

    db.session.add(new_camper)
    db.session.commit()

    return new_camper.to_dict(rules=['-signups']), 201

@app.get('/campers/<int:id>')
def get_camper_by_id(id):
    camper = Camper.query.filter(Camper.id == id).first()

    if not camper:
        return {"error": "Camper not found"}, 404
    
    return camper.to_dict(), 200

@app.patch('/campers/<int:id>')
def patch_camper_by_id(id):
    camper = Camper.query.filter(Camper.id == id).first()

    if not camper:
        return {"error": "Camper not found"}, 404
    
    json_data = request.get_json()

    # try:
    #     if 'name' in json_data:
    #         camper.name = json_data.get('name')
    #     if 'age' in json_data:
    #         camper.age = json_data.get('age')
    # except ValueError as e:
    #         return {"errors": ["validation errors"]}, 400

    for key, value in json_data.items():
        try:
            setattr(camper, key, value)
        except ValueError as e:
            return {"errors": ["validation errors"]}, 400
    
    db.session.add(camper)
    db.session.commit()

    return camper.to_dict(rules=['-signups']), 202

@app.delete('/activities/<int:id>')
def delete_activity_by_id(id):
    activity = Activity.query.filter(Activity.id == id).first()

    if not activity:
        return {"error": "Activity not found"}, 404

    db.session.delete(activity)
    db.session.commit()

    return {}, 204

if __name__ == '__main__':
    app.run(port=5555, debug=True)
