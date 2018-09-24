import json
from apis import airtable

#	features = []
#	
#	def add_feature(record):
#		
#	#	print(record['id'])
#	
#		# Extracting AirTable data
#		fields = record['fields']
#		name = fields.get('Restaurant')
#		longitude = fields.get('Longitude')
#		latitude = fields.get('Latitude')
#		status = fields.get('Statut')
#		ta_reviews = fields.get('[TA] Reviews')
#		ta_rating = fields.get('[TA] Rating')
#		ta_url = fields.get('[TA] URL')
#		address = fields.get('Adresse')
#		notes = fields.get('Notes')
#		go = fields.get('Today\'s Trip')
#	
#		if ta_rating in ['4.0', '4.5', '5.0'] :
#			features.append({
#				'type': 'Feature',
#				'geometry': {
#					'type': 'Point',
#					'coordinates': [longitude, latitude],
#				},
#				'properties': {
#					'name': name,
#					'address': address,
#					'status': status,
#					'notes': notes,
#					'ta_reviews': ta_reviews,
#					'ta_rating': ta_rating,
#					'ta_url': ta_url,
#					'go': go,
#				}
#			})
#	
#	airtable.process_records(
#		table='Restaurants',
#		params={
#		#	"fields": ["Restaurant", "Status", "Longitude", "Latitude" "[TA] ID", "[TA] Reviews", "[TA] Rating", ],
#			"filterByFormula": "{Today's Trip}",
#		#	"pageSize": 100,
#			},
#		operation=add_feature,
#		)
#	
#	filename = 'features.js'
#	with open(filename, 'w', encoding='utf-8') as file:
#		file.write("window.features = ")
#	with open(filename, 'a', encoding='utf-8') as file:
#		json.dump(features, file, ensure_ascii=False, indent = 4)
#	
###

filename = 'features.json'

#	with open(filename, 'w', encoding='utf-8') as file:
#		json.dump(features, file, ensure_ascii=False, indent = 4)

from mapbox import Uploader
from settings.secret import MAPBOX

uploader = Uploader(access_token=MAPBOX['SECRET_KEY'])
with open(filename, 'rb') as file:
	upload_response = uploader.upload(file, 'test-kadoresto')
	print(upload_response.json())

print('Uploaded data to mapbox.')