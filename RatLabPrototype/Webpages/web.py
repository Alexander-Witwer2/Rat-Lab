from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy as sa

db = sa()
app = Flask(__name__)

class Units(db.Model):  
    id = sa.Column(sa.String, primary_key = True)
    name = sa.Column(sa.String)
    sex = sa.Column(sa.String)
    birthdate = sa.Column(sa.Date)
    weaned = sa.Column(sa.Date)
    last_pair = sa.Column(sa.Date)
    last_litter = sa.Column(sa.Date)
    times_paired = sa.Column(sa.Integer)
    litter_num = sa.Column(sa.Integer)
    date_added = sa.Column(sa.Date)
    defect_litter = sa.Column(sa.Integer)
    experiment = sa.Column(sa.SmallInteger)

@app.route('/')
def index():
    rows = Units.query.all()
    return render_template('search.html',title='Overview', rows=rows)
