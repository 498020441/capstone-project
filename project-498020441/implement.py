from flask import *
import MySQLdb as mysql

#create object/instance for the class


app = Flask(__name__)


@app.route('/')
def home_page():
   return render_template("home.html")


@app.route('/login/', methods=[ "GET", "POST" ])   #import flash request url_for redirect
def login_page():
    # db = mysql.connect(host="127.0.0.1", port=3306, user="root", password='88888888', db="LSU")
    db = mysql.connect(db="lsu", host="127.0.0.1", port=3306, user="root", password="Lgg971225")
    cur = db.cursor()
    cur2 = db.cursor()
    error = ''
    try:
        if request.method == "POST":
            input_username = request.form['username']
            input_password = request.form['password']

            if input_username == "admin@psu.edu" and input_password == "password":
                return redirect(url_for('admin_page'))
            elif ((input_username != "admin@psu.edu" and input_password == "password")
                or (input_username == "admin@psu.edu" and input_password != "password")):
                error = "Invalid email or password. Try Again"
                return render_template("login.html", error=error)

            account_of_professor = cur.execute("select email, password from Professor")
            for i in range(account_of_professor):
                prof_account = cur.fetchone()
                prof_email = prof_account[0]
                prof_password = prof_account[1]
                if input_username == prof_email and input_password == prof_password:
                    return redirect(url_for('professor_page'))
                elif ((input_username != prof_email and input_password == prof_password)
                    or (input_username == prof_email and input_password != prof_password)):
                    error = "Invalid email or password. Try Again"
                    return render_template("login.html", error=error)

            account_of_student = cur2.execute("select email,password from Students")
            for j in range(account_of_student):
                stu_account = cur2.fetchone()
                stu_email = stu_account[0]
                stu_password = stu_account[1]
                if input_username == stu_email and input_password == stu_password:
                    print('emm')
                    return redirect(url_for('student_page'))
                elif ((input_username != stu_email and input_password == stu_password)
                    or (input_username == stu_email and input_password != stu_password)):
                    error = "Invalid email or password. Try Again"
                    print('what')
                    return render_template("login.html", error=error)
            error = "Invalid email or password. Try Again"

        return render_template("login.html", error=error)

    except Exception as e:
        return render_template('login.html', error=error)


@app.route('/admin/')
def admin_page():
    return render_template("admin.html")

@app.route('/students/')
def student_page():
    return render_template("students.html")

@app.route('/professors/')
def professor_page():
    return render_template("professors.html")





if __name__== '__main__':
    app.run()