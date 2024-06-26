import io
from functools import wraps

from flask import Flask, render_template, request, jsonify, url_for, redirect, session, send_file
import os
from flask_sqlalchemy import SQLAlchemy
import csv
from flask import make_response

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'identifier.sqlite')
db = SQLAlchemy(app)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('admin_login'))

    return decorated_function


@app.route('/')
def index():
    return render_template('pages/index.html')


@app.route('/form', methods=['GET'])
def form():
    return render_template('pages/form.html')


from models import Students, Achievements


@app.route('/submit-form', methods=['POST'])
def submit_form():
    fullname = request.form['fullname']
    group_name = request.form['group_name']
    course = request.form['course']
    achievement = request.form['achievement']
    description = request.form['description']
    attachment = request.files['attachment'].read()

    student = Students(fullname=fullname, group_name=group_name, course=course)
    db.session.add(student)
    db.session.commit()

    achievement = Achievements(student_id=student.student_id, achievement=achievement,
                               description=description, attachment=attachment)
    db.session.add(achievement)
    db.session.commit()

    return jsonify({'redirect': url_for('index')})


@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form['password']
        if password == '1234':
            session['logged_in'] = True
            return redirect(url_for('admin_panel'))
        else:
            return "Incorrect password. Access denied."
    return render_template('pages/admin_login.html')


@app.route('/admin-panel', methods=['GET', 'POST'])
@login_required
def admin_panel():
    students = Students.query.all()

    group_options = db.session.query(Students.group_name).distinct().all()
    group_options = [group[0] for group in group_options]

    if request.method == 'POST':
        group_name = request.form['group_name']
        if group_name != 'All':
            sorted_students = Students.query.filter_by(group_name=group_name).all()
        else:
            sorted_students = students
    else:
        sorted_students = students

    return render_template('pages/admin_panel.html', students=students, sorted_students=sorted_students,
                           group_options=group_options)


@app.route('/download-csv', methods=['GET'])
def download_csv():
    students = Students.query.all()

    csv_data = [["ФИО", "Группа", "Курс", "Достижения"]]

    for student in students:
        achievements = ', '.join([achievement.achievement for achievement in student.achievements])
        csv_data.append([student.fullname, student.group_name, student.course, achievements])

    return generate_csv_response(csv_data, "students_data.csv")


def generate_csv_response(data, filename):
    csvfile = io.StringIO()
    csvwriter = csv.writer(csvfile, delimiter=',')

    for row in data:
        csvwriter.writerow(row)

    csvfile.seek(0)

    response = make_response(csvfile.read().encode('utf-8-sig'))
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'

    return response


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
