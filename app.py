from flask import Flask, render_template
import sqlite3
app = Flask(__name__)


@app.route('/')
def index():  # put application's code here
    return render_template("index.html")

@app.route('/index')
def home():
    # return render_template("index.html")
    return index()

@app.route('/movie')
def movie():
    datalist = []
    con = sqlite3.connect("movie.db")
    cursor = con.cursor()
    sql = '''
        select  * from  movie250
    '''
    data = cursor.execute(sql)
    for item in data:
        datalist.append(item)
    cursor.close()
    con.close()
    return render_template("movie.html", movies=datalist)

@app.route('/score')
def score():
    score = []
    num = []
    con = sqlite3.connect("movie.db")
    cursor = con.cursor()
    sql = '''
        select  score, count(score) from  movie250 group by score
    '''
    data = cursor.execute(sql)
    for item in data:
        score.append(item[0])
        num.append(item[1])

    cursor.close()
    con.close()
    return render_template("score.html", score=score, num=num)

@app.route('/word')
def word():
    return render_template("word.html")

if __name__ == '__main__':
    app.run()
