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
def get_all_campers():
    if request.method == 'GET':
        campers = Camper.query.all()
        data = [c.to_dict(rules=('-signups',)) for c in campers]
        return data, 200
    else:
        data = request.json
        new_camper = Camper(
            name=data.get('name'),
            age=data.get('age')
        )
        db.session.add(new_camper)
        db.session.commit()

        return new_camper.to_dict(), 201

@app.route('/campers/<int:id>', methods=['GET', 'PATCH'])
def get_camper_by_id(id):
    camper = Camper.query.filter(
        Camper.id == id
    ).one_or_none()

    if camper is None:
        return {'error': 'camper not found'}, 404
    
    if request.method == 'PATCH':
        data = request.json
        for field in data:
            # camper.field = data[field]
            setattr(camper, field, data[field])
        db.session.add(camper)
        db.session.commit()

    return camper.to_dict(), 200

@app.route('/activities/<int:id>', methods=['DELETE'])
def get_activities_by_id(id):
    activity = Activity.query.filter(
        Activity.id == id
    ).one_or_none()

    db.session.delete(activity)
    db.session.commit()

    return {}, 200


if __name__ == '__main__':
    app.run(port=5555, debug=True)
