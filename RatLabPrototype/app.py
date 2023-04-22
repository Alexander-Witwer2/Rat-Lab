import jinja2

from flask import Flask, request, redirect, url_for, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, BooleanField, SelectField, DateField
from wtforms.validators import InputRequired, NumberRange
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
    birthdate = DateField(validators=[InputRequired()])
    supplierRat = BooleanField()
    sire = IntegerField(validators=[NumberRange(min=0)])
    dam = IntegerField(validators=[NumberRange(min=0)])
    weanedDate = DateField(validators=[InputRequired()])
    dateAddedToColony = DateField(default=date.today(), validators=[InputRequired()])
    experiment = BooleanField()
    addButton = SubmitField('Add Rat')       

class EditRatForm(FlaskForm):
    sex = SelectField(choices=['Male', 'Female'])
    number = IntegerField(validators=[NumberRange(min=0)])
    birthdate = DateField()
    last_paired_date = DateField()
    last_litter_date = DateField()
    weaned_date = DateField()
    num_times_paired = IntegerField(validators=[NumberRange(min=0, max=25)])
    num_litters = IntegerField(validators=[NumberRange(min=0, max=25)])
    date_added_to_colony = DateField()
    num_litters_with_defects = IntegerField(validators=[NumberRange(min=0, max=25)])
    experiment = SelectField(default="0", choices=[("0", "No"), ("1", "Yes")])
    supplierRat = SelectField(default="no", choices=[("no", "No"), ("yes", "Yes")])
    sire = IntegerField(validators=[NumberRange(min=0)])
    dam = IntegerField(validators=[NumberRange(min=0)])
    status = SelectField(default="Empty", choices=[('Empty', ''), ('Alive', 'Alive'), ('Euthanized', 'Dead: euthanized'), ('Unexpected', 'Dead: unexpected'), ('Transferred', 'Transferred')])
    update = SubmitField('Update')
    continueButton = SubmitField('Continue')
    
class ReportDeathForm(FlaskForm):
    sex = SelectField(choices=['Male', 'Female'])
    number = IntegerField(validators=[InputRequired(), NumberRange(min=0)])
    deathDate = DateField(default=date.today(), validators=[InputRequired()])
    mannerOfDeath = SelectField(choices=['Euthanized', 'Unexpected'])
    submit = SubmitField('Yes')

class GenerateBreedingPairsForm(FlaskForm):
    sex = SelectField(choices=['Male', 'Female'])
    number = IntegerField(validators=[InputRequired(), NumberRange(min=0)])
    swapping = BooleanField(default="checked")
    mateDropdown = SelectField(validators=[InputRequired()])
    dateOfPairing = DateField(default=date.today(), validators=[InputRequired()])
    generateButton = SubmitField('Generate')
    viewAncestryButton = SubmitField('View')
    recordButton = SubmitField('Yes')

class ReportLitterForm(FlaskForm):
    sire = IntegerField('Sire', validators=[InputRequired(), NumberRange(min=0)])
    dam = IntegerField('Dam', validators=[InputRequired(), NumberRange(min=0)])
    reportLittersWithDefects = SelectField(default="No", choices=['Yes', 'No'])
    litterDate = DateField(default=date.today(), validators=[InputRequired()])
    submit = SubmitField('Yes')
    
class RecordTransferForm(FlaskForm) :
    sex = SelectField(choices=['Male', 'Female'])
    number = IntegerField(validators=[InputRequired()])
    submit = SubmitField('Yes')

class FamilyTreeForm(FlaskForm):
    generateButton = SubmitField("View Ancestry")

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired()])
    password = StringField(validators=[InputRequired()])
    submit = SubmitField("Login")
    
class AddAdminForm(FlaskForm):
    newAdminUsername = StringField(validators=[InputRequired()])
    currentAdminUsername = StringField(validators=[InputRequired()])
    confirmField = StringField(validators=[InputRequired()])
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
    admin = Admins.query.get(current_user.username)
    if(admin == None):
        return redirect(url_for("accessdenied"))
    form = AddRatForm()

    if(request.method == "POST"):      
        rat = Rat()
        rat.sex = form.sex.data
        isValidBirthdate = isDateInBounds(form.birthdate.data)
        if(isValidBirthdate == "ok") :
            rat.birthdate = form.birthdate.data
        else:
            errorText = "Error: a rat cannot be born " + isValidBirthdate + "."
            return render_template("addrat.html", form=form, user=current_user.username, errorText=errorText, admin=admin)

        isValidWeanedDate = weanedDateCheck(form.birthdate.data, form.weanedDate.data)
        if(isValidWeanedDate == "ok") :
            rat.weaned_date = form.weanedDate.data
        else:
            errorText = isValidWeanedDate
            return render_template("addrat.html", form=form, user=current_user.username, errorText=errorText, admin=admin)

        rat.last_paired_date = date(1900, 1, 1)
        rat.last_litter_date = date(1900, 1, 1)
        rat.num_times_paired = 0
        rat.num_litters = 0
        
        isValidColonyAddedDate = addedToColonyDateCheck(form.birthdate.data, form.weanedDate.data, form.dateAddedToColony.data)
        if(isValidColonyAddedDate == "ok") :
            rat.date_added_to_colony = form.dateAddedToColony.data
        else:
            errorText = isValidColonyAddedDate
            return render_template("addrat.html", form=form, user=current_user.username, errorText=errorText, admin=admin)

        rat.current_partner = "00X"
        rat.num_litters_with_defects = 0
        rat.experiment = int(form.experiment.data)
        rat.manner_of_death = "Alive"
        rat.death_date = date(1900, 1, 1)
        
        ratNumber = ''
        if(rat.sex == "Female"):
            highestNumberFemale = db.session.execute(db.select(Rat.rat_number).
                where(Rat.sex=="Female").order_by(cast(Rat.rat_number, Integer).
                desc())).all()[0].rat_number[:-1]          
            number = int(highestNumberFemale) + 1
            ratNumber = rat.rat_number = str(number) + "F"
        else:
            highestNumberMale = db.session.execute(db.select(Rat.rat_number).
                where(Rat.sex=="Male").order_by(cast(Rat.rat_number, Integer).
                desc())).all()[0].rat_number[:-1]            
            number = int(highestNumberMale) + 1
            ratNumber = rat.rat_number = str(number) + "M"

        if(form.supplierRat.data == True and (form.sire.data != None or form.dam.data != None)):
            errorText = "Error: a rat cannot be from the supplier and from the colony."
            return render_template("addrat.html", form=form, user=current_user.username, errorText=errorText, admin=admin)

        if(form.supplierRat.data == True):
            rat.sire = "EN"
            rat.dam = "EN"
            rat.rat_name = ratNumber + "ENEN"
        else:
            sire = str(form.sire.data) + "M"
            dam = str(form.dam.data) + "F" 
            if(verifySireAndDam(sire, dam)):
                rat.sire = sire
                rat.dam = dam
                rat.rat_name = ratNumber + sire[:-1] + dam[:-1]
            else:
                errorText = "Error: invalid parents"
                return render_template("addrat.html", form=form, user=current_user.username, errorText=errorText, admin=admin)

        delta = relativedelta.relativedelta(date.today(), form.birthdate.data)
        age = delta.months + (delta.years * 12)
        rat.age_months = age

        db.session.add(rat)
        db.session.commit()
        fillGenealogyData(rat.rat_number, rat.sire, rat.dam)
        return redirect(url_for("search"))
    else:
        return render_template("addrat.html", form=form, user=current_user.username, admin=admin)

@app.route("/addadmin", methods=["GET", "POST"])
@login_required
def addAdmin():
    form = AddAdminForm()
    if(Admins.query.get(current_user.username) == None):
        return redirect(url_for("accessdenied"))
    if(request.method == "POST"):
        print(form.data.items())
        if(form.currentAdminUsername.data == current_user.username and 
           form.confirmField.data == "CONFIRM" and 
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
    admin = Admins.query.get(current_user.username)
    if(admin == None):
        return redirect(url_for("accessdenied"))
    form = GenerateBreedingPairsForm()
    if(request.method == "POST"):
        ratNumber = str(form.number.data) + form.sex.data[0]
        
        if(not ratIDCheck(ratNumber)):
            errorText="Error: rat does not exist"
            return render_template("breedingpairs.html", form=form, showMateDropdown=False, num=ratNumber, errorText=errorText, user=current_user.username, admin=admin)       
        rat = db.session.query(Rat).filter(Rat.rat_number == ratNumber).one()  
        if(rat.age_months < 3):
            errorText = "Error: the rat is too young to breed."
            return render_template("breedingpairs.html", form=form, showMateDropdown=False, num=ratNumber, errorText=errorText, user=current_user.username, admin=admin)

        possibleMates = pairing(ratNumber, form.swapping.data)

        if (isinstance(possibleMates, str)):
            return render_template("breedingpairs.html", form=form, showMateDropdown=False, num=ratNumber, errorText=possibleMates, user=current_user.username, admin=admin)
             
        else:
            possibleMates.reverse()
            form.mateDropdown.choices = possibleMates
            query = db.session.execute(db.select(Rat).filter(Rat.rat_number.in_(possibleMates)).order_by(cast(Rat.rat_number, Integer).desc())).scalars()   

            return render_template("breedingpairs.html", form=form, query=query, showMateDropdown=True, num=ratNumber, errorText="", user=current_user.username, admin=admin)
    return render_template("breedingpairs.html", form=form, user=current_user.username, admin=admin)

@app.route("/recordpairing<num>", methods=["GET", "POST"])
@login_required
def recordPairing(num):
    admin = Admins.query.get(current_user.username)
    if(admin == None):
        return redirect(url_for("accessdenied"))
    if( request.method == "POST"):
        #print("date of pairing is: " + str(form.dateOfPairing.data) )
        dateOfPairing = datetime.date(datetime.strptime(request.form.get("dateOfPairing"), "%Y-%m-%d"))
        print(str(dateOfPairing))
        if(isDateInBounds(dateOfPairing) != "ok"):
            errorText="Error: date of pairing is " + isDateInBounds(dateOfPairing) + "."
            return render_template("breedingpairs.html", form=GenerateBreedingPairsForm(), showMateDropdown=False, errorText=errorText, user=current_user.username, admin=admin)  

        rat = db.session.query(Rat).filter(Rat.rat_number == num).one()  
        rat.current_partner = request.form.get("mateDropdown")
        rat.last_paired_date = dateOfPairing
        rat.num_times_paired = rat.num_times_paired + 1

        #TODO: *shouldn't* need to modify the rat's old partner here.  Test and verify
        newPartner = db.session.query(Rat).filter(Rat.rat_number == request.form.get("mateDropdown")).one()
        newPartner.current_partner = rat.rat_number
        newPartner.last_paired_date = dateOfPairing
        newPartner.num_times_paired = newPartner.num_times_paired + 1
        db.session.commit()
        return redirect(url_for("search"))
    return redirect(url_for("search"))

@app.route("/search")
@login_required
def search():
    updateAges()
    form = FamilyTreeForm()   
    query = db.session.execute(db.select(Rat).order_by(cast(Rat.rat_number, Integer).desc())).scalars()
    #print(query.all())
    # Whatever you do, do NOT run print(query.all()) before the return statement
    # that'll clear out the query variable or something, because then read.html 
    # will be blank
    admin = (Admins.query.get(current_user.username) != None)
    return render_template("search.html", query = query, form=form, user=current_user.username, admin=admin)

@app.route("/familytree<num>", methods=["GET", "POST"])
@login_required
def showFamilyTree(num):
    if(request.method == "POST"):
        rat = db.session.query(Rat).filter(Rat.rat_number == num).one()
        # note: don't need to validate that the rat exists here because this is accessed
        # from the search page, which only contains rats that are already in the database
        admin = (Admins.query.get(current_user.username) != None)
        return render_template("FamilyTree.html", rat=rat, user=current_user.username, admin=admin)
    else:
        return redirect(url_for(num))
    
@app.route("/editrecords", methods=['GET', 'POST'])
@login_required
def editRecords():
    admin = Admins.query.get(current_user.username)
    if(admin == None):
        return redirect(url_for("accessdenied"))
    form = EditRatForm()
    
    if(request.method == "POST"):
        number = str(form.number.data) + form.sex.data[0]
        isValidRat = ratIDCheck(number)
        if (not isValidRat):
            errorText = "Error: rat does not exist"
            return render_template("editrecords.html", form=form, user=current_user.username, errorText=errorText, editSpecificRat=False, admin=admin)
        else:
            return render_template("editrecords.html", form=form, user=current_user.username, editSpecificRat=True, num=number, admin=admin)
    return render_template("editrecords.html", form=form, user=current_user.username, editSpecificRat=False, admin=admin)


@app.route("/editrecord<num>", methods=['GET', 'POST'])
@login_required
def editSpecificRat(num):
    admin = Admins.query.get(current_user.username)
    if(admin == None):
        return redirect(url_for("accessdenied"))
    if(request.method == "POST"):
        rat = db.session.query(Rat).filter(Rat.rat_number == num).one()
        if( request.form.get("birthdate") != ''):
            formBirthdate = datetime.date(datetime.strptime(request.form.get("birthdate"), "%Y-%m-%d"))
            isValidBirthdate = isDateInBounds(formBirthdate)
            if(isValidBirthdate == "ok") :
                rat.birthdate = formBirthdate
                delta = relativedelta.relativedelta(date.today(), formBirthdate)
                age = delta.months + (delta.years * 12)
                rat.age_months = age
                db.session.commit()
            else:
                errorText = "Error: a rat cannot be born " + isValidBirthdate + "."
                return render_template("editrecords.html", form=EditRatForm(), user=current_user.username, errorText=errorText, admin=admin)
        
        print(request.form.get("last_paired_date"))
        if(request.form.get("last_paired_date") != ''):
            formPairedDate = datetime.date(datetime.strptime(request.form.get("last_paired_date"), "%Y-%m-%d"))

            isValidPairedDate = isDateInBounds(formPairedDate)
            if(rat.current_partner == '00X') :
                errorText = "Error: Rat must be paired to edit pairing or litter info."
                return render_template("editrecords.html", form=EditRatForm(), user=current_user.username, errorText=errorText, admin=admin)
            if(isValidPairedDate != "ok") :
                errorText = "Error: a rat cannot be paired " + isValidPairedDate + "."
                return render_template("editrecords.html", form=EditRatForm(), user=current_user.username, errorText=isValidPairedDate, admin=admin)
            if(formPairedDate < (rat.birthdate + relativedelta.relativedelta(months=3)) ):
                errorText = "Error: this paired date is before the rat was 3 months old and eligible to breed."
                return render_template("editrecords.html", form=EditRatForm(), user=current_user.username, errorText=errorText, admin=admin)
            else:
                rat.last_paired_date = formPairedDate

        if(request.form.get("last_litter_date") != ''):
            formLitterDate = datetime.date(datetime.strptime(request.form.get("last_litter_date"), "%Y-%m-%d"))

            isValidLitterDate = isDateInBounds(formLitterDate)
            if(rat.current_partner == '00X') :
                errorText = "Error: Rat must be paired to edit pairing or litter info."
                return render_template("editrecords.html", form=EditRatForm(), user=current_user.username, errorText=errorText, admin=admin)
            if(isValidLitterDate != "ok") :
                errorText = "Error: cannot record a litter " + isValidLitterDate + "."
                return render_template("editrecords.html", form=EditRatForm(), user=current_user.username, errorText=errorText, admin=admin)
            if(formLitterDate < (rat.birthdate + relativedelta.relativedelta(months=3)) ):
                errorText = "Error: this litter date is before the rat was 3 months old and eligible to breed."
                return render_template("editrecords.html", form=EditRatForm(), user=current_user.username, errorText=errorText, admin=admin)
            else:
                rat.last_litter_date = formLitterDate
        
        if(request.form.get("weaned_date") != ''):
            formWeanedDate = datetime.date(datetime.strptime(request.form.get("weaned_date"), "%Y-%m-%d"))

            isValidWeanedDate = weanedDateCheck(rat.birthdate, formWeanedDate)
            if(isValidWeanedDate != "ok") :
                return render_template("editrecords.html", form=EditRatForm(), user=current_user.username, errorText=isValidWeanedDate, admin=admin)
            else:
                rat.weaned_date = formWeanedDate
                db.session.commit()
        
        if(request.form.get("num_times_paired") != ''):
            if(rat.current_partner == '00X') :
                errorText = "Error: Rat must be paired to edit pairing or litter info."
                return render_template("editrecords.html", form=EditRatForm(), user=current_user.username, errorText=errorText, admin=admin)
            else :
                rat.num_times_paired = request.form.get("num_times_paired")
        
        if(request.form.get("num_litters") != ''):
            if(rat.current_partner == '00X') :
                errorText = "Error: Rat must be paired to edit pairing or litter info."
                return render_template("editrecords.html", form=EditRatForm(), user=current_user.username, errorText=errorText, admin=admin)
            elif(request.form.get("num_litters") == 0):
                if(rat.sex == "Male"):
                    if (sireCheck(rat.rat_number)):
                        errorText="Error: rat is the sire of at least 1 other rat in the colony, it cannot have 0 litters."
                        return render_template("editrecords.html", form=EditRatForm(), user=current_user.username, errorText=errorText, admin=admin)
                if(rat.sex == "Female"):
                    if(damCheck(rat.rat_number)):
                        errorText="Error: rat is the dam of at least 1 other rat in the colony, it cannot have 0 litters."
                        return render_template("editrecords.html", form=EditRatForm(), user=current_user.username, errorText=errorText, admin=admin)
            else :
                rat.num_litters = request.form.get("num_litters")
                db.session.commit()
        
        if(request.form.get("date_added_to_colony") != ''):
            formDateAddedToColonyDate = datetime.date(datetime.strptime(request.form.get("date_added_to_colony"), "%Y-%m-%d"))

            isValidAddedToColonyDate = addedToColonyDateCheck(rat.birthdate, rat.weaned_date, formDateAddedToColonyDate)
            if(isValidAddedToColonyDate != "ok") :
                return render_template("editrecords.html", form=EditRatForm(), user=current_user.username, errorText=isValidAddedToColonyDate, admin=admin)
            else:
                rat.date_added_to_colony = formDateAddedToColonyDate
        
        if(request.form.get("num_litters_with_defects") != ''):
            if(rat.current_partner == '00X') :
                errorText = "Error: Rat must be paired to edit pairing or litter info."
                return render_template("editrecords.html", form=EditRatForm(), user=current_user.username, errorText=errorText, admin=admin)
            if(rat.num_litters == 0):
                errorText = "Error: rat has not been involved in any litters, it cannot have had any litters with defects."
                return render_template("editrecords.html", form=EditRatForm(), user=current_user.username, errorText=errorText, admin=admin)
            else:
                rat.num_litters_with_defects = request.form.get("num_litters_with_defects")
        
        if(request.form.get("experiment") != rat.experiment):
            rat.experiment = request.form.get("experiment")
        
        formSire = request.form.get("sire")
        formDam = request.form.get("dam")
        if(request.form.get("supplierRat") == "yes" and ( formSire != '' or formDam != '')):
            errorText = "Error: a rat cannot be from the supplier and from the colony."
            return render_template("editrecords.html", form=EditRatForm(), user=current_user.username, errorText=errorText, admin=admin)

        if(request.form.get("supplierRat") == "yes"):
            rat.sire = "EN"
            rat.dam = "EN"
            rat.rat_name = rat.rat_number + "ENEN"
            fillGenealogyData(rat.rat_number, "EN", "EN")
        elif (formSire != '' and formDam != ''):
            sire = str(formSire) + "M"
            dam = str(formDam) + "F" 
            if(sire == rat.rat_number or dam == rat.rat_number):
                errorText = "Error: a rat cannot be its own sire or dam."
                return render_template("editrecords.html", form=EditRatForm(), user=current_user.username, errorText=errorText, admin=admin)
            if(verifySireAndDam(sire, dam)):
                rat.sire = sire
                rat.dam = dam
                newName = rat.rat_number + sire[:-1] + dam[:-1]
                rat.rat_name = newName
                fillGenealogyData(rat.rat_number, sire, dam)
            else:
                errorText = "Error: the updated sire and dam are an invalid pairing."
                return render_template("editrecords.html", form=EditRatForm(), user=current_user.username, errorText=errorText, admin=admin)
        elif (formSire != ''):
            sire = str(formSire) + "M"
            if(sire == rat.rat_number):
                errorText = "Error: a rat cannot be its own sire."
                return render_template("editrecords.html", form=EditRatForm(), user=current_user.username, errorText=errorText, admin=admin)
            if(verifySireAndDam(sire, rat.dam)):
                rat.sire = sire
                rat.rat_name = rat.rat_number + sire[:-1] + rat.dam
                fillGenealogyData(rat.rat_number, sire, rat.dam)
            else:
                errorText = "Error: the updated sire is an invalid pairing with the rat's dam."
                return render_template("editrecords.html", form=EditRatForm(), user=current_user.username, errorText=errorText, admin=admin)
        elif (formDam != ''):
            dam = str(formDam) + "F"
            if(dam == rat.rat_number):
                errorText = "Error: a rat cannot be its own dam."
                return render_template("editrecords.html", form=EditRatForm(), user=current_user.username, errorText=errorText, admin=admin)
            if(verifySireAndDam(rat.sire, dam)):
                rat.dam = dam
                rat.rat_name = rat.rat_number + rat.sire + dam[:-1]
                fillGenealogyData(rat.rat_number, rat.sire, dam)
            else:
                errorText = "Error: the updated dam is an invalid pairing with the rat's sire."
                return render_template("editrecords.html", form=EditRatForm(), user=current_user.username, errorText=errorText, admin=admin)
        
        if(request.form.get("status") != "Empty" and request.form.get("status") != rat.manner_of_death):
            rat.manner_of_death = request.form.get("status")
            if(request.form.get("status") == "Euthanized" or request.form.get("status") == "Unexpected"):
                rat.death_date = date.today()
                if(ratIDCheck(rat.current_partner)):
                    partner = Rat.query.get(rat.current_partner)
                    partner.current_partner = "DEC"
            if(request.form.get("status") == "Transferred"):
                if(ratIDCheck(rat.current_partner)):
                    partner = Rat.query.get(rat.current_partner)
                    partner.current_partner = "DEC"
            elif(request.form.get("status") == "Transferred" or request.form.get("status") == "Alive"):
                rat.death_date = date(1900, 1, 1) # to be consistent with displaying N/A on search screen
         
        db.session.commit()
        
        return render_template("editrecords.html", form=EditRatForm(), user=current_user.username, admin=admin)
    else:
        return render_template("editrecords.html", form=EditRatForm(), user=current_user.username, admin=admin)

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
    admin = Admins.query.get(current_user.username)
    if(admin == None):
        return redirect(url_for("accessdenied"))
    form = RecordTransferForm()
    
    if(request.method == "POST") :
        rat_number =  str(form.number.data) + form.sex.data[0]
        isValidRat = ratIDCheck(rat_number)
        if(not isValidRat):
            errorText = "Error: Not an existing rat."
            return render_template("recordtransfer.html", form=form, user=current_user.username, errorText=errorText, admin=admin)
        else:
            rat = Rat.query.get(rat_number)
            if(rat.manner_of_death != "Alive"):
                errorText = "Error: can't transfer a deceased or transferred rat."
                return render_template("recordtransfer.html", form=form, user=current_user.username, errorText=errorText, admin=admin)
            rat.manner_of_death = "Transferred"
            if(ratIDCheck(rat.current_partner)):
                partner = Rat.query.get(rat.current_partner)
                partner.current_partner = "DEC"
            db.session.commit()
        
        return render_template("recordtransfer.html", form=form, user=current_user.username, admin=admin)
    else:
        return render_template("recordtransfer.html", form=form, user=current_user.username, admin=admin)

@app.route("/reportlitter", methods=['POST', 'GET'])
@login_required
def reportLitter():
    admin = Admins.query.get(current_user.username)
    if(admin == None):
        return redirect(url_for("accessdenied"))
    form = ReportLitterForm()
    
    if(request.method == "POST") :
        sire_number = str(form.sire.data) + "M"
        dam_number = str(form.dam.data) + "F"
        if(not (ratIDCheck(sire_number) and ratIDCheck(dam_number))):
            errorText = "Error: this is not a valid pairing."
            return render_template("reportlitter.html", form=form, user=current_user.username, errorText=errorText, admin=admin)
            # Not restricting to only rats that are currently paired with each other
            # in case the rat had a litter, then the stakeholder swapped breeding pairs
            # before they got the chance to record the litter.  If I had time to make a 
            # pairing table I would restrict to sire and dam paired together 
            # within the past month, but unfortunately, I don't.
        isValidDate = isDateInBounds(form.litterDate.data)
        if( isValidDate != "ok"):
            errorText = "Error: can't report a litter born " + isValidDate + "."
            return render_template("reportlitter.html", form=form, user=current_user.username, errorText=errorText, admin=admin)
        else:
            sire = Rat.query.get(sire_number)
            dam = Rat.query.get(dam_number)

            if(sire.manner_of_death != "Alive"):
                errorText = "Error: can't report a litter if the sire is deceased or transferred."
                return render_template("reportlitter.html", form=form, user=current_user.username, errorText=errorText, admin=admin)
            if(dam.manner_of_death != "Alive"):
                errorText = "Error: can't report a litter if the dam is deceased or transferred."
                return render_template("reportlitter.html", form=form, user=current_user.username, errorText=errorText, admin=admin)

            sire.num_litters = sire.num_litters + 1
            dam.num_litters = dam.num_litters + 1
            sire.last_litter_date = form.litterDate.data
            dam.last_litter_date = form.litterDate.data
            #References drop down menu options for if litter has defects or not
            if(form.reportLittersWithDefects.data == "Yes") :
                sire.num_litters_with_defects = sire.num_litters_with_defects + 1
                dam.num_litters_with_defects = dam.num_litters_with_defects + 1
        db.session.commit()
    return render_template("reportlitter.html", form=form, user=current_user.username, admin=admin)

@app.route("/reportdeath", methods=['POST', 'GET'])
@login_required
def reportDeath():
    admin = Admins.query.get(current_user.username)
    if(admin == None):
        return redirect(url_for("accessdenied"))
    form = ReportDeathForm()
    
    if(request.method == "POST"):       
        rat_number = str(form.number.data) + form.sex.data[0]
 
        isValidRat = ratIDCheck(rat_number)
        
        if(isValidRat):
            rat = Rat.query.get(rat_number)
            if(rat.manner_of_death != "Alive"):
                errorText = "Error: can't report the death of a deceased or transferred rat."
                return render_template("reportdeath.html", form=form, user=current_user.username, errorText=errorText, admin=admin)
            isValidDate = isDateInBounds(form.deathDate.data)
            if(isValidDate != "ok"):
                errorText = "Can't report a death that happened " + isValidDate + "."
                return render_template("reportdeath.html", form=form, user=current_user.username, errorText=errorText, admin=admin)
            
            rat.manner_of_death = form.mannerOfDeath.data
            if(rat.current_partner != '' and rat.current_partner != "UNK" 
                and rat.current_partner != "DEC" and rat.current_partner != "00X"):
                current_partner = Rat.query.get(rat.current_partner)
                current_partner.current_partner = "DEC"
            db.session.commit()
        else :
            errorText = "Error: Not an existing rat."
            return render_template("reportdeath.html", form=form, user=current_user.username, errorText=errorText, admin=admin)
        return redirect(url_for("search"))
    else:
        return render_template("reportdeath.html", form=form, user=current_user.username, admin=admin)
    
@app.route("/userguide")
@login_required
def userGuide():
    admin = Admins.query.get(current_user.username)
    return render_template("userguide.html", user=current_user.username, admin=admin)

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
    input_rat_ancestor_numbers = [input_rat.sire, input_rat.dam, input_rat.pgsire, input_rat.pgdam, input_rat.mgsire, input_rat.mgdam,
                                  input_rat.pg11sire, input_rat.pg11dam, input_rat.pg12sire, input_rat.pg12dam,
                                  input_rat.mg11sire, input_rat.mg11dam, input_rat.mg12sire, input_rat.mg12dam]  
    
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
        # Also, not excluding children or grandchildren here like I do for colony rats, 
        # because this rat hasn't been paired before, so those won't exist 
        colony_rats_without_partner = db.session.execute(db.select(Rat.rat_number, Rat.sire, Rat.dam, Rat.pgsire, Rat.pgdam, Rat.mgsire, Rat.mgdam, 
                      Rat.pg11sire, Rat.pg11dam, Rat.pg12sire, Rat.pg12dam,
                      Rat.mg11sire, Rat.mg11dam, Rat.mg12sire, Rat.mg12dam).where(
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
            finalDatingPool = compareAncestors(input_rat_ancestor_numbers=input_rat_ancestor_numbers, datingPool=colony_rats_without_partner, input_rat=input_rat)
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
       
    if(swapping_existing_pairs): # case: swapping colony rats (paired rats)
        datingPool = db.session.execute(
            db.select(Rat.rat_number, Rat.sire, Rat.dam, Rat.pgsire, Rat.pgdam, Rat.mgsire, Rat.mgdam, 
                      Rat.pg11sire, Rat.pg11dam, Rat.pg12sire, Rat.pg12dam,
                      Rat.mg11sire, Rat.mg11dam, Rat.mg12sire, Rat.mg12dam).where(
                (Rat.sex != input_rat.sex) &
                (Rat.manner_of_death == "Alive") & 
                (Rat.current_partner != "00X") & # narrow search to only paired rats
                (Rat.rat_number != input_rat.current_partner) & # narrow search to exclude input_rat's current partner                    
                (Rat.age_months >= 3) &
                (Rat.num_litters_with_defects <= 2 ) &
                (Rat.sire != "XX") & # prevent unknown sire/dam rats from being paired per stakeholder
                (Rat.dam != "XX") &
                (Rat.sire != "5X") &
                (Rat.dam != "5X") &
                (Rat.dam != input_rat.rat_number) & # prevent the rat's children from being put into the dating pool
                (Rat.sire != input_rat.rat_number) & 
                (Rat.pgsire != input_rat.rat_number) & # prevent the rat's grandchildren from being put into the dating pool
                (Rat.pgdam != input_rat.rat_number) & 
                (Rat.mgsire != input_rat.rat_number) & 
                (Rat.mgdam != input_rat.rat_number)
            )
        ).all()
        printDatingPool(datingPool, input_rat.rat_number)
        
    else: # case: input is a colony rat and we're adding spare (new, unpaired) rat to colony
        datingPool = db.session.execute(
            db.select(Rat.rat_number, Rat.sire, Rat.dam, Rat.pgsire, Rat.pgdam, Rat.mgsire, Rat.mgdam).where(
                (Rat.sex != input_rat.sex) &
                (Rat.manner_of_death == "Alive") & 
                (Rat.current_partner == "00X") & # search for unpaired rats
                (Rat.age_months >= 3) &
                (Rat.num_litters_with_defects <= 2 ) & 
                (Rat.sire != "XX") & # prevent unknown sire/dam rats from being paired per stakeholder
                (Rat.dam != "XX") &
                (Rat.sire != "5X") &
                (Rat.dam != "5X") &
                (Rat.dam != input_rat.rat_number) & # prevent the rat's children from being put into the dating pool
                (Rat.sire != input_rat.rat_number) &
                (Rat.pgsire != input_rat.rat_number) & # prevent the rat's grandchildren from being put into the dating pool
                (Rat.pgdam != input_rat.rat_number) & 
                (Rat.mgsire != input_rat.rat_number) & 
                (Rat.mgdam != input_rat.rat_number)
            )
        ).all()
        
    # ENEN rats are a special case, they have no up-tree to check because of their ancestry
    if(input_rat.sire == "EN" and input_rat.dam == "EN"):
        finalDatingPool = [ rat[0] for rat in datingPool]
        return finalDatingPool
    else: 
        # colony-born rat, so have to check the rat's up-tree (compare ancestors) to get the final dating pool
        print("datingPool = ")
        printDatingPool(datingPool, input_rat.rat_number)

        finalDatingPool = compareAncestors(datingPool=datingPool, input_rat_ancestor_numbers=input_rat_ancestor_numbers, input_rat=input_rat)
        if (len(finalDatingPool) == 0): # no unrelated rats error
            return "ERROR: there are no unrelated paired rats that " + input_rat.rat_number + " can be paired with."
        else:
            return finalDatingPool
    return finalDatingPool



# helper function to check if a rat shares common ancestors with potential mates
# checking up-tree from the perspective of the input rat
def compareAncestors(datingPool, input_rat_ancestor_numbers, input_rat):
   
    finalDatingPool = []
    
    print("input rat ancestors = " + str(input_rat_ancestor_numbers))
    printDatingPool(datingPool, input_rat.rat_number)
    
    for rat in datingPool:
        finalDatingPool.append(rat.rat_number)
        
        # check parents and grandparents real quick before going any farther
        if rat.rat_number in input_rat_ancestor_numbers[:3]:
            print(rat.rat_number + " rejected because it's in the list of input rat's parents and grandparents: " + str(input_rat_ancestor_numbers))
            finalDatingPool.remove(rat.rat_number)
            continue
        
        potential_partner_ancestors = [rat.sire, rat.dam, rat.pgsire, rat.pgdam, rat.mgsire, rat.mgdam,
                                       rat.pg11sire, rat.pg11dam, rat.pg12sire, rat.pg12dam, 
                                       rat.mg11sire, rat.mg11dam, rat.mg12sire, rat.mg12dam]
        print("looking at potential partner " + rat.rat_number + ", ancestors = " + str(potential_partner_ancestors))
        potential_partner_great_grandparents = [rat.pg11sire, rat.pg11dam, rat.pg12sire, rat.pg12dam, 
                                       rat.mg11sire, rat.mg11dam, rat.mg12sire, rat.mg12dam]
        
        for ancestor in potential_partner_ancestors:
            
            # technically a rat can breed with their great-grandparent because that's 3 generations apart
            if ancestor in potential_partner_great_grandparents:
                continue
            
            # use great-grandparent info to rule out related grandparents
            elif ancestor != "EN" and ancestor in input_rat_ancestor_numbers:
                print(rat.rat_number + " rejected because its ancestor " + ancestor + " is in the list of input rat's ancestors: " + str(input_rat_ancestor_numbers))
                finalDatingPool.remove(rat.rat_number)
                break
        
    
    return finalDatingPool

 
                
                




# helper function to compare birthdates for a given rat vs their potential dating pool
# this rules out common ancestors
def compareBirthdates(datingPool, input_rat_ancestor_numbers, input_rat):
   
    finalDatingPool = []

    input_rat_ancestor_birthdays = []
    inputRat50sAncestorsFlag = False
    
    # STEP 1: get the ancestor's birthdates. Include EN in 2nd if stmt b/c grandparents could be EN
    for ancestor in input_rat_ancestor_numbers:
        pattern = re.compile(r'5\d[MF]|5X|4[78][MF]')
        isAncestorIn50sOr5X = pattern.match(ancestor)

        # TODO shouldn't this if stmt be isAncestorIn50sOr5X != None, set true, break?
        if(ancestor == "5X" or isAncestorIn50sOr5X != None):
            inputRat50sAncestorsFlag = True
        
        # don't query for unreachable data
        if(ancestor != "XX" and ancestor != "5X" and ancestor != "EN"):
            data = Rat.query.get(ancestor)
            # don't include ENEN rat birthdates in the ancestor birthdate list, otherwise it'll exclude
            # unrelated descendants of ENEN rats (b/c ENEN rats have the same birthdate) 
            if(data.rat_name[-4:] != "ENEN"):  
                input_rat_ancestor_birthdays.append(data.birthdate)

    print("input rat ancestors = " + str(input_rat_ancestor_numbers))
    printDatingPool(datingPool, input_rat.rat_number)
    for rat in datingPool:
        finalDatingPool.append(rat.rat_number)
        potential_partner_ancestors = [rat.sire, rat.dam, rat.pgsire, rat.pgdam, rat.mgsire, rat.mgdam]
        print("looking at " + rat.rat_number)
        print(rat.rat_number + " ancestors: " + str(potential_partner_ancestors))
        
        if rat.rat_number != "EN" and rat.rat_number in input_rat_ancestor_numbers:
            print(rat.rat_number + " rejected because it's in the list of input rat's ancestors: " + str(input_rat_ancestor_numbers))
            finalDatingPool.remove(rat.rat_number)
            continue

        for ancestor in potential_partner_ancestors: 
            
            # previous/was working: ancestor != "EN" and ancestor in input_rat_ancestor_numbers
            # step 1: assume complete information and look for common ancestors by number
            # ignore XX, 5X, EN because that will cause false negatives
            # If they share an ancestor, reject and break
            if ( ancestor != "XX" and ancestor != "5X" and ancestor != "EN" and ancestor in input_rat_ancestor_numbers ):
                print(rat.rat_number + " rejected because its ancestor " + ancestor + " is in the list of input rat's ancestors: " + str(input_rat_ancestor_numbers))
                finalDatingPool.remove(rat.rat_number)
                break
        
            # step 2: incomplete data part 1: the 5X exception rejection station
            if(inputRat50sAncestorsFlag == True):
                pattern = re.compile(r'5\d[MF]|5X|4[78][MF]')
                isPartnerAncestorIn50sOr5X = pattern.match(ancestor)
                if(isPartnerAncestorIn50sOr5X != None):
                    print(rat.rat_number + " rejected because " + ancestor + " matches " + str(isPartnerAncestorIn50sOr5X))
                    finalDatingPool.remove(rat.rat_number)
                    break
            
            # step 3: incomplete data part 2
            # only compare birthdates if there's incomplete data in input_rat_partner_birthdays (which is why the != 6 thing)
            # otherwise it should've had complete data and been handled in step 1
            # still have check for if ancestor != 5X because the if stmt above only activates
            # if input_rat has 50s or 5X ancestors, not if potential_partner has a 5X ancestor
            if(len(input_rat_ancestor_birthdays) != 6 and ancestor != "XX" and ancestor != "5X" and ancestor != "EN" and ancestor != None):
                partner_ancestor_birthdate = Rat.query.get(ancestor).birthdate
                #print(ancestor + " " + str(partner_ancestor_birthdate))
                if(partner_ancestor_birthdate in input_rat_ancestor_birthdays or partner_ancestor_birthdate == input_rat.birthdate):
                    print(rat.rat_number + " rejected because " + ancestor + " birthdate " + str(partner_ancestor_birthdate))
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
    if (number in ratNumbers or number == "EN"):
        return True
    else:
        return False


# this combines sireCheck, damCheck, and enCheck
# does NOT verify that they are alive, only that they 
# are valid rat numbers and have had litters so could be the parents of a rat
# unfortunately, due to not having time to implement a pairing table to track pairings,
# this is the best I can do
def verifySireAndDam(sire, dam):
    if(sire == "EN" and dam == "EN"): # case ENEN rats
        return True
    if(sire == "EN" or dam == "EN"): # if one rat is EN but not the other, error
        return False
    if(not ratIDCheck(sire) or not ratIDCheck(dam)): # case one of the rats is invalid
        return False
    sire = Rat.query.get(sire)
    dam = Rat.query.get(dam)
    
    # can't verify that sire and dam were paired *together* b/c no pairing table
    # so doing the best I can with the information I have.
    if(sire.current_partner == "00X" or dam.current_partner == "00X" or 
       sire.num_litters == 0 or dam.num_litters == 0):
        return False
    return True

#Check to ensure date is not in the future
def isDateInBounds(input_date) :
    
    futureBlock = date.today() + timedelta(days=1)
    pastBlock = date.today() + relativedelta.relativedelta(years=-10)
      
    if (input_date >= futureBlock) :
        return "in the future"
    if(input_date <= pastBlock) :
        return "more than 10 years in the past"
    return "ok"
    
def weanedDateCheck(birthdate, weanedDate):
    if(isDateInBounds(birthdate) != "ok"):
        return "Error: a rat cannot be born " + isDateInBounds(birthdate) + "."
    if(isDateInBounds(weanedDate) != "ok"):
        return "Error: a rat cannot be weaned " + isDateInBounds(weanedDate) + "."
    if( weanedDate < (birthdate + relativedelta.relativedelta(weeks=3)) ):
        return "Error: a rat's weaned date must be at least 3 weeks after it is born."
    return "ok"

def addedToColonyDateCheck(birthdate, weanedDate, addedToColonyDate): 
    if(isDateInBounds(addedToColonyDate) != "ok"):
        return "Error: a rat cannot be added to the colony " + isDateInBounds(addedToColonyDate) + "."
    
    if( weanedDateCheck(birthdate, weanedDate) == "ok" and
       weanedDate <= addedToColonyDate ):
        return "ok"
    return "Error: a rat must be weaned before it is added to the colony."

def sireCheck(sire):
    ratCheck = [sire for sire, in db.session.query(Rat.sire)]
    if(sire in ratCheck) :
        return True
    else :
        return False
        
def damCheck(dam):
    ratCheck = [dam for dam, in db.session.query(Rat.dam)]
    if(dam in ratCheck) :
        return True
    else :
        return False
    
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
