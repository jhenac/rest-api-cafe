from flask import Flask, jsonify, render_template, request
#https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/
from flask_sqlalchemy import SQLAlchemy
#https://flask-marshmallow.readthedocs.io/en/latest/
from flask_marshmallow import Marshmallow
import random



app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)

##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

#https://flask-marshmallow.readthedocs.io/en/latest/#flask_marshmallow.sqla.SQLAlchemyAutoSchema
class CafeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Cafe

cafe_schema = CafeSchema()

@app.route("/")
def home():
    return render_template("index.html")


## HTTP GET - Read Record
@app.route("/random", methods=["GET"])
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    cafe = cafe_schema.dump(random_cafe)
    return jsonify({"cafe": cafe})

@app.route("/all", methods=["GET"])
def get_all_cafes():
    cafes = db.session.query(Cafe).all()
    all_cafes = []
    for cafe in cafes:
        each_cafe = cafe_schema.dump(cafe)
        all_cafes.append(each_cafe)
    return jsonify({"cafes": all_cafes})

@app.route("/search", methods=["GET"])
def find_cafes():
    query_location = request.args.get("loc").title()
    cafes = db.session.query(Cafe).filter_by(location=query_location).all()
    filtered_cafes = []
    for cafe in cafes:
        each_cafe = cafe_schema.dump(cafe)
        filtered_cafes.append(each_cafe)

    if filtered_cafes:
        return jsonify({"cafes_in_the_area": filtered_cafes})
    return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})


## HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def add_new_cafe():
    api_key = request.args.get("api_key")
    if api_key == "TopSecretAPIKey":
        new_cafe = Cafe(
            name=request.form.get("name"),
            map_url=request.form.get("map_url"),
            img_url=request.form.get("img_url"),
            location=request.form.get("loc"),
            seats=request.form.get("seats"),
            has_toilet=bool(request.form.get("toilet")),
            has_wifi=bool(request.form.get("wifi")),
            has_sockets=bool(request.form.get("sockets")),
            can_take_calls=bool(request.form.get("calls")),
            coffee_price=request.form.get("coffee_price"),
        )
        db.session.add(new_cafe)
        db.session.commit()
        return jsonify(response={"success:": "Successfully added the new cafe."})
    return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."})


# HTTP PUT/PATCH - Update Record
@app.route("/update_price/<int:cafe_id>", methods=["PATCH"])
def patch_new_price(cafe_id):
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        new_price = request.args.get("new_price")
        cafe.coffee_price = new_price
        db.session.commit()
        updated_cafe = cafe_schema.dump(cafe)
        return jsonify(response={"updated_cafe": updated_cafe}), 200
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404

# HTTP DELETE - Delete Record
@app.route("/report-closed/<cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        api_key = request.args.get("api_key")
        if api_key == "TopSecretAPIKey":
            db.session.delete(cafe)
            db.session.commit()
            return jsonify({"success": "Cafe successfully deleted."})
        else:
            return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."})
    return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."})



if __name__ == '__main__':
    app.run(debug=True)
