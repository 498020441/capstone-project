from flask import *
#create object/instance for the class
import MySQLdb as mysql

db = mysql.connect(host="127.0.0.1", port=3306, user="root", password='88888888', db="LSU")
cur = db.cursor()

#pp= cur.execute("select email  from Students")
#p=cur.fetchone()[0]


rows_of_student= cur.execute("select email,password from Students")

for i in range(rows_of_student):
    a = cur.fetchone()
    p = a[0]
    q = a[1]
    print(i,',', p, ',', q,',a =,' ,a)
    print(type(a))


"""
app = Flask(__name__)



@app.route('/', methods=[ "GET", "POST" ])   #import flash request url_for redirect
def login_page():
    error = ''
    try:
        if request.method == "POST":
            input_username = request.form['username']
            input_password = request.form['password']

            if input_username == "admin@psu.edu" and input_password == "password":
                return redirect(url_for('admin_page'))
            else:
                error = "Invalid email or password. Try Again"

        return render_template("test2.html", error=error)

    except Exception as e:
        return render_template('test2.html', error=error)

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
"""