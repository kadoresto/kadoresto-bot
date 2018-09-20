import requests, json, urllib, traceback
from datetime import datetime, timedelta
from secret import api_key
from bs4 import BeautifulSoup
from scraping_tools import tripadvisor

airtable_table_url = "https://api.airtable.com/v0/appCFLZH7zvAoTdY5/Restaurants"

class Restaurant:

	def __init__(self, tripadvisor_id, name, review_count=0, rating=None):
		self.tripadvisor_id = tripadvisor_id
		self.name = name
#		self.street_address = street_address
		self.review_count = review_count
		self.rating = rating

	def __repr__(self):
		return self.__str__()


def call_airtable(url, request_type="GET", data=None):

	headers = {
		'authorization': 'Bearer ' + api_key,
		'content-type': 'application/json'
		}

	if data :
		# Convert data to airtable-compatible format
		data = {"fields": data}
		data = json.dumps(data)

	if request_type == "GET" :
		response = requests.get(url, headers=headers)

	elif request_type == "PATCH" :
		response = requests.patch(url, headers=headers, data=data)
	return response

def check_for_offset(response_data):
	if "offset" in response_data :
		offset = response_data['offset']
	else :
		offset = False
	return offset

def update_records(records):


	for index, record in enumerate(records, start=1) :

		# Extracting AirTable data
		fields = record['fields']
		tripadvisor_id = fields['[TA] ID']
		restaurant_name = fields['Restaurant']
		previous_review_count = fields['[TA] Reviews']
		previous_rating = fields['[TA] Rating']

		# Check when restaurant was last updated
		recently_updated = False
		if "Last updated" in fields :
			last_updated = datetime.strptime(fields['Last updated'], '%Y-%m-%d')
			time_since_update = datetime.now() - last_updated
			if time_since_update.days < 3 :
				recently_updated = True

		# Creating new restaurant instance
		restaurant = Restaurant(tripadvisor_id=tripadvisor_id, name=restaurant_name)

		# Preparing base message for console
		progress = "{}/{}".format(index, len(response_data['records']))
		base_message = "{} | TA #{} | '{}', ".format(progress, tripadvisor_id, restaurant_name)

		if recently_updated :
			print(base_message + 'was recently updated.')
		else :
#			try :

			# Fetching TripAdvisor data
			page = requests.get('https://www.tripadvisor.fr/Restaurant_Review-g187147-d' + str(tripadvisor_id))
			html = BeautifulSoup(page.content, 'lxml')		
			restaurant.review_count = int(html.find("",  {"href": "#REVIEWS", "class": "more", }).span.string.replace(' ', '').replace('avis', ''))
			restaurant.rating = str(html.find(class_='ui_bubble_rating')['class'][1]).replace('bubble_', '')
			restaurant.rating = restaurant.rating[0] + "." + restaurant.rating[1]

			# Logging results
			rating_change = float(restaurant.rating) - float(previous_rating)
			review_count_change = int(restaurant.review_count) - int(previous_review_count)

			if rating_change == 0 and review_count_change == 0 :
				message = base_message + "unchanged."
			else :
				message = base_message + "rating changed by {0}, reviews changed by {1:+}.".format(rating_change, review_count_change)

			new_data = {
				"[TA] Rating": restaurant.rating,
				"[TA] Reviews": restaurant.review_count,
				"Last updated": datetime.now().date().isoformat(),
				}
			url_to_update = airtable_table_url + '/' + record['id']
			patch_response = call_airtable(url=url_to_update, request_type="PATCH", data=new_data)
			if patch_response.status_code == 200 :
				print(message + " | Updated successfully.")
			else :
				print(message + " | Could not update ! ")
				print('Status code : {}'.format(patch_response.status_code))
				print(patch_response.json())

#			except Exception:
#				print(base_message + ' could not collect data from TripAdvisor. ABORTED.')

params = {
	"fields": ["[TA] ID", "[TA] Reviews", "[TA] Rating"],
#	"filterByFormula": "{Today's Trip}",
	"pageSize": 100,
	}
	
params = urllib.parse.urlencode(params)
url_for_listing_records = airtable_table_url + "/?=" + params

# "?" + "fields[]=[TA] ID" +
# "&" + "fields[]=[TA] Reviews" +
# "&" + "fields[]=[TA] Rating" +
# "&" + "filterByFormula={Today's Trip}" +
# "&" + "pageSize=4"
	
response = call_airtable(url_for_listing_records)
response_data = response.json()
offset = check_for_offset(response_data)

while offset :
	# if there are multiple pages of records
	print('Offset : ' + offset)
	update_records(response_data['records'])
	response = call_airtable(url_for_listing_records + "&offset=" + offset)
	response_data = response.json()
	offset = check_for_offset(response_data)
else :
	# if there is only one page of records, or when dealing with last page
	update_records(response_data['records'])


#	restaurant.street_address = html.find(class_='street-address').string
#	restaurant.locality = html.find(class_='locality').string.replace(',','')
#	restaurant.url = page.url
