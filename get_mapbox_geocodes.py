import json, time
from mapbox import Geocoder
from apis import airtable
from settings.secret import MAPBOX

geocoder = Geocoder(access_token=MAPBOX['PUBLIC_KEY'])

PARIS_BOUNDING_BOX = [2.224268, 48.814355, 2.420423, 48.906108]

def geocode(address):
	return geocoder.forward(address, bbox=PARIS_BOUNDING_BOX, limit=1, languages=['fr-FR', ])

def geocode_restaurant(record):
	
	# Extracting AirTable data
	fields = record['fields']
	name = fields['Restaurant']
	address = fields['Adresse']

	if 'Longitude' in fields and 'Latitude' in fields :
		print("{} | Already geocoded.".format(name))
	else :
		# Calling MapBox Geocoding
		response = geocode(address)
		while response.status_code == 429 :
			# Rate limit exceeded, wait 10 seconds and try again
			print('[Rate limit exceeded. Waiting 10 seconds then retrying...]')
			time.sleep(10)
			response = geocode(address)
		response_data = response.json()
		features = response_data['features']
		if features :
			feature = features[0]
			relevance = round(feature['relevance'], 2)
			coordinates = feature['geometry']['coordinates']
			longitude, latitude = coordinates[0], coordinates[1]
			new_data = {
				"Longitude": longitude,
				"Latitude": latitude,
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
	#	"filterByFormula": "{Today's Trip}",
	#	"pageSize": 100,
		},
	operation=geocode_restaurant,
	)