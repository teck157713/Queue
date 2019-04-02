from flask import Flask, jsonify, request, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from io import BytesIO
import os
import base64
import requests
import json
import datetime
import argparse
import logging
from PIL import Image
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
logger = logging.getLogger(__name__)

repo_path = os.path.curdir
app = Flask(__name__)
app.debug = True

#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://teck:password@/smuqueue?host=/cloudsql/smuqueue:asia-southeast1:smuqueue'
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://teck:password@127.0.0.1:5432/smuqueue'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import INFO, TIME_LOG
from localize_image import YOLODetector

def microsoftapi(img):
	#Microsoft Face API
	apikey = "e7290e03190c41148ec555889daf2f64"
	assert apikey
	api_url = "https://southeastasia.api.cognitive.microsoft.com/vision/v2.0/"
	analyse_api = api_url + "analyze"
	image_data = img
	headers = {"Ocp-Apim-Subscription-Key": apikey,
	'Content-Type': 'application/octet-stream'}
	params = {'visualFeatures':'Categories,Description,Color,Objects,Faces'}
	response = requests.post(
		analyse_api, headers=headers, params=params, data=image_data)
	response.raise_for_status()
	analysis = response.json()
	#image_caption = analysis["description"]["captions"][0]["text"].capitalize()
	people = 0
	for i in analysis['objects']:
		if i['object'] == 'person':
			people += 1
	describepeople = []
	for i in analysis['faces']:
		describepeople.append(i['gender'] + ' ' + str(i['age']))
	tags = analysis['description']['tags']
	return[people, describepeople, tags]

def neuralnetwork(imgresult):
	image = Image.open(imgresult)
	yolo_model = YOLODetector(score_threshold=float(0.3),
                              iou_threshold=float(0.45))
	detected_image = yolo_model.detect_image(image)
	return detected_image[1]

@app.route('/main/', methods=['GET'])
def givedefault():
	return jsonify('Welcome to this retarded page.')

@app.route('/newvendor/', methods=['POST'])
def add_vendor():
	Vendor = request.form['Vendor']
	Menu = request.files.get('Menu').read()
	Queue_Image = request.files.get('Queue_Image').read()
	new_vendor = INFO(Vendor=Vendor, Menu=base64.b64encode(Menu), Queue_Image=base64.b64encode(Queue_Image))
	db.session.add(new_vendor)
	db.session.commit()
	res = microsoftapi(Queue_Image)
	res2 = neuralnetwork(request.files.get('Queue_Image'))
	new_log = TIME_LOG(info_id=new_vendor.id, Time=datetime.datetime.now(), Queue_Length=res2, Audience=res[1], Activities_Of_Interest=res[2])
	db.session.add(new_log)
	db.session.commit()
	return jsonify(new_vendor.serialize())

@app.route('/getvendors/', methods=['GET'])
def get_vendors():
	all_vendors = INFO.query.all()
	return jsonify([a.serialize() for a in all_vendors])

@app.route('/getlogs/', methods=['GET'])
def get_logs():
	all_logs = TIME_LOG.query.all()
	return jsonify([l.serialize() for l in all_logs])

@app.route('/getvendor/', methods=['POST'])
def get_vendor():
	Vendor = request.form['Vendor']
	all_vendors = INFO.query.filter(INFO.Vendor==Vendor).all()
	return jsonify([a.serialize() for a in all_vendors])

@app.route('/SMUqueue/<vendor_name>', methods=['DELETE'])
def deleteVendor(vendor_name):
	delvendor = INFO.query.filter(INFO.Vendor==vendor_name).one()
	db.session.delete(delvendor)
	db.session.commit()
	return jsonify(delvendor.serialize())

@app.route('/SMUqueue/<vendor_name>', methods=['PUT'])
def update_name(vendor_name):
	update_vendor_name = request.form['updated_vendor_name']
	updatevendor = INFO.query.filter(INFO.Vendor==vendor_name).first()
	updatevendor.Vendor = update_vendor_name
	db.session.commit()
	return jsonify(updatevendor.serialize())

@app.route('/SMUqueue/<vendor_name>', methods=['PUT'])
def update_menu(vendor_name):
	updated_menu = base64.b64encode(request.files.get('updated_menu').read())
	updatemenu = INFO.query.filter(INFO.Vendor==vendor_name).first()
	updatemenu.Menu = updated_menu
	db.session.commit()
	return jsonify(updatemenu.serialize())

@app.route('/updatequeue/<vendor_name>', methods=['PUT'])
def update_queue(vendor_name):
	newimage = request.files.get('updated_queue').read()
	updated_queue = base64.b64encode(newimage)
	updatequeue = INFO.query.filter(INFO.Vendor==vendor_name).first()
	updatequeue.Queue_Image = updated_queue
	db.session.commit()
	res = microsoftapi(newimage)
	res2 = neuralnetwork(request.files.get('updated_queue'))
	new_log = TIME_LOG(info_id=updatequeue.id, Time=datetime.datetime.now(), Queue_Length=res2, Audience=res[1], Activities_Of_Interest=res[2])
	db.session.add(new_log)
	db.session.commit()
	return jsonify(new_log.serialize())

if __name__ == '__main__':
	#app.run(host='127.0.0.1', port=8080, debug=True)
	app.run(debug=True)



