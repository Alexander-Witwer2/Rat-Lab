import jinja2

from flask import Flask, request, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, BooleanField, SelectField, DateField
from wtforms.validators import DataRequired
from datetime import date
import re

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
    weaned_date = db.Column(db.Date)
    last_paired_date = db.Column(db.Date)
    last_litter_date = db.Column(db.Date)
    num_times_paired = db.Column(db.Integer)
    num_litters = db.Column(db.Integer)
    date_added_to_colony = db.Column(db.Date)
    num_litters_with_defects = db.Column(db.Integer)
    experiment = db.Column(db.Integer)
    current_partner = db.Column(db.String)
    manner_of_death = db.Column(db.String)
    death_date = db.Column(db.Date)
    age_months = db.Column(db.Integer)
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

# input_data: string, the input rat's rat_number
# input_swapping_existing_pairs: bool
#   true if swapping existing pairs
#   false if adding new rat to colony
def pairing(input_data, input_swapping_existing_pairs):
    
    swapping_existing_pairs = input_swapping_existing_pairs
    datingPool = []
    finalDatingPool = []

    # STEP 1: query for input_rat's information and separate out the parents and grandparents names
    input_rat = Rat.query.get(input_data)
    input_rat_ancestor_names = [input_rat.sire, input_rat.dam, input_rat.pgsire, input_rat.pgdam, input_rat.mgsire, input_rat.mgdam]  
    
    # case 1: input_rat is spare rat, swapping = True
    if(swapping_existing_pairs == True and input_rat.current_partner == "00X"):
        return "ERROR: cannot swap existing pairs if the inputted rat is a spare rat"
    
    # case 2: input_rat is spare rat, swapping = False
    if(swapping_existing_pairs == False and input_rat.current_partner == "00X"):
        # not excluding XXXX and 5X5X rats in this query like I will do in the future because
        # at time of writing there may be 5X5X and XXXX rats who need a new partner from the spare rats
        # ok to cast len into bool because it'll be True if there are multiple vacancies in the colony
        # so if the user reports multiple colony rat deaths then wants to find partners from the 
        # spare rats, this will still behave properly
        colony_rats_without_partner = db.session.execute(
                db.select(Rat.rat_number, Rat.sire, Rat.dam, Rat.pgsire, Rat.pgdam, Rat.mgsire, Rat.mgdam).where(
                    (Rat.sex != input_rat.sex) &
                    (Rat.manner_of_death == "Alive") & 
                    (Rat.current_partner == "DEC") & # narrow search to only paired rats
                    (Rat.age_months >= 3) #&
                    #(Rat.num_litters_with_defects <= 2 ) #TODO: uncomment this line when using full database
                )
            ).all()
        does_colony_have_vacancy = bool(len(colony_rats_without_partner))
        if(does_colony_have_vacancy == False): # case 2a: no vacancy error
            return "ERROR: there are no unpaired rats to pair the given rat with"
        else: # case 2b and 2c
            # the user could've reported multiple deaths before looking for new partners
            # so there could be multiple rats in colony_rats_without_partner, need to check all of them
            finalDatingPool = compareBirthdates(input_rat_ancestor_names=input_rat_ancestor_names, datingPool=colony_rats_without_partner, input_rat=input_rat)
            if (len(finalDatingPool) == 0): # case 2b: no unrelated rats error
                return "ERROR: there are no unrelated rats that " + input_rat.rat_number + " can be paired with"
            else: # case 2c: succeeded in finding unrelated rat with DEC partner
                return finalDatingPool
            
    # case input_rat is a colony rat
    
    if(swapping_existing_pairs == True and input_rat.current_partner == "DEC"):
        return "ERROR: cannot swap existing pairs if input rat's partner is deceased, must add new rat to colony first"
    
    # handle ENEN rats because they're a special case.  They can breed with anyone, 
    # including other ENEN rats, so birthdate checking to rule out common ancestors is unnecessary
    # for them
    if(input_rat.sire == "EN" and input_rat.dam == "EN"):
        if(swapping_existing_pairs): # look for colony rat
            finalDatingPool = db.session.execute(
                db.select(Rat.rat_number).where(
                    (Rat.sex != input_rat.sex) &
                    (Rat.manner_of_death == "Alive") & 
                    (Rat.current_partner != "00X") & # narrow search to only paired rats
                    (Rat.rat_number != input_rat.current_partner) & # narrow search to exclude input_rat's current partner                    
                    (Rat.age_months >= 3) &
                    #(Rat.num_litters_with_defects <= 2 ) #TODO: uncomment this line when using full database
                    (Rat.sire != "XX") &
                    (Rat.dam != "XX") &
                    (Rat.sire != "5X") &
                    (Rat.dam != "5X")
                )
            ).all()
        else: # look for spare rat
            finalDatingPool = db.session.execute(
                db.select(Rat.rat_number).where(
                    (Rat.sex != input_rat.sex) &
                    (Rat.manner_of_death == "Alive") & 
                    (Rat.current_partner == "00X") & # search for unpaired rats
                    (Rat.age_months >= 3) &
                    #(Rat.num_litters_with_defects <= 2 ) #TODO: uncomment this line when using full database
                    (Rat.sire != "XX") &
                    (Rat.dam != "XX") &
                    (Rat.sire != "5X") &
                    (Rat.dam != "5X")
                )
            ).all()
    
    else: # handle non ENEN, so need to do birthdate checking
        if(swapping_existing_pairs): # query for colony rats
            datingPool = db.session.execute(
                db.select(Rat.rat_number, Rat.sire, Rat.dam, Rat.pgsire, Rat.pgdam, Rat.mgsire, Rat.mgdam).where(
                    (Rat.sex != input_rat.sex) &
                    (Rat.manner_of_death == "Alive") & 
                    (Rat.current_partner != "00X") & # narrow search to only paired rats
                    (Rat.rat_number != input_rat.current_partner) & # narrow search to exclude input_rat's current partner                    
                    (Rat.age_months >= 3) &
                    #(Rat.num_litters_with_defects <= 2 ) #TODO: uncomment this line when using full database
                    (Rat.sire != "XX") &
                    (Rat.dam != "XX") &
                    (Rat.sire != "5X") &
                    (Rat.dam != "5X") &
                    (Rat.birthdate != input_rat.birthdate)
                )
            ).all()
            
        else: # case: adding new rat to colony
            datingPool = db.session.execute(
                db.select(Rat.rat_number, Rat.sire, Rat.dam, Rat.pgsire, Rat.pgdam, Rat.mgsire, Rat.mgdam).where(
                    (Rat.sex != input_rat.sex) &
                    (Rat.manner_of_death == "Alive") & 
                    (Rat.current_partner == "00X") & # search for unpaired rats
                    (Rat.age_months >= 3) &
                    #(Rat.num_litters_with_defects <= 2 ) #TODO: uncomment this line when using full database
                    (Rat.sire != "XX") &
                    (Rat.dam != "XX") &
                    (Rat.sire != "5X") &
                    (Rat.dam != "5X") &
                    (Rat.birthdate != input_rat.birthdate)
                )
            ).all()
                
        # compare birthdates to get the final dating pool
        finalDatingPool = compareBirthdates(datingPool=datingPool, input_rat_ancestor_names=input_rat_ancestor_names, input_rat=input_rat)
    return finalDatingPool

# helper function to compare birthdates for a given rat vs their potential dating pool
# this rules out common ancestors
def compareBirthdates(datingPool, input_rat_ancestor_names, input_rat):
   
    finalDatingPool = []

    input_rat_ancestor_birthdays = []
    inputRat50sAncestorsFlag = False
    
    # STEP 1: get the ancestor's birthdates. Include EN in 2nd if stmt b/c grandparents could be EN
    for ancestor in input_rat_ancestor_names:
        pattern = re.compile(r'5\d[MF]|5X|4[78][MF]')
        isAncestorIn50sOr5X = pattern.match(ancestor)

        if(ancestor == "5X" or isAncestorIn50sOr5X != None):
            inputRat50sAncestorsFlag = True
        if(ancestor != "XX" and ancestor != "5X" and ancestor != "EN"):
            data = Rat.query.get(ancestor)
            input_rat_ancestor_birthdays.append(data.birthdate)

    for rat in datingPool:
        finalDatingPool.append(rat.rat_number)
        potential_partner_ancestors = [rat.sire, rat.dam, rat.pgsire, rat.pgdam, rat.mgsire, rat.mgdam]
        #print(rat.rat_number + " ancestors: " + str(potential_partner_ancestors))
        for ancestor in potential_partner_ancestors: 
            if(inputRat50sAncestorsFlag == True):
                pattern = re.compile(r'5\d[MF]|5X|4[78][MF]')
                isPartnerAncestorIn50sOr5X = pattern.match(ancestor)
                if(isPartnerAncestorIn50sOr5X != None):
                    #print(rat.rat_number + " rejected because " + ancestor + " matches " + str(isPartnerAncestorIn50sOr5X))
                    finalDatingPool.remove(rat.rat_number)
                    break
            
            # still have check for if ancestor != 5X because the if stmt above only activates
            # if input_rat has 50s or 5X ancestors, not if potential_partner has a 5X ancestor
            if(ancestor != "XX" and ancestor != "5X" and ancestor != "EN"):
                partner_ancestor_birthdate = Rat.query.get(ancestor).birthdate
                #print(ancestor + " " + str(partner_ancestor_birthdate))
                if(partner_ancestor_birthdate in input_rat_ancestor_birthdays or partner_ancestor_birthdate == input_rat.birthdate):
                    #print(rat.rat_number + " rejected because " + ancestor + " birthdate " + str(partner_ancestor_birthdate))
                    finalDatingPool.remove(rat.rat_number)
                    break
    return finalDatingPool

def printDatingPool(datingPool, rat_number):
    datingPoolString = rat_number + " dating pool: "
    for i in datingPool:
        datingPoolString += i[0]
        datingPoolString += "   " 
    print(datingPoolString)

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
            #print(str(rat.rat_number) + " " + str(age))
        else:
            years_to_months =  (deathDate.year - birthdate.year) * 12
            months = deathDate.month - birthdate.month
            age = years_to_months + months
            #print(str(rat.rat_number) + " " + str(age))
        db.session.execute(db.update(Rat).where(Rat.rat_number == rat.rat_number).values(age_months = age))
        
    db.session.commit()

if __name__ == '__main__':
    app.run()