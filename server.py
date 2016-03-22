import os
from flask import Flask, render_template, request
import random
import psycopg2
import psycopg2.extras

app = Flask(__name__)

def connectToDB():
    connectionString = 'dbname=hephaestus user=heph password=4SrGY9gPFU72aJxh host=localhost'
    try:
        return psycopg2.connect(connectionString)
    except:
        print("Can't connect to database.")

@app.route('/')
def mainIndex():
    return render_template("index.html");
    
#@app.route('/article/'+world+'/'+category+'/'+article)
@app.route('/article')
def article():
    return render_template("article.html");
    
#@app.route('/user/'+user)
app.route('/user')
def user():
    return render_template("user.html");

if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)), debug = True)