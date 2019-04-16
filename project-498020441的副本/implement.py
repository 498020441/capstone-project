from flask import *
import MySQLdb as mysql
from passlib.hash import hex_sha256
import os
# create object/instance for the class


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

@app.route('/')
def home_page():
    return render_template("home.html")

@app.route('/login/', methods=["GET", "POST"])  # import flash request url_for redirect
def login_page():

    db = mysql.connect(host="localhost", port=3306, user="root", password='88888888', db="LSU")
    cur = db.cursor()
    cur2 = db.cursor()
    error = ''
    try:
        if request.method == "POST":
            input_username = request.form['username']
            input_password = request.form['password']
            hash_password = hex_sha256.hash(input_password)
            if input_username == "admin@psu.edu" and input_password == "password":
                session['logged_in'] = True
                session['Admin_username'] = input_username
                return redirect(url_for('admin_page'))

            account_of_professor = cur.execute("select P.password from Professor P where P.email=(%s)", [input_username])
            if account_of_professor > 0:
                prof_account = cur.fetchone()
                prof_password = prof_account[0]
                if prof_password == hash_password:
                    session['logged_in'] = True
                    session['Prof_username'] = input_username
                    return redirect(url_for('professor_page'))

            account_of_student = cur2.execute("select S.password from Students S where S.email =(%s)", [input_username])
            if account_of_student > 0:
                stu_account = cur2.fetchone()
                stu_password = stu_account[0]
                if stu_password == hash_password:
                    session['logged_in'] = True
                    session['Stu_username'] = input_username
                    return redirect(url_for('student_page'))
            db.close()
            error = "Invalid email or password. Try Again"
        return render_template("login.html", error=error)

    except Exception as e:
        return render_template('login.html', error=error)

@app.route('/login/admin/')
def admin_page():
    if session.get('logged_in') and 'Admin_username' in session:
        return render_template('admin.html')
    return redirect(url_for('login_page'))



@app.route('/login/students/')
def student_page():
    if session.get('logged_in') and 'Stu_username' in session:
        db = mysql.connect(host="localhost", port=3306, user="root", password='88888888', db="LSU")
        cur = db.cursor()
        s_email = session.get('Stu_username')
        cur.execute("select S.s_name from Students S where S.email=(%s)", [s_email])
        student_name = cur.fetchone()[0]
        print(student_name)
        db.close()
        return render_template('header.html')
    return redirect(url_for('login_page'))


@app.route('/login/students/courses_info/')
def student_course_page():
    if session.get('logged_in') and 'Stu_username' in session:
        db = mysql.connect(host="localhost", port=3306, user="root", password='88888888', db="LSU")
        cur = db.cursor()
        s_email = session.get('Stu_username')

        count_courses = cur.execute("select E.course_id, E.section_no from Enrolls E where E.student_email = (%s)",[s_email])
        #store course_id and section_no in p
        p = cur.fetchall()
        listy = [[] for i in range(3)]
        for i in range (count_courses):
            cur.execute("select S.section_type, S.prof_team_id from Sections S where S.course_id = (%s) and sec_no = (%s)", [p[i][0],p[i][1]])
            sec_info = cur.fetchone()
            listy[i].append(sec_info[0])  #section type
            listy[i].append(sec_info[1])  #professor team id

            if sec_info[0] == 'Reg':
                cur.execute('select C.course_name, C.course_description from Course C where C.course_id =(%s)', [p[i][0]])
                course_name_and_description = cur.fetchone()
                listy[i].append(course_name_and_description[0])
                listy[i].append(course_name_and_description[1])

                cur.execute("select P.prof_email from Prof_teams_members P where P.team_id=(%s)", [sec_info[1]])
                professor_email = cur.fetchone()[0]
                listy[i].append(professor_email)

                cur.execute("select P.office_address from Professor P where P.email=(%s)", [professor_email])
                profess_office = cur.fetchone()[0]
                listy[i].append(profess_office)

                cur.execute("select H.grade from Homework_grades H where H.student_email =(%s) and H.course_id =(%s) and "
                            "H.sec_no =(%s) ", [s_email, p[i][0], p[i][1]])
                student_hw_grade = cur.fetchone()[0]
                listy[i].append(student_hw_grade)

                cur.execute("select E.grades from Exam_grades E where E.student_email =(%s) and E.course_id =(%s) and E.sec_no =(%s) ",
                            [s_email, p[i][0], p[i][1]])
                student_ex_grades = cur.fetchone()[0]
                listy[i].append(student_ex_grades)
                """
                print(listy)
                
                print("course", i+1, "id: ", p[i][0], ",course ", i+1, "section: ", p[i][1], ", section_type: ", listy[i][0], ", prof_team_id: ", listy[i][1],
                      ", course name: ", listy[i][2], ", course description: ", listy[i][3],
                      ", professor email: ",  listy[i][4],", professor office: ", listy[i][5], ", hw grade: ", listy[i][6]
                      , ", exam grade: ", listy[i][7])
                """
            else : #capstone section
                cur.execute("select P.prof_email from Prof_teams_members P where P.team_id =(%s)", [listy[i][1]])
                listy[i].append(cur.fetchone()[0])  #professor email

                cur.execute("select C.student_email from Capstone_Team_Members C where C.course_id = (%s) and C.sec_no = (%s)",
                            [p[i][0], p[i][1]])
                team_stu_email = cur.fetchall()
                for c in team_stu_email:
                    listy[i].append(c[0])

                list_len = (len(listy[i])-3)
                for k in range(list_len):
                    cur.execute("select S.s_name from Students S Where S.email=(%s)", [listy[i][k+3]])
                    listy[i].append(cur.fetchone()[0])

        listy_length = int((len(listy[i])-3)/2)
        # print(listy_length)
        # print(len(listy[2]))
        # print(listy[2])
        # print(listy_length)
        # print(listy[1][56])
        db.close()
        return render_template('student_courses_enrolled_info.html', value=p, value2=listy, len=listy_length)
    return redirect(url_for('login_page'))


@app.route('/login/students/self_info/',  methods=['POST','GET'])
def student_info_page():
    if session.get('logged_in') and 'Stu_username' in session:
        db = mysql.connect(host="localhost", port=3306, user="root", password='88888888', db="LSU")
        cur = db.cursor()
        s_email = session.get('Stu_username')
        cur.execute("select email, s_name, age, gender, major, street, zipcode from Students where email = (%s)", [s_email])
        stud_info = cur.fetchone()
        # print('email: ' ,stud_info[0],'\nname: ', stud_info[1],'\nage: ', stud_info[2], '\ngender: ',stud_info[3],
        #       '\nmajor: ', stud_info[4], '\nzipcode: ', stud_info[5])
        if request.method == "POST":
            input_password = request.form['old_password']
            new_password = request.form['new_password']
            s_email = session.get('Stu_username')
            hash_input_password = hex_sha256.hash(input_password)

            cur.execute("select S.password from Students S where S.email =(%s)", [s_email])
            stored_old_password =cur.fetchone()[0]
            hash_new_password = hex_sha256.hash(new_password)

            print(stored_old_password)
            print(hash_input_password)
            print(hash_new_password)

            if hash_input_password == hash_new_password:
                flash("Please do not enter the same password")
                return redirect(url_for('student_info_page'))
            if not hash_input_password == stored_old_password:
                flash("Old Password doesn't match")
                return redirect(url_for('student_info_page'))

            cur.execute("update Students S set S.password = (%s) where S.email =(%s)",
                            [hash_new_password, s_email])
            flash("Successfully change the password!")

        db.close()
        return render_template('student_self_info.html', value=stud_info)
    return redirect(url_for('login_page'))


@app.route('/login/professors/')
def professor_page():
    if session.get('logged_in') and 'Prof_username' in session:
        db = mysql.connect(host="localhost", port=3306, user="root", password='88888888', db="LSU")
        cur = db.cursor()
        p_email = session.get('Prof_username')
        cur.execute("select p_name from Professor where email=(%s)", [p_email])
        professor_name = cur.fetchone()[0]
        print(professor_name)
        db.close()
        return ("hi", professor_name)
    return redirect(url_for('login_page'))


@app.route("/logout/")
def logout():
    session['logged_in'] = False
    return render_template('home.html')


if __name__ == '__main__':
    app.run() #(debug= True)
