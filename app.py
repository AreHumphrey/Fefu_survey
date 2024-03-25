from flask import Flask, render_template, request, jsonify, url_for, redirect
import os
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'identifier.sqlite')
db = SQLAlchemy(app)


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
            return redirect(url_for('admin_panel'))
        else:
            return "Incorrect password. Access denied."
    return render_template('pages/admin_login.html')


@app.route('/admin-panel', methods=['GET', 'POST'])
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


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
