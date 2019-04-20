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

@app.route('/test/')
def test2_page():
    return render_template("test2.html")


@app.route('/login/', methods=["GET", "POST"])  # import flash request url_for redirect
def login_page():

    db = mysql.connect(host="localhost", port=3306, user="root", password='88888888', db="LSU")
    cur = db.cursor()
    cur2 = db.cursor()
    error = ''

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



@app.route('/login/students/')
def student_page():
    if session.get('logged_in') and 'Stu_username' in session:
        # db = mysql.connect(host="localhost", port=3306, user="root", password='88888888', db="LSU")
        # cur = db.cursor()
        # s_email = session.get('Stu_username')
        # cur.execute("select S.s_name from Students S where S.email=(%s)", [s_email])
        # student_name = cur.fetchone()[0]
        # print(student_name)
        # db.close()
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
                list_len=0
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
                # print(list_len)
                for k in range(list_len):
                    cur.execute("select S.s_name from Students S Where S.email=(%s)", [listy[i][k+3]])
                    listy[i].append(cur.fetchone()[0])

                # listy_length = int(list_len*2)
        #         print(listy_length)
        # # print(listy_length)
        #
        # print(listy[1])
        # # print(listy_length)
        # # print(listy[1][56])
        db.close()
        return render_template('student_courses_enrolled_info.html', value=p, value2=listy, len=list_len)
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

            # print(stored_old_password)
            # print(hash_input_password)
            # print(hash_new_password)

            if not hash_input_password == stored_old_password:
                flash("Old Password doesn't match")
                return redirect(url_for('student_info_page'))

            if hash_input_password == hash_new_password:
                flash("Please do not enter the same password")
                return redirect(url_for('student_info_page'))

            cur.execute("update Students S set S.password = (%s) where S.email =(%s)",[hash_new_password, s_email])
            db.commit()
            flash("Successfully change the password!")
        db.close()
        return render_template('student_self_info.html', value=stud_info)
    return redirect(url_for('login_page'))


@app.route('/login/admin/')
def admin_page():
    if session.get('logged_in') and 'Admin_username' in session:
        return render_template('admin.html')
    return redirect(url_for('login_page'))


@app.route('/login/admin/manage/')
def admin_manage_page():
    if session.get('logged_in') and 'Admin_username' in session:
        db = mysql.connect(host="localhost", port=3306, user="root", password='88888888', db="LSU")
        cur = db.cursor()
        admin = session.get('Admin_username')

        cur.execute("select  C.course_id, C.course_name,S.section_type, S.sec_no, S.s_limit, P.p_name,T.prof_email,S.prof_team_id "
                    "from Course C , Sections S, Prof_teams_members T, Professor P "
                    "where C.course_id =S.course_id and S.prof_team_id = T.team_id and T.prof_email = P.email")
        c_list = cur.fetchall()
        # print(c_list) #2D list
        db.close()
        return render_template('management.html', value=c_list )
    return redirect(url_for('login_page'))


@app.route('/login/admin/add/', methods=['POST','GET'])
def add_course():
    if session.get('logged_in') and 'Admin_username' in session:
        if request.method == "POST":
            db = mysql.connect(host="localhost", port=3306, user="root", password='88888888', db="LSU")
            cur = db.cursor()
            c_id = request.form['course_id']
            c_name = request.form['course_name']
            c_type= request.form['course_type']
            c_sec = request.form['course_sec']
            c_limit = request.form['course_limit']
            s_name = request.form['course_prof']
            s_email = request.form['course_prof_email']
            s_team_id = request.form['course_team_id']
            c_description = 'Regular 3 credit course offered only on campus'
            c_hw_deatil = 'Submit this homework on CanvasPath. Grade is out of 100'
            c_exam_details = 'Closed book exam for 100 marks'
            c_hw_num = '0'
            c_exam_num = '0'
            c_capstone_grade = '0'
            c_capstone_pro_no = '9999'

            exist_s = cur.execute("select S.course_id,S.sec_no from Sections S where S.course_id =(%s) and S.sec_no =(%s)", [c_id, c_sec])
            exist_c = cur.execute("select C.course_id,C.course_name from Course C where C.course_id =(%s) and C.course_name =(%s)"
                                  , [c_id, c_name])
            if exist_c > 0 or exist_s > 0:
                flash('Course Exists')
            else:
                check_course_name = cur.execute("select C.course_name from Course C where C.course_name = (%s)", [c_name])
                if c_limit == '0':
                    flash('Course limit should not be 0')
                elif not check_course_name == 0:
                    flash ('Course Name is duplicated')
                else:
                    exist_p = cur.execute("select P.p_name, P.email, T.team_id from Professor P, Prof_teams_members T "
                                          "where P.email=T.prof_email and P.p_name =(%s) and P.email = (%s) and T.team_id = (%s)"
                                          , [s_name, s_email,s_team_id])
                    if exist_p > 0:
                        if c_type.lower() == 'Reg'.lower():
                            cur.execute("insert into Course (course_id, course_name, course_description) values (%s, %s,%s)"
                                        ,[c_id, c_name,c_description])
                            cur.execute("insert into Sections (course_id, sec_no, section_type, s_limit, prof_team_id) values (%s, %s, %s, %s, %s)"
                                        , [c_id, c_sec, c_type, c_limit,s_team_id])
                            cur.execute("insert into Homework (course_id, sec_no, hw_no, hw_details) values (%s,%s,%s,%s)"
                                        , [c_id,c_sec,c_hw_num,c_hw_deatil ])
                            cur.execute("insert into Exams (course_id, sec_no, exam_no, exam_details) values (%s,%s,%s,%s)"
                                , [c_id, c_sec, c_exam_num, c_exam_details])
                            db.commit()
                            flash('Course has been add to the database successfully.')
                        else:  #capstone
                            cur.execute("insert into Course (course_id, course_name, course_description) values (%s, %s,%s)"
                                , [c_id, c_name, c_description])
                            cur.execute("insert into Sections (course_id, sec_no, section_type, s_limit, prof_team_id) values (%s, %s, %s, %s, %s)"
                                , [c_id, c_sec, c_type, c_limit, s_team_id])
                            cur.execute("insert into Homework (course_id, sec_no, hw_no, hw_details) values (%s,%s,%s,%s)"
                                , [c_id, c_sec, c_hw_num, c_hw_deatil])
                            cur.execute("insert into Exams (course_id, sec_no, exam_no, exam_details) values (%s,%s,%s,%s)"
                                , [c_id, c_sec, c_exam_num, c_exam_details])
                            cur.execute("insert into Capstone_section (course_id, sec_no, proj_no, sponsor_id) values (%s,%s,%s,%s)"
                                        ,[c_id, c_sec, c_capstone_pro_no, s_email])
                            cur.execute(" insert into Capstone_Team (course_id, sec_no, team_id, project_no) values (%s,%s,%s,%s)"
                                        , [c_id, c_sec, s_team_id,c_capstone_pro_no])
                            cur.execute(" insert into Capstone_grades (course_id, sec_no, team_id, grade) values (%s,%s,%s,%s)"
                                        , [c_id,c_sec, s_team_id,c_capstone_grade])
                            db.commit()
                            flash('Course has been add to the database successfully.')
                    else:
                        check_email = cur.execute("select P.email from Professor P where P.email =(%s)", [s_email])
                        check_name = cur.execute("select P.p_name from Professor P where P.p_name =(%s)", [s_name])
                        check_team_id = cur.execute("select P.team_id from Prof_teams_members P where P.prof_email = (%s) and P.team_id =(%s)"
                                                    , [s_email, s_team_id])
                        if check_name == 0 and check_email== 0 and check_team_id==0:
                            flash('Check The Assigned Instruction Information')
                        else:
                            if check_name == 0:
                                flash('Instructor Name is not correct')
                            if check_email == 0:
                                flash('Instructor Email is not correct')
                            if check_team_id == 0:
                                flash('Instructor Team ID is not correct')
            db.close()
        return render_template('add_course.html')
    return redirect(url_for('login_page'))

@app.route('/login/admin/remove/' , methods=['POST','GET'])
def remove_course():
    if session.get('logged_in') and 'Admin_username' in session:
        if request.method == "POST":
            db = mysql.connect(host="localhost", port=3306, user="root", password='88888888', db="LSU")
            cur = db.cursor()
            course_id = request.form['course_id']
            course_sec = request.form['course_sec']
            course_prof = request.form['prof_email']

            check_prof = cur.execute ("select P.email from Professor P where P.email = (%s)", [course_prof] )
            if check_prof == 0:
                flash("Invalid Instructor Email")

            check_course = cur.execute("select S.course_id from Sections S, Prof_teams_members T "
                                       "where S.prof_team_id = T.team_id and S.course_id = (%s) and T.prof_email = (%s)"
                                       , [course_id, course_prof])
            if check_course == 0:
                flash("Not found Course ID with the Instructor Email")
            else:
                check_team_id = cur.execute(
                    "select S.prof_team_id from Sections S, Prof_teams_members P where S.prof_team_id = P.team_id "
                    "and P.prof_email = (%s)", [course_prof])
                print (check_team_id)

                if check_team_id == 1 :
                    flash("Each professor must assign one course.")
                else:
                    cur.execute("select S.section_type from Sections S where S.course_id=(%s) and S.sec_no=(%s)",
                        [course_id, course_sec])
                    course_type = cur.fetchone()

                    if course_type[0] == "Reg":
                        cur.execute("delete from Course where course_id = (%s)", [course_id])
                        cur.execute("delete from Sections where course_id = (%s) and sec_no =(%s)", [course_id,course_sec])
                        cur.execute("delete from Homework_grades where course_id = (%s) and sec_no =(%s)",
                                    [course_id, course_sec])
                        cur.execute("delete from Homework where course_id = (%s) and sec_no =(%s)",
                                    [course_id, course_sec])
                        cur.execute ("delete from Exams where course_id = (%s) and sec_no =(%s)",
                                    [course_id, course_sec])
                        cur.execute("delete from Exam_grades where course_id = (%s) and sec_no =(%s)",
                                    [course_id, course_sec])
                        cur.execute("delete from Enrolls where course_id = (%s) and section_no =(%s)",
                                    [course_id, course_sec])
                        db.commit()
                        db.close()
                        flash("Course has been removed from database successfully")
                    else:
                        cur.execute("delete from Course where course_id = (%s)", [course_id])
                        cur.execute("delete from Sections where course_id = (%s) and sec_no =(%s)",
                                    [course_id, course_sec])
                        cur.execute("delete from Homework_grades where course_id = (%s) and sec_no =(%s)",
                                    [course_id, course_sec])
                        cur.execute("delete from Homework where course_id = (%s) and sec_no =(%s)",
                                    [course_id, course_sec])
                        cur.execute("delete from Exams where course_id = (%s) and sec_no =(%s)",
                                    [course_id, course_sec])
                        cur.execute("delete from Exam_grades where course_id = (%s) and sec_no =(%s)",
                                    [course_id, course_sec])
                        cur.execute("delete from Enrolls where course_id = (%s) and section_no =(%s)",
                                    [course_id, course_sec])
                        cur.execute("delete from Capstone_Team_Members where course_id = (%s) and sec_no =(%s)",
                                    [course_id, course_sec])
                        cur.execute("delete from Capstone_Team where course_id = (%s) and sec_no =(%s)",
                                    [course_id, course_sec])
                        cur.execute("delete from Capstone_section where course_id = (%s) and sec_no =(%s)",
                                    [course_id, course_sec])
                        cur.execute("delete from Capstone_grades where course_id = (%s) and sec_no =(%s)",
                                    [course_id, course_sec])
                        db.commit()
                        db.close()
                        flash("Course has been removed from database successfully")
        return render_template('remove_course.html')

    return redirect(url_for('login_page'))




@app.route('/login/admin/add_students/', methods=['POST','GET'])
def add_students():
    if session.get('logged_in') and 'Admin_username' in session:
        db = mysql.connect(host="localhost", port=3306, user="root", password='88888888', db="LSU")
        cur = db.cursor()

        flash('hi')
        db.commit()
        db.close()
        return render_template('add_students.html')

    return redirect(url_for('login_page'))





@app.route('/login/professors/')
def professor_page():
    if session.get('logged_in') and 'Prof_username' in session:
        db = mysql.connect(host="localhost", port=3306, user="root", password='88888888', db="LSU")
        cur = db.cursor()
        p_email = session.get('Prof_username')
        cur.execute("select p_name from Professor where email=(%s)", [p_email])
        professor_name = cur.fetchone()[0]
        # print(professor_name)
        db.close()
        return ("hi", professor_name)
    return redirect(url_for('login_page'))


@app.route("/logout/")
def logout():
    session['logged_in'] = False
    return render_template('home.html')


if __name__ == '__main__':
    app.run() #(debug= True)
