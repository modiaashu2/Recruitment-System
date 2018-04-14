from __future__ import print_function # In python 2.7
from flask import Flask,render_template,session, request, url_for, redirect
import sys
import MySQLdb
app=Flask(__name__)
app.debug=True


conn = MySQLdb.connect(host = "localhost", user = "root", passwd = "Kanha@123#", db = "HRSystem")
c = conn.cursor()


@app.route('/')
def main():
    return render_template('index.html')

@app.route('/apply/')
def apply():
    return render_template('register.html')


@app.route('/jobs/')
def jobs():
    return render_template('jobs.html')

@app.route('/events/')
def events():
    return render_template('events.html')

global_role = ""
@app.route('/home/')
def dash(role = global_role):
    if global_role == 'admin':
        return render_template('admin.html')
    else:
        return render_template('pos.html')

#insert applicant
@app.route('/addapp/',methods=['POST'])
def register():
    sq="insert into applicant(A_Name,A_mail) values (%s,%s)"
    t=(request.form['name'],request.form.get('email'))
    c.execute(sq,t)
    conn.commit()
    return "inserted"

@app.route('/login/', methods = ['POST','GET'])
def login():
    uname = request.form.get('username')
    pname = request.form.get('password')
    #temp_data=(uname,pname)

    #c.close()
    if request.method == 'POST':
        sql = "select * from employee"
        c.execute(sql)
        abc = c.fetchall()
        print(abc, file=sys.stderr)
        sql="select role from employee where EID='" + uname +"'and password='" + pname +"'"
        c.execute(sql)


        data=c.fetchone()
        #print (data)
        print(data[0], file=sys.stderr)
        global global_role
        if data == None:
            #return redirect(url_for('hi'))
            return redirect(url_for('login'))
        else:
            global_role = data[0]
            session['username'] = request.form.get('username')
            #return redirect(url_for('login'))
            return redirect(url_for('dash'))
    return render_template('login.html')

app.secret_key = 'asd'

if __name__=='__main__':
    app.run()
