from flask import Flask, render_template, redirect, url_for, flash
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
    id = request.args.get('id')
    category = query_db("SELECT * FROM ToDodb.event_type")
    if id is None:
        return render_template('add_event.html', resp={'category':category})
    else:
        existingevent = query_db("SELECT * FROM ToDodb.todos where id = '{id}'".format(id=id))
        return render_template('editevent.html', resp={'existingevent':existingevent[0], 'category':category})


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
    gettingevents = query_db("SELECT title, description, starttime, endtime, categoryid, id from todos where "
                             "starttime > '{starttime}' and starttime < '{endtime}'".format(starttime=begin, endtime=end))
    for event in gettingevents:
        starttime=event['starttime']
        event['date']=starttime.strftime('%Y-%m-%d %I:%M %p')
    return jsonify({'data': gettingevents})





@app.route("/editevent", methods=['GET'])
def edit_event(): #function called edit_event
    id = request.args.get('id') #var id asks for event id
    category = query_db("SELECT * FROM ToDodb.event_type") #var category gets all categories from database

    if id is None: #if the event doen't exist in the database,
        return render_template('add_event.html') #go to add_event page

    else: #if the event does exist,
        query = ("SELECT id, title, description, starttime, endtime FROM ToDodb.todos where id= '{a}'".format(a=id)) #var query gets bunch of stuff from db w/ right id
        result = query_db(query)

        #below is for starttime

        d = result[0]['starttime']
        result[0]['month'] = str(d.month)
        result[0]['day'] = d.day
        result[0]['year'] = d.year
        result[0]['date'] = str(d.day) + "/" + str(d.month) + "/" + str(d.year)


        if d.hour > 12: #if the hour is greater than 12 it's pm
            result[0]['hour'] = d.hour - 12
            result[0]['ampm'] = 'pm'

        else: #it's am
            result[0]['hour'] = d.hour
            result[0]['ampm'] = 'am'
        result[0]['minutes'] = d.minute


        #below is for endtime

        e = result[0]['endtime']
        result[0]['endmonth'] = str(e.month)
        result[0]['endday'] = e.day
        result[0]['endyear'] = e.year
        result[0]['enddate'] = str(e.day) + "/" + str(e.month) + "/" + str(e.year)


        if e.hour > 12: #if the hour is greater than 12 it's pm
            result[0]['endhour'] = e.hour - 12
            result[0]['endampm'] = 'pm'

        else: #it's am
            result[0]['endhour'] = e.hour
            result[0]['endampm'] = 'am'
        result[0]['endminutes'] = e.minute


        #return render_template('editevent.html', resp={'existingevent':existingevent[0], 'category':category, 'starttime':starttime, 'endtime':endtime,}) #rendering templates is confusing
        return render_template('editevent.html', resp={'existingevent':result[0], 'category':category}) #rendering templates is confusing
#return result to template the usual way


@app.route("/editevent", methods=['POST'])
def editing_event():
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
    '''insert="INSERT INTO ToDodb.todos(title, description, starttime, endtime, categoryid) VALUES ('{title}', '{description}', '{starttimestamp}', '{endtimestamp}', '{category}')".format(
                                                                                                                                                                               title=title, description=description, starttimestamp=starttimestamp, endtimestamp=endtimestamp, category=category)
    g.cursor.execute(insert)
    g.conn.commit()
    '''


    
    
if __name__ == "__main__":
  app.run(debug=True)
  
  
