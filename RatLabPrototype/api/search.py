import mariadb
import json
import flask
from flask import request
from flask import Blueprint

search = Blueprint('search', __name__)

# connection parameters
conn_params= {
    "user" : "test",
    "password" : "ratlab!!",
    "host" : "capstone6.cs.kent.edu",
    "database" : "test1"
}

@search.route('/api/search', methods=['GET', 'POST', 'PUT', 'DELETE'])
def index():
    # Establish a connection
    connection = mariadb.connect(**conn_params)

    # grab curson
    cursor = connection.cursor()

    # create empty JSON data
    json_data = []
    
    if request.method == 'GET':

        # Retrieve data
        cursor.execute("SELECT * FROM rats")
        
        row_headers = [x[0] for x in cursor.description]
        row_values = cursor.fetchall()
        for result in row_values:
            json_data.append(dict(zip(row_headers, result)))
    
    return json.dumps(json_data), 200, {'ContentType':'application/json'}


    # print content
    #row= cursor.fetchall()
    #print(*row, sep=' ')

    # free resources
    #cursor.close()
    #connection.close()
