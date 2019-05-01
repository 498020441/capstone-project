from flask import *
import MySQLdb as mysql
from passlib.hash import hex_sha256
import os

# create object/instance for the class
app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.loopcontrols') # break statement in jinja2
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
        return render_template('header.html')
    return redirect(url_for('login_page'))


@app.route('/login/students/courses_info/')
def student_course_page():
    if session.get('logged_in') and 'Stu_username' in session:
        db = mysql.connect(host="localhost", port=3306, user="root", password='88888888', db="LSU")
        cur = db.cursor()
        s_email = session.get('Stu_username')

        count_courses = cur.execute("select E.course_id, E.section_no from Enrolls E where E.student_email = (%s)"
                                    , [s_email])
        # store course_id and section_no in p
        p = cur.fetchall()
        listy = [[] for i in range(count_courses)]
        pass_len = 1
        for i in range(count_courses):
            print(p[i][0],p[i][1])
            cur.execute("select S.section_type, S.prof_team_id from Sections S where S.course_id = (%s) and S.sec_no = (%s)"
                        ,[p[i][0], p[i][1]])
            sec_info = cur.fetchone()
            listy[i].append(sec_info[0])  # section type
            listy[i].append(sec_info[1])  # professor team id
            if sec_info[0] == 'Reg':
                list_len = 0
                cur.execute('select C.course_name, C.course_description from Course C where C.course_id =(%s)',
                            [p[i][0]])
                course_name_and_description = cur.fetchone()
                listy[i].append(course_name_and_description[0])
                listy[i].append(course_name_and_description[1])

                cur.execute("select P.prof_email from Prof_teams_members P where P.team_id=(%s)", [sec_info[1]])
                professor_email = cur.fetchone()[0]
                listy[i].append(professor_email)

                cur.execute("select P.office_address from Professor P where P.email=(%s)", [professor_email])
                profess_office = cur.fetchone()[0]
                listy[i].append(profess_office)

            else:  # capstone section
                cur.execute("select P.prof_email from Prof_teams_members P where P.team_id =(%s)", [listy[i][1]])
                listy[i].append(cur.fetchone()[0])  # professor email

                cur.execute(
                    "select C.student_email from Capstone_Team_Members C where C.course_id = (%s) and C.sec_no = (%s)",
                    [p[i][0], p[i][1]])
                team_stu_email = cur.fetchall()
                for c in team_stu_email:
                    listy[i].append(c[0])

                list_len = (len(listy[i]) - 3)
                # print(list_len)
                for k in range(list_len):
                    cur.execute("select S.s_name from Students S Where S.email=(%s)", [listy[i][k + 3]])
                    listy[i].append(cur.fetchone()[0])
                pass_len = list_len
        db.close()
        return render_template('student_courses_enrolled_info.html', value=p, value_len=count_courses,  value2=listy
                               , len=pass_len)
    return redirect(url_for('login_page'))


@app.route('/login/students/grades/')
def student_course_grades_page():
    if session.get('logged_in') and 'Stu_username' in session:
        db = mysql.connect(host="localhost", port=3306, user="root", password='88888888', db="LSU")
        cur = db.cursor()
        s_email = session.get('Stu_username')
        number_course = cur.execute("select H.course_id, H.sec_no, H.hw_no, H.grade, E.exam_no, E.grades, S.section_type "
                                    "from Homework_grades H,Exam_grades E, Sections S where H.course_id = E.course_id "
                                    "and S.course_id = H.course_id and S.course_id = E.course_id and S.sec_no = H.sec_no and S.sec_no = E.sec_no "
                                    "and H.sec_no = E.sec_no and H.student_email = E.student_email and H.student_email =(%s)", [s_email])
        student_assignment_info= cur.fetchall()
        # print(student_assignment_info)
        # print(len(student_assignment_info))
        list = [[] for i in range(number_course)]
        for i in range(number_course):
            if student_assignment_info[i][6] == 'Reg':
                cur.execute("select AVG(grade) from Homework_grades where course_id = (%s) and sec_no = (%s) and hw_no = (%s)"
                            , [student_assignment_info[i][0], student_assignment_info[i][1], student_assignment_info[i][2]])
                hw_avg = cur.fetchone()[0]
                list[i].append(round(hw_avg,2))
                cur.execute("select MIN(grade) from Homework_grades where course_id = (%s) and sec_no = (%s) and hw_no = (%s) "
                            , [student_assignment_info[i][0], student_assignment_info[i][1],student_assignment_info[i][2]])
                hw_min = cur.fetchone()[0]
                list[i].append(hw_min)
                cur.execute("select MAX(grade) from Homework_grades where course_id = (%s) and sec_no = (%s) and hw_no = (%s) "
                            , [student_assignment_info[i][0], student_assignment_info[i][1],student_assignment_info[i][2]])
                hw_max = cur.fetchone()[0]
                list[i].append(hw_max)

                cur.execute("select AVG(grades) from Exam_grades where course_id = (%s) and sec_no = (%s) and exam_no = (%s) "
                            , [student_assignment_info[i][0], student_assignment_info[i][1],student_assignment_info[i][4]])
                exam_avg = cur.fetchone()[0]
                list[i].append(round(exam_avg,2))
                cur.execute("select MIN(grades) from Exam_grades where course_id = (%s) and sec_no = (%s) and exam_no = (%s) "
                            , [student_assignment_info[i][0], student_assignment_info[i][1],student_assignment_info[i][4]])
                exam_min = cur.fetchone()[0]
                list[i].append(exam_min)
                cur.execute("select MAX(grades) from Exam_grades where course_id = (%s) and sec_no = (%s) and exam_no = (%s) "
                            , [student_assignment_info[i][0],student_assignment_info[i][1],student_assignment_info[i][4]])
                exam_max = cur.fetchone()[0]
                list[i].append(exam_max)
            else:
                cur.execute(
                    "select AVG(grade) from Homework_grades where course_id = (%s) and sec_no = (%s) and hw_no = (%s)"
                    , [student_assignment_info[i][0], student_assignment_info[i][1], student_assignment_info[i][2]])
                cap_hw_avg = cur.fetchone()[0]
                list[i].append(round(cap_hw_avg,2))
                cur.execute(
                    "select MIN(grade) from Homework_grades where course_id = (%s) and sec_no = (%s) and hw_no = (%s) "
                    , [student_assignment_info[i][0], student_assignment_info[i][1], student_assignment_info[i][2]])
                cap_hw_min = cur.fetchone()[0]
                list[i].append(cap_hw_min)
                cur.execute(
                    "select MAX(grade) from Homework_grades where course_id = (%s) and sec_no = (%s) and hw_no = (%s) "
                    , [student_assignment_info[i][0], student_assignment_info[i][1], student_assignment_info[i][2]])
                cap_hw_max = cur.fetchone()[0]
                list[i].append(cap_hw_max)
        db.close()
        return render_template('student_grades.html', value=student_assignment_info, len=number_course, value2=list)
    return redirect(url_for('login_page'))


@app.route('/login/students/self_info/',  methods=['POST','GET'])
def student_info_page():
    if session.get('logged_in') and 'Stu_username' in session:
        db = mysql.connect(host="localhost", port=3306, user="root", password='88888888', db="LSU")
        cur = db.cursor()
        s_email = session.get('Stu_username')
        cur.execute("select email, s_name, age, gender, major, street, zipcode from Students where email = (%s)", [s_email])
        stud_info = cur.fetchone()
        if request.method == "POST":
            input_password = request.form['old_password']
            new_password = request.form['new_password']
            s_email = session.get('Stu_username')
            hash_input_password = hex_sha256.hash(input_password)

            cur.execute("select S.password from Students S where S.email =(%s)", [s_email])
            stored_old_password = cur.fetchone()[0]
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
        # admin = session.get('Admin_username')

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
            c_type = request.form['course_type']
            c_sec = request.form['course_sec']
            c_limit = request.form['course_limit']
            s_name = request.form['course_prof']
            s_email = request.form['course_prof_email']
            s_team_id = request.form['course_team_id']
            c_description = 'Regular 3 credit course offered only on campus'
            # c_hw_detail = 'Submit this homework on CanvasPath. Grade is out of 100'
            # c_exam_details = 'Closed book exam for 100 marks'
            # c_hw_num = '0'
            # c_exam_num = '0'
            c_capstone_grade = '0'
            c_capstone_pro_no = '9999'

            exist_s = cur.execute("select S.course_id,S.sec_no from Sections S where S.course_id =(%s) and S.sec_no =(%s)", [c_id, c_sec])
            exist_c = cur.execute("select C.course_id,C.course_name from Course C where C.course_id =(%s) and C.course_name =(%s)"
                                  , [c_id, c_name])
            if exist_c > 0 or exist_s > 0:
                flash('Course Exists')
            else:
                if c_type.lower() == "Reg".lower() or c_type.lower() == "Cap".lower():
                    check_course_name = cur.execute("select C.course_name from Course C where C.course_name = (%s)", [c_name])
                    if c_limit == '0':
                        flash('Course limit should not be 0')
                    elif not check_course_name == 0:
                        flash('Course Name is duplicated')
                    else:
                        exist_p = cur.execute("select P.p_name, P.email, T.team_id from Professor P, Prof_teams_members T "
                                              "where P.email=T.prof_email and P.p_name =(%s) and P.email = (%s) and T.team_id = (%s)"
                                              , [s_name, s_email,s_team_id])
                        if exist_p > 0:
                            cur.execute("insert into Course (course_id, course_name, course_description) values (%s, %s,%s)"
                                        , [c_id, c_name, c_description])
                            cur.execute(
                                "insert into Sections (course_id, sec_no, section_type, s_limit, prof_team_id) values (%s, %s, %s, %s, %s)"
                                , [c_id, c_sec, c_type, c_limit, s_team_id])
                            # cur.execute("insert into Homework (course_id, sec_no, hw_no, hw_details) values (%s,%s,%s,%s)"
                            #             , [c_id, c_sec, c_hw_num, c_hw_detail])
                            # cur.execute("insert into Exams (course_id, sec_no, exam_no, exam_details) values (%s,%s,%s,%s)"
                            #             , [c_id, c_sec, c_exam_num, c_exam_details])
                            if c_type.lower() == 'Reg'.lower():
                                db.commit()
                            else:  #capstone
                                cur.execute("insert into Capstone_section (course_id, sec_no, proj_no, sponsor_id) values (%s,%s,%s,%s)"
                                            ,[c_id, c_sec, c_capstone_pro_no, s_email])
                                cur.execute(" insert into Capstone_Team (course_id, sec_no, team_id, proj_no) values (%s,%s,%s,%s)"
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
                            if check_name == 0 and check_email == 0 and check_team_id == 0:
                                flash('Check The Assigned Instruction Information')
                            else:
                                if check_name == 0:
                                    flash('Instructor Name is not correct')
                                if check_email == 0:
                                    flash('Instructor Email is not correct')
                                if check_team_id == 0:
                                    flash('Instructor Team ID is not correct')
                else:
                    flash("Invalid Course Type")
            db.close()
        return render_template('add_course.html')
    return redirect(url_for('login_page'))


@app.route('/login/admin/remove/', methods=['POST', 'GET'])
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
            check_section = cur.execute ("select course_id from Sections where course_id =(%s) and sec_no =(%s)"
                                         , [course_id,course_sec])
            if check_course == 0:
                flash("Not found Course ID with the Instructor Email")
            elif check_section == 0:
                flash("This section not exist")
            else:
                check_team_id = cur.execute(
                    "select S.prof_team_id from Sections S, Prof_teams_members P where S.prof_team_id = P.team_id "
                    "and P.prof_email = (%s)", [course_prof])
                if check_team_id == 1:
                    flash("Each professor must assign one course.")
                else:
                    cur.execute("select S.section_type from Sections S where S.course_id=(%s) and S.sec_no=(%s)",
                        [course_id, course_sec])
                    course_type = cur.fetchone()

                    check_number_of_sections = cur.execute("select S.course_id from Sections S where S.course_id =(%s)", [course_id] )
                    if check_number_of_sections == 1:
                        cur.execute("delete from Course where course_id = (%s)", [course_id])

                    cur.execute("delete from Sections where course_id = (%s) and sec_no =(%s)", [course_id, course_sec])
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

                    if course_type[0] == "Reg":
                        db.commit()
                    else:

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
        if request.method == "POST":
            db = mysql.connect(host="localhost", port=3306, user="root", password='88888888', db="LSU")
            cur = db.cursor()
            s_email = request.form['student_email']
            c_id = request.form['course_id']
            c_sec = request.form['course_sec']

            check_student_valid = cur.execute("select S.email from Students S where S.email = (%s)", [s_email])
            if check_student_valid == 1:
                check_course_with_section = cur.execute("select S.course_id, S.sec_no, S.section_type, S.prof_team_id, S.s_limit "
                                                        "from Sections S where S.course_id = (%s) and S.sec_no = (%s)", [c_id, c_sec])
                course_info = cur.fetchone()
                if check_course_with_section == 1:
                    check_limit = cur.execute("select E.student_email from Enrolls E where E.course_id =(%s) and E.section_no = (%s)"
                                ,[c_id, c_sec])
                    if check_limit + 1 <= course_info[4]:
                        check_student_enroll = cur.execute("select E.student_email from Enrolls E where E.student_email = (%s) and "
                            " E.course_id = (%s) ", [s_email, c_id])
                        if check_student_enroll == 0:
                            c_type = course_info[2]
                            # cur.execute(
                            #     "select E.exam_no, H.hw_no from Exams E, Homework H where E.course_id = H.course_id and "
                            #     " E.sec_no = H.sec_no and E.course_id = (%s) and E.sec_no = (%s)", [c_id, c_sec])
                            # exam_hw_info = cur.fetchone()
                            # exam_no = exam_hw_info[0]
                            # hw_no = exam_hw_info[1]

                            cur.execute("insert into Enrolls (student_email, course_id, section_no) values (%s,%s,%s)"
                                        , [s_email, c_id, c_sec])
                            # cur.execute(" insert into Exam_grades (student_email, course_id, sec_no, exam_no,grades) "
                            #             "values (%s,%s,%s,%s,%s)", [s_email, c_id, c_sec, exam_no, '0'])
                            # cur.execute("insert into Homework_grades (student_email, course_id, sec_no, hw_no, grade)"
                            #             "values (%s,%s,%s,%s,%s)", [s_email, c_id, c_sec, hw_no, '0'])

                            if c_type == "Reg":
                                db.commit()
                            else:
                                cur.execute("insert into Capstone_Team_Members (student_email, team_id, course_id, sec_no)"
                                            "values (%s,%s,%s,%s)", [s_email, course_info[3], c_id, c_sec])
                                db.commit()
                            flash("Student has been add to this course section")
                        else:
                            flash("Student is already in this course ")
                    else:
                        flash("Sorry this course section has no more seat for student")
                else:
                    flash("Invalid Course Info")
            else:
                flash("Invalid Student Email")
            db.close()
        return render_template('add_students.html')
    return redirect(url_for('login_page'))


@app.route('/login/professors/')
def professor_page():
    if session.get('logged_in') and 'Prof_username' in session:
        db = mysql.connect(host="localhost", port=3306, user="root", password='88888888', db="LSU")
        cur = db.cursor()
        p_email = session.get('Prof_username')
        count_unique_course = cur.execute("select S.section_type from Sections S, Prof_teams_members P where S.prof_team_id = P.team_id and "
                    " P.prof_email =(%s)", [p_email])
        c_unique_type = cur.fetchall()
        return render_template('professors.html', value_unique=c_unique_type, len_unique=count_unique_course)
    return redirect(url_for('login_page'))


@app.route('/login/professors/create_assignment/', methods=["POST", "GET"])
def professor_create_assignment_page():
    if session.get('logged_in') and 'Prof_username' in session:
        db = mysql.connect(host="localhost", port=3306, user="root", password='88888888', db="LSU")
        cur = db.cursor()

        p_email = session.get('Prof_username')
        count_unique_course = cur.execute(
            "select S.section_type from Sections S, Prof_teams_members P where S.prof_team_id = P.team_id and "
            " P.prof_email =(%s)", [p_email])
        c_unique_type = cur.fetchall()

        cur.execute("select team_id from Prof_teams_members where prof_email=(%s)", [p_email])
        prof_team_id = cur.fetchone()[0]
        count_courses = cur.execute("select S.course_id, S.sec_no from Sections S where S.prof_team_id = (%s)"
                                    , [prof_team_id])
        prof_teachings = cur.fetchall()

        if request.method == "POST":
            assignment_type = request.form.get('course_type')
            assignment_id = request.form['assignment_id']
            exam_detail = "Closed book exam for 100 marks"
            hw_detail = "Submit this homework on CanvasPath. Grade is out of 100"
            course = request.form.get('course_id_sec')
            if course == 'Assigned Courses' or assignment_type == 'Assignment Type':
                flash("Please Select Course Or Assignment Type")
            else:
                course = course.split('#')
                course_id = course[0]
                course_sec = course[1]

                cur.execute("select S.section_type from Sections S where S.course_id = (%s) and S.sec_no=(%s)", [course_id, course_sec])
                c_type = cur.fetchone()[0]
                if c_type == "Reg":
                    if assignment_type == 'Homework':
                        check_hw_exist = cur.execute("select H.hw_no from Homework H where H.course_id =(%s) and "
                                                     "H.sec_no = (%s) and H.hw_no = (%s)", [course_id,course_sec, assignment_id])
                        if check_hw_exist == 0:
                            #add hw to Homework_grades and Homework
                            cur.execute("insert into Homework (course_id, sec_no, hw_no, hw_details) values (%s,%s,%s,%s)"
                                        , [course_id,course_sec, assignment_id, hw_detail])
                            count_students = cur.execute("select E.student_email from Enrolls E where E.course_id = (%s) and E.section_no = (%s)"
                                        ,[course_id, course_sec])
                            student_email = cur.fetchall()
                            for i in range(count_students):
                                cur.execute("insert into Homework_grades (student_email, course_id, sec_no, hw_no,grade)"
                                            "values (%s,%s,%s,%s,%s)", [student_email[i][0], course_id,course_sec,assignment_id,'0'])
                            flash('Homework Updates Successfully')
                            db.commit()
                        else:
                            flash("Homework Has Already Existed")
                    else: #reg exam
                        check_exam_exist = cur.execute("select E.exam_no from Exams E where E.course_id =(%s) and "
                                        "E.sec_no = (%s) and E.exam_no = (%s)", [course_id, course_sec, assignment_id])
                        if check_exam_exist == 0:
                            # add exam to Exam_grades and Exam

                            cur.execute("insert into Exams (course_id, sec_no, exam_no, exam_details) values (%s,%s,%s,%s)"
                                        , [course_id, course_sec, assignment_id, exam_detail])
                            count_students = cur.execute("select E.student_email from Enrolls E where E.course_id = (%s) and E.section_no = (%s)"
                                                        ,[course_id, course_sec])
                            student_email = cur.fetchall()
                            for i in range(count_students):
                                cur.execute("insert into Exam_grades (student_email, course_id, sec_no, exam_no,grades)"
                                            "values (%s,%s,%s,%s,%s)",
                                            [student_email[i][0], course_id, course_sec, assignment_id, '0'])
                            flash('Exam Updates Successfully')
                            db.commit()
                        else:
                            flash("Exam Has Already Existed")
                else:
                    if assignment_type == 'Homework':
                        check_hw2_exist = cur.execute("select H.hw_no from Homework H where H.course_id =(%s) and "
                                                    "H.sec_no = (%s) and H.hw_no = (%s)",[course_id, course_sec, assignment_id])
                        if check_hw2_exist == 0:
                            #add hw to Homework_grades and Homework
                            cur.execute("insert into Homework (course_id, sec_no, hw_no, hw_details) values (%s,%s,%s,%s)"
                                        , [course_id, course_sec, assignment_id, hw_detail])
                            count_students = cur.execute(
                                "select E.student_email from Enrolls E where E.course_id = (%s) and E.section_no = (%s)"
                                , [course_id, course_sec])
                            student_email = cur.fetchall()
                            for i in range(count_students):
                                cur.execute("insert into Homework_grades (student_email, course_id, sec_no, hw_no, grade)"
                                            "values (%s,%s,%s,%s,%s)",
                                            [student_email[i][0], course_id, course_sec, assignment_id, '0'])
                            flash('Homework Updates Successfully')
                            db.commit()
                        else:
                            flash("Homework Has Already Existed")
                    else:
                        flash("Capstone Section Doesn't Require Exam")
            db.close()
        return render_template('p_create_assignment.html', value=prof_teachings, len1=count_courses,
                               value_unique=c_unique_type, len_unique=count_unique_course)
    return redirect(url_for('login_page'))


@app.route('/login/professors/student_score/', methods=["POST","GET"])
def professor_student_score_list_page():
    if session.get('logged_in') and 'Prof_username' in session:
        db = mysql.connect(host="localhost", port=3306, user="root", password='88888888', db="LSU")
        cur = db.cursor()
        p_email = session.get('Prof_username')
        count_unique_course = cur.execute(
            "select S.section_type from Sections S, Prof_teams_members P where S.prof_team_id = P.team_id and "
            " P.prof_email =(%s)", [p_email])
        c_unique_type = cur.fetchall()

        cur.execute("select team_id from Prof_teams_members where prof_email=(%s)", [p_email])
        prof_team_id = cur.fetchone()[0]
        count_reg_courses = cur.execute(" select S.course_id, S.sec_no, S.section_type from Sections S where S.prof_team_id = (%s)"
                                        " and S.section_type = (%s)", [prof_team_id, 'Reg'])
        prof_teachings = cur.fetchall()
        list_course=[[] for i in range(count_reg_courses)]
        list_student_in_section = []
        count_sections = cur.execute("select sec_no from Sections where section_type = (%s) and prof_team_id =(%s)",['Reg', prof_team_id])
        student_hw_info = [[] for i in range(count_sections)]
        student_exam_info = [[] for i in range(count_sections)]
        for i in range(count_reg_courses):
            list_course[i].append(prof_teachings[i][0])
            list_course[i].append(prof_teachings[i][1])
            list_course[i].append(prof_teachings[i][2])
            cur.execute("select s_limit from Sections where course_id = (%s) and sec_no = (%s)"
                        , [prof_teachings[i][0], prof_teachings[i][1]])
            section_limit = cur.fetchone()[0]
            list_course[i].append(section_limit)

            count_student_in_section = cur.execute("select S.s_name, S.email from Students S, Enrolls E where E.student_email = S.email "
                        "and E.course_id = (%s) and E.section_no = (%s)", [prof_teachings[i][0], prof_teachings[i][1]])
            student_info = cur.fetchall()
            list_student_in_section.append(student_info)
            # print(count_student_in_section)
            # print(list_student_in_section[i])
            for j in range(count_student_in_section):
                s_email = list_student_in_section[i][j][1]
                cur.execute("select hw_no, grade from Homework_grades where student_email =(%s) and course_id = (%s) "
                            "and sec_no = (%s)", [s_email, prof_teachings[i][0], prof_teachings[i][1]])
                s_hw_info = cur.fetchall()
                student_hw_info[i].append(s_hw_info)

                cur.execute("select exam_no, grades from Exam_grades where student_email = (%s) and course_id = (%s) "
                            "and sec_no = (%s)",[s_email, prof_teachings[i][0], prof_teachings[i][1]])
                s_exam_info = cur.fetchall()
                student_exam_info[i].append(s_exam_info)
        # print((student_hw_info))
        # print(student_hw_info[0])
        # print(len(student_hw_info[0][0]))
        # print(student_hw_info[0][0][0])
        db.close()
        return render_template('student_score_list.html', value_unique=c_unique_type, len_unique=count_unique_course,
                               value_course=list_course, len_course=count_reg_courses, value2=list_student_in_section,
                               value_hw=student_hw_info, value_exam=student_exam_info)
    return redirect(url_for('login_page'))


@app.route('/login/professors/submit_score/', methods=["POST","GET"])
def professor_submit_score_page():
    if session.get('logged_in') and 'Prof_username' in session:
        db = mysql.connect(host="localhost", port=3306, user="root", password='88888888', db="LSU")
        cur = db.cursor()
        p_email = session.get('Prof_username')
        count_unique_course = cur.execute(
            "select S.section_type from Sections S, Prof_teams_members P where S.prof_team_id = P.team_id and "
            " P.prof_email =(%s)", [p_email])
        c_unique_type = cur.fetchall()

        cur.execute("select team_id from Prof_teams_members where prof_email=(%s)", [p_email])
        prof_team_id = cur.fetchone()[0]
        count_courses = cur.execute(" select S.course_id, S.sec_no,S.section_type from Sections S where S.prof_team_id = (%s)"
                                    , [prof_team_id])
        prof_teachings = cur.fetchall()

        if request.method == "POST":
            course = request.form.get('course_id_sec')
            assignment_type = request.form.get('course_type')

            if course == 'Assigned Courses' or assignment_type == 'Assignment Type':
                flash("Please Select Course Or Assignment Type")
            else:
                course = course.split('#')
                c_id = course[0]
                c_sec = course[1]
                assignment_no = request.form['assignment_no']
                student_id = request.form['student_id']
                assignment_grade = request.form['assignment_grade']

                cur.execute("select S.section_type from Sections S where S.course_id =(%s) and S.sec_no =(%s)",
                            [c_id, c_sec])
                s_type = cur.fetchone()[0]

                check_student_exist = cur.execute("select S.email from Students S where S.email=(%s)", [student_id])
                if check_student_exist > 0:
                    check_student_section = cur.execute("select E.student_email from Enrolls E where E.student_email =(%s) and "
                                                        "E.course_id =(%s) and E.section_no =(%s)",[student_id, c_id, c_sec])
                    if check_student_section > 0:
                        if s_type == 'Reg':
                            if assignment_type == "Homework":
                                check_hw_exist = cur.execute("select course_id from Homework where course_id = (%s) and "
                                                                    "sec_no =(%s) and hw_no =(%s)", [c_id, c_sec, assignment_no])
                                if check_hw_exist > 0:
                                    cur.execute("update Homework_grades set grade = (%s) where student_email = (%s) and "
                                                "hw_no = (%s) and course_id = (%s) and sec_no = (%s)"
                                                ,[assignment_grade, student_id, assignment_no, c_id,c_sec])
                                    flash("Graded Successfully")
                                    db.commit()
                                else:
                                    flash("Invalid Homework Number.")
                            else:
                                check_exam_exist = cur.execute("select course_id from Exams where course_id =(%s) and "
                                                               "sec_no = (%s) and exam_no =(%s)", [c_id,c_sec,assignment_no])
                                if check_exam_exist > 0:
                                    cur.execute("update Exam_grades set grades = (%s) where student_email = (%s) and "
                                                "exam_no =(%s) and course_id =(%s) and sec_no =(%s)"
                                                , [assignment_grade, student_id, assignment_no,c_id,c_sec])
                                    flash("Graded Successfully")
                                    db.commit()
                                else:
                                    flash("Invalid Exam Number")
                        else:
                            if assignment_type == "Homework":
                                check_hw_exist = cur.execute(
                                    "select course_id from Homework where course_id = (%s) and "
                                    "sec_no =(%s) and hw_no =(%s)", [c_id, c_sec, assignment_no])
                                if check_hw_exist > 0:
                                    cur.execute(
                                        "update Homework_grades set grade = (%s) where student_email = (%s) and "
                                        "hw_no = (%s) and course_id = (%s) and sec_no = (%s)"
                                        , [assignment_grade, student_id, assignment_no, c_id, c_sec])
                                    flash("Graded Successfully")
                                    db.commit()
                            else:
                                flash("Capstone Doesn't Require To Grade Exam")
                    else:
                        flash("Student Not In This Section")
                else:
                    flash("Invalid Student Email")
        db.close()
        return render_template('p_submit_score.html', value=prof_teachings, len1=count_courses,value_unique=c_unique_type
                               , len_unique=count_unique_course)
    return redirect(url_for('login_page'))


@app.route('/login/professors/capstone_team_list/', methods=["POST","GET"])
def professor_capstone_teamlist_page():
    if session.get('logged_in') and 'Prof_username' in session:
        db = mysql.connect(host="localhost", port=3306, user="root", password='88888888', db="LSU")
        cur = db.cursor()
        p_email = session.get('Prof_username')
        count_unique_course = cur.execute(
            "select S.section_type from Sections S, Prof_teams_members P where S.prof_team_id = P.team_id and "
            " P.prof_email =(%s)", [p_email])
        c_unique_type = cur.fetchall()
        #update capstone team number with 1,2 for different sections
        count_capstone_course = cur.execute("select course_id, sec_no from Capstone_section where sponsor_id = (%s)", [p_email])
        course = cur.fetchall()

        list = [[]for i in range(count_capstone_course)]
        list_student_info = []
        for i in range(count_capstone_course):
            cur.execute("select S.s_limit from Sections S where S.course_id =(%s) and S.sec_no =(%s)"
                        , [course[i][0], course[i][1]])
            s_limit = cur.fetchone()[0]
            list[i].append(s_limit)   #course_limit

            cur.execute("select S.email, S.s_name, H.hw_no,H.grade, C1.course_id, C1.sec_no,C1.team_id,C2.grade "
                        "from Students S , Capstone_Team_Members C1, Homework_grades H, Capstone_grades C2 where C1.student_email = S.email "
                        "and C1.student_email = H.student_email and C1.course_id = H.course_id and C1.course_id =C2.course_id and C1.sec_no = C2.sec_no"
                " and C1.sec_no = H.sec_no and C1.course_id =(%s) and C1.sec_no =(%s)", [course[i][0], course[i][1]])
            student_info = cur.fetchall()
            list_student_info.append(student_info)
        # print(list_student_info[0][1][7])
        # print(list_student_info[1])
        # # print(list_student_info[0][17][0])
        # print(len(list_student_info[1][27]))
        # # print(list_student_info[1][0][1])
        # # print (len(list_student_info[1][0]))
        cur.execute("select team_id from Prof_teams_members where prof_email=(%s)", [p_email])
        prof_team_id = cur.fetchone()[0]
        count_courses = cur.execute("select S.course_id, S.sec_no,s.section_type from Sections S where S.prof_team_id = (%s)"
                                    , [prof_team_id])
        prof_teachings = cur.fetchall()

        if request.method == "POST":
            grade = request.form['student_grade']
            course = request.form.get('course_id_sec')
            if course == 'Assigned Courses':
                flash("Please Select Course And Section")
            else:
                course = course.split('#')
                c_id = course[0]
                c_sec = course[1]
                cur.execute("update Capstone_grades set grade =(%s) where course_id =(%s) and sec_no =(%s)"
                            , [grade, c_id, c_sec])
                db.commit()
                flash("Grade Successfully")

                db.close()
        return render_template('p_organize_team.html', value_unique=c_unique_type, len_unique=count_unique_course
                               , value=prof_teachings, len=count_courses, value1=list, len1=len(list)
                               , value2=list_student_info)
    return redirect(url_for('login_page'))

@app.route('/login/professors/organize_team/', methods=["POST","GET"])
def professor_organize_page():
    if session.get('logged_in') and 'Prof_username' in session:
        db = mysql.connect(host="localhost", port=3306, user="root", password='88888888', db="LSU")
        cur = db.cursor()
        p_email = session.get('Prof_username')
        count_unique_course = cur.execute(
            "select S.section_type from Sections S, Prof_teams_members P where S.prof_team_id = P.team_id and "
            " P.prof_email =(%s)", [p_email])
        c_unique_type = cur.fetchall()

        cur.execute("select team_id from Prof_teams_members where prof_email=(%s)", [p_email])
        prof_team_id = cur.fetchone()[0]
        count_courses = cur.execute(
            " select S.course_id, S.sec_no,S.section_type from Sections S where S.prof_team_id = (%s)"
            , [prof_team_id])
        prof_teachings = cur.fetchall()
        if request.method == 'POST':
            course = request.form.get('course_id_sec')
            student_id = request.form['student_id']
            team_id = request.form['team_id']
            if course == 'Assigned Courses':
                flash("Please Select Course Or Assignment Type")
            else:
                course = course.split('#')
                c_id = course[0]
                c_sec = course[1]

                check_student = cur.execute("select email from Students where email=(%s)", [student_id])
                if check_student > 0:
                    check_in_section = cur.execute("select student_email from Enrolls where student_email =(%s)"
                                                   " and course_id =(%s) and section_no=(%s)", [student_id,c_id,c_sec])
                    if check_in_section > 0:
                        # check_student_team_id = cur.execute("select team_id from Capstone_Team_Members where "
                        #                                     "student_email =(%s) and course_id =(%s) and sec_no =(%s)"
                        #                                     ,[student_id, c_id, c_sec])
                        # student_team_id = cur.fetchone()[0]
                        # print(student_team_id, team_id)
                        # if student_team_id == team_id:
                        #     flash('Student Already In This Team')
                        # else:
                        cur.execute('update Capstone_Team_Members set team_id=(%s) where student_email=(%s) and '
                                    'course_id =(%s) and sec_no=(%s)', [team_id,student_id,c_id,c_sec])
                        db.commit()
                        flash("Student Organized Successfully")
                    else:
                        flash("Student Not In This Course Section")
                else:
                    flash("Invalid Student Email")
        db.close()
        return render_template('organize_capstone_team.html', value_unique=c_unique_type, len_unique=count_unique_course,
                               value=prof_teachings, len1=count_courses)
    return redirect(url_for('login_page'))


@app.route("/logout/")
def logout():
    session['logged_in'] = False
    return render_template('home.html')


if __name__ == '__main__':
    app.run() #(debug= True)
