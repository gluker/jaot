import re
from parse import *
from datetime import datetime
from flask import render_template, request, redirect, url_for
from database import db_session
from . import app
from models import Course, ProblemSet, Problem, Requirement

@app.route('/')
@app.route('/courses/')
def showAllCourses():
    courses = db_session.query(Course).all()
    return render_template("showallcourses.html",courses=courses)

###  Views for courses ###
@app.route('/courses/new/', methods=['POST','GET'])
def newCourse():
    if request.method == "POST":
        name = request.form['name']
        course = Course(name=name)
        db_session.add(course)
        db_session.commit()
        return redirect(url_for('showAllCourses'))
    return render_template("newcourse.html")

@app.route('/courses/<int:course_id>/')
@app.route('/courses/<int:course_id>/psets/')
def showCourse(course_id):
    course = db_session.query(Course).get(course_id)
    psets = course.problemsets
    return render_template("showcourse.html",course=course,psets=psets)

@app.route('/courses/<int:course_id>/edit', methods=['GET','POST'])
def editCourse(course_id):
    course = db_session.query(Course).get(course_id)
    if request.method == "POST":
        course.name = request.form['name']
        db_session.commit()
        return redirect(url_for("showCourse",course_id=course.id))
    return render_template("editcourse.html",course=course)

@app.route('/courses/<int:course_id>/delete/', methods=['GET','POST'])
def deleteCourse(course_id):
    course = db_session.query(Course).get(course_id)
    if request.method == "POST":
        db_session.delete(course)
        db_session.commit()
        return redirect(url_for("showAllCourses"))
    return render_template("deletecourse.html",course=course)

### Views for Problem Sets ###
@app.route('/courses/<int:course_id>/psets/new/', methods=['GET','POST'])
def newPSet(course_id):
    course = db_session.query(Course).get(course_id)
    if request.method == "POST":
        form = request.form
        pset = ProblemSet(
            title = form['title'],
            opens = datetime.strptime(form['opens'],"%d/%m/%Y"),
            due = datetime.strptime(form['due'],"%d/%m/%Y"),
            course_id=course.id)
        course.problemsets.append(pset)
        db_session.commit()
        return redirect(url_for("showCourse",course_id=course.id))
    return render_template("newpset.html",course=course)

@app.route('/courses/<int:course_id>/psets/<int:pset_id>/')
@app.route('/courses/<int:course_id>/psets/<int:pset_id>/problems/')
def showPSet(course_id,pset_id):
    course = db_session.query(Course).get(course_id)
    pset = db_session.query(ProblemSet).get(pset_id)
    problems = pset.problems
    return render_template("showpset.html",course=course,pset=pset,problems=problems)

@app.route('/courses/<int:course_id>/psets/<int:pset_id>/edit/',methods=['POST','GET'])
def editPSet(course_id,pset_id):
    course = db_session.query(Course).get(course_id)
    pset = db_session.query(ProblemSet).get(pset_id)
    if request.method == "POST":
        pset.title = form['title']
        pset.opens = datetime.strptime(form['opens'],"%d/%m/%Y")
        pset.due = datetime.strptime(form['due'],"%d/%m/%Y")
        db_session.commit()
        return redirect(url_for('showPSet',course_id=course.id,pset_id=pset.id))
    return render_template("editpset.html",course=course,pset=pset)

@app.route('/courses/<int:course_id>/psets/<int:pset_id>/delete/', methods=["GET",'POST'])
def deletePSet(course_id,pset_id):
    pset = db_session.query(ProblemSet).get(pset_id)
    if request.method == "POST":
        db_session.delete(pset)
        db_session.commit()
        return redirect(url_for('showCourse',course_id=course_id))
    return render_template("deletepset.html",course=course,pset=pset)

### Views for Problems ###
@app.route('/courses/<int:course_id>/psets/<int:pset_id>/problems/new/', methods=['GET','POST'])
def newProblem(course_id, pset_id):
    course = db_session.query(Course).get(course_id)
    pset = db_session.query(ProblemSet).get(pset_id)
    
    if request.method == "POST":
        print request.form
        problem = Problem(text=request.form['text'])
        pset.problems.append(problem)
        for cnt in range(1,int(request.form['counter'])+1):
           req = Requirement(condition = request.form['condition'+str(cnt)],
                        comment = request.form['comment'+str(cnt)])
           problem.requirements.append(req) 
        db_session.commit()
        return redirect(url_for('showPSet',course_id=course.id,pset_id=pset.id))
    return render_template("newproblem.html",course=course,pset=pset)

@app.route('/courses/<int:course_id>/psets/<int:pset_id>/problems/<int:problem_id>/')
def showProblem(course_id,pset_id,problem_id):
    course = db_session.query(Course).get(course_id)
    pset = db_session.query(ProblemSet).get(pset_id)
    problem = db_session.query(Problem).get(problem_id)
    
    return render_template("showproblem.html",course=course,pset=pset,problem=problem)

@app.route('/courses/<int:course_id>/psets/<int:pset_id>/problems/<int:problem_id>/edit/', methods=['GET','POST'])
def editProblem(course_id,pset_id,problem_id):
    course = db_session.query(Course).get(course_id)
    pset = db_session.query(ProblemSet).get(pset_id)
    problem = db_session.query(Problem).get(problem_id)
    if request.method == "POST":
        problem.text = request.form['text']
        db_session.commit()
        return redirect(url_for('showProblem',course_id=course.id,pset_id=pset.id,problem_id=problem.id))
    return render_template("editproblem.html",course=course,pset=pset,problem=problem)

@app.route('/courses/<int:course_id>/psets/<int:pset_id>/problems/<int:problem_id>/delete/')
def deleteProblem(course_id,pset_id,problem_id):
    return render_template("deleteproblem.html",course=course,pset=pset,problem=problem)


@app.route('/courses/<int:course_id>/psets/<int:pset_id>/problems/<int:problem_id>/check/', methods=["POST","GET"])
def checkProblem(course_id,pset_id,problem_id):
    problem = db_session.query(Problem).get(problem_id)
    form = request.form
    reqvars = []
    for req in problem.requirements:
        divider =  re.search('==',req.condition)
        if divider:
            left = req.condition[:divider.start(0)]
            right = req.condition[divider.end():]
            print search('$[{}]',left)
            print search('$[{}]',right)

            print left+" equal to "+ right
        else:
            print "dunno!"
        print search('$[{}]',req.condition).spans

        print req.condition
    return "qwe"
