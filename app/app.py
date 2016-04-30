from flask import Flask, render_template, redirect, url_for, flash
from flask import g
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
    flash("Event Saved!")
    return redirect(url_for('displayevent'))
    
    
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
        query = ("SELECT id, title, description, starttime, endtime, categoryid FROM ToDodb.todos where id= '{a}'".format(a=id)) #var query gets bunch of stuff from db w/ right id
        result = query_db(query)

        #below is for starttime

        d = result[0]['starttime']
        result[0]['startmonth'] = str(d.month)
        result[0]['startday'] = d.day
        result[0]['startyear'] = d.year
        result[0]['startdate'] = str(d.month) + "/" + str(d.day) + "/" + str(d.year)


        if d.hour > 12: #if the hour is greater than 12 it's pm
            result[0]['starthour'] = d.hour - 12
            result[0]['startampm'] = 'pm'

        else: #it's am
            result[0]['starthour'] = d.hour
            result[0]['startampm'] = 'am'
        result[0]['startminutes'] = d.minute


        e = result[0]['endtime']
        result[0]['endmonth'] = str(e.month)
        result[0]['endday'] = e.day
        result[0]['endyear'] = e.year
        result[0]['enddate'] = str(e.month) + "/" + str(e.day) + "/" + str(e.year)


        if e.hour > 12:
            result[0]['endhour'] = e.hour - 12
            result[0]['endampm'] = 'pm'

        else:
            result[0]['endhour'] = e.hour
            result[0]['endampm'] = 'am'
        result[0]['endminutes'] = e.minute


        return render_template('editevent.html', resp={'existingevent':result[0], 'category':category})



@app.route("/editevent", methods=['POST'])
def editing_event():
    id=request.form.get("id")
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

    query = ("UPDATE ToDodb.todos "
             "SET title='{title}', "
             "description='{description}', "
             "starttime='{starttimestamp}', "
             "endtime='{endtimestamp}', "
             "categoryid='{category}' "
             ""
             "WHERE id= '{id}'"
             .format(id=id, title=title, description=description, starttimestamp=starttimestamp, endtimestamp=endtimestamp, category=category))


    g.cursor.execute(query)
    g.conn.commit()

    return redirect(url_for('displayevent'))

@app.route("/monthlyevents", methods=['GET'])
def monthlyevents():
    return render_template('monthlyevents.html')

@app.route("/deleteevent", methods=['DELETE'])
def deletingevent():
    id = request.args.get('id')
    query = ("DELETE from ToDodb.todos "
             "WHERE id= '{id}'"
             .format(id=id))

    g.cursor.execute(query)
    g.conn.commit()

    return jsonify({'success': True})
    
if __name__ == "__main__":
  app.run(debug=True)
  
  
