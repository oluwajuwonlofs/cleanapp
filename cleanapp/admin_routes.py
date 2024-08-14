import secrets, os
from functools import wraps

from flask import render_template,request,redirect,url_for,flash,session,abort, jsonify
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

from cleanapp import app
from cleanapp.models import db,Admin,Role, Service, Localgovernment, State, User, Item, Clothingtype, Request, Dispatcher, Drycleaner




def get_admin_by_id(admin_id):
    admin_deets =db.session.query(Admin).get(admin_id)
    return admin_deets

#decorator function
def adminlogin_required(f):
    @wraps(f)
    def check_adminlogin(*args,**kwargs):
        if session.get('adminonline') != None:
           return f(*args, **kwargs)
        else:
            flash("You must be logged in to view this page", category="error")
            return redirect("/admin/")
    return check_adminlogin



@app.route("/viewdispatchers/", methods=['POST', 'GET'])
def dispatchers():
    admin_id=session.get('adminonline') #retrieve the id from session
    if admin_id != None:
        admindeets = get_admin_by_id(admin_id)
        dispatchers=Dispatcher.query.all()
        return render_template("admin/dispatcherlist.html",admindeets=admindeets, dispatchers=dispatchers, title="Dispatcher List")
    else:
        flash("You must be logged in to view this page", category="error")
        return redirect("/admin/")

@app.route("/viewdrycleaners/", methods=['POST', 'GET'])
def drycleaners():
    admin_id=session.get('adminonline') #retrieve the id from session
    if admin_id != None:
        admindeets = get_admin_by_id(admin_id)
        drycleaners=Drycleaner.query.all()
        return render_template("admin/drycleanerslist.html",admindeets=admindeets, drycleaners=drycleaners, title="Drycleaner List")
    else:
        flash("You must be logged in to view this page", category="error")
        return redirect("/admin/")


@app.route("/viewclients/", methods=['POST', 'GET'])
def view_clients():
    admin_id=session.get('adminonline') #retrieve the id from session
    if admin_id != None:
        admindeets = get_admin_by_id(admin_id)
        users=User.query.all()
        return render_template("admin/clientlist.html",admindeets=admindeets, users=users, title="Users List")
    else:
        flash("You must be logged in to view this page", category="error")
        return redirect("/admin/")

@app.route('/assign_dispatcher/<int:request_id>/', methods=['POST'])
def assign_dispatcher(request_id):
    admin_id = session.get('adminonline')
    if admin_id is not None:
        user_request = Request.query.get_or_404(request_id)
        dispatchers = Dispatcher.query.all()

        if request.method == 'POST':
            dispatcher_id = request.form.get('dispatcher_id')
            
            # Validating the dispatcher_id
            if dispatcher_id:
                dispatcher = Dispatcher.query.get(dispatcher_id)
                if dispatcher is None:
                    flash('Invalid dispatcher selected.', 'error')
                    return redirect(url_for('assign_dispatcher', request_id=request_id))  #endpint
            try:
                # Updating the client request with the assigned dispatcher
                user_request.dispatcher_id = dispatcher_id
                db.session.commit()
                flash('Dispatcher assigned successfully.', 'success')
                return redirect(url_for('view_requests'))
            
            except IntegrityError as e:
                db.session.rollback()
                flash('IntegrityError: Failed to assign dispatcher. Please try again.', 'error')
                app.logger.error(f"IntegrityError: {str(e)}")
        return redirect(url_for('view_requests'))  # Redirecing to view_requests if it is not POST or  incase validation fails
    return redirect(url_for('login'))  # Redirecting to admin dashboard if admin is not logged in

@app.route('/assign_drycleaner/<int:request_id>/', methods=['POST'])
def assign_drycleaner(request_id):
    admin_id = session.get('adminonline')
    if admin_id is not None:
        user_request = Request.query.get_or_404(request_id)
        drycleaners = Drycleaner.query.all()

        if request.method == 'POST':
            drycleaner_id = request.form.get('drycleaner_id')
            
            # Validate drycleaner_id
            if drycleaner_id:
                drycleaner = Drycleaner.query.get(drycleaner_id)
                if drycleaner is None:
                    flash('Invalid drycleaner selected.', 'error')
                    return redirect(url_for('assign_drycleaner', request_id=request_id))  # Corrected endpoint
            
            try:
                # Update the client request with the assigned drycleaner
                user_request.drycleaner_id = drycleaner_id
                db.session.commit()
                flash('Drycleaner assigned successfully.', 'success')
                return redirect(url_for('view_requests'))
            
            except IntegrityError as e:
                db.session.rollback()
                flash('IntegrityError: Failed to assign drycleaner. Please try again.', 'error')
                app.logger.error(f"IntegrityError: {str(e)}")
        
        return redirect(url_for('view_requests'))  # Redirect to view_requests if not POST or validation fails
    
    return redirect(url_for('view_requests'))  # Redirect to admin dashboard if admin is not logged in


@app.route("/viewrequests/", methods=['POST', 'GET'])
def view_requests():
        admin_id = session.get('adminonline')  # retrieve the id from session
        if admin_id:
            admindeets = get_admin_by_id(admin_id)
            requests = Request.query.all()  # Query all client requests from your database
            dispatchers=Dispatcher.query.all()
            drycleaners=Drycleaner.query.all()
            return render_template("admin/requests.html", admindeets=admindeets, requests=requests,dispatchers=dispatchers, drycleaners=drycleaners, title="View Requests")
        else:
            flash("You must be logged in to view this page", category="error")
            return redirect("/admin/")
   


@app.route("/viewpricelist/", methods=['POST', 'GET'])
def view_pricelist():
    admin_id=session.get('adminonline') #retrieve the id from session
    if admin_id != None:
        admindeets = get_admin_by_id(admin_id)
        return render_template("admin/pricelist.html",admindeets=admindeets, title="Price List")
    else:
        flash("You must be logged in to view this page", category="error")
        return redirect("/admin/")



@app.route("/viewservices/", methods=['POST', 'GET'])
def view_services():
    admin_id=session.get('adminonline') #retrieve the id from session
    services= Service.query.all()
    if admin_id != None:
        admindeets = get_admin_by_id(admin_id)
        return render_template("admin/services.html",admindeets=admindeets, services=services, title="Our Services")
    else:
        flash("You must be logged in to view this page", category="error")
        return redirect("/admin/")




@app.route("/addservice/", methods=['POST','GET'])
def addservice():
    if session.get('adminonline') != None:
        if request.method=='GET':
            return render_template("admin/addservice.html")
        else:
            serv_name=request.form.get("serv_name")
            serv_price=request.form.get("serv_price")
            serv_status=request.form.get("serv_status")
            serv_description=request.form.get("serv_description")
            fileobj=request.files.get("serv_image")
            filename=fileobj.filename
            allowed=["jpg", "png", "jpeg"]
            if filename and serv_name:
                file_deets= filename.split(".")
                ext= file_deets[-1]
                if ext in allowed:
                    newname= secrets.token_hex(8)+ "." +ext
                    fileobj.save("cleanapp/static/service_images/"+ newname)
                    service= Service(serv_name=serv_name,serv_price=serv_price,serv_status=serv_status,serv_description=serv_description,serv_image=newname)
                    db.session.add(service)
                    db.session.commit()
                    flash("Service created successfully", category="success")
                    return redirect("/adminbreakout/")
                else:
                    flash("File extension not allowed, allowed extensions are jpg,png and jpeg", category="error")
                    return redirect("/additem/")
            else:
                flash("You need to select a file for upload and ensure you provide the name", category="error")
                return redirect("/addservice/")
    else:
        flash("You must be logged in to access this page", category="error")
        return redirect("/admin/")


@app.route("/deleteservice/<int:id>/")
def service_delete(id):
    if session.get('adminonline') !=None:
        service=db.session.query(Service).get_or_404(id)
        actual_image= service.serv_image
        db.session.delete(service)
        db.session.commit()
        #delete the physical file from the folder
        os.remove(f"cleanapp/static/service_images/{actual_image}")
        flash("Service has been deleted")
        return redirect("/adminbreakout/")
    else:
        flash("You must be logged in to access this page", category="error")
        return redirect("/admin/")

@app.route("/editservice/<int:id>/")
def edit_service(id):
    if session.get('adminonline') !=None:
        services=db.session.query(Service).filter(Service.serv_id==id).first()
        if services:
            return render_template("admin/editservice.html", services=services)
        else:
            abort(400)
    else:
        flash("You must be logged in to access this page", category="error")
        return redirect("/admin/")


@app.route("/viewitem/", methods=['POST', 'GET'])
def view_item():
    admin_id=session.get('adminonline') #retrieve the id from session
    items= Item.query.all()
    if admin_id != None:
        admindeets = get_admin_by_id(admin_id)
        return render_template("admin/item.html",admindeets=admindeets, items=items, title="Our Items")
    else:
        flash("You must be logged in to view this page", category="error")
        return redirect("/admin/")

    
@app.route("/additem/", methods=['POST','GET'])
def additem():
    if session.get('adminonline') != None:
        clothingtypes=Clothingtype.query.all()
        if request.method=='GET':
            return render_template("admin/additem.html", clothingtypes=clothingtypes)
        else:
            item_clothingtype=request.form.get("item_clothingtype")
            item_name=request.form.get("item_name")
            item_price=request.form.get("item_price")
            item_status=request.form.get("item_status")
            item_description=request.form.get("item_description")
            fileobj=request.files.get("item_image")
            filename=fileobj.filename
            allowed=["jpg", "png", "jpeg"]
            if filename and item_name:
                file_deets= filename.split(".")
                ext= file_deets[-1]
                if ext in allowed:
                    newname= secrets.token_hex(8)+ "." +ext
                    fileobj.save("cleanapp/static/item_images/"+ newname)
                    item= Item(item_name=item_name,item_price=item_price,item_status=item_status,item_description=item_description,item_image=newname,item_clothingtype=item_clothingtype)
                    db.session.add(item)
                    db.session.commit()
                    flash("Item created successfully", category="success")
                    return redirect("/adminbreakout/")
                else:
                    flash("File extension not allowed, allowed extensions are jpg,png and jpeg", category="error")
                    return redirect("/additem/")
            else:
                flash("You need to select a file for upload and ensure you provide the name", category="error")
                return redirect("/additem/")
    else:
        flash("You must be logged in to access this page", category="error")
        return redirect("/admin/")

@app.route("/deleteitem/<int:id>/")
def item_delete(id):
    if session.get('adminonline') !=None:
        item=db.session.query(Item).get_or_404(id)
        actual_image= item.item_image
        db.session.delete(item)
        db.session.commit()
        #delete the physical file from the folder
        os.remove(f"cleanapp/static/item_images/{actual_image}")
        flash("Item has been deleted")
        return redirect("/adminbreakout/")
    else:
        flash("You must be logged in to access this page", category="error")
        return redirect("/admin/")

@app.route("/edititem/<int:id>/")
def edit_item(id):
    if session.get('adminonline') !=None:
        items=db.session.query(Item).filter(Item.item_id==id).first()
        clothingtypes= Clothingtype.query.all()
        if items:
            return render_template("admin/edititem.html", items=items, clothingtypes=clothingtypes)
        else:
            abort(400)
    else:
        flash("You must be logged in to access this page", category="error")
        return redirect("/admin/")




@app.route("/deleteclient/<int:id>/")
def delete_user(id):
    if session.get('adminonline') !=None:
        user=db.session.query(User).get_or_404(id)
        actual_image= user.user_pix
        db.session.delete(user)
        db.session.commit()
        #delete the physical file from the folder
        os.remove(f"cleanapp/static/client_uploads/{actual_image}")
        flash("User has been deleted")
        return redirect("/adminbreakout/")
    else:
        flash("You must be logged in to access this page", category="error")
        return redirect("/admin/")

@app.route("/deletedispatcher/<int:id>/")
def delete_dispatcher(id):
    if session.get('adminonline') !=None:
        dispatcher=db.session.query(Dispatcher).get_or_404(id)
        actual_image= dispatcher.dispatcher_pix
        db.session.delete(dispatcher)
        db.session.commit()
        #delete the physical file from the folder
        os.remove(f"cleanapp/static/dispatcher_uploads/{actual_image}")
        flash("Dispatcher has been deleted")
        return redirect("/adminbreakout/")
    else:
        flash("You must be logged in to access this page", category="error")
        return redirect("/admin/")
    
@app.route("/deletedrycleaner/<int:id>/")
def delete_drycleaner(drycleaner_id):
    if session.get('adminonline') !=None:
        drycleaner=db.session.query(Dispatcher).get_or_404(drycleaner_id)
        actual_image= drycleaner.drycleaner_pix
        db.session.delete(drycleaner)
        db.session.commit()
        #delete the physical file from the folder
        os.remove(f"cleanapp/static/drycleaner_uploads/{actual_image}")
        flash("Drycleaner has been deleted")
        return redirect("/adminbreakout/")
    else:
        flash("You must be logged in to access this page", category="error")
        return redirect("/admin/")


@app.route("/adminbreakout/")
def breakout():
    if session.get('adminonline') !=None:
        services=db.session.query(Service).all()
        items=db.session.query(Item).all()
        return render_template("admin/adminbreakout.html", services=services, items=items)
    else:
        flash("You must be logged in to access this page", category="error")
        return redirect("/admin/")

@app.route("/admin/dashboard/")
def admin_dashboard():
    if session.get('adminonline') != None:
        return render_template("admin/dashboard.html")
    else:
        flash("You need to login to access this page", category="error")
        return redirect("/admin/")
    

@app.route("/admin/profilepage//")
def admin_profilepage():
    id=session.get('adminonline') #retrieve the id from session
    if id != None:
        admindeets = get_admin_by_id(id)
        return render_template("admin/adminprofilepage.html",admindeets=admindeets)
    else:
        flash("You must be logged in to view this page", category="error")
        return redirect("/admin/")
    
@app.route("/admin/", methods=['POST', 'GET'])
def admn_login():
    if request.method=='GET':
        return render_template("admin/cleanappadminloginform.html")
    else:
        #retrieve the form data
        admin_username = request.form.get('admin_username')
        admin_pwd = request.form.get('admin_pwd')
        if admin_username == '' or admin_pwd =='':
            flash('Both fields must be supplied',category='error')
            return redirect("/admin/")
        else:
            admin=db.session.query(Admin).filter(Admin.admin_username==admin_username).first() #to know the stored hash if email is not unique we use .first()
            if admin != None:
               stored_hash=admin.admin_pwd #hashedpassword from datatbase
               chk= check_password_hash(stored_hash,admin_pwd) #
               if chk: #login was succesul
                    flash("Logged in successfully", category='success')
                    session['adminonline']= admin.admin_id
                    return redirect('/admin/dashboard/')
               else:
                    flash('Invalid Password', category='error')
            else:
                flash('Invalid Username', category='error')
            return redirect("/admin/")
        
@app.route("/admin/logout/")
def admin_logout():
    if session.get('adminonline') !=None:
        session.pop('adminonline')
        flash("You have logged out succesfully", category="success")
    return redirect("/admin/")



@app.route("/userstory/", methods=['POST', 'GET'])
def userstory():
    return render_template("admin/userstory.html" , title='Welcome to Our Home Page' , page='home')

@app.route("/about/our-team/management/<id>/")
def about_cleanapp():
    return render_template("admin/aboutmanagement.html", title='About Us' , page='about')


@app.route("/blog/latest-contents/all/")
def cleanapp_blog():
    return render_template("admin/ourblog.html", title='Our blog', page='blog' )

@app.route("/contactus/")
def contact_cleanapp():
    return render_template("admin/contact.html", title='Our contact', page='contact')





#error handling for cleanapp
@app.errorhandler(404)
def page_not_found(error):
    return render_template("admin/error.html", error=error),404


@app.errorhandler(410)
def page_gone(error):
    return render_template("admin/pagegoneerror.html", error=error),410



@app.errorhandler(500)
def server_error(error):
    return render_template("admin/servererror.html", error=error),500


# # @app.route("/update_processing_date/<int:request_id>", methods=['POST'])
# # def update_processing_date(request_id):
# #     # Fetching the request from the database
# #     request_obj = Request.query.get(request_id)

# #     if not request_obj:
# #         flash(f"Request with ID {request_id} does not exist.", category="error")
# #         return redirect(url_for('admin_dashboard'))  

# #     # Get processing date from form
# #     processing_date = request.form.get('processing_date')

# #     # Updating request_processeddate if the request has been picked up
# #     if request_obj.pickedup_status == 'pickedup':
# #         flash("Processing date cannot be updated as the request has already been picked up.", category="error")
# #     else:
# #         request_obj.request_processeddate = processing_date
# #         db.session.commit()
# #         flash(f"Processing date updated successfully for Request ID {request_id}.", category="success")

#     return redirect(url_for('admin_dashboard')) 