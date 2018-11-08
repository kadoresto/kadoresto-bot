import requests, asyncio
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from scraping_tools import tripadvisor
from apis import airtable

class Restaurant:

	def __init__(self, tripadvisor_id, name, review_count=0, rating=None):
		self.tripadvisor_id = tripadvisor_id
		self.name = name
#		self.street_address = street_address
		self.review_count = review_count
		self.rating = rating

	def __repr__(self):
		return self.__str__()

async def update_record(record):

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
	base_message = "TA #{} | '{}', ".format(tripadvisor_id, restaurant_name)

	if recently_updated :
		print(base_message + 'was recently updated.')
	else :

		# Fetching TripAdvisor data
		page = requests.get('https://www.tripadvisor.fr/Restaurant_Review-g187147-d' + str(tripadvisor_id))
		html = BeautifulSoup(page.content, 'lxml')		

		try :
			restaurant.review_count = int(html.find("",  {"href": "#REVIEWS", "class": "more", }).span.string.replace(' ', '').replace('avis', ''))
			restaurant.rating = str(html.find(class_='ui_bubble_rating')['class'][1]).replace('bubble_', '')
			restaurant.rating = restaurant.rating[0] + "." + restaurant.rating[1]
		except Exception :
			message = base_message + "couldn't parse TripAdvisor correctly !!!"
			new_data = {
				"[TA] Error": True,
				"Last updated": datetime.now().date().isoformat(),
				}
		else :
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

		update_response = airtable.update_record('Restaurants', record['id'], data=new_data)
		if update_response.status_code == 200 :
			print(message + " | Updated successfully.")
		else :
			print(message + " | Could not update ! ")
			print('Status code : {}'.format(update_response.status_code))
			print(update_response.json())

loop = asyncio.get_event_loop()
future = asyncio.ensure_future(
	airtable.async_process_records(
		table='Restaurants',
		params={
			"fields": ["Restaurant", "Last updated", "[TA] ID", "[TA] Reviews", "[TA] Rating", ],
		#	"filterByFormula": "{Today's Trip}",
		#	"pageSize": 100,
			},
		operation=update_record,
	)
)
loop.run_until_complete(future)