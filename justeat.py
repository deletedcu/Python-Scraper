import sys
from urllib.parse import urljoin
import json
import requests
from bs4 import BeautifulSoup

args = sys.argv
baseURL = 'https://just-eat.ca/'

def getTowns():
	print('Listing available towns ..')

	page = requests.get(baseURL)
	soup = BeautifulSoup(page.content, 'html.parser')
	temp = soup.select('div.c-footer-panel')[1]
	links = temp.select('ul li a');

	urls = {}
	for link in links:
		fullURL = urljoin(baseURL, link['href'])
		town = link.get_text().split()[0]
		urls[town] = fullURL
	with open('towns.json', 'w') as towns_file:
		json.dump(urls, towns_file, indent=4, separators=(',', ': '))

def getRestaurants(Town):
	result = []
	
	def fetch(url):
		page = requests.get(url)
		soup = BeautifulSoup(page.content, 'html.parser')
		lists = soup.select('div.restaurantWithLogo')
		for l in lists:
			restaurant = {}

			temp = l.select('section.restaurantDetails')[0]
			link = temp.select('a')[0]
			restaurant['name'] = link.get_text()
			restaurant['restaurantURL'] = urljoin(baseURL, link['href'])

			temp = l.select('p.restaurantCuisines')[0]
			restaurant['categories'] = temp.get_text()[12:].split(', ')

			result.append(restaurant)

	with open('towns.json', 'r') as towns_file:
		towns = json.load(towns_file)
	
	if(Town == ''):
		for town, url in towns.items():
			print('Fetching restaurants in ', town, '..')
			fetch(url)
			print('done.')
	else:
		url = towns[Town] if Town in towns else ''
		if url != '':
			print('Fetching restaurants in ', Town, '..')
			fetch(url)
			print('done.')

	with open('restaurants.json', 'w') as res_file:
		json.dump(result, res_file, indent=4, separators=(',', ': '))

def getItems(limit):
	result = []

	def fetch(url, id):
		page = requests.get(url)
		soup = BeautifulSoup(page.content, 'html.parser')
		elements = soup.select('div.menu-product.product')
		for element in elements:
			product = {}
			product['name'] = element.select('h4.product-title')[0].get_text().strip()
			product['restaurantID'] = id
			product['salePrice'] = element.select('div.product-price')[0].get_text()
			desc = element.select('div.product-description')
			product['description'] = desc[0].get_text() if len(desc) > 0 else ''
			result.append(product)

	with open('restaurants.json', 'r') as res_file:
		restaurants = json.load(res_file);
	for idx, restaurant in enumerate(restaurants):
		id = restaurant['ID']
		url = restaurant['restaurantURL']
		if limit>0 and idx == limit:
			break
		print('Fetching menu items in ', restaurant['name'], '..')
		fetch(url, id)
		print('done.')

	with open('products.json', 'w') as product_file:
		json.dump(result, product_file, indent=4, separators=(',', ': '))

try:
	if args[1] == 'towns':
		getTowns()
	elif args[1] == 'restaurants':
		Town = args[2] if len(args) > 2 else ''
		getRestaurants(Town)
	elif args[1] == 'items':
		limit = int(args[2]) if len(args) > 2 else 0
		getItems(limit)
except IndexError:
	print('You need to provide some arguments')

