import json
from apis import airtable

features = []

def add_pin(record):
	
	# Extracting AirTable data
	fields = record['fields']
	tripadvisor_id = fields['[TA] ID']

	geocode(record)
	features.append({
		'type': 'Feature',
		'geometry': {
			'type': 'Point',
			'coordinates': [-77.032, 38.913],
		},
		'properties': {
			'title': 'Mapbox',
			'description': 'Washington, D.C.'
		}
	})

add_pin('potato')

filename = 'features.json'
with open(filename, 'w', encoding='utf-8') as file:
	json.dump(features, file, ensure_ascii=False, indent = 4)
print('Created or updated "{}".'.format(filename))

#	airtable.process_records(
#		table='Restaurants',
#		params={
#			"fields": ["Restaurant", "Last updated", "[TA] ID", "[TA] Reviews", "[TA] Rating", ],
#		#	"filterByFormula": "{Today's Trip}",
#		#	"pageSize": 100,
#			},
#		operation=add_pin,
#		)