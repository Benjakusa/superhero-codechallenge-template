# server/app.py
#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

class Heroes(Resource):
    def get(self):
        heroes = Hero.query.all()
        return make_response(jsonify([hero.to_dict() for hero in heroes]), 200)

api.add_resource(Heroes, '/heroes')

# Add to server/app.py
class HeroById(Resource):
    def get(self, id):
        hero = Hero.query.get(id)
        if not hero:
            return make_response(jsonify({"error": "Hero not found"}), 404)
        return make_response(jsonify(hero.to_dict_with_powers()), 200)

api.add_resource(HeroById, '/heroes/<int:id>')

# Add to server/app.py
class Powers(Resource):
    def get(self):
        powers = Power.query.all()
        return make_response(jsonify([power.to_dict() for power in powers]), 200)

api.add_resource(Powers, '/powers')

# Add to server/app.py
class PowerById(Resource):
    def get(self, id):
        power = Power.query.get(id)
        if not power:
            return make_response(jsonify({"error": "Power not found"}), 404)
        return make_response(jsonify(power.to_dict()), 200)

api.add_resource(PowerById, '/powers/<int:id>')

# Add to server/app.py
class PowerById(Resource):
    def get(self, id):
        power = Power.query.get(id)
        if not power:
            return make_response(jsonify({"error": "Power not found"}), 404)
        return make_response(jsonify(power.to_dict()), 200)
    
    def patch(self, id):
        power = Power.query.get(id)
        if not power:
            return make_response(jsonify({"error": "Power not found"}), 404)
        
        data = request.get_json()
        
        try:
            if 'description' in data:
                power.description = data['description']
            
            db.session.commit()
            return make_response(jsonify(power.to_dict()), 200)
        except ValueError as e:
            db.session.rollback()
            return make_response(jsonify({"errors": [str(e)]}), 400)
        except Exception:
            db.session.rollback()
            return make_response(jsonify({"errors": ["Validation errors"]}), 400)

# Add to server/app.py
class HeroPowers(Resource):
    def post(self):
        data = request.get_json()
        
        # Validate required fields
        if not all(k in data for k in ('strength', 'power_id', 'hero_id')):
            return make_response(jsonify({"errors": ["Missing required fields"]}), 400)
        
        # Check if hero and power exist
        hero = Hero.query.get(data['hero_id'])
        power = Power.query.get(data['power_id'])
        
        if not hero or not power:
            return make_response(jsonify({"errors": ["Hero or Power not found"]}), 404)
        
        try:
            hero_power = HeroPower(
                strength=data['strength'],
                hero_id=data['hero_id'],
                power_id=data['power_id']
            )
            
            db.session.add(hero_power)
            db.session.commit()
            
            # Return with hero and power data
            return make_response(jsonify(hero_power.to_dict_with_both()), 201)
            
        except ValueError as e:
            db.session.rollback()
            return make_response(jsonify({"errors": [str(e)]}), 400)
        except Exception:
            db.session.rollback()
            return make_response(jsonify({"errors": ["Validation errors"]}), 400)

api.add_resource(HeroPowers, '/hero_powers')

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"error": "Resource not found"}), 404)

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({"error": str(error)}), 400)

@app.errorhandler(500)
def internal_error(error):
    return make_response(jsonify({"error": "Internal server error"}), 500)

if __name__ == '__main__':
    app.run(port=5555, debug=True)