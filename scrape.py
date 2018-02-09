import urllib.request, urllib.error, urllib.parse
import requests
from bs4 import BeautifulSoup
import json
import sys
import os
from url_normalize import url_normalize

map_link_to_resource = open("index.keys", "w")
pages_parsed = set()

def manageFile(relative):
	def useLink(link):
		download_file = link + "/" + relative['href']
		name = relative['href']
		while os.path.isfile(name):
			(root, ext) = os.path.splitext(name)
			name = root + "(1)" + ext
			name += "_1"
		try:
			urllib.request.urlretrieve(download_file, filename=name)
		except:
			print("not working: " + link)
	return useLink

def manageLink(relative):
	def useLink(link):
		extension = link.split('/')[3:]
		extension = "/" + ('/').join(extension)
		end = relative['href']
		transformed = extension + "/" + relative['href']
		relative['href'] = transformed
		parse_page(link + "/" + end)
	return useLink

def doNothing():
	return doNothing

def chooseLinkOption(relative):
	if ".mp4" in relative['href']:
		return doNothing
	if "." in relative['href']:
		return manageFile(relative)
	return manageLink(relative)

def parse_page(link):
	print(link)
	if link in pages_parsed:
		return
	pages_parsed.add(link)
	site = link
	directory = link.split('/')[-1]
	hdr = {'User-Agent': 'Mozilla/5.0'}
	req = urllib.request.Request(site,headers=hdr)
	page = urllib.request.urlopen(req)
	if 'text/html' not in page.headers['Content-Type']:
		urllib.request.urlretrieve(link, filename=directory)
		return
	soup = BeautifulSoup(page, 'html.parser')
	#print soup
	try:
		html = soup.find("div", {"id": "parent-fieldname-text" })
	except Exception as e:
		print(e)
		return
	try:
		os.makedirs(directory)
	except Exception as e:
		print(e)
	os.chdir(directory)
	try:
		links = html.find_all('a', {"class":"internal-link"})
		images = html.find_all('img')
	except Exception as e:
		print("not a content page " + str(e))

	for image in images:
		image_link = image.get('src')
		if not "https://" or not "http://" in image_link:
			image_link = url_normalize(link + "/" + image_link)
		try:
			path = urllib.request.urlopen(image_link)
			if '@@images' in path.url:
				filename = path.url.split('/')[-4]
			else:
				filename = path.url.split('/')[-1]
			if filename is 'thumb' or filename is 'preview' or filename is 'mini':
				print('url not getting translated: ' + path.url)
			image['alt'] = filename
			while os.path.isfile(filename):
				(root, ext) = os.path.splitext(filename)
				filename = root + "(1)" + ext
			urllib.request.urlretrieve(image_link, filename=filename)
		except:
			print("not working: " + link)
	
	for href in links:
		chooseLinkOption(href)(link)
	output = open("index.html", "w")
	output.write(html.prettify())
	output.close()

if __name__ == '__main__':
	if len(sys.argv) < 1:
		raise AttributeError("please call with a url") 
	parse_page(sys.argv[1])
