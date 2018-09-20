import requests, json
from secret import api_key
from bs4 import BeautifulSoup
from scraping_tools import tripadvisor

airtable_table_url = "https://api.airtable.com/v0/appCFLZH7zvAoTdY5/Restaurants"

class Restaurant:

	def __init__(self, tripadvisor_id, review_count=0, rating=None):
		self.tripadvisor_id = tripadvisor_id
#		self.street_address = street_address
		self.review_count = review_count
		self.rating = rating

	def __str__(self):
		return "TripAdvisor #{}, rated {} with {} reviews.".format(self.tripadvisor_id, self.rating, self.review_count)

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
		print(data)

	if request_type == "GET" :
		return requests.get(url, headers=headers)

	elif request_type == "PATCH" :
		return requests.patch(url, headers=headers, data=data)


response = call_airtable(
	airtable_table_url +
	"?" + "fields[]=[TA] ID" +
	"&" + "fields[]=[TA] Reviews" +
	"&" + "fields[]=[TA] Rating" +
	"&" + "filterByFormula={Today's Trip}"
	)

response = response.json()

restaurants = {}

for index, record in enumerate(response['records'][0:1], start=1) :

	# Extracting AirTable data
	tripadvisor_id = record['fields']['[TA] ID']
	previous_review_count = record['fields']['[TA] Reviews']
	previous_rating = record['fields']['[TA] Rating']

	# Fetching TripAdvisor data
	page = requests.get('https://www.tripadvisor.fr/Restaurant_Review-g187147-d' + str(tripadvisor_id))
	html = BeautifulSoup(page.content, 'lxml')

	# Creating new restaurant instance
	restaurant = Restaurant(tripadvisor_id=tripadvisor_id)

	# Converting TripAdvisor data to useable formats, and saving to new instance
	restaurant.review_count = int(html.find("",  {"href": "#REVIEWS", "class": "more", }).span.string.replace(' ', '').replace('avis', ''))
	restaurant.rating = str(html.find(class_='ui_bubble_rating')['class'][1]).replace('bubble_', '')
	restaurant.rating = restaurant.rating[0] + "." + restaurant.rating[1]

	# Logging results
	progress = "{}/{}".format(index, len(response['records']))
	rating_change = float(restaurant.rating) - float(previous_rating)
	review_count_change = int(restaurant.review_count) - int(previous_review_count)
	if rating_change == 0 and review_count_change == 0 :
		print("{} | TripAdvisor #{}, unchanged.".format(progress, tripadvisor_id))
	else :
		print("{0} | TripAdvisor #{1}, rating changed by {2}, reviews changed by {3:+}.".format(progress, tripadvisor_id, rating_change, review_count_change))

	new_data = {
		"[TA] Rating": restaurant.rating,
		"[TA] Reviews": restaurant.review_count,
		}
	url_to_update = airtable_table_url + '/' + record['id']
	print('Updating : ' + url_to_update)
	patch_response = call_airtable(url=url_to_update, request_type="PATCH", data=new_data)
	print(patch_response)

#	restaurant.street_address = html.find(class_='street-address').string
#	restaurant.locality = html.find(class_='locality').string.replace(',','')
#	restaurant.url = page.url
