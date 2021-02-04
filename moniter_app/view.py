from flask import render_template, url_for, redirect, send_from_directory
from flask import request, session, flash, json
from werkzeug.utils import secure_filename
from sqlalchemy import exc

from moniter_app import app, pjdir
from moniter_app import db
from moniter_app.database import *
#from moniter_app.page import FormLogin 

import datetime, os

@app.route("/", methods=["GET","POST"])
def index():
    user = session.get("username")
    if user:
        ## get districts
        districts_query = "select distinct(district) from schools"
        query_data = db.engine.execute(districts_query)
        districts = [row[0] for row in query_data]

        return render_template("dashboard.html", districts=districts)
    else:
        return redirect(url_for("login"))

@app.route('/login',methods=['GET','POST'])
def login():
    # form=FormLogin()
    # if form.validate_on_submit():
    #     query_row = Account.query.filter_by(username=form.username.data).first()
    #     if query_row:
    #         if query_row.password == form.password.data:
    #             session["username"] = form.username.data
    #             return redirect(url_for("index"))
    #         else:
    #             flash("wrong password")
    #             return render_template('login.html', form=form)
    #     else:
    #         flash("unavailable username")
    #         return render_template('login.html', form=form)
    if request.method == "POST":
        query_row = Account.query.filter_by(username=request.form.get("username")).first()
        if query_row:
            if query_row.password == request.form.get("password"):
                session["username"] = request.form.get("username")
                session["authority"] = query_row._type
                return redirect(url_for("index"))
            else:
                flash("wrong password")
                return render_template('login.html', modal="show")
        else:
            flash("unavailable username")
            return render_template('login.html', modal="show")
    return render_template('login.html', modal="hide")

@app.route("/dashboard_data", methods=["POST"])
def dashboard():
    if request.method == "POST":
        if request.form.get("type") == "progress":
            ## get progress for initial pie chart
            progress_query = "select type, count(*) from progress where finished=1 group by type"
            query_data = db.engine.execute(progress_query)
            progress = {"location":0, "construction":0, "inventory":0, "completed":0}#, "acceptance":0}
            for row in query_data:
                progress[row[0]] = row[1]

            return {"progress":progress}
        elif request.form.get("type") == "schools":
            district = request.form.get("district")

            ## get school names for update barchart of each district
            schools_query = "select id,name from schools where district='{}' order by id".format(district)
            query_data = db.engine.execute(schools_query)
            schoolNames = ["{:0>3d}{}".format(row[0], row[1])for row in query_data]

            ## get school progress
            schools_progress_query = "select id,name,type,finished from schools inner join progress on schools.id=progress.school_id where district='{}' order by id".format(district)
            query_data = db.engine.execute(schools_progress_query)
            schoolProgress = [list(row) for row in query_data.fetchall()]
            # print(type(schoolProgress))
            # print(schoolProgress)

            return {"schools":schoolNames, "progress":schoolProgress}
        elif request.form.get("type") == "pieList":
            ## get the list of schools which meet the conditions
            finished = "" if request.form.get("finished") == "1" else " not"

            # get schools names
            schools_query = "select id,name from schools where id{} in (select school_id from progress where finished=1 and type='{}') order by id".format(finished, request.form.get("stage"))
            query_data = db.engine.execute(schools_query)
            schoolNames = ["{:0>3d}{}".format(row[0], row[1])for row in query_data]

            # get progress of each school
            schools_progress_query = "select id,name,type,finished from schools inner join progress on school_id=id where id{} in (select school_id from progress where finished=1 and type='{}') order by id".format(finished, request.form.get("stage"))
            query_data = db.engine.execute(schools_progress_query)
            schoolProgress = [list(row) for row in query_data.fetchall()]

            return {"schools":schoolNames, "progress":schoolProgress}

@app.route("/info/school_<schoolId>", methods=["GET", "POST"])
def schoolInfo(schoolId):
    user = session.get("username")
    authority = session.get("authority")
    change_flag = "disabled" if authority == "user" else ""
    if request.method == "POST":
        if request.json:
            if "schools" in request.json["target"]:
                if authority == "user":
                    return {"state":False, "msg":"unauthorized"}

                ## for update school data
                schoolData = Schools.query.filter_by(id=int(schoolId)).first()
                if schoolData:
                    for field, value in request.json["data"].items():
                        setattr(schoolData, field, value)

                    db.session.commit()
                    return {"state":True}
                    # try:
                    #     db.session.commit()
                    # except exc.SQLAlchemyError as e:
                    #     return {"state":False, "msg":e.__dict__['orig']}
                    # return {"state":True}
                else:
                    # It won't be used
                    return {"state":False, "msg":"Unavailable school"}
            elif "progress" in request.json["target"]:
                ## for initial progress of this school
                progress_query = "select type,finished from progress where school_id='{}'".format(schoolId)
                query_data = db.engine.execute(progress_query)
                finished = {"location":0, "construction":0, "inventory":0, "completed":0}#, "acceptance":0}
                
                for row in query_data:
                    finished[row[0]] = row[1]
                return finished
            else:
                # it won't be used
                return {"state":False, "msg":"invalid target"}
        else:
            # it won't be used
            return {"state":False, "msg":"not json data"}
    else:
        if user:
            schoolData = Schools.query.filter_by(id=int(schoolId)).first()
            if schoolData:
                query_data = Progress.query.filter_by(school_id=int(schoolId))
                progress = {"location":None, "construction":None, "inventory":None, "completed":None,}# "acceptance":None}
                for row in query_data:
                    progress[row._type] = row
                return render_template("SchInfomation.html", school=schoolData, progress=progress, change_flag=change_flag)
            else:
                # It won't be used
                return "Unavailable school"
        else:
            return redirect(url_for("login"))

@app.route("/info/school_<schoolId>/<progress_type>", methods=["GET", "POST"])
def progressInfo(schoolId, progress_type):
    user = session.get("username")
    authority = session.get("authority")
    change_flag = "disabled" if authority == "user" else ""
    if request.method == "POST":
        if request.json:
            if authority == "user":
                return {"state":False, "msg":"unauthorized"}

            if "progress" in request.json["target"]:
                progress = Progress.query.filter_by(school_id=int(schoolId), _type=progress_type).first()
                if progress:
                    ## for update progress
                    for field, value in request.json.items():
                        if field != "target":
                            ## handle multi files 
                            '''if progress_type == "construction" and field == "lastFile":
                                lastFile = json.loads(value)
                                progress_file = json.loads(progress.lastFile)
                                for k,v in lastFile.items():
                                    progress_file[k] = v

                                progress.lastFile = json.dumps(progress_file)
                                continue '''

                            setattr(progress, field, value)
                            if field == "actualDate" and value:
                                actual = datetime.date(*map(int, value.split("-")))
                                if actual <= datetime.date.today():
                                    setattr(progress, "finished", 1)
                                else:
                                    setattr(progress, "finished", 0)
                else:
                    ## for insert progress
                    if progress_type in ["location", "construction", "inventory", "completed"]:#, "acceptance"]:
                        newProgress = Progress()
                        setattr(newProgress, "school_id", schoolId)
                        setattr(newProgress, "_type", progress_type)
                        for field, value in request.json.items():
                            if field != "target":
                                setattr(newProgress, field, value)
                                if field == "actualDate" and value:
                                    actual = datetime.date(*map(int, value.split("-")))
                                    if actual <= datetime.date.today():
                                        setattr(newProgress, "finished", 1)
                                    else:
                                        setattr(newProgress, "finished", 0)
                        db.session.add(newProgress)
                    else:
                        # It won't be used
                        return {"state":False, "msg":"invalid progress type"}
            
            ## for update inventory, only update
            if "inventory" in request.json["target"]:
                inventory = DeviceInventory.query.filter_by(school_id=int(schoolId))
                for i, value in enumerate(inventory):
                    value.count = request.json["inventory"][i]

            db.session.commit()
            return {"state":True}
            # try:
            #     db.session.commit()
            # except exc.SQLAlchemyError as e:
            #     return {"state":False, "msg":e.__dict__['orig']}
            # return {"state":True}
        elif request.files:
            if authority == "user":
                return {"state":False, "msg":"unauthorized"}
                
            ## for upload file
            filenames = {}
            upload_path = os.path.join(pjdir,"uploads",schoolId)
            if not os.path.isdir(upload_path):
                os.makedirs(upload_path)
            for k, f in request.files.items():
                #print(f)
                #print(dir(f.filename))
                #import sys
                #locale.setlocale(locale.LC_ALL, 'zh_TW.UTF-8')
                #raise NameError(sys.getfilesystemencoding())
                with open(os.path.join(upload_path, f.filename.encode('raw_unicode_escape').decode("utf-8")), "wb") as test:
                    test.write(f.stream.read())
                #f.save(os.path.join(upload_path, f.filename))
                filenames[k] = f.filename

                ## update database
                progress = Progress.query.filter_by(school_id=int(schoolId), _type=progress_type).first()
                if progress:
                    progress_file = json.loads(progress.lastFile) if progress.lastFile else {}
                    progress_file[k] = f.filename
                    progress.lastFile = json.dumps(progress_file)
                else:
                    ## add new row
                    newProgress = Progress()
                    setattr(newProgress, "school_id", schoolId)
                    setattr(newProgress, "_type", progress_type)
                    setattr(newProgress, "lastFile", json.dumps(filenames))
                    db.session.add(newProgress)

            db.session.commit()
            return {"state":True, "filenames":filenames}
        else:
            progress = Progress.query.filter_by(school_id=int(schoolId), _type=progress_type).first()
            if progress:
                ## return initial data to pages
                result_json = progress.__dict__
                result_json.pop("_sa_instance_state")

                ## for test
                #result_json["remarks"] = "test"
                #result_json["lastFile"] = "lastfile_2020-10-01.dat"

                return result_json
            else:
                # will not return any data
                return {}
    else:
        if user:
            schoolData = Schools.query.filter_by(id=int(schoolId)).first()
            if schoolData:
                #progress = Progress.query.filter_by(school_id=int(schoolId), _type=progress_type).first()
                #progress = Progress.query.filter_by(_type=progress_type).first()
                #if progress:
                if progress_type == "location":
                    return render_template("SSRRequirement.html", school=schoolData, change_flag=change_flag)
                elif progress_type == "construction":
                    return render_template("Construction.html", school=schoolData, change_flag=change_flag)
                elif progress_type == "inventory":
                    ## get total number of each device
                    inventory_query = "select total,count from deviceInventory where school_id={} order by device_id".format(schoolId)
                    query_data = db.engine.execute(inventory_query)
                    inventory = [(row[0],row[1]) for row in query_data]
                    return render_template("EQUInfo.html", school=schoolData, inventory=inventory, change_flag=change_flag)
                elif progress_type == "completed":
                    return render_template("Completed.html", school=schoolData, change_flag=change_flag)
                #elif progress_type == "acceptance":
                #    return render_template("Acceptance.html", school=schoolData)
                else:
                    # It won't be used
                    return "Unavailable progress type: {}".format(progress_type,)
                # else:
                #     # It won't be used
                #     return "Unavailable progress type: {}".format(progress_type)
            else:
                # It won't be used
                return "Unavailable school"
        else:
            return redirect(url_for("login"))

@app.route("/uploads/school_<schoolId>/<filename>", methods=["GET", "POST"])
def getFile(schoolId, filename):
    return send_from_directory(os.path.join(pjdir,'uploads',schoolId), filename.encode('raw_unicode_escape').decode("utf-8"))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(pjdir+'/static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')