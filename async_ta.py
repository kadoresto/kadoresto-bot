import requests, asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from scraping_tools import tripadvisor
from apis import airtable
from aiohttp import ClientSession


@dataclass
class Restaurant(object):

	tripadvisor_id: int
	airtable_id: str
	name: str
	old_reviews: int=None
	old_rating: str=None
	new_reviews: int=None
	new_rating: str=None

	def __str__(self):
		return '<Restaurant #{} - "{}">'.format(self.tripadvisor_id, self.name)

	def __repr__(self):
		return str(self)


def setup_restaurant(record):

	# Extracting AirTable data
	fields = record['fields']
	restaurant = Restaurant(
		airtable_id = record['id'],
		tripadvisor_id = fields['[TA] ID'],
		name = fields['Restaurant'],
		old_reviews = fields['[TA] Reviews'],
		old_rating = fields['[TA] Rating'],
		)

	return restaurant


async def operation(record, session):

	tripadvisor_id = record['fields']['[TA] ID']

	async with session.get('https://www.tripadvisor.fr/Restaurant_Review-g187147-d' + str(tripadvisor_id)) as page:
		page.raise_for_status()
		return await page.text()

def process_tripadvisor_pages(pages):

	restaurants = []

	for page in pages:
		try:
			html = BeautifulSoup(page, 'lxml')
			tripadvisor_id = html.find("div", class_="blRow")['data-locid']
			reviews = int(html.find("",  {"href": "#REVIEWS", "class": "more", }).span.string.replace(' ', '').replace('avis', ''))
			rating = str(html.find(class_='ui_bubble_rating')['class'][1]).replace('bubble_', '')
			rating = rating[0] + "." + rating[1]
			restaurants.append({
				'tripadvisor_id': tripadvisor_id,
				'reviews': reviews,
				'rating': rating,
				})
		except Exception:
			print("Parsing of a TripAdvisor page has failed!")
	return restaurants




async def process_records(records):

	restaurants = {}

	tasks = [] # asynchronous tasks

	async with ClientSession() as session:
		for record in records:
			restaurant = setup_restaurant(record)
			restaurants[restaurant.tripadvisor_id] = restaurant
			task = asyncio.ensure_future(operation(record, session))
			tasks.append(task)
		pages = await asyncio.gather(*tasks)
		fetched_data = process_tripadvisor_pages(pages)
		for fetched_restaurant in fetched_data:
			tripadvisor_id = int(fetched_restaurant['tripadvisor_id'])
			restaurant = restaurants[tripadvisor_id]
			restaurant.new_reviews = fetched_restaurant['reviews']
			restaurant.new_rating = fetched_restaurant['rating']
		for restaurant in restaurants.values():
			print(restaurant.old_reviews, restaurant.new_reviews)

'''			rating_change = float(restaurant.rating) - float(old_rating)
			review_count_change = int(restaurant.review_count) - int(old_review_count)

			if rating_change == 0 and review_count_change == 0 :
				message = base_message + "unchanged."
			else :
				message = base_message + "rating changed by {0}, reviews changed by {1:+}.".format(rating_change, review_count_change)

			new_data = {
				"[TA] Rating": restaurant.rating,
				"[TA] Reviews": restaurant.review_count,
				"Last updated": datetime.now().date().isoformat(),
				}
				'''



response = airtable.list_records('Restaurants')
response_data = response.json()
records = response_data['records'][0:5]

loop = asyncio.get_event_loop()
future = asyncio.ensure_future(process_records(records))
loop.run_until_complete(future)
