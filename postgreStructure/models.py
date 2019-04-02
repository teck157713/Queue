from app import db
import datetime

class INFO(db.Model):
	__tablename__='info'
	id = db.Column(db.Integer, primary_key=True)
	Vendor = db.Column(db.String(80), unique=True, nullable=False)
	Menu = db.Column(db.LargeBinary, nullable=True)
	Queue_Image = db.Column(db.LargeBinary, nullable=True)
	timelogs = db.relationship('TIME_LOG', back_populates='info', cascade='all', lazy=True, uselist=True)

	def __init__(self, Vendor, Menu=None, Queue_Image=None, timelogs=None):
		self.Vendor = Vendor
		Menu = [] if Menu is None else Menu
		self.Menu = Menu
		Queue_Image = [] if Queue_Image is None else Queue_Image
		self.Queue_Image = Queue_Image
		timelogs = [] if timelogs is None else timelogs
		self.timelogs = timelogs

	def __repr__(self):
		return '<id {}>'.format(self.id)
    
	def serialize(self):
		return {
			'id' : self.id,
            'Vendor': self.Vendor,
			'Menu': str(self.Menu),
            'Queue_Image': str(self.Queue_Image),
			'timelogs' : [t.serialize() for t in self.timelogs]
        }

class TIME_LOG(db.Model):
	__tablename__= 'timelog'
	__table_args__ = (
		db.UniqueConstraint('info_id', 'Time', name='composite_unique'),
	)
	id = db.Column(db.Integer, primary_key=True)
	Time = db.Column(db.DateTime, default=datetime.datetime.now().date(), onupdate=datetime.datetime.now().date())
	Queue_Length = db.Column(db.Integer, nullable=False)
	Audience = db.Column(db.String(200), nullable=False)
	Activities_Of_Interest = db.Column(db.String(500), nullable=False)
	info_id = db.Column(db.Integer, db.ForeignKey('info.id'), nullable=False)
	info = db.relationship('INFO', back_populates='timelogs')

	def __init__(self, Time, Queue_Length, Audience, Activities_Of_Interest, info_id):
		self.Time = Time
		self.Queue_Length = Queue_Length
		self.Audience = Audience
		self.Activities_Of_Interest = Activities_Of_Interest
		self.info_id = info_id
    
	def serialize(self):
		return {
			'id' : self.id,
            'Time': self.Time,
            'Queue_Length': self.Queue_Length,
            'Audience': self.Audience,
            'Activities_Of_Interest': self.Activities_Of_Interest,
			'info_id' : self.info_id
        }