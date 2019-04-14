from flask import *
import MySQLdb as mysql
from passlib.hash import hex_sha256

# create object/instance for the class


app = Flask(__name__)


@app.route('/')
def home_page():
    return render_template("home.html")


@app.route('/login/', methods=["GET", "POST"])  # import flash request url_for redirect
def login_page():
    db = mysql.connect(host="127.0.0.1", port=3306, user="root", password='88888888', db="LSU")
    cur = db.cursor()
    cur2 = db.cursor()
    error = ''
    try:
        if request.method == "POST":
            input_username = request.form['username']
            input_password = request.form['password']
            hash_password = hex_sha256.hash(input_password)
            if input_username == "admin@psu.edu" and input_password == "password":
                return redirect(url_for('admin_page'))

            account_of_professor = cur.execute("select password from Professor where email=(%s)", [input_username])
            if account_of_professor > 0:
                prof_account = cur.fetchone()
                prof_password = prof_account[0]
                if prof_password == hash_password:
                    return redirect(url_for('professor_page'))

            account_of_student = cur2.execute("select password from Students where email =(%s)", [input_username])
            if account_of_student > 0:
                stu_account = cur2.fetchone()
                stu_password = stu_account[0]
                if stu_password == hash_password:
                    return redirect(url_for('student_page'))

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


if __name__ == '__main__':
    app.run() #(debug= True)
