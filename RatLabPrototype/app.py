import jinja2

from flask import Flask, request, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask
app = Flask(__name__)

db = SQLAlchemy()

#TODO: remove the charset at the end once stable
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://lauren:laurenpwd@capstone6.cs.kent.edu/rat_database?charset=utf8mb4"

db.init_app(app)

class Rat(db.Model):
    __tablename__ = 'rats'
    rat_number = db.Column(db.String, primary_key=True) 
    rat_name = db.Column(db.String)
    sex = db.Column(db.String)
    birthdate = db.Column(db.Date)
    weaned_date = db.Column(db.Date)
    last_paired_date = db.Column(db.Date)
    last_litter_date = db.Column(db.Date)
    num_times_paired = db.Column(db.Integer)
    num_litters = db.Column(db.Integer)
    date_added_to_colony = db.Column(db.Date)
    num_litters_with_defects = db.Column(db.Integer)
    experiment = db.Column(db.Integer)
    manner_of_death = db.Column(db.String)
    death_date = db.Column(db.Date)
    sire = db.Column(db.String)
    dam = db.Column(db.String)
    pgsire = db.Column(db.String)
    pgdam = db.Column(db.String)
    mgsire = db.Column(db.String)
    mgdam = db.Column(db.String)
    pg1sire = db.Column(db.String)
    pg1dam = db.Column(db.String)
    mg1sire = db.Column(db.String)
    mg1dam = db.Column(db.String)
    pg2sire = db.Column(db.String)
    pg2dam = db.Column(db.String)
    pg21sire = db.Column(db.String)
    pg21dam = db.Column(db.String)
    mg2sire = db.Column(db.String)
    mg2dam = db.Column(db.String)
    mg21sire = db.Column(db.String)
    mg21dam = db.Column(db.String)
    pg3sire = db.Column(db.String)
    pg3dam = db.Column(db.String)
    pg31sire = db.Column(db.String)
    pg31dam = db.Column(db.String)
    pg32sire = db.Column(db.String)
    pg32dam = db.Column(db.String)
    pg33sire = db.Column(db.String)
    pg33dam = db.Column(db.String)
    mg3sire = db.Column(db.String)
    mg3dam = db.Column(db.String)
    mg31sire = db.Column(db.String)
    mg31dam = db.Column(db.String)
    mg32sire = db.Column(db.String)
    mg32dam = db.Column(db.String)
    mg33sire = db.Column(db.String)
    mg33dam = db.Column(db.String)
    
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/search")
def search():
    
    query = db.session.execute(db.select(Rat).order_by(Rat.rat_number)).scalars()

    #print(query.all())
    # Whatever you do, do NOT run print(query.all()) before the return statement
    # that'll clear out the query variable or something, because then read.html 
    # will be blank
   
    return render_template("search.html", query = query)

@app.route("/reportdeath")
def reportDeath():
    return render_template("reportdeath.html")

# Routing to actually update the rat - user doesn't interact with this endpoint
@app.route("/enforcedeath", methods = ["POST", "GET"])
def enforceDeath():
        
    if request.method == "POST":
        # Get the data from the form and placed into a variable. 
        # input_data = request.form

        # # Search for the rat to change based on the rat id
        # #query = db.session.query(Rat).filter(Rat.rat_number == rat_number).one()  
        
        # # Write the changes to the database
        # query.rat_number = input_data["rat_number"]
        # query.rat_name = input_data["rat_name"]
        # db.session.commit()
        return redirect(url_for("reportdeath")) 
    else:
        return redirect(url_for("reportdeath"))


if __name__ == '__main__':
    app.run()