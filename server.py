import os
from flask import Flask, render_template, request
import random
import psycopg2
import psycopg2.extras

app = Flask(__name__)

def formatDate(date):
    #Get those months
    months = ['Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec'];
    newDate = "";
    
    splitDate = str(date).split("-");
    newDate += months[int(splitDate[1])-1];
    newDate += " " + str(splitDate[2]);
    newDate += ", " + str(splitDate[0]);
    
    return newDate;
    
def connectToDB():
    connectionString = 'dbname=hephaestus user=heph password=4SrGY9gPFU72aJxh host=localhost'
    try:
        return psycopg2.connect(connectionString)
    except:
        print("Can't connect to database.")

@app.route('/')
def mainIndex():
    return render_template("index.html");
    
@app.route('/article')
def article():
    return render_template("article.html");
    
@app.route('/user/<username>')
def user(username):
    #Database connection
    conn = connectToDB()
    cur = conn.cursor()
    
    #Get the user info for their page
    try:
        cur.execute("""SELECT username, joindate, (SELECT email FROM member WHERE dispemail IS True AND LOWER(username) = LOWER('%s')) email FROM member WHERE LOWER(username) = LOWER('%s');""" %(username, username))
        results = cur.fetchall()
        results = list(results[0]);
        results[1] = formatDate(results[1]);
    except:
        print("Failed to execute the following: ")
        print(cur.mogrify("""SELECT username, joindate, (SELECT email FROM member WHERE dispemail IS True AND LOWER(username) = LOWER('%s')) email FROM member WHERE LOWER(username) = LOWER('%s');""" %(username, username)))
        results = None;
    
    color="#aaaaaa";
    
    return render_template("user.html", user_info = results, color=color);

if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)), debug = True)