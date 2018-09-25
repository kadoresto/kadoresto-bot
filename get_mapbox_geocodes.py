import json, time
from mapbox import Geocoder
from apis import airtable
from settings.secret import MAPBOX

geocoder = Geocoder(access_token=MAPBOX['PUBLIC_KEY'])

#	PARIS_BOUNDING_BOX = [2.25, 48.814355, 2.419898, 48.816082]

def geocode(address):
	return geocoder.forward(address, lon=2.338814, lat=48.861645, limit=1, languages=['fr-FR', ])

def geocode_restaurant(record):
	
	# Extracting AirTable data
	fields = record['fields']
	name = fields.get('Restaurant', '')
	address = fields.get('Adresse', '')

#	if 'Longitude' in fields and 'Latitude' in fields :
#		print("{} | Already geocoded.".format(name))
	potato = False
	if potato :
		pass
	else :
		# Calling MapBox Geocoding
		response = geocode(address)
		while response.status_code == 429 :
			# Rate limit exceeded, wait 10 seconds and try again
			print('[Rate limit exceeded. Waiting 10 seconds then retrying...]')
			time.sleep(10)
			response = geocode(address)
		response_data = response.json()
		features = response_data.get('features', '')
		if features :
			feature = features[0]
			relevance = round(feature['relevance'], 2)
			coordinates = feature['geometry']['coordinates']
			longitude, latitude = coordinates[0], coordinates[1]
			new_data = {
				"Longitude": longitude,
				"Latitude": latitude,
				"Geocode Relevance": relevance, 
				}
			update_response = airtable.update_record('Restaurants', record['id'], data=new_data)
			if update_response.status_code == 200:
				print("{} | Relevance {} | Lat {}, Long {} | Update successful.".format(name, relevance, longitude, latitude))
			else :
				print("{} | Relevance {} | Lat {}, Long {} | Could not update !".format(name, relevance, longitude, latitude))
		else :
			print("{} | Geocoding failed !".format(name))

airtable.process_records(
	table='Restaurants',
	params={
		"fields": ["Restaurant", "Adresse", "Longitude", "Latitude" ],
#		"filterByFormula": "{Today's Trip}",
#		"pageSize": 2,
		},
	operation=geocode_restaurant,
	)