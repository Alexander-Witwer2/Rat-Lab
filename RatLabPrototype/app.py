import jinja2

from flask import Flask, request, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, BooleanField, SelectField, DateField
from wtforms.validators import DataRequired
from datetime import date

# Initialize Flask
app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')

db = SQLAlchemy()
db.init_app(app)

class Rat(db.Model):
    __tablename__ = 'rats'
    rat_number = db.Column(db.String, primary_key=True) 
    rat_name = db.Column(db.String)
    sex = db.Column(db.String)
    birthdate = db.Column(db.Date)
    last_paired_date = db.Column(db.Date)
    current_partner = db.Column(db.String)
    manner_of_death = db.Column(db.String)
    death_date = db.Column(db.Date)
    sire = db.Column(db.String)
    dam = db.Column(db.String)
    pgsire = db.Column(db.String)
    pgdam = db.Column(db.String)
    mgsire = db.Column(db.String)
    mgdam = db.Column(db.String)
    age_months = db.Column(db.Integer)
    
class EditRatForm(FlaskForm):
    sex = SelectField(choices=['Male', 'Female'])
    number = IntegerField()
    birthdate = DateField()
    dateLastPairing = DateField()
    dateLastLitter = DateField()
    numPairings = IntegerField()
    numlitters = IntegerField()
    dateAddedToColony = DateField()
    numLittersWithDefects = IntegerField()
    experiment = BooleanField(default="unchecked")
    sire = StringField('Sire')
    dam = StringField('Dam')
    update = SubmitField('Update')
    
class ReportDeathForm(FlaskForm):
    sex = SelectField(choices=['Male', 'Female'])
    number = IntegerField()
    deathDate = DateField()
    mannerOfDeath = SelectField(choices=['Euthanized', 'Unexpected'])
    submit = SubmitField('Yes')
    
@app.route("/")
def default():
    return render_template("dashboard.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/addrat")
def addRat():
    return render_template("addrat.html")

@app.route("/adduser")
def addUser():
    return render_template("adduser.html")

@app.route("/breedingpairs")
def breedingPairs():
    return render_template("breedingpairs.html")

@app.route("/editrecords", methods=['GET', 'POST'])
def editRecords():
    pairing()
    #abc = Rat.query.get("19F")
    #print(abc)
    # stmt = db.session.select(Rat.rat_name).where(Rat.rat_number == "19F")
    #stmt = Rat.select()
    
    form = EditRatForm()
    if(request.method == "POST"):
        print(form.data)
        return redirect(url_for("editRecords"))
    else:
        return render_template("editrecords.html", form=form)

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/recordtransfer")
def recordTransfer():
    return render_template("recordtransfer.html")

@app.route("/reportlitter")
def reportLitter():
    updateAges()
    #pairing()
    return render_template("reportlitter.html")

@app.route("/search")
def search():
    query = db.session.execute(db.select(Rat).order_by(Rat.rat_number)).scalars()
    #print(query.all())
    # Whatever you do, do NOT run print(query.all()) before the return statement
    # that'll clear out the query variable or something, because then read.html 
    # will be blank
    return render_template("search.html", query = query)

@app.route("/reportdeath", methods=['POST', 'GET'])
def reportDeath():
    form = ReportDeathForm()
    
    if(request.method == "POST"):       
        rat_number = str(form.number.data) + form.sex.data[0]
 
        rat = Rat.query.get(rat_number)
        rat.manner_of_death = form.mannerOfDeath.data
        rat.death_date = form.deathDate.data
        db.session.commit()
        
        #TODO: route to confirmation screen instead(?) definitely not search
        return redirect(url_for("search"))
    else:
        return render_template("reportdeath.html", form=form)

# updates ages, rat's age in months
# TODO make this skip rats that are dead once 
def updateAges():
    
    res = db.session.execute(db.select(Rat.rat_number, Rat.age_months)).all()
    for item in res:
        rat = Rat.query.get(item[0])
        age = 0
        deathDate = rat.death_date
        birthdate = rat.birthdate

        if deathDate.year == 1900:
            years_to_months =  (date.today().year - birthdate.year) * 12
            months = date.today().month - birthdate.month
            age = years_to_months + months
            print(str(rat.rat_number) + " " + str(age))
        else:
            years_to_months =  (deathDate.year - birthdate.year) * 12
            months = deathDate.month - birthdate.month
            age = years_to_months + months
            print(str(rat.rat_number) + " " + str(age))
        db.session.execute(db.update(Rat).where(Rat.rat_number == rat.rat_number).values(age_months = age))
        
    db.session.commit()

if __name__ == '__main__':
    app.run()