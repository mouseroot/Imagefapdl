from tornado.httpclient import HTTPClient
import tornado.ioloop
from bs4 import BeautifulSoup
from optparse import OptionParser
import os

gallery_list = []
photo_lists = []

def main(url,downloadto):
	#url = "http://www.imagefap.com/pictures/4148883/Waiting-for-Daddy?gid=4148883&view=2"
	client = HTTPClient()
	print "Gathering links from Gallery"
	gallery_response = client.fetch(url)
	gallery_pool = BeautifulSoup(gallery_response.body)
	gallery_links = gallery_pool.findAll("a")
	for gallery_link in gallery_links:
		if "/photo" in gallery_link["href"]:
			photo_page_url = "".join(["http://imagefap.com",gallery_link["href"]])
			gallery_list.append(photo_page_url)

	print "Parsing individual pages for actual image"
	for link in gallery_list:
		photo_response = client.fetch(link)
		photo_pool = BeautifulSoup(photo_response.body)
		photo_images = photo_pool.findAll("img",src=True)
		for image in photo_images:
			if image["src"].startswith("http://fap.to"):
				image_src = image["src"]
				filename = image_src.split("/")[-1:][0]
				image_response = client.fetch(image_src)
				print "Downloading %s" % filename
				dest = "".join([downloadto,"/",filename])
				with open(dest,"wb") as f:
					f.write(image_response.body)


if __name__ == "__main__":
	usage = "Usage: imagefapdl [Options] gallery_url"
	desc = "Downloads all imagefap images from a one-page gallery or a single page of a gallery"
	parser = OptionParser(usage=usage,description=desc)
	parser.add_option("-f","--folder",default=".",dest="output_folder",help="Location where to download the images")
	(options,args) = parser.parse_args()
	if len(args) > 0:
		url = args[0]
		folder = options.output_folder
		if not os.path.exists(folder):
			print "Folder %s not found...creating" % folder
			os.mkdir(folder)
		main(url,folder)
	else:
		parser.print_help()


