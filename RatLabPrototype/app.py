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
    #updateAges()
    pairing()
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


# CASE 1: num_paired_rats is even, so the user is swapping existing pairs
#           ACTION: return an unrelated, currently paired rat
# CASE 2: num_paired_rats is odd, so the user needs to add a new rat to the colony
#           from the "spare" unpaired rats who have not been previously paired
#           ACTION: return an unrelated, unpaired rat
# in calling function, query DB for input_rat and pass that rat to this function
def pairing():
    
    
    #TODO: DELETE INPUT_RAT LINE ONCE THIS IS ACTUALLY BEING PASSED DATA
    input_data = "88M"
    
    datingPool = []
    
    # STEP 1: check number of paired rats to determine what case we're in:
    num_paired_rats = db.session.execute(
        db.select(Rat).where(
            (Rat.manner_of_death=="Alive") & (Rat.current_partner != "00X")
        )
    ).all()
    
    # STEP 2: query for input_rat's information and separate out the parents and grandparents names
    input_rat = Rat.query.get(input_data)
    ancestor_names = [input_rat.sire, input_rat.dam, input_rat.pgsire, input_rat.pgdam, input_rat.mgsire, input_rat.mgdam]  
    input_rat_ancestor_birthdays = []
    
    # STEP 3: handle ENEN rats because they're a special case.  They can breed with anyone, 
    # including other ENEN rats, so birthdate checking to rule out common ancestors is unnecessary
    # for them
    if(input_rat.sire == "EN" and input_rat.dam == "EN"):
        #case 1: query for rats who are paired, excluding the rat’s current partner if known (! UNK and !00X)
        if((len(num_paired_rats) % 2) == 0 ):
            datingPool = db.session.execute(
                db.select(Rat).where(
                    (Rat.sex != input_rat.sex) &
                    (Rat.manner_of_death == "Alive") & 
                    (Rat.current_partner != "00X") & # narrow search to only paired rats
                    (Rat.current_partner != input_rat.current_partner) & # narrow search to exclude input_rat's current partner                    
                    (Rat.age_months >= 3) &
                    #(Rat.num_litters_with_defects <= 2 ) #TODO: uncomment this line when using full database
                    (Rat.sire != "XX") &
                    (Rat.dam != "XX")
                )
            ).all()
        else:
            # case 2: query for rats who aren't paired
            datingPool = db.session.execute(
                db.select(Rat).where(
                    (Rat.sex != input_rat.sex) &
                    (Rat.manner_of_death == "Alive") & 
                    (Rat.current_partner == "00X") & # search for unpaired rats
                    (Rat.age_months >= 3) &
                    #(Rat.num_litters_with_defects <= 2 ) #TODO: uncomment this line when using full database
                    (Rat.sire != "XX") &
                    (Rat.dam != "XX")
                )
            ).all()
        #TODO: this might be excessive, but order rats in datingPool by highest number of XX 
        # ancestors first before returning?
    
    # STEP 4: handle colony rats.  Need to compare birthdates of input_rat and their ancestors
    # to the birthdates of potential mates and their ancestors to exclude related rats
    else:
       # STEP 4a: get the ancestor's birthdates. Include EN b/c grandparents could be EN
        for ancestor in ancestor_names:
            if(ancestor != "XX" and ancestor != "5X" and ancestor != "EN"):
                data = Rat.query.get(ancestor)
                input_rat_ancestor_birthdays.append(data.birthdate)
                
        #STEP 4b: generate dating pool based on which case we're in
        
        # case 1, query for rats who are paired.  exclude current partner.  
        # include input_rat's birthdate because these are colony rats and checking != birthdate
        # is a quick way to exclude siblings born on the same day 
        # this isn't necessarily all siblings, but it helps narrow down the dating pool
        if((len(num_paired_rats) % 2) == 0 ):
            datingPool = db.session.execute(
                db.select(Rat.rat).where(
                    (Rat.sex != input_rat.sex) &
                    (Rat.manner_of_death == "Alive") & 
                    (Rat.current_partner != "00X") & # narrow search to only paired rats
                    (Rat.current_partner != input_rat.current_partner) & # narrow search to exclude input_rat's current partner                    
                    (Rat.age_months >= 3) &
                    #(Rat.num_litters_with_defects <= 2 ) #TODO: uncomment this line when using full database
                    (Rat.sire != "XX") &
                    (Rat.dam != "XX") &
                    (Rat.birthdate != input_rat.birthdate)
                )
            ).all()
            
        else: # case 2
            datingPool = db.session.execute(
                db.select(Rat.rat_number, Rat.sire, Rat.dam, Rat.pgsire, Rat.pgdam, Rat.mgsire, Rat.mgdam).where(
                    (Rat.sex != input_rat.sex) &
                    (Rat.manner_of_death == "Alive") & 
                    (Rat.current_partner == "00X") & # search for unpaired rats
                    (Rat.age_months >= 3) &
                    #(Rat.num_litters_with_defects <= 2 ) #TODO: uncomment this line when using full database
                    (Rat.sire != "XX") &
                    (Rat.dam != "XX") &
                    (Rat.birthdate != input_rat.birthdate)
                )
            ).all()
            
        # print("rat number: " + input_rat.rat_number)     
        # print("datingPool: ")
        # for rat in datingPool:
        #     print(rat.rat_number)
      
        finalDatingPool = []
        
        for rat in datingPool:
            finalDatingPool.append(rat.rat_number)
            potential_partner_ancestors = [rat.sire, rat.dam, rat.pgsire, rat.pgdam, rat.mgsire, rat.mgdam]
            #print(rat.rat_number + " ancestors: " + str(potential_partner_ancestors))
            for ancestor in potential_partner_ancestors:
                if(ancestor != "XX" and ancestor != "5X" and ancestor != "EN"):
                    partner_ancestor_birthdate = Rat.query.get(ancestor).birthdate
                    #print(ancestor + " " + str(partner_ancestor_birthdate))
                    if(partner_ancestor_birthdate in input_rat_ancestor_birthdays):
                        #print(rat.rat_number + " rejected because " + ancestor + " birthdate " + str(partner_ancestor_birthdate))
                        finalDatingPool.remove(rat.rat_number)
                        break
                            
        #print("finalDatingPool: " + str(finalDatingPool))    
    return datingPool



# updates ages, rat's age in months
# TODO make this skip rats that are dead 
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