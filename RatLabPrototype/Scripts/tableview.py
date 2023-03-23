@app.route('/tableview')
def index():
    rows = Units.query.all()
    return render_template('tableview.html',
                            title='Overview',
                            rows=rows)