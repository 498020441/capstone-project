from passlib.hash import hex_sha256
import MySQLdb as mysql


db = mysql.connect(host="127.0.0.1", port=3306, user="root", password='88888888', db="sys")
u= "meng lin"

cur = db.cursor()
p = cur.execute("select user_password from password_test where username=(%s)", [u])
#print(cur.fetchone()[0])
print(type(p))
p1 = cur.fetchone()
print(p1[0])
p2=hex_sha256.hash("123456789")
print (p2)
if p1[0]==p2:
    print("the same")
"""
p = "password"
p1 = sha256_crypt.encrypt("password")
p2 = sha256_crypt.encrypt("password")
print(p1)
print(p2)

if p1 == p2:
    print("p1=p2: true")


if sha256_crypt.verify(p, p1):
   print("crypt.verify:true")
else:
    print("?")
    """

"""from flask import *
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

"""
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
           """

"""
           if (sha256_crypt.verify("admin@psu.edu", input_username)
                   and sha256_crypt.verify("password", input_password)):
               return redirect(url_for('admin_page'))

           elif ((not sha256_crypt.verify("admin@psu.edu", input_username)
                  and sha256_crypt.verify("password", input_password))
                 or (sha256_crypt.verify("admin@psu.edu", input_username)
                     and not sha256_crypt.verify("password", input_password))):
               error = "Invalid email or password. Try Again"
               return render_template("login.html", error=error)

           account_of_professor = cur.execute("select email, password from Professor")
           for i in range(account_of_professor):
               prof_account = cur.fetchone()
               prof_email = prof_account[0]
               prof_password = prof_account[1]
               if (sha256_crypt.verify(prof_email, input_username)
                       and sha256_crypt.verify(prof_password, input_password)):
                   return redirect(url_for('professor_page'))

               elif ((not sha256_crypt.verify(prof_email, input_username)
                      and sha256_crypt.verify(prof_password, input_password))
                     or (sha256_crypt.verify(prof_email, input_username)
                         and not sha256_crypt.verify(prof_password, input_password))):
                   error = "Invalid email or password. Try Again"
                   return render_template("login.html", error=error)

           account_of_student = cur2.execute("select email,password from Students")
           for j in range(account_of_student):
               stu_account = cur2.fetchone()
               stu_email = stu_account[0]
               stu_password = stu_account[1]
               if (sha256_crypt.verify(stu_email, input_username)
                  and sha256_crypt.verify(stu_password, input_password)):
                   return redirect(url_for('student_page'))
               elif ((not sha256_crypt.verify(stu_email, input_username)
                      and sha256_crypt.verify(stu_password, input_password))
                     or (sha256_crypt.verify(stu_email, input_username)
                     and not sha256_crypt.verify(stu_password, input_password))):
                   error = "Invalid email or password. Try Again"
                   print('what')
                   return render_template("login.html", error=error)
           """