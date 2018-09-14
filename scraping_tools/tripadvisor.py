# -*- coding: utf-8 -*-


def get_key(r):

	return r['id'].replace('eatery_', '')



def get_name(r):

	return r.find(class_='property_title').string.replace('\n', '')



def get_rating(r):

	bubble = r.find(class_='ui_bubble_rating')['class'][1]
	# should look like : bubble_50

	rating = str(bubble).replace('bubble_', '')
	# should look like : 50

	return rating



def get_reviews(r):

	result = r.find(class_='reviewCount').a.string.replace(' ', '').replace('avis', '')

	return int(result)


def get_rank(r):

	rank_text = r.find(class_='popIndex').string
	# should look like : N°12 sur 13 023 Restaurants à Paris

	return rank_text[5:len(rank_text)-32]



def get_url(r):

	return "https://www.tripadvisor.fr/" + r.find(class_="property_title")['href']



def get_photo(r):

	img = result = r.find(class_="photo_image")

	if img :
		return img['src']
	else :
		return None
