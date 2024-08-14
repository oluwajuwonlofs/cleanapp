from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# from sqlalchemy import create_engine, Column, Boolean, Float, Decimal, LargeBinary 


db = SQLAlchemy()

# creating a table in database for assigning roles incase if user can has multiple roles: User ID, RoleId

# class Userrole(db.Model):
#     __tablename__='userroles'
    # user_id= db.Column(db.Integer, db.ForeignKey('users.user_id'))
    # dispatcher_id= db.Column(db.Integer, db.ForeignKey('dispatchers.dispatcher_id'))
    # drycleaner_id= db.Column(db.Integer, db.ForeignKey('drycleaners.drycleaner_id'))
    # role_id= db.Column(db.Integer, db.ForeignKey('roles.roles_id'))

    # user= db.relationship("User", back_populates="userrole")
    # dispatcher= db.relationship("Dispatcher", back_populates="userrole")
    # drycleaner= db.relationship("Drycleaner", back_populates="userrole")
    
    # role= db.relationship("Role", back_populates="userrole")


class Role(db.Model): 
    __tablename__='roles'
    role_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    role_name = db.Column(db.String(100))




class Request(db.Model):
    __tablename__='requests'
    request_id = db.Column(db.Integer, primary_key=True)
    request_createddate= db.Column(db.DateTime(), nullable=False )
    request_processeddate= db.Column(db.DateTime(), nullable=True)
    # request_ref=db.Column(db.String(200),nullable=True)

    pickedup_status = db.Column(db.Enum('pending', 'accepted', 'pickedup', 'delivered'), default='pending') # status before pick up
    delivered_status = db.Column(db.Enum('pending', 'pickedup', 'delivered'), default='pending ') #status after pick up by dispatcher
  

    client_id  =  db.Column(db.Integer, db.ForeignKey('users.user_id'))
    user=db.relationship("User", back_populates="request")

    dispatcher_id = db.Column(db.Integer, db.ForeignKey('dispatchers.dispatcher_id'),nullable=True)
    dispatcher=db.relationship("Dispatcher", back_populates="request")

    drycleaner_id = db.Column(db.Integer, db.ForeignKey('drycleaners.drycleaner_id'),nullable=True)
    drycleaner=db.relationship("Drycleaner", back_populates="request")


class State(db.Model):
    __tablename__='states'
    state_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    state_name = db.Column(db.String(50),nullable=False)

    user= db.relationship("User", back_populates="state")
    dispatcher= db.relationship("Dispatcher", back_populates="state")
    drycleaner= db.relationship("Drycleaner", back_populates="state")

class Localgovernment(db.Model):
    __tablename__='localgovernments'
    lg_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    lg_name = db.Column(db.String(100),nullable=False)
    user = db.relationship("User", back_populates="localgovernment")
    dispatcher= db.relationship("Dispatcher", back_populates="localgovernment")
    drycleaner= db.relationship("Drycleaner", back_populates="localgovernment")

class Wainitem(db.Model):
    __tablename__='wainitems'
    wainitem_id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    item_id = db.Column(db.Integer, db.ForeignKey('items.item_id'))
    item = db.relationship("Item", back_populates="wainitem")

   

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    user = db.relationship("User", back_populates="wainitem")

    # wainitem = db.relationship("Wainitem", back_populates="user")

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_fname = db.Column(db.String(100), nullable=False)
    user_lname = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(100), nullable=False, unique=True)
    user_username = db.Column(db.String(40), nullable=False)
    user_password = db.Column(db.String(255), nullable=False)
    user_dob = db.Column(db.DateTime(), nullable=True)
    user_phone = db.Column(db.String(15), nullable=False)
    user_address = db.Column(db.String(100))
    user_pix = db.Column(db.String(120), nullable=True)
    user_gender = db.Column(db.String(10), nullable=True)
    user_regdate = db.Column(db.DateTime, default=datetime.now)
    user_lg = db.Column(db.Integer, db.ForeignKey('localgovernments.lg_id'))
    localgovernment = db.relationship("Localgovernment", back_populates="user")
    user_state = db.Column(db.Integer, db.ForeignKey('states.state_id'))
    state= db.relationship("State", back_populates="user")

    payment = db.relationship("Payment", back_populates="user")

    request = db.relationship("Request", back_populates="user")

    wainitem = db.relationship("Wainitem", back_populates="user")
  
    # user_drycleaner=db.Column(db.Integer, db.ForeignKey('drycleaners.drycleaner_id'))
    # drycleaner=db.relationship("Drycleaner", back_populates="user")

    # dispatcher= db.relationship("Dispatcher", back_populates="user")
    # drycleaner= db.relationship("Drycleaner", back_populates="user")


    # drycleaner = db.relationship("Drycleaner", back_populates="user")
    # dispatcher = db.relationship("Dispatcher", back_populates="user")








   






class Payment(db.Model):
    __tablename__='payments'
    payment_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    payment_amount =  db.Column(db.Float,nullable=False)
    
    payment_userid = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    user = db.relationship("User", back_populates="payment")
    
    payment_date= db.Column(db.DateTime(), default=datetime.now)
    payment_status = db.Column(db.Enum('pending', 'paid', 'failed'), nullable=False, default='pending')
    payment_payer=db.Column(db.String(200),nullable=True)

    payment_email=db.Column(db.String(120),nullable=True)

    payment_ref=db.Column(db.String(200),nullable=True)    
    payment_paygate=db.Column(db.String(200),nullable=True)
    payment_dateupdated=db.Column(db.DateTime())
    
    
   

   


   


  





   

class Item(db.Model):
    __tablename__='items'
    item_id= db.Column(db.Integer, autoincrement=True,primary_key=True)
    item_name = db.Column(db.String(200), nullable=False)
    item_image = db.Column(db.String(255), nullable=False)
    item_description = db.Column(db.String(255), nullable=False)
    item_price = db.Column(db.Float,nullable=False)
    item_status=db.Column(db.Enum('1','0'),nullable=True, server_default=("0"))

    item_clothingtype=  db.Column(db.Integer, db.ForeignKey('clothingtypes.clothingtype_id'))
    clothingtype=db.relationship("Clothingtype", back_populates="item")

    wainitem = db.relationship("Wainitem", back_populates="item")

class Clothingtype(db.Model):
    __tablename__='clothingtypes'
    clothingtype_id= db.Column(db.Integer, autoincrement=True,primary_key=True)
    clothingtype_name = db.Column(db.String(200), nullable=False)
    
    item=db.relationship("Item", back_populates="clothingtype")


class Service(db.Model):
    __tablename__='services'
    serv_id= db.Column(db.Integer, autoincrement=True,primary_key=True)
    serv_name = db.Column(db.String(200), nullable=False)
    serv_image = db.Column(db.String(255), nullable=False)
    serv_description = db.Column(db.String(255), nullable=False)
    serv_price = db.Column(db.Float,nullable=False)
    serv_status=db.Column(db.Enum('1','0'),nullable=False, server_default=("0"))

    # item=db.relationship("Item", back_populates="clothingtype")

    # serv_quantity= db.Column(db.String(45))
  
    
    
class Dispatcher(db.Model):
    __tablename__='dispatchers'
    dispatcher_id= db.Column(db.Integer, autoincrement=True,primary_key=True)
    dispatcher_email = db.Column(db.String(100), nullable=False, unique=True)
    dispatcher_username = db.Column(db.String(40), nullable=False)
    dispatcher_password = db.Column(db.String(255), nullable=False)
    dispatcher_phone = db.Column(db.String(15), nullable=False)
    dispatcher_pix = db.Column(db.String(120), nullable=True)
   
    dispatcher_businessname = db.Column(db.String(80), nullable=False)
    dispatcher_officeaddress = db.Column(db.String(200), nullable=False)
    dispatcher_businessregdate= db.Column(db.Date(), nullable=True)
    dispatcher_certofreg= db.Column(db.String(100), nullable=True)
    dispatcher_idcard= db.Column(db.Integer, nullable=True)
    dispatcher_bankname= db.Column(db.String(100), nullable=True)
    dispatcher_accountno= db.Column(db.String(100), nullable=True)
    dispatcher_price= db.Column(db.String(80), nullable=True)
   
    dispatcher_status = db.Column(db.Enum('pending', 'success', 'failed'), nullable=False, default='pending')
    dispatcher_platenumber= db.Column(db.String(15), nullable=True)

    dispatcher_lg = db.Column(db.Integer, db.ForeignKey('localgovernments.lg_id'))
    localgovernment= db.relationship("Localgovernment", back_populates="dispatcher")

    dispatcher_state=db.Column(db.Integer, db.ForeignKey('states.state_id'))
    state= db.relationship("State", back_populates="dispatcher")
    

    request=db.relationship("Request", back_populates="dispatcher")

    # user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    # user = db.relationship("User", back_populates="dispatcher")

   



class Drycleaner(db.Model):
    __tablename__='drycleaners'
    drycleaner_id= db.Column(db.Integer, autoincrement=True,primary_key=True)
    drycleaner_email = db.Column(db.String(100), nullable=False, unique=True)
    drycleaner_username = db.Column(db.String(40), nullable=False)

    drycleaner_password = db.Column(db.String(255), nullable=False)
    
    drycleaner_pix = db.Column(db.String(120), nullable=True)
    drycleaner_phone = db.Column(db.String(15), nullable=False)
    drycleaner_businessname = db.Column(db.String(80), nullable=False)
    drycleaner_officeaddress = db.Column(db.String(200), nullable=False)
    drycleaner_businessregdate= db.Column(db.Date(), nullable=True)
    drycleaner_certofreg= db.Column(db.Integer, nullable=True)
    
   
    drycleaner_bankname= db.Column(db.String(100), nullable=True)
    drycleaner_accountno= db.Column(db.String(100), nullable=True)
    dispatcher_price= db.Column(db.String(80), nullable=True)
    drycleaner_status = db.Column(db.Enum('pending', 'sucecess', 'failed'), nullable=False, default='pending')
    
    drycleaner_lg = db.Column(db.Integer, db.ForeignKey('localgovernments.lg_id'))
    localgovernment= db.relationship("Localgovernment", back_populates="drycleaner")
    
    drycleaner_state=db.Column(db.Integer, db.ForeignKey('states.state_id'))
    state= db.relationship("State", back_populates="drycleaner")
    
   
    request=db.relationship("Request", back_populates="drycleaner")

    # user=db.relationship("User", back_populates="drycleaner")
    # user_id= db.Column(db.Integer, db.ForeignKey('users.user_id'))
    # user=db.relationship("User", back_populates="drycleaner")
    # user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    # user = db.relationship("User", back_populates="drycleaner")
   


 







  



class Requestdetail(db.Model):
    __tablename__='requestdetails'
    rqstdetail_id= db.Column(db.Integer, autoincrement=True,primary_key=True)
    rqstdetail_qty_of_serv= db.Column(db.String(45))

    # rquestdetail_serv=  db.Column(db.Integer, db.ForeignKey('services.serv_id'))
    # service=db.relationship("Service", back_populates="requestdetail")




class Admin(db.Model):
    __tablename__='administrations'
    admin_id=db.Column(db.Integer, autoincrement=True,primary_key=True)
    admin_username=db.Column(db.String(20),nullable=False)
    admin_pwd=db.Column(db.String(255),nullable=False)
    admin_email= db.Column(db.String(70), nullable=False)
    admin_signupdate= db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    admin_lastlogin= db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    
   











