import urllib.request, urllib.error, urllib.parse
import requests
from bs4 import BeautifulSoup
import json
import sys
import os
from url_normalize import url_normalize
import re

pathInfo = {}
rootDir = os.path.abspath(os.path.curdir)
map_link_to_resource = open("index.keys", "w")
errors = open("errors.txt", "w")
pages_parsed = set()

def manageFile(relative):
	def useLink(link):
		if link not in relative['href']:
			download_file = url_normalize(link + "/" + relative['href'])
		else:
			download_file = relative['href']

		name = relative['href'].replace("../", "")
		while os.path.isfile(name):
			(root, ext) = os.path.splitext(name)
			name = root + "(1)" + ext
		try:
			urllib.request.urlretrieve(download_file, filename=name)
		except urllib.error.HTTPError as e:
			print("file download not working: " + download_file)
			print(e)
			errors.write(download_file+"\n")
	return useLink

def manageLink(relative):
	def useLink(link):
		extension = link.split('/')[3:]
		hostname = link.split('/')[2:3][0]
		extension = "/" + ('/').join(extension)
		end = relative['href']
		if not hostname in end:
			transformed = extension + "/" + relative['href']
			goto = link + '/' + end
			relative['href'] = transformed
		else:
			goto = end
			relative['href'] = "/" + ('/').join(end.split('/')[3:])
		currentDirectory = os.path.abspath(os.path.curdir)
		os.chdir(rootDir)
		parse_page(goto)
		os.chdir(currentDirectory)
	return useLink

def doNothing(*args):
	if args is not None and args[0] is not None: 
		errors.write("doing nothing for" + str(args[0]) + "\n")
		print("doing nothing for" + str(args[0]) + "\n")
	return doNothing

def chooseLinkOption(relative):
	if ".mp4" in relative['href']:
		return doNothing
	if "." in relative['href'].split('/')[-1]:
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
	try:
		page = urllib.request.urlopen(req)
	except Exception as e:
		errors.write("cannot parse page " + link + "with error: " + str(e))
		print("cannot parse page " + link + " with error: " + str(e))
		return
	if 'text/html' not in page.headers['Content-Type']:
		os.chdir(os.path.abspath('../'))
		try:
			urllib.request.urlretrieve(link, filename=directory)
		except Exception as e:
			errors.write("cannot save file at regular url" + link + " error: " + str(e))
			print("cannot save file at regular url" + link + " error: " + str(e))
		return
	soup = BeautifulSoup(page, 'html.parser')
	#print soup
	try:
		html = soup.find("div", {"id": re.compile("parent-fieldname-text*") })
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
		return
	for image in images:
		image_link = image.get('src')
		try:
			if not "https://" or not "http://" in image_link:
				image_link = url_normalize(link + "/" + image_link)
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
			print("image link not working: " + str(link) + ": " + str(image_link))
			errors.write(str(link) + ": " + str(image_link)+"\n")
	
	for href in links:
		chooseLinkOption(href)(link)
	output = open("index.html", "wb")
	pathInfo[directory] = link
	output.write(html.encode())
	output.close()

if __name__ == '__main__':
	if len(sys.argv) < 1:
		raise AttributeError("please call with a url") 
	parse_page(sys.argv[1])
	map_link_to_resource.write(str(pathInfo))
	map_link_to_resource.close()
