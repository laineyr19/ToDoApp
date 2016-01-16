from flask import Flask, render_template, redirect, url_for, flash
from flask import g
from flask import Response
from flask import request
import json
import MySQLdb
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'some_secret'

@app.before_request
def db_connect():
  g.conn = MySQLdb.connect(host='localhost',
                              user='root',
                              passwd='WugaWuga19',
                              db='ToDodb')
  g.cursor = g.conn.cursor()

@app.after_request
def db_disconnect(response):
  g.cursor.close()
  g.conn.close()
  return response

def query_db(query, args=(), one=False):
  g.cursor.execute(query, args)
  rv = [dict((g.cursor.description[idx][0], value)
  for idx, value in enumerate(row)) for row in g.cursor.fetchall()]
  return (rv[0] if rv else None) if one else rv
 
@app.route("/")
def hello():
  return "Hello World!"
  
@app.route("/addevent", methods=['GET'])
def adding_event():
    category = query_db("SELECT * FROM ToDodb.event_type")
    return render_template('add_event.html', resp={'category':category})

@app.route("/saveevent", methods=['POST'])
def saving_event():
    title=request.form.get("title")
    description=request.form.get("description")
    startdate=request.form.get("startdate")
    starthour=request.form.get("starthour")
    startminute=request.form.get("startminute")
    startampm=request.form.get("startampm")
    endhour=request.form.get("endhour")
    endminute=request.form.get("endminute")
    endampm=request.form.get("endampm")
    category=request.form.get("category")
    import pdb; pdb.set_trace()
    starttimestamp=datetime.strptime(startdate + " " + starthour + ":" + startminute + startampm,'%m/%d/%Y %I:%M%p')
    #starttimestamp=datetime.strptime(startdate + " " + starthour + ":" + startminute + " " + startampm, '%m/%d/%Y %I:%M %p')
    return datetime.now()

if __name__ == "__main__":
  app.run(debug=True)
  
  
