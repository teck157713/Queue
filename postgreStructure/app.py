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
app.debug = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://teck:password@127.0.0.1:5000/smuqueue'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import INFO, TIME_LOG

@app.route('/newvendor/', methods=['POST'])
def add_vendor():
	Vendor = request.form['Vendor']
	Menu = request.files.get('Menu').read()
	Queue_Image = request.files.get('Queue_Image').read()
	new_vendor = INFO(Vendor=Vendor, Menu=base64.b64encode(Menu), Queue_Image=base64.b64encode(Queue_Image))
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
	
	return jsonify(new_log)

@app.route('/getvendors/', methods=['GET'])
def get_vendors():
	all_vendors = INFO.query.all()
	return jsonify(all_vendors.data)

@app.route('/getlogs/', methods=['GET'])
def get_logs():
	all_logs = TIME_LOG.query.all()
	return jsonify(all_logs.data)

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
	return jsonify(delvendor)

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
	return jsonify(new_log)



if __name__ == '__main__':
	app.run(debug=True)
