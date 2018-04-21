from __future__ import print_function  # In python 2.7
from flask import Flask, render_template, session, request, url_for, redirect, make_response, flash, send_from_directory, current_app
from werkzeug import secure_filename
import sys
import os
import MySQLdb
app = Flask(__name__)
app.debug = True

UPLOAD_FOLDER = './uploads/'
ALLOWED_EXTENSIONS = set(['pdf'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

conn = MySQLdb.connect(host = "localhost", user = "root", passwd = "Kanha@123#", db = "HRSystem")
c = conn.cursor()


@app.route('/')
def main():
    return render_template('index.html')


abc = {}


@app.route('/apply/', methods = ['GET', 'POST'])
def apply():
    if request.method == 'POST':
        abc["name"] = request.form.get('name')
        abc["phone_no"] = request.form.get('phone_no')
        abc["password"] = request.form.get('password')
        abc["email"] = request.form.get('email')
        abc["op_id"] = request.form.get('op_id')
        abc["link"] = UPLOAD_FOLDER + abc["email"]
        abc["address"] = request.form.get('address')
        f = request.files['resume']
        filename = abc["email"]
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect('/firstregister')
        # return redirect("/addapp/")
    return render_template('register.html')




@app.route('/home/')
def dash():
    # print(role, file=sys.stderr)
    if session.get('role') == 'Admin':
        return redirect('/admindash')
    elif session.get('role') == 'HRM':
        return redirect('/hrdash')
    elif session.get('role') == 'DM':
        return redirect('/dmdash')
    elif session.get('role') == 'Int':
        return redirect('/intdash')
    else:
        return redirect('/')


# insert applicant
@app.route('/hrdash')
def hrdash():
    # print(session['role'], file=sys.stderr)
    if session.get('username', False) == False:
        return redirect('/')
    if session['role'] != 'HRM':
        return redirect('/')
    print(session['username'], file = sys.stderr)
    sql = "select * from Applicant where Status = 'Stage2' and Opportunity_id = (select Department from Employee where E_ID = '" + str(session.get("username")) + "')"
    c.execute(sql)
    records = c.fetchall()
    # print(records, file=sys.stderr)
    return render_template('dash_hr.html', records = records)


@app.route('/dmdash')
def dmdash():
    # print(session['role'], file=sys.stderr)
    if session['role'] != 'DM':
        return redirect('/')
    sql = "select * from Applicant where Status = 'Stage3' and Opportunity_id = (select Department from Employee where E_ID = '" + str(session.get("username")) + "')"
    c.execute(sql)
    records = c.fetchall()
    # print(records, file=sys.stderr)
    return render_template('dash_dept.html', records = records)


@app.route('/intdash')
def intdash():
    # print(session['role'], file=sys.stderr)
    if session['role'] != 'Int':
        return redirect('/')
    sql = "select * from Applicant where Status = 'Stage4' and Opportunity_id = (select Department from Employee where E_ID = '" + str(session.get("username")) + "')"
    c.execute(sql)
    records = c.fetchall()
    # print(records, file=sys.stderr)
    return render_template('dash_interviewer.html', records = records)



@app.route('/reject/<id>')
def reject(id):
    sql = "update Applicant set Status = 'Rejected' where A_ID = '" + id + "'"
    c.execute(sql)
    conn.commit()
    return redirect('/home/')

@app.route('/logout')
def logout():
    if session.get('username', False) == False:
        session.pop('A_ID')
    else:
        session.pop('username')
        session.pop('role')
    # flash('Logged Out!!')
    return redirect('/login')

@app.route('/firstregister', methods=['POST', 'GET'])
def register():
    print(abc, file=sys.stderr)
    sq = "insert into Applicant(Resume, Email_id, Phone_no, Address, Status, Opportunity_id, Name, Password) values (%s, %s, %s, %s, %s, %s, %s, %s)"
    c.execute(sq, (abc["link"], abc["email"], abc["phone_no"], abc["address"], 'New', abc["op_id"], abc["name"], abc["password"]))
    conn.commit()

    sq = "select A_ID from Applicant where Email_id = %s"
    c.execute(sq, [abc["email"]])
    data = c.fetchone()

    sql = "select Status from Applicant where A_ID = '" + str(data[0]) + "'"
    c.execute(sql)
    data2 = c.fetchone()
    status = data2[0]
    session['A_ID'] = data[0]
    return render_template('applicant.html', stri = "Inserted with Applicant_ID " + str(data[0]), status = status)


@app.route('/login/', methods = ['POST', 'GET'])
def login():

    # temp_data=(uname,pname)

    # c.close()
    if request.method == 'POST':
        uname = request.form.get('E_ID')
        pname = request.form.get('password')
        flag = request.form.get('flag')
        if flag == "1":
            sql = "select * from Employee"
            c.execute(sql)
            abc = c.fetchall()
            print(uname, file=sys.stderr)
            sql = "select Role from Employee where E_ID='" + uname + "' and Password = '" + pname + "'"
            c.execute(sql)

            data = c.fetchone()
            # print (data)
            # print(data[0], file=sys.stderr)
            if data is None:
                # return redirect(url_for('hi'))
                return render_template('login.html', str = 'Invalid')
            else:
                session['role'] = data[0]
                session['username'] = request.form.get('E_ID')
                # return redirect(url_for('login'))
                return redirect(url_for('dash'))
        else:
            sql = "select * from Applicant"
            c.execute(sql)
            abc = c.fetchall()
            print(flag, file=sys.stderr)
            sql = "select * from Applicant where A_ID='" + uname + "' and Password = '" + pname + "'"
            c.execute(sql)

            data = c.fetchone()
            # print (data)
            # print(data[0], file=sys.stderr)
            if data is None:
                # return redirect(url_for('hi'))
                return render_template('login.html', str = 'Invalid')
            else:
                session['A_ID'] = data[0]
                # return redirect(url_for('login'))
                return redirect(url_for('appdash'))
    return render_template('login.html', str = 'Valid')


@app.route('/loginapp/')
def appdash():
    sql = "select Status from Applicant where A_ID = '" + str(session.get('A_ID')) + "'"
    c.execute(sql)
    data = c.fetchone()
    status = data[0]
    return render_template('applicant.html', status = status, A_ID = session.get('A_ID'))


@app.route('/accept/<uid>/<stage>', methods = ['GET', 'POST'])
def Accept(uid, stage):
    print("sada", file=sys.stderr)
    sql = "update Applicant set Status = 'Stage2' where A_ID = %s"
    if stage == 's2':
        sql = "update Applicant set Status = 'Stage3' where A_ID = %s"
    if stage == 's3':
        sql = "update Applicant set Status = 'Stage4' where A_ID = %s"
    if stage == 's4':
        sql = "update Applicant set Status = 'AC' where A_ID = %s"
    c.execute(sql, [uid])
    conn.commit()
    return redirect('/home/')


@app.route('/admindash')
def abcd():
    # print(session['role'], file=sys.stderr)
    if session['role'] != 'Admin':
        return redirect('/')
    sql = "select * from Applicant"
    c.execute(sql)
    records = c.fetchall()
    # print(records, file=sys.stderr)
    return render_template('dash_admin.html', records = records)


@app.route('/acceptapp/<id>')
def acceptapp(id):
    sql = "select * from Applicant where A_ID = '" + id + "'"
    c.execute(sql)
    data = c.fetchone()
    sql = "select count(*) from Employee"
    c.execute(sql)
    eid = "E0" + str(1 + c.fetchone()[0])
    sql = "insert into Employee values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    c.execute(sql, [eid, data[2], data[3], data[4], 'Assistant Engineer', data[6], data[7], 'Int', data[8]])
    conn.commit()
    # sql = "delete from Applicant where A_ID = '" + id + "'"
    # c.execute(sql)
    # conn.commit()
    return render_template('dash_applicant.html', strng = ("New E_ID is " + str(eid)))


@app.route('/rejectapp/<id>')
def rejectapp(id):
    sql = "delete from Applicant where A_ID = '" + id + "'"
    c.execute(sql)
    conn.commit()
    session.pop('A_ID')
    return redirect('/')


@app.route('/viewpdf/<id>')
def viewpdf(id):
    uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(directory=uploads, filename=(id))

app.secret_key = 'asd'


if __name__ == '__main__':
    app.run()
