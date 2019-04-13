import pandas as pd
from sqlalchemy import *



#engine = create_engine("mysql://root:88888888@127.0.0.1:3306/LSU")
engine = create_engine("mysql+pymysql://root:Lgg971225@127.0.0.1:3306/lsu", pool_pre_ping=True)
skr = engine.connect()


df = pd.read_csv('Students.csv', header=0)
df1 = pd.read_csv('Professors.csv', header=0)


#db = mysql.connect(host="127.0.0.1",port=3306, user="root", password='88888888', db="LSU")  # schema => database
#skr = db.cursor()

skr.execute(" CREATE TABLE IF NOT EXISTS Students( email CHAR(50), password CHAR(20), s_name CHAR(50), age INT, gender CHAR(1), "
            "major CHAR(10), street CHAR(50), zipcode CHAR(5),PRIMARY KEY (email)) ")
skr.execute(" CREATE TABLE IF NOT EXISTS Zipcode(zipcode CHAR(5), city CHAR(20), state CHAR(20), PRIMARY KEY (zipcode)) ")
skr.execute(" CREATE TABLE IF NOT EXISTS Professor( email CHAR(50), password CHAR(20), p_name CHAR(50), age INT, gender CHAR(1), "          
            " office_address CHAR(50), department CHAR(10), title CHAR(10), PRIMARY KEY (email) )")                                                 # office_address = office
skr.execute(" CREATE TABLE IF NOT EXISTS Department(dept_id CHAR(10), dept_name CHAR(50), dept_head CHAR(50), PRIMARY KEY (dept_id))")              # dept_head = professor name
                                                                                                                                                    # dept_id = department
skr.execute("CREATE TABLE IF NOT EXISTS Course(course_id CHAR(15), course_name CHAR(50), course_description CHAR(50), PRIMARY KEY (course_id))")    # course_id =course1,2,3
skr.execute("CREATE TABLE IF NOT EXISTS Sections(course_id CHAR(15), sec_no INT, section_type CHAR(5), s_limit INT, prof_team_id INT, "             # prof_team_id= team_id  | section_type=course_type
            "PRIMARY KEY (course_id,sec_no) )")                                                                                                     # course_description=details
skr.execute("CREATE TABLE IF NOT EXISTS Enrolls(student_email CHAR(50), course_id CHAR(15), section_no INT, PRIMARY KEY (student_email, course_id) )")
skr.execute("CREATE TABLE IF NOT EXISTS Prof_teams(team_id INT,PRIMARY KEY (team_id) )")
skr.execute("CREATE TABLE IF NOT EXISTS Prof_teams_members(prof_email CHAR(50), team_id INT, PRIMARY KEY (prof_email))")
skr.execute("CREATE TABLE IF NOT EXISTS Homework(course_id CHAR(15), sec_no INT, hw_no INT, hw_details CHAR(60), PRIMARY KEY (course_id, sec_no, hw_no))")
skr.execute("CREATE TABLE IF NOT EXISTS Homework_grades( student_email CHAR(50), course_id CHAR(15), sec_no INT, hw_no INT, grade INT, "
            "PRIMARY KEY (student_email,course_id, sec_no,hw_no ))")
skr.execute("CREATE TABLE IF NOT EXISTS Exams(course_id CHAR(15), sec_no INT, exam_no INT, exam_details CHAR(60), PRIMARY KEY (course_id,sec_no))")
skr.execute("CREATE TABLE IF NOT EXISTS Exam_grades(student_email CHAR(50), course_id CHAR(15), sec_no INT, exam_no INT, grades INT, "
            "PRIMARY KEY (student_email,course_id,sec_no))")
skr.execute("CREATE TABLE IF NOT EXISTS Capstone_section(course_id CHAR(15), sec_no INT, project_no INT, sponsor_id CHAR(50), "                     # sponsor_id = professor_email
            "PRIMARY KEY(course_id, sec_no, project_no))")                                                                                          # project_no = ?
skr.execute("CREATE TABLE IF NOT EXISTS Capstone_Team( course_id CHAR(15), sec_no INT, team_id INT, project_no INT,PRIMARY KEY(course_id,sec_no,team_id) )")
skr.execute("CREATE TABLE IF NOT EXISTS Capstone_Team_Members( student_email CHAR(50), team_id INT, course_id CHAR(15), sec_no INT, "
            "PRIMARY KEY (student_email,course_id,sec_no) )")
skr.execute("CREATE TABLE IF NOT EXISTS Capstone_grades(course_id CHAR(15), sec_no INT,team_id INT, grade INT,PRIMARY KEY (course_id,sec_no,team_id,grade) )")

#print(type(df['Full Name']))
#print((df.T).ix[0])
#print (df['Full Name'].values[0])
#print(df['Age'].values)
#sql_prof_team='INSERT INTO LSU.Prof_teams VALUES(%s)'
#prof_team_info=[ 10,20,30,40]
#skr.executemany(sql_prof_team,prof_team_info)


####import data to table : students
student_df = df[["Email","Password","Full Name","Age", "Gender", "Major","Street", "Zip"]]
student_df.columns=["email","password","s_name","age","gender","major","street","zipcode"]
#student_df.to_sql(name="Students", con=skr, if_exists="append", index=False)

####import data to table: zipcode
zipcode_df = df[["Zip", "City", "State"]]
zipcode_df.columns=["zipcode","city","state"]
zipcode_df.drop_duplicates(keep="first",inplace=True)
#zipcode_df.to_sql(name="Zipcode", con=skr, if_exists="append", index=False)

####import data to table: professor
prof_df = df1 [["Email", "Password", "Name", "Age", "Gender", "Office", "Department", "Title"]]
prof_df.columns=["email",'password','p_name',"age","gender","office_address","department","title"]
#prof_df.to_sql(name="Professor", con=skr, if_exists="append", index=False)

####import data to table: department
D_info_df = df1.loc[ df1["Title"] == "Head"]
Department_df = D_info_df[["Department", "Department Name", "Name"]]
Department_df.columns= ["dept_id","dept_name","dept_head"]
#Department_df.to_sql(name="Department", con=skr, if_exists="append", index=False)

####import data to table: course
Course1_df = df[["Courses 1", "Course 1 Name", "Course 1 Details"]]
Course2_df = df[["Courses 2", "Course 2 Name", "Course 2 Details"]]
Course3_df = df[["Courses 3", "Course 3 Name", "Course 3 Details"]]

Course1_df.columns=["course_id", "course_name", "course_description"]
Course2_df.columns=["course_id", "course_name", "course_description"]
Course3_df.columns=["course_id", "course_name", "course_description"]

Course_df = Course1_df.append(Course2_df.append(Course3_df))
Course_df.drop_duplicates(subset="course_id",keep="first",inplace=True)
#Course_df.to_sql(name="Course", con=skr, if_exists="append",index=False)


####import data to table: section
Course1_sec_df = df[["Courses 1", "Course 1 Section", "Course 1 Type","Course 1 Section Limit"]]
Course2_sec_df = df[["Courses 2", "Course 2 Section", "Course 2 Type","Course 2 Section Limit"]]
Course3_sec_df = df[["Courses 3", "Course 3 Section", "Course 3 Type","Course 3 Section Limit"]]

Course1_sec_df.columns = ["course_id", "sec_no", "section_type", "s_limit"]
Course2_sec_df.columns = ["course_id", "sec_no", "section_type", "s_limit"]
Course3_sec_df.columns = ["course_id", "sec_no", "section_type", "s_limit"]

Section_df = Course1_sec_df.append(Course2_sec_df.append(Course3_sec_df))
Section_df.drop_duplicates(subset=["course_id", "sec_no"],keep="first",inplace=True)

Prof_teach_team_df = df1 [["Teaching", "Team ID"]]
Section_df = Section_df.merge(Prof_teach_team_df, left_on= "course_id", right_on="Teaching")
Section_with_team_id_df = Section_df[["course_id", "sec_no", "section_type", "s_limit", "Team ID"]]
Section_with_team_id_df.columns = ["course_id", "sec_no", "section_type", "s_limit","prof_team_iD"]
#Section_with_team_id_df.to_sql(name="Sections", con=skr, if_exists="append",index=False)


####import data to table: enroll
Enroll1_df = df[["Email", "Courses 1", "Course 1 Section"]]
Enroll2_df = df[["Email", "Courses 2", "Course 2 Section"]]
Enroll3_df = df[["Email", "Courses 3", "Course 3 Section"]]

Enroll1_df.columns =["student_email", "course_id", "section_no"]
Enroll2_df.columns =["student_email", "course_id", "section_no"]
Enroll3_df.columns =["student_email", "course_id", "section_no"]
Enroll_df = Enroll1_df.append(Enroll2_df.append(Enroll3_df))
#Enroll_df.to_sql(name="Enrolls", con=skr,if_exists="append", index=False)

####import data to table: Prof_team
Prof_team_df = df1[["Team ID"]]
Prof_team_df.columns = ["team_id"]
#Prof_team_df.to_sql(name="Prof_teams", con=skr, if_exists="append", index=False)

####import data to table: Prof_teams_member
Prof_team_member_df = df1[["Email", "Team ID"]]
Prof_teach_team_df.columns =["prof_email", "team_id"]
#Prof_teach_team_df.to_sql(name="Prof_teams_members", con=skr, if_exists="append", index=False)

####import data to table: Homework
Homework1_df = df[["Courses 1", "Course 1 Section", "Course 1 HW_No","Course 1 HW_Details"]]
Homework2_df = df[["Courses 2", "Course 2 Section", "Course 2 HW_No","Course 2 HW_Details"]]
Homework3_df = df[["Courses 3", "Course 2 Section", "Course 2 HW_No","Course 2 HW_Details"]]

Homework1_df.columns = ["course_id","sec_no","hw_no","hw_details"]
Homework2_df.columns = ["course_id","sec_no","hw_no","hw_details"]
Homework3_df.columns = ["course_id","sec_no","hw_no","hw_details"]
Homework_df = Homework1_df.append(Homework2_df.append(Homework3_df))
Homework_df.drop_duplicates(subset=["course_id","sec_no","hw_no"], keep="first", inplace=True)
#Homework_df.to_sql(name="Homework", con=skr, if_exists="append", index=False)

####import data to table: Homework_grades
Homework1_grade_df = df[["Email", "Courses 1", "Course 1 Section", "Course 1 HW_No", "Course 1 HW_Grade"]]
Homework2_grade_df = df[["Email", "Courses 2", "Course 2 Section", "Course 2 HW_No", "Course 2 HW_Grade"]]
Homework3_grade_df = df[["Email", "Courses 3", "Course 2 Section", "Course 2 HW_No", "Course 3 HW_Grade"]]

Homework1_grade_df.columns = ["student_email", "course_id", "sec_no", "hw_no","grade"]
Homework2_grade_df.columns = ["student_email", "course_id", "sec_no", "hw_no","grade"]
Homework3_grade_df.columns = ["student_email", "course_id", "sec_no", "hw_no","grade"]
Homework_grade_df = Homework1_grade_df.append(Homework2_grade_df.append(Homework3_grade_df))
#Homework_grade_df.to_sql(name="Homework_grades", con=skr, if_exists="append", index=False)

####import data to table: Exams
Exam1_df = df[["Courses 1", "Course 1 Section", "Course 1 EXAM_No", "Course 1 Exam_Details"]]
Exam2_df = df[["Courses 2", "Course 2 Section", "Course 2 EXAM_No", "Course 2 Exam_Details"]]
Exam3_df = df[["Courses 3", "Course 3 Section", "Course 3 EXAM_No", "Course 3 Exam_Details"]]

Exam1_df.columns = ["course_id", "sec_no", "exam_no", "exam_details"]
Exam2_df.columns = ["course_id", "sec_no", "exam_no", "exam_details"]
Exam3_df.columns = ["course_id", "sec_no", "exam_no", "exam_details"]
Exam_df = Exam1_df.append(Exam2_df.append(Exam3_df))
Exam_df.drop_duplicates(subset=["course_id","sec_no","exam_no"],keep="first",inplace=True)
#Exam_df.to_sql(name = "Exams", con=skr, if_exists="append", index=False)

####import data to table: Exam_grades
Exam1_grade_df = df[["Email", "Courses 1", "Course 1 Section", "Course 1 EXAM_No", "Course 1 EXAM_Grade"]]
Exam2_grade_df = df[["Email", "Courses 2", "Course 2 Section", "Course 2 EXAM_No", "Course 3 EXAM_Grade"]]
Exam3_grade_df = df[["Email", "Courses 3", "Course 3 Section", "Course 3 EXAM_No", "Course 3 EXAM_Grade"]]

Exam1_grade_df.columns = ["student_email", "course_id", "sec_no", "exam_no","grades"]
Exam2_grade_df.columns = ["student_email", "course_id", "sec_no", "exam_no","grades"]
Exam3_grade_df.columns = ["student_email", "course_id", "sec_no", "exam_no","grades"]
Exam_grade_df = Exam1_grade_df.append(Exam2_grade_df.append(Exam3_grade_df))
#Exam_grade_df.to_sql(name="Exam_grades", con=skr, if_exists="append", index=False)

####import data to table:Capstone_section(course_id CHAR(15), sec_no INT, project_no INT, sponsor_id CHAR(50), PRIMARY KEY(course_id, sec_no, project_no))")
Cap_df = Section_df.loc[Section_df["section_type"]== "Cap"]
Cap_df = Cap_df[["course_id", "sec_no", "Team ID"]]
Cap_section_df = Cap_df.merge(Prof_teach_team_df, left_on="Team ID", right_on="team_id" )
Cap_team_df = Cap_section_df
Cap_section_df = Cap_section_df[["course_id","sec_no","prof_email"]]
Cap_section_df.columns = ["course_id", "sec_no", "sponsor_id"]
#Cap_section_df.to_sql(name="Capstone_section", con=skr, if_exists="append")  #then set index to project_no in mysql manually

###import data to table: Capstone_Team( course_id CHAR(15), sec_no INT, team_id INT, project_no INT,PRIMARY KEY(team_id) )")
Cap_team_df = Cap_team_df[["course_id", "sec_no", "Team ID"]]
Cap_team_df.columns = ["course_id", "sec_no", "team_id"]
#Cap_team_df.to_sql(name="Capstone_Team", con=skr, if_exists="append")  #then set index to project_no in mysql manually

###import data to table:  Capstone_Team_Members
Cap_team_member_df = Enroll_df.merge(Cap_team_df, left_on = "course_id" , right_on="course_id")
Cap_team_member_df.drop_duplicates(subset="student_email", keep="first", inplace=True)
Cap_team_member_df = Cap_team_member_df[["student_email", "team_id", "course_id", "sec_no"]]
#Cap_team_member_df.to_sql(name="Capstone_Team_Members", con=skr, if_exists="append", index=False)

###import data to table: Capstone_grades(course_id CHAR(15), sec_no INT,team_id INT, grade INT,PRIMARY KEY (course_id,sec_no,team_id) )"
#print(Cap_team_df)
# grade of cap hw
#print(Homework_grade_df)

Capstone_grade_df = Homework_grade_df.merge(Cap_team_df, left_on="course_id", right_on="course_id")
Capstone_grade_df = Capstone_grade_df[["course_id", "sec_no_y", "team_id", "grade"]]
Capstone_grade_df.columns = ["course_id", "sec_no", "team_id", "grade"]
Capstone_grade_df.drop_duplicates(keep="first", inplace=True)
#Capstone_grade_df.to_sql(name="Capstone_grades", con=skr, if_exists="append", index=False)


#p=skr.execute("SELECT email FROM LSU.Professor")
#p1=p.fetchall()
#print(p1[1])


skr.close()


