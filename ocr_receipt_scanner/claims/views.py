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
from django.core.files.storage import FileSystemStorage

from ocr_receipt_scanner.claims.models import *
from ocr_receipt_scanner.claims.info_retrieval import *
from ocr_receipt_scanner.claims.info_retrieval_vars import *

#IP Address 13.126.130.131

try:
    from PIL import Image
except ImportError:
    import Image


class Home(TemplateView):

	def get(self, request, *args, **kwargs):

		try:

			self.template_name = 'claims/add-claim.html'

			# corpus = 'CITYCAB PTE LTD\nSHC72925\nTRIP NO\n101120291\nSTART 11/10/2018 20:29\nEND 11/10/2018 20:49\nDISTANCE RUN 13.80 KM\nMETER FARE $\nCITY AREA SUR $\nPEAK HOUR 25% $\nTOTAL FARE $\n12.70\n3.00\n3.20\n18.90\nAMOUNT PAID\n$\n18.90\n'

			# contents = InformationRetrieval(corpus).get_receipt_contents()
			# print(contents)

			# InformationRetrievalTests.perform_tests()

			context = {}

			return self.render_to_response(context)

		except Exception as e:
			print(e)
			kwargs.update({'message': 'Failed ... '})

			response = HttpResponse(json.dumps(kwargs), 
				content_type='application/json')
			response.status_code = 400

			return response



class UploadReceipt(View):

	def post(self, request, *args, **kwargs):
		try:

			receipt = request.FILES.get('receipt')		

			print('receipt', receipt)

			# =======================================================
			fs = FileSystemStorage()
			filename = fs.save(receipt.name, receipt)
			file_name = fs.url(filename)

			# location = '/app/ocr_receipt_scanner/{}'.format(file_name)

			# with io.open(location, "rb") as image_file:
			# 	content = image_file.read()	
			# =======================================================

			# location_to_save = '/app/receipts/{name}'.format(**{
			# 	'name': receipt.name
			# })
			# print('location_to_save', location_to_save)

			# receipt_image = Image.open(receipt)
			# print('receipt_image', receipt_image, type(receipt_image))
			# receipt_image.save(location_to_save)



			# Instantiates a client
			print('instantiating client ... ')
			# https://cloud.google.com/blog/products/gcp/help-keep-your-google-cloud-service-account-keys-safe
			client = vision.ImageAnnotatorClient()
			print('client instantiated ... ')

			# The name of the image file to annotate
			# file_name = os.path.join(
			# 	os.path.dirname(__file__),
			# 	'resources/wakeupcat.jpg')

			# file_name = location_to_save

			file_name = os.path.join(str(settings.APPS_DIR), file_name)

			# Loads the image into memory
			with io.open(file_name, 'rb') as image_file:
				content = image_file.read()

			image = types.Image(content=content)

			# # Performs label detection on the image file
			response = client.document_text_detection(image=image)
			texts = response.text_annotations

			corpus = texts[0].description

			print('corpus', corpus)

			# corpus = 'SHOTS\nESPRESSO BAR\nwww. shots, con se\nJABLZ0B2CHE\nPax: 1\nOP:Cashier 1\nPOS Title POS001\nCashier 1\nPUS: POS001\nRept# 11000035434 31/12/2011 22:12\n1 Cafe Mocha\n1 Cold Cafe Mocha\n$5.80\n$6.20\nSUBTOTAL\n$12.00\nInc. 7% GST\n$0.79\nTOTAL\n$12.00\nCASH\n$50.00\nChange\n$38.00\nClosed Bill\n- 31/12/2011 22:13---\n8 Ann Siang Hill\nS(069788)\nTel: 52248502\nemail: infushots.com.sg\n*XXXXXXXXXXX\nThank You\nPlease Come Again\n'

			results = InformationRetrieval(corpus).get_receipt_contents()	

			receipt_no_tags = results.pop('receipt_no_tags')
			receipt_amt_tags = results.pop('receipt_amt_tags')

			fields = {
				'corpus': corpus,
				'receipt_no_tags': str(receipt_no_tags),
				'receipt_amt_tags': str(receipt_amt_tags),
				'receipt_data': str(results)
			}

			ReceiptScan.objects.create(**fields)

			payload = {
				'results': results
			}

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

