import requests
from apis import airtable


def add_pin(record):
	pass


airtable.process_records(
	table='Restaurants',
	params={
		"fields": ["Restaurant", "Last updated", "[TA] ID", "[TA] Reviews", "[TA] Rating", ],
	#	"filterByFormula": "{Today's Trip}",
	#	"pageSize": 100,
		},
	operation=update_record,
	)
