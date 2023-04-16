import jinja2

from flask import Flask, request, redirect, url_for, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, BooleanField, SelectField, DateField
from wtforms.validators import DataRequired
from datetime import date, datetime, timedelta
from dateutil import relativedelta
import re
from sqlalchemy import cast, Integer, Date, extract
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# Initialize Flask
app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')

db = SQLAlchemy()
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

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
    current_partner = db.Column(db.String)
    num_litters_with_defects = db.Column(db.Integer)
    experiment = db.Column(db.Integer)
    manner_of_death = db.Column(db.String)
    death_date = db.Column(db.Date)
    age_months = db.Column(db.Integer)
    sire = db.Column(db.String)
    dam = db.Column(db.String)
    
    # paternal and maternal grandparents
    pgsire = db.Column(db.String)
    pgdam = db.Column(db.String)
    mgsire = db.Column(db.String)
    mgdam = db.Column(db.String)
    
    # paternal and maternal 1st great-grandparents, 1st and 2nd sets (see diagram)
    pg11sire = db.Column(db.String)
    pg11dam = db.Column(db.String)
    pg12sire = db.Column(db.String)
    pg12dam = db.Column(db.String)
    
    mg11sire = db.Column(db.String)
    mg11dam = db.Column(db.String)
    mg12sire = db.Column(db.String)
    mg12dam = db.Column(db.String)
    
    # paternal and paternal 2nd great-grandparents, 1st, 2nd, 3rd, 4th sets (see diagram)
    pg21sire = db.Column(db.String)
    pg21dam = db.Column(db.String)
    pg22sire = db.Column(db.String)
    pg22dam = db.Column(db.String)
    pg23sire = db.Column(db.String)
    pg23dam = db.Column(db.String)
    pg24sire = db.Column(db.String)
    pg24dam = db.Column(db.String)
    
    mg21sire = db.Column(db.String)
    mg21dam = db.Column(db.String)
    mg22sire = db.Column(db.String)
    mg22dam = db.Column(db.String)
    mg23sire = db.Column(db.String)
    mg23dam = db.Column(db.String)
    mg24sire = db.Column(db.String)
    mg24dam = db.Column(db.String)

class User(UserMixin, db.Model):
    __tablename__ = "Users"
    username = db.Column(db.String, primary_key=True)
    password = db.Column(db.String)
    
    def get_id(self):
        return self.username
    
class Admins(db.Model):
    __tablename__ = "admins"
    username = db.Column(db.String, db.ForeignKey(User.username), primary_key=True)
    admin = db.Column(db.Boolean)

@login_manager.user_loader
def load_user(username):
    users = [username for username, in db.session.query(User.username)]
    if( username in users ):
        return User.query.get(username)
    else:
        return None

class AddRatForm(FlaskForm):
    sex = SelectField(choices=['Male', 'Female'])
    birthdate = DateField()
    sire = StringField('Sire')
    dam = StringField('Dam')
    weanedDate = DateField()
    dateAddedToColony = DateField(default=date.today())
    experiment = BooleanField()
    addButton = SubmitField('Add Rat')       

class EditRatForm(FlaskForm):
    sex = SelectField(choices=['Male', 'Female'])
    number = IntegerField()
    birthdate = DateField()
    last_paired_date = DateField()
    last_litter_date = DateField()
    weaned_date = DateField()
    num_times_paired = IntegerField()
    num_litters = IntegerField()
    date_added_to_colony = DateField()
    num_litters_with_defects = IntegerField()
    experiment = BooleanField()
    sire = StringField('Sire')
    dam = StringField('Dam')
    status = SelectField(default="Empty", choices=[('Empty', ''), ('Alive', 'Alive'), ('Euthanized', 'Dead: euthanized'), ('Unexpected', 'Dead: unexpected'), ('Transferred', 'Transferred')])
    update = SubmitField('Update')
    
class ReportDeathForm(FlaskForm):
    sex = SelectField(choices=['Male', 'Female'])
    number = IntegerField()
    deathDate = DateField(default=date.today())
    mannerOfDeath = SelectField(choices=['Euthanized', 'Unexpected'])
    submit = SubmitField('Yes')

class GenerateBreedingPairsForm(FlaskForm):
    sex = SelectField(choices=['Male', 'Female'])
    number = IntegerField()
    swapping = BooleanField(default="checked")
    mateDropdown = SelectField()
    generateButton = SubmitField('Generate')
    mateDropdown = SelectField()
    recordButton = SubmitField('Yes')

class ReportLitterForm(FlaskForm):
    sire = IntegerField('Sire')
    dam = IntegerField('Dam')
    reportLittersWithDefects = SelectField(default="No", choices=['Yes', 'No'])
    litterDate = DateField(default=date.today())
    submit = SubmitField('Yes')
    
class RecordTransferForm(FlaskForm) :
    sex = SelectField(choices=['Male', 'Female'])
    number = IntegerField()
    submit = SubmitField('Yes')

class FamilyTreeForm(FlaskForm):
    generateButton = SubmitField("View Ancestry")

class LoginForm(FlaskForm):
    username = StringField()
    password = StringField()
    submit = SubmitField("Login")
    generateButton = SubmitField("View Ancestry")
    
class AddAdminForm(FlaskForm):
    newAdminUsername = StringField()
    currentAdminUsername = StringField()
    currentAdminPassword = StringField()
    submitButton = SubmitField("Confirm")
    
@app.route("/")
def default():
    form = LoginForm()
    return render_template("login.html", form=form)

@app.route("/dashboard")
@login_required
def dashboard():
    livingRats = len(db.session.execute(db.select(Rat.rat_number).where(
        (Rat.manner_of_death == "Alive"))).all())
    
    oldRats = db.session.execute(db.select(Rat.rat_number, Rat.age_months).where(
        (Rat.manner_of_death == "Alive")).order_by(cast(Rat.rat_number, Integer).asc())).all()[0:9]
    
    past30days = date.today() - timedelta(days=30)
    numLittersInPast30Days = len(db.session.execute(db.session.query(Rat.last_litter_date).filter(Rat.last_litter_date >= past30days)).all())//2
    users = db.session.execute(db.session.query(User)).all()
    numUsers = len(users)
    admin = (Admins.query.get(current_user.username) != None)
    return render_template("dashboard.html", livingRats = livingRats, oldRats = oldRats, user=current_user.username, admin=admin, numUsers=numUsers, numLitters=numLittersInPast30Days)

@app.route("/addrat", methods=['POST', 'GET'])
@login_required
def addRat():
    if(Admins.query.get(current_user.username) == None):
        return redirect(url_for("accessdenied"))
    form = AddRatForm()
    
    date_Check = False
    sire_Check = False
    dam_Check = False
    
    if(request.method == "POST"):
        rat = Rat()
        rat.sex = form.sex.data
        date_Check = dateCheck(form.birthdate.data)
        if(date_Check != False) :
            rat.birthdate = form.birthdate.data
        date_Check = dateCheck(form.weanedDate.data)
        if(date_Check != False) :
            rat.weaned_date = form.weanedDate.data
        rat.last_paired_date = date(1900, 1, 1)
        rat.last_litter_date = date(1900, 1, 1)
        rat.num_times_paired = 0
        rat.num_litters = 0
        date_Check = dateCheck(form.dateAddedToColony.data)
        if(date_Check != False) :
            rat.date_added_to_colony = form.dateAddedToColony.data
        rat.current_partner = "00X"
        rat.num_litters_with_defects = 0
        rat.experiment = int(form.experiment.data)
        rat.manner_of_death = "Alive"
        rat.death_date = date(1900, 1, 1)
        sire_Check = sireCheck(form.sire.data)
        if(sire_Check != False) :
            rat.sire = form.sire.data
        dam_Check = damCheck(form.dam.data)
        if(dam_Check != False) :
            rat.dam = form.dam.data

        if(rat.sex == "Female"):
            highestNumberFemale = db.session.execute(db.select(Rat.rat_number).
                where(Rat.sex=="Female").order_by(cast(Rat.rat_number, Integer).
                desc())).all()[0].rat_number[:-1]          
            number = int(highestNumberFemale) + 1
            rat.rat_number = str(number) + "F"
        else:
            highestNumberMale = db.session.execute(db.select(Rat.rat_number).
                where(Rat.sex=="Male").order_by(cast(Rat.rat_number, Integer).
                desc())).all()[0].rat_number[:-1]            
            number = int(highestNumberMale) + 1
            rat.rat_number = str(number) + "M"
        
        rat.rat_name = rat.rat_number + rat.sire[:-1] + rat.dam[:-1]
        delta = relativedelta.relativedelta(date.today(), form.birthdate.data)
        age = delta.months + (delta.years * 12)
        rat.age_months = age

        db.session.add(rat)
        db.session.commit()
        fillGenealogyData(rat.rat_number, rat.sire, rat.dam)
        return redirect(url_for("search"))
    else:
        return render_template("addrat.html", form=form, user=current_user.username)

@app.route("/addadmin", methods=["GET", "POST"])
@login_required
def addAdmin():
    form = AddAdminForm()
    if(Admins.query.get(current_user.username) == None):
        return redirect(url_for("accessdenied"))
    if(request.method == "POST"):
        if(form.currentAdminUsername.data == current_user.username and 
           form.currentAdminPassword.data == current_user.password and 
           User.query.get(form.newAdminUsername.data) != None):
            newAdmin = Admins()
            newAdmin.username = form.newAdminUsername.data
            newAdmin.admin = True
            db.session.add(newAdmin)
            db.session.commit()
            flash("Success!  " + newAdmin.username + " is now an administrator.")
        else:
            flash("Something went wrong.  Please try again.")
    return render_template("addadmin.html", user=current_user.username, form=form)

@app.route("/breedingpairs", methods=['GET', 'POST'])
@login_required
def breedingPairs():
    if(Admins.query.get(current_user.username) == None):
        return redirect(url_for("accessdenied"))
    form = GenerateBreedingPairsForm()
    if(request.method == "POST"):
        ratNumber = str(form.number.data) + form.sex.data[0]
        possibleMates = pairing(ratNumber, form.swapping.data)

        if (isinstance(possibleMates, str)):
            return render_template("breedingpairs.html", form=form, showMateDropdown=False, num=ratNumber, errorText=possibleMates, user=current_user.username)
             
        else:
            possibleMates.reverse()
            form.mateDropdown.choices = possibleMates
            query = db.session.execute(db.select(Rat).filter(Rat.rat_number.in_(possibleMates)).order_by(cast(Rat.rat_number, Integer).desc())).scalars()   

            return render_template("breedingpairs.html", form=form, query=query, showMateDropdown=True, num=ratNumber, errorText="", user=current_user.username)
    return render_template("breedingpairs.html", form=form, user=current_user.username)

@app.route("/recordpairing/<num>", methods=["GET", "POST"])
@login_required
def recordPairing(num):
    if(Admins.query.get(current_user.username) == None):
        return redirect(url_for("accessdenied"))
    if( request.method == "POST"):
        rat = db.session.query(Rat).filter(Rat.rat_number == num).one()  
        rat.current_partner = request.form.get("mateDropdown")
        rat.last_paired_date = date.today()
        rat.num_times_paired = rat.num_times_paired + 1

        #TODO: *shouldn't* need to modify the rat's old partner here.  Test and verify
        newPartner = db.session.query(Rat).filter(Rat.rat_number == request.form.get("mateDropdown")).one()
        newPartner.current_partner = rat.rat_number
        newPartner.last_paired_date = date.today()
        newPartner.num_times_paired = newPartner.num_times_paired + 1
        db.session.commit()
        # TODO: add a date field that defaults to today for the current date, in case the user is 
        # recording a previously made pairing?
        return redirect(url_for("search"))
    return redirect(url_for("search"))

@app.route("/search")
@login_required
def search():
    form = FamilyTreeForm()   
    query = db.session.execute(db.select(Rat).order_by(cast(Rat.rat_number, Integer).desc())).scalars()
    #print(query.all())
    # Whatever you do, do NOT run print(query.all()) before the return statement
    # that'll clear out the query variable or something, because then read.html 
    # will be blank
    admin = (Admins.query.get(current_user.username) != None)
    return render_template("search.html", query = query, form=form, user=current_user.username, admin=admin)

@app.route("/familytree/<num>", methods=["GET", "POST"])
@login_required
def showFamilyTree(num):
    if(request.method == "POST"):
        rat = db.session.query(Rat).filter(Rat.rat_number == num).one()
        # note: don't need to validate that the rat exists here because this is accessed
        # from the search page, which only contains rats that are already in the database
        admin = (Admins.query.get(current_user.username) != None)
        return render_template("FamilyTree.html", rat=rat, user=current_user.username, admin=admin)
    else:
        return redirect(url_for("search"))
    
@app.route("/editrecords", methods=['GET', 'POST'])
@login_required
def editRecords():   
    if(Admins.query.get(current_user.username) == None):
        return redirect(url_for("accessdenied"))
    form = EditRatForm()
    sire_Check = False
    dam_Check = False
    date_Check = False
    en_Check = 0
    
    if(request.method == "POST"):
        number = str(form.number.data) + form.sex.data[0]
        rat = db.session.query(Rat).filter(Rat.rat_number == number).one()
        
        if(form.birthdate.data != None):
            date_Check = dateCheck(form.birthdate.data)
            if(date_Check != False) :
                rat.birthdate = form.birthdate.data
                #TODO: recalculate rat's age when given new birthdate
        if(form.last_paired_date.data != None):
            date_Check = dateCheck(form.last_paired_date.data)
            if(rat.current_partner == '00X') :
                print(str("Error: Rat must be paired to edit pairing or litter info."))
            elif(date_Check != False) :
                rat.last_paired_date = form.last_paired_date.data
        if(form.last_litter_date.data != None):
            date_Check = dateCheck(form.last_litter_date.data)
            if(rat.current_partner == '00X') :
                print(str("Error: Rat must be paired to edit pairing or litter info."))
            elif(date_Check != False) :
                rat.last_litter_date = form.last_litter_date.data
        if(form.weaned_date.data != None):
            date_Check = dateCheck(form.weaned_date.data)
            if(date_Check != False) :
                rat.weaned_date = form.weaned_date.data
        if(form.num_times_paired.data != None):
            if(rat.current_partner == '00X') :
                print(str("Error: Rat must be paired to edit pairing or litter info."))
            else :
                rat.num_times_paired = form.num_times_paired.data  
        if(form.num_litters.data != None):
            if(rat.current_partner == '00X') :
                print(str("Error: Rat must be paired to edit pairing or litter info."))
            #to-do: if number of litters is set to 0 then query database to see if rat is listed as sire/dam for another rat
            #elif(form.num_litters.data == 0) :
            else :
                rat.num_litters = form.num_litters.data
        if(form.date_added_to_colony.data != None):
            date_Check = dateCheck(form.date_added_to_colony.data)
            if(date_Check != False) :
                rat.date_added_to_colony = form.date_added_to_colony.data
        if(form.num_litters_with_defects.data != None):
            rat.num_litters_with_defects = form.num_litters_with_defects.data
        if(form.experiment.data != None):
            rat.experiment = form.experiment.data
        #to-do: comment out prints used for testing inputs
        if(form.sire.data != ''):
            print(str("Calling sire check"))
            sire_Check = sireCheck(form.sire.data)
            print(str(sire_Check))
            en_Check = enCheck(form.sire.data, form.dam.data)
            print(str(en_Check))
            #Case 1: Valid sire & both sire/dam input as EN
            if (sire_Check != False and en_Check == 1) :
                rat.sire = form.sire.data
                #fillGenealogyData(number, form.sire.data, rat.dam)
                updateName(number, form.sire.data, form.dam.data)
            #Case 2: Valid sire & both sire/dam input NOT as EN
            # -if statement to allow change of EN entries
            elif (sire_Check != False and en_Check == 2) :
                if (rat.sire == 'EN' or rat.dam == 'EN') :
                  rat.sire = form.sire.data
                  #fillGenealogyData(number, form.sire.data, rat.dam)
                  updateName(number, form.sire.data, form.dam.data)
                else :
                  rat.sire = form.sire.data
                  #fillGenealogyData(number, form.sire.data, rat.dam)
                  updateName(number, form.sire.data, rat.dam)
            #Case 3: Valid sire & inputs not a set of paired EN
            elif (sire_Check != False and en_Check == 3) :
                print(str("Error: EN must pair with EN"))
        if(form.dam.data != ''):
            print(str("Calling dam check"))
            dam_Check = damCheck(form.dam.data)
            print(str(dam_Check))
            en_Check = enCheck(form.sire.data, form.dam.data)
            print(str(en_Check))
            if (dam_Check != False and en_Check == 1) :
                rat.dam = form.dam.data
                #fillGenealogyData(number, rat.sire, form.dam.data)
                updateName(number, form.sire.data, form.dam.data)
            elif (dam_Check != False and en_Check == 2) :
                if (rat.sire == 'EN' or rat.dam == 'EN') :
                  rat.dam = form.dam.data
                  #fillGenealogyData(number, form.sire.data, rat.dam)
                  updateName(number, form.sire.data, form.dam.data)
                else :
                  rat.dam = form.dam.data
                  #fillGenealogyData(number, rat.sire, form.dam.data)
                  updateName(number, rat.sire, form.dam.data)
            elif (dam_Check != False and en_Check == 3) :
                print(str("Error: EN must pair with EN"))
        if(form.status.data != "Empty" and form.status.data != rat.manner_of_death):
            rat.manner_of_death = form.status.data
         
        db.session.commit()
        
        return redirect(url_for("editRecords"))
    else:
        return render_template("editrecords.html", form=form, user=current_user.username)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if( request.method == "POST"):
        user = User.query.filter_by(username = form.username.data).first()        
        if not user or (form.password.data != user.password):
            return redirect(url_for("accessdenied"))
        else:
            login_user(user, remember=True)
            return redirect(url_for("dashboard"))
    
    return render_template("login.html", form=form)

@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    form=LoginForm()
    return render_template("login.html", form=form)

@app.route("/accessdenied", methods=["POST", "GET"])
def accessdenied():
    return render_template("accessdenied.html")

@app.route("/recordtransfer", methods=['POST', 'GET'])
@login_required
def recordTransfer():
    if(Admins.query.get(current_user.username) == None):
        return redirect(url_for("accessdenied"))
    form = RecordTransferForm()
    
    if(request.method == "POST") :
        rat_number =  str(form.number.data) + form.sex.data[0]
        isValidRat = ratIDCheck(rat_number)
        if(isValidRat) :
          rat = Rat.query.get(rat_number)
          rat.manner_of_death = "Transferred"
          db.session.commit()
        else :
          print(str("Error: Not an existing rat."))
        
        return render_template("recordtransfer.html", form=form, user=current_user.username)
    else:
        return render_template("recordtransfer.html", form=form, user=current_user.username)

@app.route("/reportlitter", methods=['POST', 'GET'])
@login_required
def reportLitter():
    if(Admins.query.get(current_user.username) == None):
        return redirect(url_for("accessdenied"))
    form = ReportLitterForm()
    
    if(request.method == "POST") :
        rat_number = str(form.number.data) + form.sex.data[0]
        isValidRat = ratIDCheck(rat_number)
        
        if(isValidRat):
            rat = Rat.query.get(rat_number)
            #References drop down menu options for if litter has defects or not
            if(form.reportLittersWithDefects.data != "No") :
                rat.num_litters_with_defects = rat.num_litters_with_defects + 1
                rat.num_litters = rat.num_litters + 1
                db.session.commit()
            else:
                rat.num_litters = rat.num_litters + 1
                db.session.commit()
        else:
            print(str("Error: Not an existing rat."))
        sire_number = str(form.sire.data) + "M"
        dam_number = str(form.dam.data) + "F"
        #TODO: verify that sire and dam exist
        sire = Rat.query.get(sire_number)
        dam = Rat.query.get(dam_number)
        sire.num_litters = sire.num_litters + 1
        dam.num_litters = dam.num_litters + 1
        sire.last_litter_date = form.litterDate.data
        dam.last_litter_date = form.litterDate.data
        #References drop down menu options for if litter has defects or not
        if(form.reportLittersWithDefects.data == "Yes") :
            sire.num_litters_with_defects = sire.num_litters_with_defects + 1
            dam.num_litters_with_defects = dam.num_litters_with_defects + 1

        db.session.commit()


    return render_template("reportlitter.html", form=form, user=current_user.username)

@app.route("/reportdeath", methods=['POST', 'GET'])
@login_required
def reportDeath():
    if(Admins.query.get(current_user.username) == None):
        return redirect(url_for("accessdenied"))
    form = ReportDeathForm()
    dCheck = False
    
    if(request.method == "POST"):       
        rat_number = str(form.number.data) + form.sex.data[0]
 
        isValidRat = ratIDCheck(rat_number)
        
        if(isValidRat):
           rat = Rat.query.get(rat_number)
           rat.manner_of_death = form.mannerOfDeath.data
           dCheck = dateCheck(form.deathDate.data)
           if dCheck != False :
              rat.death_date = form.deathDate.data
              # don't have to update the inputted rat's partner because that rat is now deceased 
              # so it doesn't matter who they're paired with.  their current partner is still alive
              # though, so we have to update that rat's partner to DEC because they will be repaired
              # and it matters who they're paired with  
              if(rat.current_partner != '' and rat.current_partner != "UNK" 
                and rat.current_partner != "DEC" and rat.current_partner != "00X"):
                 current_partner = Rat.query.get(rat.current_partner)
                 current_partner.current_partner = "DEC"
              db.session.commit()
        else :
            print(str("Error: Not an existing rat."))
        #TODO: route to confirmation screen instead(?) definitely not search
        return redirect(url_for("search"))
    else:
        return render_template("reportdeath.html", form=form, user=current_user.username)
    
@app.route("/userguide")
@login_required
def userGuide():
    return render_template("userguide.html", user=current_user.username)

# this function MUST be called *after* a new rat has been added to the database
# it fills in the new rat's genealogical fields
# assumetion: the new rat has an entry in the database.  sire number and dam number are valid
# input: the new rat's number, sire number, and dam number
# output: updates the genealogical fields of the new rat's entry in the database
#         this function does not return anything 
def fillGenealogyData(new_rat_number, sire_number, dam_number):
    
    new_rat = Rat.query.get(new_rat_number)
    
    # if rat is ENEN, fill in ancestry data with all ENs
    if(sire_number == "EN" and dam_number == "EN"):
        new_rat.pgsire = "EN"
        new_rat.pgdam = "EN"
        new_rat.pg11sire = "EN"
        new_rat.pg11dam = "EN"
        new_rat.pg12sire = "EN"
        new_rat.pg12dam = "EN"
        new_rat.pg21sire = "EN"
        new_rat.pg21dam = "EN"
        new_rat.pg22sire = "EN"
        new_rat.pg22dam = "EN"
        new_rat.pg23sire = "EN"
        new_rat.pg23dam = "EN"
        new_rat.pg24sire = "EN"
        new_rat.pg24dam = "EN"
    
        new_rat.mgsire = "EN"
        new_rat.mgdam = "EN"
        new_rat.mg11sire = "EN"
        new_rat.mg11dam = "EN"
        new_rat.mg12sire = "EN"
        new_rat.mg12dam = "EN"
        new_rat.mg21sire = "EN"
        new_rat.mg21dam = "EN"
        new_rat.mg22sire = "EN"
        new_rat.mg22dam = "EN"
        new_rat.mg23sire = "EN"
        new_rat.mg23dam = "EN"
        new_rat.mg24sire = "EN"
        new_rat.mg24dam = "EN"

    else: # rat is from colony, get data from database
        sire = Rat.query.get(sire_number)
        dam = Rat.query.get(dam_number)

        # fill in new rat's paternal side
        new_rat.pgsire = sire.sire
        new_rat.pgdam = sire.dam
        new_rat.pg11sire = sire.pgsire
        new_rat.pg11dam = sire.pgdam
        new_rat.pg12sire = sire.mgsire
        new_rat.pg12dam = sire.mgdam
        new_rat.pg21sire = sire.pg11sire
        new_rat.pg21dam = sire.pg11dam
        new_rat.pg22sire = sire.pg12sire
        new_rat.pg22dam = sire.pg12dam
        new_rat.pg23sire = sire.mg11sire
        new_rat.pg23dam = sire.mg11dam
        new_rat.pg24sire = sire.mg12sire
        new_rat.pg24dam = sire.mg12dam
        
        # # fill in new rat's maternal side
        new_rat.mgsire = dam.sire
        new_rat.mgdam = dam.dam
        new_rat.mg11sire = dam.pgsire
        new_rat.mg11dam = dam.pgdam
        new_rat.mg12sire = dam.mgsire
        new_rat.mg12dam = dam.mgdam
        new_rat.mg21sire = dam.pg11sire
        new_rat.mg21dam = dam.pg11dam
        new_rat.mg22sire = dam.pg12sire
        new_rat.mg22dam = dam.pg12dam
        new_rat.mg23sire = dam.mg11sire
        new_rat.mg23dam = dam.mg11dam
        new_rat.mg24sire = dam.mg12sire
        new_rat.mg24dam = dam.mg12dam
    
    db.session.commit()
    return 

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
    
    # case 0: immediate error checking
    if( input_rat.manner_of_death != "Alive"):
        return "ERROR: cannot pair a deceased or transferred rat."
    
    # case 1: input_rat is spare rat, swapping = True
    if(swapping_existing_pairs == True and input_rat.current_partner == "00X"):
        return "ERROR: cannot swap existing pairs if the inputted rat is unpaired."
    
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
                    (Rat.age_months >= 3) &
                    (Rat.num_litters_with_defects <= 2 ) 
                )
            ).all()
        does_colony_have_vacancy = bool(len(colony_rats_without_partner))
        if(does_colony_have_vacancy == False): # case 2a: no vacancy error
            return "ERROR: there are no rats with deceased partners rats to pair " + input_rat.rat_number + " with."
        else: # case 2b and 2c
            # the user could've reported multiple deaths before looking for new partners
            # so there could be multiple rats in colony_rats_without_partner, need to check all of them
            finalDatingPool = compareBirthdates(input_rat_ancestor_names=input_rat_ancestor_names, datingPool=colony_rats_without_partner, input_rat=input_rat)
            if (len(finalDatingPool) == 0): # case 2b: no unrelated rats error
                return "ERROR: " + input_rat.rat_number + "cannot be added to the colony.  " + input_rat.rat_number + " can only be paired with a rat that has a deceased partner, and " + input_rat.rat_number + " is too closely related to the available rats with deceased partners."
            else: # case 2c: succeeded in finding unrelated rat with DEC partner
                #print(finalDatingPool)
                return finalDatingPool
    
    # looking at colony rats from here down
    # two checks to rule out deceased partner errors because those only apply to colony rats
    if(swapping_existing_pairs == True and input_rat.current_partner == "DEC" ):
        return "ERROR: cannot swap existing pairs.  " + input_rat.rat_number + " is paired with a deceased rat.  Pairs cannot be swapped unless all rats have living partners.  Try again and uncheck the checkbox on the previous page to look for a spare rat to pair " + input_rat.rat_number + " with."
    if(swapping_existing_pairs == False and input_rat.current_partner != "DEC"):
        return "ERROR: cannot add a new rat to the colony when the inputted rat is paired.  Check the checkbox on the previous page and try again."
       
    # handle ENEN rats because they're a special case.  They can breed with anyone, 
    # including other ENEN rats, so birthdate checking to rule out common ancestors is unnecessary
    # for them.  Don't need to check the l
    if(input_rat.sire == "EN" and input_rat.dam == "EN"):
        if(swapping_existing_pairs): # look for colony rat
            datingPool = db.session.execute(
                db.select(Rat.rat_number).where(
                    (Rat.sex != input_rat.sex) &
                    (Rat.manner_of_death == "Alive") & 
                    (Rat.current_partner != "00X") & # narrow search to only paired rats
                    (Rat.rat_number != input_rat.current_partner) & # narrow search to exclude input_rat's current partner                    
                    (Rat.age_months >= 3) &
                    (Rat.num_litters_with_defects <= 2 ) & 
                    (Rat.sire != "XX") &
                    (Rat.dam != "XX") &
                    (Rat.sire != "5X") &
                    (Rat.dam != "5X")
                )
            ).all()
            finalDatingPool = [ rat[0] for rat in datingPool]

        else: # look for spare rat
            datingPool = db.session.execute(
                db.select(Rat.rat_number).where(
                    (Rat.sex != input_rat.sex) &
                    (Rat.manner_of_death == "Alive") & 
                    (Rat.current_partner == "00X") & # search for unpaired rats
                    (Rat.age_months >= 3) &
                    (Rat.num_litters_with_defects <= 2 ) &
                    (Rat.sire != "XX") &
                    (Rat.dam != "XX") &
                    (Rat.sire != "5X") &
                    (Rat.dam != "5X")
                )
            ).all()
            finalDatingPool = [ rat[0] for rat in datingPool]

    else: # handle non ENEN, so need to do birthdate checking
        if(swapping_existing_pairs): # query for colony rats
            datingPool = db.session.execute(
                db.select(Rat.rat_number, Rat.sire, Rat.dam, Rat.pgsire, Rat.pgdam, Rat.mgsire, Rat.mgdam).where(
                    (Rat.sex != input_rat.sex) &
                    (Rat.manner_of_death == "Alive") & 
                    (Rat.current_partner != "00X") & # narrow search to only paired rats
                    (Rat.rat_number != input_rat.current_partner) & # narrow search to exclude input_rat's current partner                    
                    (Rat.age_months >= 3) &
                    (Rat.num_litters_with_defects <= 2 ) &
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
                    (Rat.num_litters_with_defects <= 2 ) & 
                    (Rat.sire != "XX") &
                    (Rat.dam != "XX") &
                    (Rat.sire != "5X") &
                    (Rat.dam != "5X") &
                    (Rat.birthdate != input_rat.birthdate)
                )
            ).all()
                
        # compare birthdates to get the final dating pool
        finalDatingPool = compareBirthdates(datingPool=datingPool, input_rat_ancestor_names=input_rat_ancestor_names, input_rat=input_rat)
        if (len(finalDatingPool) == 0): # no unrelated rats error
            return "ERROR: there are no unrelated paired rats that " + input_rat.rat_number + " can be paired with."

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
    
    res = db.session.execute(db.select(Rat.rat_number, Rat.age_months).where(Rat.manner_of_death=="Alive")).all()
    for item in res:
        rat = Rat.query.get(item[0])
        age = 0
        deathDate = rat.death_date
        birthdate = rat.birthdate
        if deathDate.year == 1900:
            delta = relativedelta.relativedelta(date.today(), birthdate)
            age = delta.months + (delta.years * 12) 
            #print(str(rat.rat_number) + " " + str(age))
        else:
            delta = relativedelta.relativedelta(deathDate, birthdate)
            age = delta.months + (delta.years * 12) 
            #print(str(rat.rat_number) + " " + str(age))
        db.session.execute(db.update(Rat).where(Rat.rat_number == rat.rat_number).values(age_months = age))
        
    db.session.commit()

def updateName(new_rat_number, sire_number, dam_number) :

    if(sire_number == 'EN' and dam_number == 'EN') :
        new_rat = Rat.query.get(new_rat_number)
        new_rat.rat_name = new_rat.rat_number + sire_number + dam_number
        
        print(str(new_rat.rat_number))
        print(str(sire_number))
        print(str(dam_number))	
        print(str(new_rat.rat_name))
    else:
        new_rat = Rat.query.get(new_rat_number)
        sire = Rat.query.get(sire_number)
        dam = Rat.query.get(dam_number)
    
        new_rat.rat_name = new_rat.rat_number + sire.rat_number[:-1] + dam.rat_number[:-1]
        print(str(new_rat.rat_number))
        print(str(sire.rat_number))
        print(str(dam.rat_number))	
        print(str(new_rat.rat_name))
    db.session.commit()

#Check if rat ID exists in database	
def ratIDCheck(number):
    ratNumbers = [rat for rat, in db.session.query(Rat.rat_number)]
    if (number in ratNumbers):
        return True
    else:
        return False
        
#Check to ensure date is not in the future
def dateCheck(date) :
    
    blocked = date.today()
    print(str(date))
    print(str(blocked))
    
    if date >= blocked:
        dCheck = False
        print(str("Error: Date cannot be in the future."))
        #return "Error: Date cannot be in the future."
    else:
        #return "Date not blocked"
        dCheck = True
        print(str("Date not blocked"))
    
    return dCheck

def sireCheck(sire) :

    ratCheck = [sire for sire, in db.session.query(Rat.sire)]
    if(sire in ratCheck or sire == 'EN') :
        rat_Check = True
        print(str("Valid Sire"))
    else :
        rat_Check = False
        print(str("Error: Invalid Sire"))
    
    return rat_Check
    
def damCheck(dam) :

    ratCheck = [dam for dam, in db.session.query(Rat.dam)]
    if(dam in ratCheck or dam == 'EN') :
        rat_Check = True
        print(str("Valid Dam"))
    else :
        rat_Check = False
        print(str("Error: Invalid Dam"))
    
    return rat_Check
    
def enCheck(sire, dam) :

    if(sire == 'EN' and dam == 'EN') :
        en_Check = 1
        print(str("Valid EN Pairing"))
    elif(sire != 'EN' and dam != 'EN') :
        en_Check = 2
    elif(sire != 'EN' or dam != 'EN') :
        en_Check = 3

    return en_Check		
if __name__ == '__main__':
    app.run()
