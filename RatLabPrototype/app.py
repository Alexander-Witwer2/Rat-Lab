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

correctOutputColonyRatsSwappingPairsTrue = {
    "41F" : ['60M', '61M', '65M', '66M', '73M', '74M', '75M', '77M', '78M', '79M', '80M', '81M', '82M', '86M', '87M', '93M', '94M'],
    "59M" : ['63F', '64F', '65F', '71F', '72F', '73F', '74F', '75F', '80F', '81F', '82F', '94F', '95F', '96F', '97F'],
    "66F" : ['61M', '65M', '66M', '71M', '75M', '78M', '79M', '81M', '82M', '86M', '87M', '93M', '94M'],
    "83M" : ['61F', '63F', '71F', '72F', '80F', '82F', '94F', '95F', '96F', '97F'],
    "65F" : ['61M', '65M', '66M', '71M', '75M', '78M', '79M', '81M', '82M', '86M', '87M', '93M', '94M'],
    "71M" : ['61F', '63F', '64F', '65F', '71F', '72F', '73F', '74F', '82F', '94F', '95F', '96F', '97F'],
    "81F" : ['61M', '65M', '66M', '75M', '78M', '79M', '81M', '82M', '86M', '87M', '94M'],
    "80M" : ['61F', '63F', '71F', '72F', '82F', '94F', '95F', '97F'],
    "94F" : [('60M',), ('61M',), ('65M',), ('66M',), ('71M',), ('73M',), ('74M',), ('75M',), ('77M',), ('78M',), ('79M',), ('80M',), ('81M',), ('82M',), ('86M',), ('87M',), ('93M',), ('94M',)],
    "78M" : [('61F',), ('63F',), ('64F',), ('65F',), ('71F',), ('72F',), ('73F',), ('74F',), ('75F',), ('80F',), ('81F',), ('82F',), ('94F',), ('95F',), ('96F',), ('97F',)]
}

correctOutputColonyRatsSwappingPairsFalse = {
    "41F" : ['84M', '85M', '88M', '89M', '90M'],
    "59M" : ['100F', '102F', '103F', '104F', '87F', '88F', '89F', '90F', '98F', '99F'],
    "66F" : ['84M', '85M'],
    "83M" : ['100F', '101F', '104F', '106F', '62F', '78F', '79F', '91F', '92F', '99F'],
    "65F" : ['84M', '85M'],
    "71M" : ['100F', '102F', '103F', '62F', '76F', '77F', '78F', '79F', '87F', '88F', '89F', '90F', '99F'],
    "81F" : ['84M', '85M'],
    "80M" : ['100F', '62F', '78F', '79F', '99F'],
    "94F" : [('84M',), ('85M',), ('88M',), ('89M',), ('90M',), ('91M',), ('92M',), ('96M',)],
    "78M" : [('100F',), ('101F',), ('102F',), ('103F',), ('104F',), ('106F',), ('62F',), ('76F',), ('77F',), ('78F',), ('79F',), ('87F',), ('88F',), ('89F',), ('90F',), ('91F',), ('92F',), ('98F',), ('99F',)]
}

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

def testColonyRats(swappingExistingPairs):
    currently_paired_rats_to_test = ['41F', '59M', '66F', '83M', '65F', '71M', '81F', '80M', '94F', '78M']
    for rat in currently_paired_rats_to_test:
        result = pairing(rat, swappingExistingPairs)
        # print(rat + ": " + str(result))
        if(swappingExistingPairs == True):
            if(result == correctOutputColonyRatsSwappingPairsTrue[rat]):
                print(rat + " passed")
            else:
                print(rat + " FAILED")
        else:
            if(result == correctOutputColonyRatsSwappingPairsFalse[rat]):
                print(rat + " passed")
            else:
                print(rat + " FAILED")

@app.route("/reportlitter")
def reportLitter():
    #updateAges()

    print("TESTING: swapping existing pairs = true, input = colony rat")
    testColonyRats(True)
    print("TESTING: swapping existing pairs = false, input = colony rat")
    testColonyRats(False)
    
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
def pairing(input_data, input_swapping_existing_pairs):
    
    input_data = input_data
    swapping_existing_pairs = input_swapping_existing_pairs
    datingPool = []
    finalDatingPool = []

    # STEP 1: query for input_rat's information and separate out the parents and grandparents names
    input_rat = Rat.query.get(input_data)
    ancestor_names = [input_rat.sire, input_rat.dam, input_rat.pgsire, input_rat.pgdam, input_rat.mgsire, input_rat.mgdam]  
    input_rat_ancestor_birthdays = []
    inputRat50sAncestorsFlag = False

    
    # STEP 2: handle ENEN rats because they're a special case.  They can breed with anyone, 
    # including other ENEN rats, so birthdate checking to rule out common ancestors is unnecessary
    # for them
    if(input_rat.sire == "EN" and input_rat.dam == "EN"):
        #case 1: query for rats who are paired, excluding the rat’s current partner if known (! UNK and !00X)
        if(swapping_existing_pairs):
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
        else:
            # case 2: query for rats who aren't paired
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
        #print(str(datingPool))
        #TODO: this might be excessive, but order rats in datingPool by highest number of XX 
        # ancestors first before returning?
    
    # STEP 3: handle colony rats.  Need to compare birthdates of input_rat and their ancestors
    # to the birthdates of potential mates and their ancestors to exclude related rats
    else:
       # STEP 3a: get the ancestor's birthdates. Include EN b/c grandparents could be EN
        for ancestor in ancestor_names:
            pattern = re.compile(r'5\d[MF]|5X|4[78][MF]')
            isAncestorIn50sOr5X = pattern.match(ancestor)

            if(ancestor == "5X" or isAncestorIn50sOr5X != None):
                inputRat50sAncestorsFlag = True
            if(ancestor != "XX" and ancestor != "5X" and ancestor != "EN"):
                data = Rat.query.get(ancestor)
                input_rat_ancestor_birthdays.append(data.birthdate)
                
        #STEP 3b: generate dating pool based on which case we're in
        
        # case 1, query for rats who are paired.  exclude current partner.  
        # include input_rat's birthdate because these are colony rats and checking != birthdate
        # is a quick way to exclude siblings born on the same day 
        # this isn't necessarily all siblings, but it helps narrow down the dating pool
        if(swapping_existing_pairs):
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
            
        else: # case 2: adding new rat to colony
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
            
        datingPoolString = ""
        for i in datingPool:
            datingPoolString += i[0]
            datingPoolString += "   " 
        #print("rat " + input_data + " datingPool = " + datingPoolString)
     
        
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
        #print("finalDatingPool: " + str(finalDatingPool))    
    return finalDatingPool



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