import requests, random, os, json,secrets
import imghdr
import uuid
from datetime import datetime
from functools import wraps

from flask import render_template, request, redirect, flash, make_response, session, abort,url_for,jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from cleanapp import app
from cleanapp.models import db, User, Role, Localgovernment ,Payment,Service,State,Requestdetail, Item, Clothingtype, Dispatcher, Drycleaner, Request
from cleanapp.forms import DpForm


from cleanapp import Message, mail


def get_user_by_id(id):
    deets =db.session.query(User).get(id)
    return deets

#decorator function
def login_required(f):
    @wraps(f)
    def check_login(*args,**kwargs):
        if session.get('useronline') != None:
           return f(*args, **kwargs)
        else:
            flash("You must be logged in to view this page", category="error")
            return redirect("/login/")
    return check_login


@app.route("/description/<int:id>/")
def description(id):
    items= db.session.query(Item).filter(Item.item_id==id)
    return render_template("user/descriptions.html", title="Description of items", items=items)

@app.route("/clothingtype/", methods=['POST', 'GET'])
def clothingtype():
    items= db.session.query(Item).all()
    return render_template("user/clothingtype.html", items=items, title="Our Items")


@app.route("/messages/")
@login_required
def messages():
    id=session.get('useronline') #retrieving the id from session
    if id != None:
        users = get_user_by_id(id)
        return render_template("user/messages.html",users=users)
    else:
        flash("You must be logged in to view this page", category="error")
        return redirect("/login/")

@app.route("/report/", methods=['POST', 'GET'])
def report():
    pass
        
@app.route("/sendmail/", methods=['POST'])
@login_required
def sendmail():
    id=session.get('useronline') #retrieve the id from session
    if id != None:
        user = get_user_by_id(id)
        email=request.form.get("user_email")
        content=request.form.get("content")

        #from cleanapp imported message
        # msg=Message(Subject,sender,recipients=["email@example.com"])
        sender="Cleanapp Website"
        subject="Your message was received"
        msg=Message(subject=subject, sender=sender, recipients=[email])
        msg.html=f"Thank you, your message was received as follows:{content} <img src= 'https://media.istockphoto.com/id/1289323170/photo/visual-contents-concept-social-networking-service-streaming-video-communication-network.jpg?s=1024x1024&w=is&k=20&c=bsb8_bvun2B8DFxnvwKkJeeUbm0y93SWhDOVr_HaM20='>"
        mail.send(msg) #from devapp import mail
        return f"Thank you {email}" 
    else:
        flash("You must be logged in to view this page", category="error")
        return redirect("/login/")
    

@app.route("/paystack/initialize/", methods=['POST','GET'])
def paystack_initiatize():
    ref= session.get("payref")
    if ref != None:
        payments=Payment.query.filter(Payment.payment_ref==ref).first()
        amount = payments.payment_amount * 100 #coversion to kobo
        email = payments.user.user_email
        callback_url= "http://127.0.0.1:5000/pay/landing/"
        headers= {"Content-Type":"application/json", "Authorization": "Bearer sk_test_e5ba136f5167af0b5428c31c3d54a5c6a2a7b70b"}
        url= "https://api.paystack.co/transaction/initialize"
        data= {"amount":amount, "email":email,"reference":ref,"callback_url":callback_url}
        try: 
            response= requests.post(url,headers=headers,data=json.dumps(data))#connecting to paystack
            response_json=response.json()
            if response_json and response_json["status"]==True:
                checkoutpage= response_json['data']["authorization_url"]
                return redirect(checkoutpage)
            else:
                flash(f"Paystack returned an error {response_json['message']}", category="error")
                return redirect("/payments/")
        except:
            flash("We could not connect to paystack" , category="error")
            return redirect("/payments/")
    else:
        flash("Please complete the form" , category="error")
        return redirect("/payments/")


@app.route("/payconfirm/", methods=['POST', 'GET'])
def payconfirm():
    """Route fetches details of the payment made by the client so they can confirm if they want to go ahead to edit"""
    ref = session.get("payref")
    if ref != None:
        payments=Payment.query.filter(Payment.payment_ref==ref).first()
        return render_template("user/payconfirm.html", payments=payments)
    else:
        flash("Please complete the donation form", category="error")
        return redirect("/payments/")


@app.route("/payments/",methods=['POST','GET'])
def user_payments():
    id=session.get("useronline")
    user = get_user_by_id(id)
    
    if request.method =='GET':
        active_items = db.session.query(Item).filter(Item.item_status=="1").all()
        
        
        return render_template("user/payments.html", active_items=active_items, user=user)
    else:
        fullname=request.form.get("fullname")
        email=request.form.get("email")
        amt=request.form.get("amt")
        if float(amt) > 0:
            #inserting into payments table
            ref = "CLEAN" + str(int(random.random()*100000000)) #generating payment reference
            session["payref"]= ref #saving ref one we can access anytime
            pay=Payment(payment_amount=amt,payment_userid=id,payment_status="pending",payment_email=email,payment_ref=ref)
            db.session.add(pay)
            db.session.commit()
            return redirect("/payconfirm/")
        else:
            flash("Enter an amount greater than 0", category="error")
            return redirect("/payments/")



@app.route("/pay/landing/")
def payment_landing_page():
    ref=session.get("payref") #the one we know about
    paystackref=request.args.get("reference") #the one coming from paystack
    if ref == paystackref:
        url="https://api.paystack.co/transaction/verify/" + ref
        headers={"Content-Type":"application/json", "Authorization": "Bearer sk_test_e5ba136f5167af0b5428c31c3d54a5c6a2a7b70b"}
        response= requests.get(url,headers=headers)#connecting to paystack
        response_json=response.json()
        #update database
        pay =Payment.query.filter(Payment.payment_ref==ref).first()
        if response_json['status']==True:
            ip = response_json["data"]["ip_address"]
            pay.payment_status="paid"
            pay.payment_dateupdated=datetime.now()
        else:
            pay.payment_status="failed"
        db.session.commit()
        flash( "Thank you, your payment is complete")
        return redirect("/profilepage/")
    else:
        flash("Invalid Parameter detected",category="error")
        return redirect("/reports/")



@app.route("/logout/")
def logout():
    if session.get('useronline')!=None:
        session.pop('useronline')
    return redirect("/login/")


@app.route("/requesthistory/")
@login_required
def request_history():
    user_id = session.get('useronline')  # Retrieving the user_id from session
    
    if user_id is not None:
        user = User.query.get(user_id)  # Fetching the User object using user_id
        if user:
            # Fetching all requests associated with the user
            requests = Request.query.filter_by(client_id=user.user_id).all()
            
            # Querying dispatchers and drycleaners based on the local government of the client
            localgovernment = user.user_lg  # Adjust this according to your User model
            dispatchers = Dispatcher.query.filter_by(dispatcher_lg=localgovernment).all()
            drycleaners = Drycleaner.query.filter_by(drycleaner_lg=localgovernment).all()
            
            return render_template("user/requesthistory.html", user=user, requests=requests, dispatchers=dispatchers, drycleaners=drycleaners)
        else:
            flash("User not found", category="error")
    else:
        flash("You must be logged in to view this page", category="error")
        return redirect("/login/")


@app.route("/clientrequest/",methods=['POST','GET'])
@login_required
def client_request():
    id=session.get("useronline")
    user = get_user_by_id(id)
    if request.method =='GET':
        requests = db.session.query(Request).all()
        return render_template("user/requests.html", requests=requests, user=user)
    else:
        request_createddate=request.form.get("request_createddate")
        if request_createddate:
            new_request=Request(request_createddate=request_createddate, client_id=user.user_id)
            db.session.add(new_request)
            db.session.commit()
            return redirect("/payments/")
        else:
            flash("Enter a pickup date", category="error")
            return redirect("/clientrequest/")


def MagerDicts(dict1,dict2):
    if isinstance(dict1,list) and isinstance(dict2,list):
        return dict1 + dict2
    elif isinstance(dict1,dict) and isinstance(dict2,dict):
        return dict(list(dict1.items()) + list(dict2.items()))
    return False

@app.route('/wain/', methods=['POST','GET'])
@login_required
def wain():
    if 'Laundrywain' not in session or len(session['Laundrywain'])==0:
        return redirect("/cleanappitempage/")
    Subtotal= 0
    grandtotal= 0
    for key, item in session['Laundrywain'].items():
        Subtotal += float(item['price']) * int(item['quantity'])
        grandtotal= float("%.2f"%(1 * Subtotal))
        tax=("%.2f" %(.06* float(Subtotal) ))
        session['Laundrywain']
        session['total']=grandtotal
    return render_template("user/wain.html", grandtotal=grandtotal,Subtotal=Subtotal,tax=tax, item=item)

@app.route("/addwain/", methods=['POST'])
def addwain():
    try:
        item_id=request.form.get("item_id")
        quantity=request.form.get("quantity")
        item= Item.query.filter_by(item_id=item_id).first()
        
        if item_id and quantity and request.method=='POST':
            DictItems={item_id:{'name':item.item_name,'price':item.item_price,'quantity':quantity,'image':item.item_image}}
            if 'Laundrywain' in session:
                print(session['Laundrywain'])
                
                if item_id in session['Laundrywain']:
                    print("This item is already in wain")
                else:
                    session['Laundrywain'] = MagerDicts(session['Laundrywain'],DictItems)
                    return redirect(request.referrer)
            else:
                session['Laundrywain'] = DictItems
                return redirect(request.referrer) 
    except Exception as e:
        print(e)
    finally:
        return redirect(request.referrer)


@app.route("/delete_item/<int:id>/")
def delete_item(id):
    if 'Laundrywain' not in session and len(session['Laundrywain']) <= 0:
        return redirect("/cleanappitempage/")
    try:
        session.modified= True
        for key,item in session['Laundrywain'].items():
            if int(key)==id:
                session['Laundrywain'].pop(key,None)
                return redirect("/wain/")
    except Exception as e:
        print(e)
        return redirect("/wain/")


@app.route("/upgradeaccount/", methods=['POST', 'GET'])
@login_required
def upgrade_account():
    return render_template("user/upgradeaccount.html", title="Upgrade Account")


@app.route("/changedp/", methods=['POST', 'GET'])
@login_required
def changedp():
    id=session.get("useronline")
    dpform=DpForm()
    if request.method=='GET':
        return render_template("user/changedp.html",dpform=dpform)
    else:
        if dpform.validate_on_submit():
            fileobj=request.files["dp"]
            actual_name=fileobj.filename
            #method 1 Generating a random name but pickicing the file extension from the original uploaded name
            ext=actual_name[-4:]
            #method2
            name,ext=os.path.splitext(actual_name) #spliting file into 2 parts on the extension, picked the extension, I don't need the name part ["ade", ".jpg"]
            
            #end of method 2

            newname=str(int(random.random()*1000000)) +ext

            fileobj.save("cleanapp/static/client_uploads/"+newname)
            # save it to his profile on the db
            user= db.session.query(User).get(id)
            user.user_pix=newname
            db.session.commit()
            flash("Your profile picture has been updated")
            return redirect("/profilepage/")
        else:
            return render_template("user/changedp.html",dpform=dpform)




@app.route("/profile/", methods=['POST', 'GET'])
@login_required
def profile():
        id=session.get('useronline')
        users=get_user_by_id(id)
       
        localgovernment= db.session.query(Localgovernment).all()
        state= db.session.query(State).all()
        
        #retrieving the id from session
        if request.method=='GET':
            return render_template("user/profile.html", users=users, localgovernment=localgovernment, state=state)

        else:
            user_fname=request.form.get('user_fname')
            user_lname=request.form.get('user_lname')
            user_phone=request.form.get('user_phone')
            user_lg=request.form.get('user_lg')
            user_state=request.form.get('user_state')
        

            #updating using orm
        if state:
            user=User.query.get(id)
            user.user_fname=user_fname
            user.user_lname=user_lname
            user.user_phone=user_phone
            user.user_lg=user_lg
            user.user_state=user_state
            db.session.commit()
            flash("profile updated succesfully", category="success")
        else:
            flash("Please select category", category="error")
        return redirect("/profilepage/")


    
@app.route("/profilepage/")
@login_required
def profilepage():
    id=session.get('useronline') #retrieving the id from session
    if id != None:
        user = get_user_by_id(id)
        
        return render_template("user/profilepage.html", user=user)
    else:
        flash("You must be logged in to view this page", category="error")
        return redirect("/login/")

@app.route("/login/", methods=['POST', 'GET'])
def login():
    if request.method=='GET':
        return render_template("user/login.html")
    else:
        #retrieve the form data
        user_email = request.form.get('user_email')
        user_password = request.form.get('user_password')
        if user_email == '' or user_password =='':
            flash('Both fields must be supplied',category='error')
            return redirect("/login/")
        else:
            user=db.session.query(User).filter(User.user_email==user_email).first() #to know the stored hash if email is not unique I'm using .first()
            if user != None:
                stored_hash=user.user_password #hashedpassword from datatbase
                chk= check_password_hash(stored_hash,user_password) #sotred and the pwd from the database
                if chk == True: # if login was succesul
                    session['useronline']= user.user_id
                    return redirect('/profilepage/')
                else:
                    flash('Invalid Password', 'error')
            else:
                flash('Invalid Username', 'error')
            return redirect("/login/")

@app.route("/check/username/", methods=['POST', 'GET'])
def check_username():
        email= request.args.get('username')
        data=db.session.query(User).filter(User.user_email==email).first()
        if data:
            return "<span style='color:red;'>This email already exist</span>"
        else:
            return "<span style='color:green;'>You can sign up with this email</span>"

@app.route("/signup/",methods=['POST','GET'])
def signup():
    
    if request.method=='GET':
        localgovernment = Localgovernment.query.all()
        state = State.query.all()
        return render_template("user/signup.html", localgovernment=localgovernment, state=state)
    else:
        #retrieving the form data and saving in variables respectively
        user_fname=request.form.get('user_fname')
        user_lname=request.form.get('user_lname')
        user_email=request.form.get('user_email')
        user_password=request.form.get('user_password')
        user_username=request.form.get('user_username')
        user_lg=request.form.get('user_lg')
        user_gender=request.form.get('user_gender')
        user_phone=request.form.get('user_phone')
        user_address=request.form.get('user_address')
        user_pix=request.form.get('user_pix')
        hashed= generate_password_hash(user_password)
        user= User(user_fname=user_fname,user_lname=user_lname,user_email=user_email,user_password=hashed,user_username=user_username,user_lg=user_lg,user_gender=user_gender,user_phone=user_phone,user_address=user_address, user_pix=user_pix)
        db.session.add(user)
        db.session.commit()
        userid=user.user_id
        session['useronline']=userid #saved details in session variable
        return redirect("/profilepage/") #displaying the retrieved id by virtue of linking to profilepage/Dashboard
    
@app.route("/pricelist/", methods=['POST', 'GET'])
def pricelist():
    return render_template("user/pricelist.html", title="Our Pricelist")



@app.route("/cleanappitempage/", methods=['POST', 'GET'])
def cleanappitempage():
    items= db.session.query(Item).all()
    return render_template("user/item.html", items=items,  title="Items")

@app.route("/services/", methods=['POST', 'GET'])
def services():
    services= db.session.query(Service).all()
    return render_template("user/services.html", services=services)

@app.route("/", methods=['POST', 'GET'])
def home():
    return render_template("user/index.html" , title='Welcome to Our Home Page' , page='home')



    



def get_dispatcher_by_id(id):
    dispatcher_deets =db.session.query(Dispatcher).get(id)
    return dispatcher_deets

#decorator function
def login_required(f):
    @wraps(f)
    def check_login(*args,**kwargs):
        if session.get('dispatcheronline') != None:
           return f(*args, **kwargs)
        else:
            flash("You must be logged in to view this page", category="error")
            return redirect("/dispatcherlogin/")
    return check_login

@app.route("/changedpdispatcher/", methods=['POST', 'GET'])
@login_required
def changedpdispatcher():
    id=session.get("dispatcheronline")
    dpform=DpForm()
    if request.method=='GET':
        return render_template("user/changedpdispatcher.html",dpform=dpform)
    else:
        if dpform.validate_on_submit():
            fileobj=request.files["dp"]
            actual_name=fileobj.filename
            #method 1 Generating a random name but pickicing the file extension from the original uploaded name
            ext=actual_name[-4:]
            #method2
            name,ext=os.path.splitext(actual_name) #spliting file into 2 parts on the extension, picked the extension, I don't need the name part ["ade", ".jpg"]
            
            #end of method 2

            newname=str(int(random.random()*1000000)) +ext

            fileobj.save("cleanapp/static/dispatcher_uploads/"+newname)
            # save it to his profile on the db
            dispatcher= db.session.query(Dispatcher).get(id)
            dispatcher.dispatcher_pix=newname
            db.session.commit()
            flash("Your profile picture has been updated")
            return redirect("/dispatcherprofilepage/")
        else:
            return render_template("user/changedpdispatcher.html",dpform=dpform)


@app.route("/dispatcherthankyou/", methods=['POST', 'GET'])
def dispatcher_thanks():
    return render_template("user/dispatcherthankyou.html", title="THANK YOU ")


@app.route("/dispatchersignup/",methods=['POST','GET'])
def dispactcher_signup():
    if request.method=='GET':
        localgovernment = Localgovernment.query.all()
        state = State.query.all()
        return render_template("user/dispatchersignup.html", localgovernment=localgovernment, state=state)
    else:
        #retrieving the form data and saving in variables respectively
        dispatcher_businessname=request.form.get('dispatcher_businessname')
        dispatcher_email = request.form.get('dispatcher_email')
        dispatcher_username = request.form.get('dispatcher_username')
        dispatcher_password = request.form.get('dispatcher_password')
        dispatcher_phone = request.form.get('dispatcher_phone')
        dispatcher_officeaddress=request.form.get('dispatcher_officeaddress')
        dispatcher_businessregdate=request.form.get('dispatcher_businessregdate')
        dispatcher_certofreg=request.form.get('dispatcher_certofreg')
        dispatcher_pix=request.form.get('dispatcher_pix')
        dispatcher_idcard=request.form.get('dispatcher_idcard')
        dispatcher_bankname=request.form.get('dispatcher_bankname')
        dispatcher_accountno=request.form.get('dispatcher_accountno')
        dispatcher_platenumber=request.form.get('dispatcher_platenumber')
        dispatcher_lg=request.form.get('dispatcher_lg')
        dispatcher_state=request.form.get('dispatcher_state')
        hashed= generate_password_hash(dispatcher_password)
        dispatcher= Dispatcher(dispatcher_businessname=dispatcher_businessname,dispatcher_email=dispatcher_email,dispatcher_phone=dispatcher_phone,dispatcher_username=dispatcher_username,dispatcher_password=hashed ,dispatcher_officeaddress=dispatcher_officeaddress,dispatcher_businessregdate=dispatcher_businessregdate,dispatcher_certofreg=dispatcher_certofreg,dispatcher_pix=dispatcher_pix,dispatcher_idcard=dispatcher_idcard,dispatcher_bankname=dispatcher_bankname,dispatcher_accountno=dispatcher_accountno,dispatcher_platenumber=dispatcher_platenumber,dispatcher_lg=dispatcher_lg,dispatcher_state=dispatcher_state)
        db.session.add(dispatcher)
        db.session.commit()
        dispatcherid=dispatcher.dispatcher_id
        session['dispatcheronline']=dispatcherid #saved details in session variable
        return redirect("/dispatcherprofilepage/") #displaying the retrieved id by virtue of linking to profilepage/Dashboard



@app.route('/dispatcher/assigned/history/')
def dispatcher_assigned_requests():
    dispatcher_id = session.get('dispatcheronline')  # retrieving the dispatcher_id from session
    if dispatcher_id is None:
        return redirect(url_for('dispatcher_login')) 
    dispatcher = Dispatcher.query.get_or_404(dispatcher_id)
    assigned_requests = Request.query.filter_by(dispatcher_id=dispatcher_id).all()
    return render_template('user/dispatcherrequesthistory.html', dispatcher=dispatcher, assigned_requests=assigned_requests)

@app.route('/dispatcher/markpickedup/<int:request_id>')
def mark_picked_up(request_id):
    request = Request.query.get_or_404(request_id)
    if request.pickedup_status == 'accepted':
        request.pickedup_status = 'pickedup'
        db.session.commit()
        flash('Request marked as picked up successfully.', 'success')
    return redirect(url_for('dispatcher_assigned_requests', dispatcher_id=session.get('useronline')))


@app.route('/dispatcher/markdelivered/<int:request_id>')
def mark_delivered(request_id):
    request = Request.query.get_or_404(request_id)
    if request.pickedup_status == 'pickedup' and request.delivered_status == 'pending':
        request.delivered_status = 'delivered'
        db.session.commit()
        flash('Request marked as delivered successfully.', 'success')
    return redirect(url_for('dispatcher_assigned_requests', dispatcher_id=session.get('useronline')))

@app.route("/dispatcherlogin/", methods=['POST', 'GET'])
def dispatcher_login():
    if request.method=='GET':
        return render_template("user/dispatcherloginform.html")
    else:
        #retrieving the form data
        dispatcher_email = request.form.get('dispatcher_email')
        dispatcher_password = request.form.get('dispatcher_password')
        if dispatcher_email == '' or dispatcher_password =='':
            flash('Both fields must be supplied',category='error')
            return redirect("/dispatcherlogin/")
        else:
            dispatcher=db.session.query(Dispatcher).filter(Dispatcher.dispatcher_email==dispatcher_email).first() #to know the stored hash if email is not unique we use .first()
            if dispatcher != None:
                stored_hash=dispatcher.dispatcher_password #hashedpassword from datatbase
                chk= check_password_hash(stored_hash,dispatcher_password) #stored password and the hashed from the database
                if chk: #login was succesul
                    flash("Logged in successfully", category='success')
                    session['dispatcheronline']= dispatcher.dispatcher_id
                    return redirect('/dispatcherprofilepage/')
                else:
                    flash('Invalid Password', category='error')
            else:
                flash('Invalid Username', category='error')
            return redirect("/dispatcherlogin/")


@app.route("/dispatcherprofile/", methods=['POST', 'GET'])
@login_required
def dispatcher_profile():
        id=session.get('dispatcheronline')
        dispatchers=get_dispatcher_by_id(id)
        localgovernment= db.session.query(Localgovernment).all()
        state= db.session.query(State).all()
        #retrieving the id from session
        if request.method=='GET':
            return render_template("user/dispatcherprofile.html", dispatchers=dispatchers, localgovernment=localgovernment,state=state)

        else:
            dispatcher_businessname=request.form.get('dispatcher_businessname')
            dispatcher_address=request.form.get('dispatcher_address')
            dispatcher_state=request.form.get('dispatcher_lname')
            dispatcher_phone=request.form.get('dispatcher_phone')
            dispatcher_lg=request.form.get('dispatcher_lg')

            #updating using orm
        if state:
            dispatcher=Dispatcher.query.get(id)
            dispatcher.dispatcher_businessname=dispatcher_businessname
            dispatcher.dispatcher_state=dispatcher_state
            dispatcher.dispatcher_phone=dispatcher_phone
            dispatcher.dispatcher_address=dispatcher_address
            dispatcher.dispatcher_lg=dispatcher_lg
            db.session.commit()
            flash("profile updated succesfully", category="success")
        else:
            flash("Please select category", category="error")
        return redirect("/dispatcherprofilepage/")


@app.route("/dispatcherprofilepage/")
@login_required
def dispatcher_profilepage():
    id=session.get('dispatcheronline') #retrieving the id from session
    if id != None:
        dispatchers= get_dispatcher_by_id(id)
        return render_template("user/dispatcherprofilepage.html",dispatchers=dispatchers)
    else:
        flash("You must be logged in to view this page", category="error")
        return redirect("/dispatcherlogin/")


@app.route("/dispatcherlogout/")
def dispatcher_logout():
    if session.get('dispatcheronline') !=None:
        session.pop('dispatcheronline')
        flash("You have logged out succesfully", category="success")
    return redirect("/dispatcherlogin/")





def get_drycleaner_by_id(id):
    drycleanerdeets =db.session.query(Drycleaner).get(id)
    return drycleanerdeets

#decorator function
def login_required(f):
    @wraps(f)
    def check_login(*args,**kwargs):
        if session.get('drycleaneronline') != None:
           return f(*args, **kwargs)
        else:
            flash("You must be logged in to view this page", category="error")
            return redirect("/drycleanerlogin/")
    return check_login


@app.route("/changedpdrycleaner/", methods=['POST', 'GET'])
@login_required
def changedpdrycleanerr():
    id=session.get("drycleaneronline")
    dpform=DpForm()
    if request.method=='GET':
        return render_template("user/changedpdrycleaner.html",dpform=dpform)
    else:
        if dpform.validate_on_submit():
            fileobj=request.files["dp"]
            actual_name=fileobj.filename
            #method 1 Generating a random name but pickicing the file extension from the original uploaded name
            ext=actual_name[-4:]
            #method2
            name,ext=os.path.splitext(actual_name) #spliting file into 2 parts on the extension, picked the extension, I don't need the name part ["ade", ".jpg"]
            
            #end of method 2

            newname=str(int(random.random()*1000000)) +ext

            fileobj.save("cleanapp/static/drycleaner_uploads/"+newname)
            # save it to his profile on the db
            drycleaner= db.session.query(Drycleaner).get(id)
            drycleaner.drycleaner_pix=newname
            db.session.commit()
            flash("Your profile picture has been updated")
            return redirect("/drycleanerprofilepage/")
        else:
            return render_template("user/changedpdrycleaner.html",dpform=dpform)


@app.route("/drycleanerthankyou/", methods=['POST', 'GET'])
def drycleaner_thanks():
    return render_template("user/drycleanerthankyou.html", title="THANK YOU")

@app.route("/drycleanersignup/",methods=['POST','GET'])
def drycleaner_signup():
    id=session.get("drycleaneronline")
    drycleaner = get_user_by_id(id)
    if request.method=='GET':
        localgovernment = Localgovernment.query.all()
        state = State.query.all()
        return render_template("user/drycleanersignup.html", localgovernment=localgovernment, state=state)
    else:
        #retrieving the form data and saving in variables respectively
        
        drycleaner_businessname=request.form.get('drycleaner_businessname')
        drycleaner_email = request.form.get('drycleaner_email')
        drycleaner_username = request.form.get('drycleaner_username')
        drycleaner_password = request.form.get('drycleaner_password')
        drycleaner_phone = request.form.get('drycleaner_phone')
        drycleaner_officeaddress=request.form.get('drycleaner_officeaddress')
        drycleaner_businessregdate=request.form.get('drycleaner_businessregdate')
        drycleaner_certofreg=request.form.get('drycleaner_certofreg')
        drycleaner_bankname=request.form.get('drycleaner_bankname')
        drycleaner_accountno=request.form.get('drycleaner_accountno')
        drycleaner_lg=request.form.get('drycleaner_lg')
        drycleaner_state=request.form.get('drycleaner_state')
        drycleaner_username = request.form.get('drycleaner_username')
        drycleaner_pix=request.form.get('drycleaner_pix')
        hashed= generate_password_hash(drycleaner_password)
        drycleaner=Drycleaner(drycleaner_businessname=drycleaner_businessname,drycleaner_email=drycleaner_email,drycleaner_username=drycleaner_username,drycleaner_password=hashed, drycleaner_phone=drycleaner_phone, drycleaner_officeaddress=drycleaner_officeaddress,drycleaner_businessregdate=drycleaner_businessregdate,drycleaner_certofreg=drycleaner_certofreg,drycleaner_bankname=drycleaner_bankname,drycleaner_accountno=drycleaner_accountno,drycleaner_lg=drycleaner_lg,drycleaner_state=drycleaner_state,drycleaner_pix=drycleaner_pix)
        db.session.add(drycleaner)
        db.session.commit()
        drycleanerid=drycleaner.drycleaner_id
        session['drycleaneronline']=drycleanerid #saved details in session variable
        return redirect("/drycleanerprofilepage/") #displaying the retrieved id by virtue of linking to profilepage/Dashboard

@app.route('/drycleaner/assigned/history/')
def drycleaner_assigned_requests():
    drycleaner_id = session.get('drycleaneronline')  # retrieving the dispatcher_id from session
    if drycleaner_id is None:
        # Handling a scenario or case where user is not logged in or session is expired
        return redirect(url_for('drycleaner_login'))  # Redirecting to login page
    drycleaner = Dispatcher.query.get_or_404(drycleaner_id)
    assigned_requests = Request.query.filter_by(drycleaner_id=drycleaner_id).all()
    return render_template('user/drycleanerrequesthistory.html', drycleaner=drycleaner, assigned_requests=assigned_requests)

@app.route('/drycleaner/markpickedup/<int:request_id>')
def mark_picked_up_drycleaner(request_id):
    request = Request.query.get_or_404(request_id)
    if request.pickedup_status == 'accepted':
        request.pickedup_status = 'pickedup'
        db.session.commit()
        flash('Request marked as picked up successfully.', 'success')
    return redirect(url_for('drycleaner_assigned_requests', drycleaner_id=session.get('useronline')))

@app.route('/drycleaner/markdelivered/<int:request_id>')
def mark_delivered_drycleaner(request_id):
    request = Request.query.get_or_404(request_id)
    if request.pickedup_status == 'pickedup' and request.delivered_status == 'pending':
        request.delivered_status = 'delivered'
        db.session.commit()
        flash('Request marked as delivered successfully.', 'success')
    return redirect(url_for('drycleaner_assigned_requests', drycleaner_id=session.get('useronline')))


@app.route("/drycleanerlogout/")
def drycleaner_logout():
    if session.get('drycleaneronline') !=None:
        session.pop('drycleaneronline')
        flash("You have logged out succesfully", category="success")
    return redirect("/drycleanerlogin/")


@app.route("/drycleanerlogin/", methods=['POST', 'GET'])
def drycleaner_login():
    if request.method=='GET':
        return render_template("user/drycleanerloginform.html")
    else:
        #retrieving the form data
        drycleaner_email = request.form.get('drycleaner_email')
        drycleaner_password = request.form.get('drycleaner_password')
        if drycleaner_email == '' or drycleaner_password =='':
            flash('Both fields must be supplied',category='error')
            return redirect("/drycleanerlogin/")
        else:
            drycleaner=db.session.query(Drycleaner).filter(Drycleaner.drycleaner_email==drycleaner_email).first() #to know the stored hash if email is not unique we use .first()
            if drycleaner != None:
                stored_hash=drycleaner.drycleaner_password #hashedpassword from datatbase
                chk= check_password_hash(stored_hash,drycleaner_password) #stored and the pwd from the database
                if chk == True: #login was succesul
                    session['drycleaneronline']= drycleaner.drycleaner_id
                    return redirect('/drycleanerprofilepage/')
                else:
                    flash('Invalid Password', 'error')
            else:
                flash('Invalid Username', 'error')
            return redirect("/drycleanerlogin/")
  
@app.route("/drycleanerprofile/", methods=['POST', 'GET'])
@login_required
def drycleaner_profile():
        id=session.get('drycleaneronline')
        drycleaners=get_drycleaner_by_id(id)
        localgovernment= db.session.query(Localgovernment).all()
        state= db.session.query(State).all()
        
        #retrieving the id from session
        if request.method=='GET':
            return render_template("user/drycleanerprofile.html", drycleaners=drycleaners, localgovernment=localgovernment,state=state)

        else:
            drycleaner_businessname=request.form.get('drycleaner_businessname')
            drycleaner_officeaddress=request.form.get('drycleaner_officeaddress')
            drycleaner_phone=request.form.get('drycleaner_phone')
            drycleaner_state=request.form.get('drycleaner_state')
            drycleaner_lg=request.form.get('drycleaner_lg')

            #updating using orm
        if state:
            drycleaner=Drycleaner.query.get(id)
            drycleaner.drycleaner_businessname=drycleaner_businessname
            drycleaner.drycleaner_state=drycleaner_state
            drycleaner.drycleaner_phone=drycleaner_phone
            drycleaner.drycleaner_officeaddress=drycleaner_officeaddress
            drycleaner.drycleaner_lg=drycleaner_lg
            db.session.commit()
            flash("profile updated succesfully", category="success")
        else:
            flash("Please select category", category="error")
        return redirect("/drycleanerprofilepage/")

@app.route("/drycleanerprofilepage/")
@login_required
def drycleaner_profilepage():
    id=session.get('drycleaneronline') #retrieving the id from session
    if id != None:
        drycleaners = get_drycleaner_by_id(id)
        return render_template("user/drycleanerprofilepage.html",drycleaners=drycleaners)
    else:
        flash("You must be logged in to view this page", category="error")
        return redirect("/drycleanerlogin/")
    







