from app import db

class INFO(db.Model):
	__tablename__='info'
	id = db.Column(db.Integer, primary_key=True)
	Vendor = db.Column(db.String(80), unique=True, nullable=False)
	Menu = db.Column(db.LargeBinary, nullable=True)
	Queue_Image = db.Column(db.LargeBinary, nullable=True)

	def __init__(self, Vendor, Menu, Queue_Image):
		self.Vendor = Vendor
		self.Menu = Menu
		self.Queue_Image = Queue_Image

	def __repr__(self):
		return '<id {}>'.format(self.id)
    
	def serializeinfo(self):
		return {
            'Vendor': self.Vendor,
			'Menu': self.Menu,
            'Queue_Image': self.Queue_Image
        }

class TIME_LOG(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	Vendor = db.Column(db.String(80), nullable=False)
	Time = db.Column(db.DateTime, nullable=False)
	Queue_Length = db.Column(db.Integer, nullable=True)
	Audience = db.Column(db.String(200), nullable=True)
	Activities_Of_Interest = db.Column(db.String(500), nullable=True)

	def __init__(self, Vendor, Time, Queue_Length, Audience, Activities_Of_Interest):
		self.Vendor = Vendor
		self.Time = Time
		self.Queue_Length = Queue_Length
		self.Audience = Audience
		self.Activities_Of_Interest = Activities_Of_Interest
    
	def serializetimelog(self):
		return {
            'Vendor': self.Vendor,
            'Time': self.Time,
            'Queue_Length': self.Queue_Length,
            'Audience': self.Audience,
            'Activities_Of_Interest': self.Activities_Of_Interest
        }