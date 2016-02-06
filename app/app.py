from flask import Flask, render_template, redirect, url_for, flash
from flask import g
from flask import Response
from flask import request
from flask import jsonify
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
    enddate=request.form.get("enddate")
    endhour=request.form.get("endhour")
    endminute=request.form.get("endminute")
    endampm=request.form.get("endampm")
    category=request.form.get("category")
    starttimestamp=datetime.strptime(startdate + " " + starthour + ":" + startminute + startampm,"%m/%d/%Y %I:%M%p")
    endtimestamp=datetime.strptime(enddate + " " + endhour + ":" + endminute + endampm,"%m/%d/%Y %I:%M%p")
    #starttimestamp=datetime.strptime(startdate + " " + starthour + ":" + startminute + " " + startampm, '%m/%d/%Y %I:%M %p')
    insert="INSERT INTO ToDodb.todos(title, description, starttime, endtime, categoryid) VALUES ('{title}', '{description}', '{starttimestamp}', '{endtimestamp}', '{category}')".format(
                                                                                                                                                                               title=title, description=description, starttimestamp=starttimestamp, endtimestamp=endtimestamp, category=category)
    g.cursor.execute(insert)
    g.conn.commit()
    
    
@app.route("/displayevent", methods=['GET'])
def displayevent():
    return render_template('displayevent.html')

@app.route("/getevents", methods=['GET'])
def selectmonth():
    begin = request.args['begindate']
    end = request.args['enddate']
    gettingevents = query_db("SELECT title, description, starttime, categoryid from todos where starttime > '{starttime}' and starttime < '{endtime}'".format(starttime=begin, endtime=end))
    for event in gettingevents:
        starttime=event['starttime']
        event['date']=starttime.strftime('%Y-%m-%d %I:%M %p')
    return jsonify({'data': gettingevents})
    
    
if __name__ == "__main__":
  app.run(debug=True)
  
  
