#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ----------------------------------------------
# Google App Engine Demo
# Playing with Flask in Python
# GET returns number-th position in the container 
# POST appends to the container
# ----------------------------------------------

from flask import Flask, jsonify, request, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from io import BytesIO
import os
import base64
import requests
import json
import datetime
from PIL import Image

app = Flask(__name__)
container = ['Hello World!', 'Google']

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'crud.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)

class INFO(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	Vendor = db.Column(db.String(80), unique=True, nullable=False)
	Menu = db.Column(db.LargeBinary, nullable=True)
	Queue_Image = db.Column(db.LargeBinary, nullable=True)

	def __init__(self, Vendor, Menu, Queue_Image):
		self.Vendor = Vendor
		self.Menu = Menu
		self.Queue_Image = Queue_Image

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

class INFOSchema(ma.Schema):
	class Meta:
		fields = ('Vendor', 'Menu', 'Queue_Image')

class TIME_LOGSchema(ma.Schema):
	class Meta:
		fields = ('Vendor', 'Time', 'Queue_Length', 'Audience', 'Activities_Of_Interest')

info_schema = INFOSchema()
infos_schema = INFOSchema(many=True)

timelog_schema = TIME_LOGSchema()
timelogs_schema = TIME_LOGSchema(many=True)

@app.route('/mainpage/')
def mainpage():
	return jsonify(container)

@app.route('/get/<number>', methods=['GET'])
def get(number):
	if int(number) > len(container):
		return 'That number is greater than the size of the container'
	else:
		return jsonify(container[int(number)])

@app.route('/post/<word>', methods=['POST'])
def post(word):
	container.append(word)
	return jsonify(word)

@app.route('/newvendor/', methods=['POST'])
def add_vendor():
	Vendor = request.form['Vendor']
	Menu = request.files.get('Menu').read()
	Queue_Image = request.files.get('Queue_Image').read()
	new_vendor = INFO(Vendor, base64.b64encode(Menu), base64.b64encode(Queue_Image))
	db.session.add(new_vendor)
	db.session.commit()
	#Microsoft Face API
	apikey = "e7290e03190c41148ec555889daf2f64"
	assert apikey

	api_url = "https://southeastasia.api.cognitive.microsoft.com/vision/v2.0/"

	analyse_api = api_url + "analyze"

	image_data = Queue_Image
	headers = {"Ocp-Apim-Subscription-Key": apikey,
	'Content-Type': 'application/octet-stream'}
	params = {'visualFeatures':'Categories,Description,Color,Objects,Faces'}

	response = requests.post(
		analyse_api, headers=headers, params=params, data=image_data)
	response.raise_for_status()

	analysis = response.json()
	print(analysis)
	image_caption = analysis["description"]["captions"][0]["text"].capitalize()

	people = 0
	for i in analysis['objects']:
		if i['object'] == 'person':
			people += 1
	describepeople = ""
	for i in analysis['faces']:
		describepeople += i['gender'] + " " + str(i['age']) + "\n"

	print("Number of people detected: " + str(people))
	print(describepeople)
	tags = analysis['description']['tags']
	#Microsoft Face API Ends
	new_log = TIME_LOG(Vendor, datetime.datetime.now(), people, describepeople, " ".join(tags))
	db.session.add(new_log)
	db.session.commit()
	
	return timelog_schema.jsonify(new_log)

@app.route('/delete/<number>')
def delete(number):
	if int(number) > len(container):
		return 'That number is greater than the size of the container'
	else:
		container.pop(int(number))
		return 'Success'

@app.route('/getvendors/', methods=['GET'])
def get_vendors():
	all_vendors = INFO.query.all()
	result = infos_schema.dump(all_vendors)
	return jsonify(result.data)

@app.route('/getlogs/', methods=['GET'])
def get_logs():
	all_logs = TIME_LOG.query.all()
	result = timelogs_schema.dump(all_logs)
	return jsonify(result.data)

@app.route('/getvendor/', methods=['POST'])
def get_vendor():
	Vendor = request.form['Vendor']
	all_vendors = INFO.query.filter(INFO.Vendor==Vendor).with_entities(INFO.Vendor,INFO.Menu).all()

	#return infos_schema.jsonify(all_vendors)
	return jsonify(all_vendors.data)

@app.route('/SMUqueue/<vendor_name>', methods=['DELETE'])
def deleteVendor(vendor_name):
	delvendor = INFO.query.filter(INFO.Vendor==vendor_name).one()
	db.session.delete(delvendor)
	db.session.commit()
	deltime = TIME_LOG.query.filter(TIME_LOG.Vendor==vendor_name).all()
	db.session.delete(deltime)
	db.session.commit()
	return info_schema.jsonify(delvendor)

@app.route('/SMUqueue/<vendor_name>', methods=['PUT'])
def update_name(vendor_name):
	update_vendor_name = request.form['updated_vendor_name']
	updatevendor = INFO.query.filter(INFO.Vendor==vendor_name).first()
	updatevendor.Vendor = update_vendor_name
	db.session.commit()
	updatetime = TIME_LOG.query.filter(TIME_LOG.Vendor==vendor_name).all()
	updatetime.Vendor = update_vendor_name
	db.session.commit()
	return jsonify(updatevendor)

@app.route('/SMUqueue/<vendor_name>', methods=['PUT'])
def update_menu(vendor_name):
	updated_menu = base64.b64encode(request.files.get('updated_menu').read())
	updatemenu = INFO.query.filter(INFO.Vendor==vendor_name).first()
	updatemenu.Menu = updated_menu
	db.session.commit()
	return jsonify(updatemenu)

@app.route('/updatequeue/<vendor_name>', methods=['PUT'])
def update_queue(vendor_name):
	newimage = request.files.get('updated_queue').read()
	updated_queue = base64.b64encode(newimage)
	updatequeue = INFO.query.filter(INFO.Vendor==vendor_name).first()
	updatequeue.Queue_Image = updated_queue
	db.session.commit()

	apikey = "e7290e03190c41148ec555889daf2f64"
	assert apikey

	api_url = "https://southeastasia.api.cognitive.microsoft.com/vision/v2.0/"

	analyse_api = api_url + "analyze"

	image_data = newimage
	headers = {"Ocp-Apim-Subscription-Key": apikey,
	'Content-Type': 'application/octet-stream'}
	params = {'visualFeatures':'Categories,Description,Color,Objects,Faces'}

	response = requests.post(
		analyse_api, headers=headers, params=params, data=image_data)
	response.raise_for_status()

	analysis = response.json()
	print(analysis)
	image_caption = analysis["description"]["captions"][0]["text"].capitalize()

	people = 0
	for i in analysis['objects']:
		if i['object'] == 'person':
			people += 1
	describepeople = ""
	for i in analysis['faces']:
		describepeople += i['gender'] + " " + str(i['age']) + "\n"

	print("Number of people detected: " + str(people))
	print(describepeople)
	tags = analysis['description']['tags']
	#Microsoft Face API Ends
	new_log = TIME_LOG(vendor_name, datetime.datetime.now(), people, describepeople, " ".join(tags))
	db.session.add(new_log)
	db.session.commit()
	return timelog_schema.jsonify(new_log)


if __name__ == '__main__':
	app.run(debug=True)

