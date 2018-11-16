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

from ocr_receipt_scanner.claims.info_retrieval import *
from ocr_receipt_scanner.claims.info_retrieval_vars import *


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

			InformationRetrievalTests.perform_tests()

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

			location_to_save = '/app/receipts/{name}'.format(**{
				'name': receipt.name
			})
			print('location_to_save', location_to_save)

			receipt_image = Image.open(receipt)
			print('receipt_image', receipt_image, type(receipt_image))
			receipt_image.save(location_to_save)

			# # Instantiates a client
			# print('instantiating client ... ')
			# # https://cloud.google.com/blog/products/gcp/help-keep-your-google-cloud-service-account-keys-safe
			# client = vision.ImageAnnotatorClient()
			# print('client instantiated ... ')

			# # The name of the image file to annotate
			# # file_name = os.path.join(
			# # 	os.path.dirname(__file__),
			# # 	'resources/wakeupcat.jpg')

			# file_name = location_to_save

			# # Loads the image into memory
			# with io.open(file_name, 'rb') as image_file:
			# 	content = image_file.read()

			# image = types.Image(content=content)

			# # Performs label detection on the image file
			# response = client.label_detection(image=image)
			# labels = response.label_annotations

			# print('Labels:')
			# for label in labels:
			#     print(label.description)

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


'''
'CITYCAB PTE LTD\nSHC72925\nTRIP NO\n101120291\nSTART 11/10/2018 20:29\nEND 11/10/2018 20:49\nDISTANCE RUN 13.80 KM\nMETER FARE $\nCITY AREA SUR $\nPEAK HOUR 25% $\nTOTAL FARE $\n12.70\n3.00\n3.20\n18.90\nAMOUNT PAID\n$\n18.90\n'
'00 Put ull 73%\n16:28\n+\nDriver on the way\nLim Choo Tong\nSLG67947 • Toyota Prius\nGrabShare\nFare: SGD 4.5\nVISA\nTag this trip as\nPersonal\nPromo\nTAKE5\n• 37 Jln Sempadan\nTerminal 2, Changi Airport\nCANCEL BOOKING\n'
'SHIRT\nDAILINING\nDIAL-A-CAB\nTEL: 0555 8883\nart\nMonth\nwww\nSHB408C\nRECEIPT N. 6384\nFRM 02/10/19 22:38\nTO 02/10/18 22:54\nKM RUN\n8.6\nFARE\n9.40\nom\nAIRPORT\nPEAK 25\nTUTAL SS\n14.75\nHAVE A NICE DAY\n'
'"COMFORT TRANSPORTATION\nSH 8026G\nTRIP NO 523425914\nSTART 11/01/2018 20:00\nSH\nfaiye\nBA\n.\n1\n.\nha\nust\nFOR\nniverend\n'
'Reg No.20-0304975-11\nTAXI NO.\nSHB85095\nRECEIPT NO. 4610190006\nSTART 19/10/2018 00:06\nEND 19/10/2018 00:15\nDISTANCE RUN\n7.6KM\nMETER FARE\nMIDNIGHT\nCHANGI AIRPORT\n$8.08\n$4.04\n$3.00\nTOTAL\n$1.5.12\nPAIDAMT\n$15.10\nCust Service 6476-3033\n'
"description": "COMFORT TRANSPORTATION\nSHD4062D\nTRIP NO 010408455\nSTART 04/01/2018 08:15\nEND 04/01/2018 09:01\nDISTANCE RUN 11.80 KM\nMETER FARE $\nERP\nPEAK HOUR 25% $\nTOTAL FARE\n10.45\n4.50\n2.60\n17.55\nAMOUNT PAID\n$\n17.55\n",
"description": "CITYCAB PTE LTD\nSHA8520M\nTRIP NO 010511564\nSTART 05/01/2018 11:56\nEND 05/01/2018 12:20\nDISTANCE RUN 2.80 KM\n$\nMETER FARE\nTOTAL FARE\n11.60\n11.60\nAMOUNT PAID\n$\n11.60\n",
"description": "B\nCOMFORT TRANSPORTATION\nSHA7375Y\n12\npl\nTRIP MO\n523369155\nSTART 11/01/2018 09:24\nEND 11/01/2018 09:42\nDISTANCE RUN 12.10 KM\neit.\nFLAT FARE\nTOTAL FARE\n$\n27.50\n27.50\nAMOUNT PAID\n$\n27.50\nCheck your cubpoint at\nhttps://cabrewards.\ncdytaxi com.sg\nhe\nlem\nF\n",
"description": "COMFORT TRANSPORTATION\nSH 8026G\nTRIP NO 523425914\nSTART 11/01/2018 20:00\nSH\nfaiye\nBA\n.\n1\n.\nha\nust\nFOR\nniverend\n",
"description": "@as ull 77%\n07:58\n€\n25 Oct 2017, 09:02AM\nBooking ID:\nADR-0459658-2-1787\nSJN4532\nGoh Guo Quan Edwin\nFare: SGD 7\nVISA\nTag this trip as\nPersonal\nPromo\nTAKE5\nDoor 3, T2 Arrivals, Changi Airport\nVilla Marina\nREPORT AN ISSUE\n",
"description": "CITYCAB PTE LTD\nSHA9200E\nTRIP NO 573116766\nSTART 09/01/2018 09:11\nEND 09/01/2018 09:34\nDISTANCE RUM 9.30 KM\nFLAT FARE\nTOTAL FARE\nAMOUNT PAID\n0\n18.50\n",
"description": "B\nCOMFORT TRANSPORTATION\nSHA7375Y\n12\npl\nTRIP MO\n523369155\nSTART 11/01/2018 09:24\nEND 11/01/2018 09:42\nDISTANCE RUN 12.10 KM\neit.\nFLAT FARE\nTOTAL FARE\n$\n27.50\n27.50\nAMOUNT PAID\n$\n27.50\nCheck your cubpoint at\nhttps://cabrewards.\ncdytaxi com.sg\nhe\nlem\nF\n",
"description": "...l StarHub\n1 18%O\n13:20\n10 Jan 2018, 09:25\nBOOKING ID\nIOS-2595014-3-721\nSLV3422M\nLim Kim Huat Clivee (Lin Jinfa)\nFARE: SGD 25\nVISA\nPromo\nTAKE4\nTag this trip as\nPersonal\n37 Jln Sempadan\nOmron Asia Pacific Pte Ltd - Asia Pacific Regional O...\nYou rated:\nEXCELLENT!\nREPORT AN ISSUE\n",



'''