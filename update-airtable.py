import requests, json
from bs4 import BeautifulSoup

token = "keyiXWAznJ80FXmtW"

def call_airtable(url):
	return requests.get(url, headers={
		'authorization': 'Bearer ' + token,
		'content-type': 'application/json'
		})

response = call_airtable(
	"https://api.airtable.com/v0/appCFLZH7zvAoTdY5/Restaurants" +
	"?" + "fields[]=TripAdvisor ID" +
	"&" + "filterByFormula={Today's Trip}"
	)

response = response.json()

restaurants = response['records']
list_of_tripadvisor_ids = [restaurant['fields']['TripAdvisor ID'] for restaurant in restaurants]

print()
print("=======================")
print("Running script...")
print("-----------------------")
print("Received {} restaurants".format(len(list_of_tripadvisor_ids)))
print(list_of_tripadvisor_ids)

for tripadvisor_id in list_of_tripadvisor_ids :
	page = requests.get('https://www.tripadvisor.fr/Restaurant_Review-g187147-d' + str(tripadvisor_id))
	html = BeautifulSoup(page.content, 'lxml')
	street_address = html.find(class_='street-address').string
	print(street_address)
#	locality = html.find(class_='locality').string.replace(',','')
#	url = page.url
#	restaurants.append({
#		'url': url,
#		'street_address': street_address,
#		'locality': locality,
#		})
