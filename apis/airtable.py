import json, requests, urllib
from settings.secret import AIRTABLE_DATABASE_URL, AIRTABLE_API_KEY


# CONSTANTS

headers = {
	'authorization': 'Bearer ' + AIRTABLE_API_KEY,
	'content-type': 'application/json'
	} 


# UTILITY FUNCTIONS 

def prepare_data(data):
	# Convert data to airtable-compatible format
	data = {"fields": data}
	return json.dumps(data)

def check_for_offset(response_data):
	if "offset" in response_data :
		offset = response_data['offset']
	else :
		offset = False
	return offset


# MAIN FUNCTIONS

def list_records(table, params=''):
	# Params should be given in a dictionary format
	# Offset is used when there are more than 100 records
	params = urllib.parse.urlencode(params, True)
	url = AIRTABLE_DATABASE_URL + table + "?" + params
#	print(url)
	response = requests.get(url, headers=headers)
	return response

def process_records(table, params='', operation=print):
	# Used to apply a given function to many records
	response = list_records(table, params)
	response_data = response.json()
#	print(response_data)
	offset = check_for_offset(response_data) # if there are multiple pages of records
	while offset :
		for record in response_data['records'] :
			operation(record)
		params['offset'] = offset
		response = list_records(table, params)
		response_data = response.json()
		offset = check_for_offset(response_data)
	else :
		# if there is only one page of records, or when dealing with last page
		for record in response_data['records'] :
			operation(record)

def update_record(table, record_id, data):
	url = AIRTABLE_DATABASE_URL + table + '/' + record_id
	data = prepare_data(data)
	response = requests.patch(url, headers=headers, data=data)
	return response

#	response = list_records('Restaurants', {"filterByFormula": "{TEST}"})
#	response = update_record('Restaurants', 'recwcWo2WDGQD7VIH', {'TEST': False,})
#	process_records(
#		table='Restaurants',
#		params={"filterByFormula": "{Today's Trip}", "pageSize": "3"},
#		operation=print
#		)