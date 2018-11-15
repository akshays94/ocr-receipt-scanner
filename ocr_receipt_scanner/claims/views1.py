import os
import sys
import cv2
import json
import pytesseract
import numpy as np

from django.urls import reverse
from django.conf import settings
from django.http import HttpResponse
from django.views.generic import TemplateView, View
from django.template.response import TemplateResponse

try:
    from PIL import Image
except ImportError:
    import Image

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

	def resize_image(self, image, name):
		# Rescale the image, if needed.
		print('rescaling the image ... ')
		print('\told image size', image.shape)
		
		scale_factor = 1.5
		# scale_factor = 2
		# scale_factor = 8

		image = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
		
		print('\tnew image size', image.shape)
		cv2.imwrite('/app/receipts/rescaled-{}'.format(name), image)
		return image


	def to_grayscale(self, image, name):
		# Convert to gray
		print('converting image to gray ... ')
		image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		cv2.imwrite('/app/receipts/gray-{}'.format(name), image)
		return image	


	def remove_noise(self, image, name):
		# Apply dilation and erosion to remove some noise
		print('removing noise ... ')
		
		# kernel = np.ones((1, 1), np.uint8)
		# image = cv2.dilate(image, kernel, iterations=1)
		# image = cv2.erode(image, kernel, iterations=1)
		
		image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
		image = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)

		cv2.imwrite('/app/receipts/nonoise-{}'.format(name), image)	
		return image


	def apply_blur(self, image, name):
		# Apply blur to smooth out the edges
		print('applying blur ... ')
		image = cv2.GaussianBlur(image, (5, 5), 0)
		cv2.imwrite('/app/receipts/blurred-{}'.format(name), image)
		return image	


	def apply_binarization(self, image, name): 	
		# Apply threshold to get image with only b&w (binarization)
		print('applying binarization ... ')
		

		# image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
		
		image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)[1]

		# image = cv2.threshold(image, 127, 255, cv2.THRESH_TRUNC)[1]

		# image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)

		# image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

		# blur = cv2.GaussianBlur(image, (5,5), 0)
		# image = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]

		cv2.imwrite('/app/receipts/bw-{}'.format(name), image)
		return image


	def preprocess_image(self, receipt_image, receipt):
	
		receipt_image = self.resize_image(receipt_image, receipt.name)		
		receipt_image = self.to_grayscale(receipt_image, receipt.name)
		# receipt_image = self.remove_noise(receipt_image, receipt.name)	
		# receipt_image = self.apply_blur(receipt_image, receipt.name)		
		receipt_image = self.apply_binarization(receipt_image, receipt.name)
		
		return receipt_image	
		

	def post(self, request, *args, **kwargs):

		try:

			receipt = request.FILES.get('receipt')
			print('\n\n\nreceipt', receipt.__dict__, type(receipt.file))

			location_to_save = '/app/receipts/{name}'.format(**{
				'name': receipt.name
			})
			print('location_to_save', location_to_save)

			receipt_image = Image.open(receipt)
			print('receipt_image', receipt_image, type(receipt_image))
			receipt_image.save(location_to_save)

			print('-'*50)
			print('Starting to process image ... ')

			# Change dpi
			print('changing the dpi of the image ... ')
			cmd = 'convert -units PixelsPerInch {location_to_save} -density 300 {location_to_save}'.format(**{
					'location_to_save': location_to_save
				})
			os.system(cmd)

			# adding small border to image
			# print('adding a small border to the image ... ')
			# cmd = 'convert {location_to_save} -bordercolor White -border 10x10 {location_to_save}'.format(**{
			# 		'location_to_save': location_to_save
			# 	})
			# os.system(cmd)

			# removing alpha if any
			# print('removing alpha if any ... ')
			# cmd = 'convert {location_to_save} -alpha off {location_to_save}'.format(**{
			# 		'location_to_save': location_to_save
			# 	})
			# os.system(cmd)

			

			receipt_image = cv2.imread(location_to_save)

			# PREPROCESS THE IMAGE
			receipt_image = self.preprocess_image(receipt_image, receipt)

			# TESSERACT CONFIGURATIONS
			# config = ('-l eng --oem 1 --psm 3')

			# whitelist = 'tessedit_char_whitelist=0123456789/.'

			# config = ('-l eng --oem 1 --psm 3 -c {whitelist}'.format(**{
			# 		'whitelist': whitelist
			# 	}))

			config = ('-l eng --oem 1 --psm 3')

			print('\n\n')
			print('='*25)
			print(pytesseract.image_to_boxes(receipt_image))
			print('='*25)


			image_text = pytesseract.image_to_string(receipt_image, config=config)


			image_text = image_text.encode('ascii', 'ignore').decode('ascii')

			print('\n\n')
			print('='*25)
			print(image_text)
			print('='*25)

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