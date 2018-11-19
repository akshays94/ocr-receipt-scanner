import itertools

from django.db import models


class ReceiptScan(models.Model):

	corpus 				= models.TextField()
	receipt_no_tags 	= models.TextField()
	receipt_amt_tags 	= models.TextField()
	receipt_data 		= models.TextField() 
	created_on 			= models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return '{corpus}{dots}'.format(**{
				'corpus': self.corpus[:10],
				'dots': '...' if len(self.corpus) > 10 else ''
			})

	def split_corpus(self):
		return self.corpus.split('\n')
