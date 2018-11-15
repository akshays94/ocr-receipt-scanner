import io
import os
import sys
# import cv2
import json
# import pytesseract
# import numpy as np

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types

from django.urls import reverse
from django.conf import settings
from django.http import HttpResponse
from django.views.generic import TemplateView, View
from django.template.response import TemplateResponse

try:
    from PIL import Image
except ImportError:
    import Image

# AIzaSyBbOxruuMK3ioJzceQl3DSo3O3PqaNxSfE 

# https://linuxhint.com/install-tesseract-ocr-linux/    

# https://www.linkedin.com/pulse/google-vision-api-receipt-ocr-denny-muktar/
# https://cloud.google.com/vision/

class Home(TemplateView):

	def get(self, request, *args, **kwargs):

		try:

			self.template_name = 'claims/home.html'

			context = {}

			return self.render_to_response(context)

		except Exception as e:
			print(e)



class UploadReceipt(View):

	def post(self, request, *args, **kwargs):
		try:

			receipt = request.FILES.get('receipt')		

			print('receipt', receipt)

			location_to_save = '/app/receipts/{name}'.format(**{
				'name': receipt.name
			})
			print('location_to_save', location_to_save)

			receipt_image = Image.open(receipt)
			print('receipt_image', receipt_image, type(receipt_image))
			receipt_image.save(location_to_save)

			# Instantiates a client
			print('instantiating client ... ')
			# https://cloud.google.com/blog/products/gcp/help-keep-your-google-cloud-service-account-keys-safe
			client = vision.ImageAnnotatorClient()
			print('client instantiated ... ')

			# The name of the image file to annotate
			# file_name = os.path.join(
			# 	os.path.dirname(__file__),
			# 	'resources/wakeupcat.jpg')

			file_name = location_to_save

			# Loads the image into memory
			with io.open(file_name, 'rb') as image_file:
				content = image_file.read()

			image = types.Image(content=content)

			# Performs label detection on the image file
			response = client.label_detection(image=image)
			labels = response.label_annotations

			print('Labels:')
			for label in labels:
			    print(label.description)

			payload = {}

			response = HttpResponse(json.dumps(payload), 
			content_type='application/json')
			response.status_code = 200

			return response

		except Exception as e:
			print(e)
			kwargs.update({'message': 'Failed ... '})

			response = HttpResponse(json.dumps(kwargs), 
				content_type='application/json')
			response.status_code = 400

			return response	
