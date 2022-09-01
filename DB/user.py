
# Models
class User(db.Model):
    # Id : Field which stores unique id for every row in
    # database table.
    # first_name: Used to store the first name if the user
    # last_name: Used to store last name of the user
    # Age: Used to store the age of the user
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(13), nullable=False)
    Address = db.Column(db.String(100), nullable=True)
 
    # repr method represents how one object of this datatable
    # will look like
    def __repr__(self):
        return f"UserName : {self.username}, Address: {self.Address}, Email:{self.email}, Phone:{self.phone}"
 
