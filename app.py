from flask import Flask, render_template, request, jsonify, url_for
import os
from flask_sqlalchemy import SQLAlchemy
from flask import redirect

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


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
