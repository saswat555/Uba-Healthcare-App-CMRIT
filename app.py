import py_compile
from flask import Flask, request, redirect , session
from flask_sqlalchemy import SQLAlchemy
from flask.templating import render_template
from flask_migrate import Migrate, migrate
from sqlalchemy import ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.secret_key = 'UBA project'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.config['GOOGLEMAPS_KEY'] = "AIzaSyBswMboZNxjWVLoGKOtgKUDeGVbrJfxJOg"
GoogleMaps(app)

class User(db.Model):
    id = db.Column(db.Integer,autoincrement=True, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(13), nullable=False)
    address = db.Column(db.String(100), nullable=True)
    role = db.Column(db.String(20),nullable=False)
    def __repr__(self):
        return f"userName : {self.username}, address: {self.address}, email:{self.email}, phone:{self.phone}"
class Hospital(db.Model):
    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    name = db.Column(db.String(50),unique = False, nullable = True)
    phone = db.Column(db.String(20),nullable = False)
    email = db.Column(db.String(50),nullable = False)
    latitude = db.Column(db.String(50),nullable = False)
    longitude = db.Column(db.String(50),nullable = False)
    image = db.Column(db.String(50),nullable = True)
    description = db.Column(db.Text(100),nullable=True)
    def __repr__(self):
        return f"id:{self.id},name:{self.name},phone:{self.phone},email:{self.email},latitude:{self.latitude},longitude:{self.longitude},image:{self.image},description:{self.description}"
class Doctor(db.Model):
    id = db.Column(db.Integer,db.ForeignKey(User.id),primary_key=True,nullable=False)
    ClinicOpenTiming = db.Column(db.String(20),nullable=False)
    ClinicCloseTiming = db.Column(db.String(20),nullable=False)
    Speciality = db.Column(db.Text(),nullable=False)
    appointment_price = db.Column(db.String(20),nullable = False)
    hospital = db.Column(db.Integer,ForeignKey(Hospital.id),nullable = False)
    def __repr__(self):
        return f"id : {self.id}, openingTime: {self.ClinicOpenTiming}, closingTime:{self.ClinicCloseTiming}, Speciality:{self.Speciality},appointment_cost:{self.appointment_price}"
class appointment(db.Model):
    id = db.Column(db.Integer,autoincrement = True, primary_key = True)
    doctor_id = db.Column(db.String(20),db.ForeignKey(Doctor.id))
    user_id = db.Column(db.String(20),db.ForeignKey(User.id))
    time = db.Column(db.String(20),nullable = False)
    status = db.Column(db.Boolean(),nullable = False)
    mode = db.Column(db.String(20),nullable = True)
    link = db.Column(db.String(50),nullable = True)
    symptoms = db.Column(db.Text(),nullable = True)
    def __repr__(self):
        return f"doctorid:{self.doctor_id},userid:{self.user_id},time:{self.time},status:{self.status},mode:{self.mode},link:{self.link},symptoms:{self.symptoms}"


@app.route('/')
def index():
    if('username' in session):
       return redirect('home')
    else:
        return render_template('login.html')

@app.route('/home')
def home():
    if('username' in session and session['role']=='User'):
        data = db.session.query(User,appointment,Hospital).filter(appointment.doctor_id == User.id).filter(appointment.doctor_id == Doctor.id).filter(Doctor.hospital == Hospital.id).filter(appointment.user_id==session['id']).all()
        return render_template('user_home.html',data=data)
    elif 'username' in session and session['role']=='Doctor':
        return redirect('/doctorhome')
    elif 'username' in session and session['role']=='Admin':
        return render_template('admin_home.html')   
    else:
        return redirect('/')

@app.route('/signup')
def add_data():
    return render_template('signup.html')

@app.route('/add', methods=["POST"])
def signup():
    username = request.form.get("username")
    password = request.form.get("password")
    email = request.form.get("email")
    address = request.form.get("address")
    phone = request.form.get("phone")
    role = "User"

    if username != '' and password != '' and phone is not None:
        p = User(username=username, password=generate_password_hash(password, method='sha256'), address=address, email=email,phone=phone,role=role)
        try:
            db.session.add(p)
            db.session.commit()
            return redirect('/login')
        except:
            return render_template('signup.html',msg = "There is some error, please try again later")
    else:
        return render_template('signup.html',msg = "Please fill all the fields")
    

@app.route('/login', methods=["GET","POST"])
def login():
    if request.method == "GET":
        if('username' in session):
            return redirect('/')
        else:
            return render_template("login.html")
    else:
        if('username' in session):
            return redirect('/')
        else:
            username = request.form.get("username")
            password = request.form.get("password")
            if username != '' and password != '':
                user = User.query.filter_by(username=username).first()
                if not user or not check_password_hash(user.password, password):
                    return render_template("login.html",msg = "Please fill all the details and try again.")
                else:
                    session['username'] = username
                    session['id'] = user.id
                    session['login'] = True
                    session['role'] = user.role
                    return redirect('/')
            else:
                return render_template('login.html',msg = "Please enter username and password")

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    session['login'] = False
    return redirect('/')

@app.route('/makeappointment',methods=["GET","POST"])
def makeappointment():
    if request.method == "GET":
        data = db.session.query(User,Doctor).filter(Doctor.id == User.id).filter(User.role=='Doctor').all()
        return render_template('make_appointment.html',data=data)
    elif request.method == "POST":
        doctor = request.form.get("doctor")
        date = request.form.get('date')
        symptoms = request.form.get('symptoms')
        mode = request.form.get('mode')
        status = False
        doctorid = User.query.filter_by(username = doctor).first()
        doctorid = doctorid.id
        p = appointment(doctor_id = doctorid,user_id = session['id'],time = date,status = status,mode = mode,symptoms=symptoms)
        db.session.add(p)
        db.session.commit()
        return redirect('/')

@app.route('/updateappointment',methods=['POST'])
def updateappointment():
    doctor_id = request.form.get("doctor_id")
    date = request.form.get("date")
    username = request.form.get("username")
    p = appointment.query.filter_by(user_id = username).filter_by(doctor_id = doctor_id).filter_by(time = date).first()
    p.status = 1
    db.session.commit()
    return redirect('/')

@app.route('/hospital')
def hospital():
    data = db.session.query(Hospital).all()
    return render_template('hospital.html', data=data)

@app.route('/doctorhome',methods=["GET","POST"])
def doctorhome():
    if request.method == 'GET':
        id = session['id']
        data = db.session.query(appointment,User).filter(appointment.user_id == User.id).filter(appointment.doctor_id == id).all()
        return render_template('doctor_home.html', data=data)
        
#Admin Routes

@app.route('/adddoctor',methods = ['GET','POST'])
def adddoctor():
    if request.method == "GET" and session['role'] == 'Admin':
        data = Hospital.query.all()
        data = data
        return render_template('add_doctor.html',data = data)
    elif request.method == "GET" and session['role']!='Admin':
        return "<h1><center>You are not authorised to see this page</center></h1>"
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        address = request.form.get("address")
        phone = request.form.get("phone")
        role = "Doctor"
        Clinicopen = request.form.get('open')
        Clinicclose = request.form.get('close')
        speciality = request.form.get('speciality')
        price = request.form.get('price')
        hospital = request.form.get('hospital')
        if username != '' and password != '' and phone is not None:
            p = User(username=username, password=generate_password_hash(password, method='sha256'), address=address, email=email,phone=phone,role=role)
            db.session.add(p)
            db.session.commit()
            data = User.query.filter_by(username=username).first()
            id = data.id
            x = Doctor(id = id,ClinicOpenTiming = Clinicopen,ClinicCloseTiming = Clinicclose,Speciality = speciality,appointment_price = price,hospital=hospital)
            db.session.add(x)
            db.session.commit()
            return redirect('/')
        else:
            return render_template('add_doctor.html',msg = "Please fill all the fields")

@app.route('/allbooking')
def allbooking():
    try:
        if session['role'] and session['role']=='Admin':
            data = appointment.query.all()
            return render_template('allbooking.html',data=data)
        else:
            return "You are not Allowed to access this page"
    except:
        return redirect('/')
@app.route('/hospitallist')
def hospitallist():
    try:
        if session['role'] and session['role']=='Admin':
            data = Hospital.query.all()
            return render_template('allhos.html',data=data)
        else:
            return "You are not Allowed to access this page"  
    except:
        return redirect('/')
  

@app.route('/allusers')
def allusers():
    try:
        if session['role'] and session['role']=='Admin':
            data = User.query.all()
            return render_template('alluser.html', data = data)
        else:
            return "You are not Allowed to access this page"  
    except:
        return redirect('/')

@app.route('/fullview',methods = ['GET','POST'])
def fullview():
    id = request.form.get('name')
    data = Hospital.query.filter_by(id=id).first() 
    return render_template('try.html', data=data)

@app.route('/allhospital')
def allhospital():
    data = Hospital.query.all()
    return render_template('hospital.html',data=data)

if __name__ == '__main__':
  app.run(debug=True)