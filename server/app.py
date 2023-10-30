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

@app.route('/campers', methods=['GET', 'POST'])
def all_campers():
    if request.method == 'GET':
        campers = Camper.query.all()

        # option 1: for loop
        # body = []
        # for camper in campers:
        #     body.append(camper.to_dict())

        # option 2: list comp
        body = [camper.to_dict(rules=('-signups',)) for camper in campers]
        
        return body, 200
    elif request.method == 'POST':
        data = request.get_json()
        new_camper = Camper(
            name=data.get('name'),
            age=data.get('age')
        )
        db.session.add(new_camper)
        db.session.commit()
        return new_camper.to_dict(rules=('-signups',)), 201

@app.route('/campers/<int:id>', methods=['GET', 'PATCH'])
def camper_by_id(id):
    camper = Camper.query.filter(Camper.id == id).first()

    if not camper:
        return {"error": "Camper not found"}, 404
    
    if request.method == 'GET':
        return camper.to_dict(), 200
    elif request.method == 'PATCH':
        data = request.get_json()
        for field in data:
            try:
                setattr(camper, field, data[field])
            except ValueError as e:
                return {"errors": [str(e)]}, 400
        db.session.add(camper)
        db.session.commit()
        return camper.to_dict(rules=('-signups',)), 200

@app.route('/activities', methods=['GET'])
def all_activities():
    acts = Activity.query.all()
    return [act.to_dict(rules=('-signups',)) for act in acts], 200

@app.route('/activities/<int:id>', methods=['DELETE'])
def activity_by_id(id):
    activity = Activity.query.filter(Activity.id == id).first()

    if not activity:
        return {"error": "Activity not found"}, 404
    
    db.session.delete(activity)
    db.session.commit()

    return {}, 200

@app.route('/signups', methods=['POST'])
def all_signups():
    data = request.get_json()
    new_signup = Signup(
        time = data.get('time'),
        camper_id=data.get('camper_id'),
        activity_id=data.get('activity_id')
    )
    db.session.add(new_signup)
    db.session.commit()
    return new_signup.to_dict(), 201


if __name__ == '__main__':
    app.run(port=5555, debug=True)
