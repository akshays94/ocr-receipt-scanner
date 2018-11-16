import re
import itertools

from ocr_receipt_scanner.claims.info_retrieval_vars import *


class InformationRetrievalUtils:


	def make_tags(self, tags_meta):

		try:

			# print(tags_meta)

			tags = list()

			for meta_data in tags_meta:
				# add without
				tags.append( (meta_data['rank'], meta_data['name']) )
				
				# add colon
				tags.append( (meta_data['rank'], '{}:'.format(meta_data['name'])) )

				main_tag_name = meta_data['name']

				for text, alternatives in meta_data['alternatives'].items():
					for alternative in alternatives:
						new_tag_name = main_tag_name.replace(text, alternative)
						
						# add without
						tags.append( (meta_data['rank'], new_tag_name) )

						# add colon
						tags.append( (meta_data['rank'], '{}:'.format(new_tag_name)) )

			tags = sorted(tags, key=lambda tag: tag[0])		

			return tags
		except Exception as e:
			print('error while making tags')
			raise e


	def remove_extra_spaces(self, corpus):
		'''
		input: 'amount  paid   '
		output: 'amount paid'	
		'''
		return list(map(lambda text: ' '.join(text.split()), corpus))	


	def is_excat_match(self, corpus, tags):
		
		tag_names = list(map(lambda tag: tag[1], tags))

		is_passed = False
		possible_results = list()

		for index, corpus_text in enumerate(corpus):
			if corpus_text.lower() in tag_names:
					
				next_index = index + 1

				while next_index < len(corpus):
					# Handling this case => 'RECEIPT\n:\nAKS5656'
					next_text = corpus[next_index]

					LENGTH_THRESHOLD = 2

					has_minimum_length = len(next_text) > LENGTH_THRESHOLD

					if has_minimum_length:
						is_passed = True
						possible_results.append({
							'value': next_text,
							'rank': tags[index][0]
						})
						break

					next_index += 1

		possible_results = sorted(possible_results, key=lambda result: result.get('rank'))			

		return is_passed, possible_results


	def is_excat_match_with_some_extra_text(self, corpus, tags):
							
		tag_names = list(map(lambda tag: tag[1], tags))

		is_passed = False
		possible_results = list()

		for index, corpus_text in enumerate(corpus):
			
			# ctext => 'xxxxxx trip no 6453435 3423'
			# op: ['trip', 'trip no']
			containing_tag_names = list(filter(lambda tag_name: '{} '.format(tag_name) in corpus_text.lower(), tag_names))
			
			if not containing_tag_names:
				continue

			# op: ['trip no', 'trip'] 
			containing_tag_names_desc = sorted(containing_tag_names, key=lambda tag_name: len(tag_name), reverse=True)

			# print('\tcontaining_tag_names_desc', containing_tag_names_desc)
		

			# op: 'trip no'

			contained_tag_name = containing_tag_names_desc[0]
			
			tag_name_start_index \
				= corpus_text.lower().index(contained_tag_name)

			contained_tag_name =  corpus_text[tag_name_start_index: tag_name_start_index + len(contained_tag_name)] 	

			# print('\tcontained_tag_name', contained_tag_name)

			# op: ['xxxxxx ', ' 6453435 3423']
			tag_name_removed_text = corpus_text.split(contained_tag_name)
			
			# print('\ttag_name_removed_text', corpus_text, tag_name_removed_text)

			for text in tag_name_removed_text:
				text = text.strip()
				if text:
					is_passed = True
					possible_results.append({
						'value': text,
						'rank': 999
					})

			# op: ' 6453435 3423 xf4545' 
			qualifier_text = max(tag_name_removed_text, key=len)
			qualifier_text = qualifier_text.strip()

			# print('\tqualifier_text', qualifier_text)

			qualifier_texts = qualifier_text.split()

			# print('\tqualifier_texts', qualifier_texts)

			has_many_qualifier_texts = len(qualifier_texts) > 1	

			if has_many_qualifier_texts:
				# op: ' 6453435 xf4545 3423'
				qualifier_texts_desc = sorted(qualifier_texts, key=lambda text: len(text), reverse=True)
				for index, text in enumerate(qualifier_texts_desc):
					text = text.strip()
					if text:
						is_passed = True
						possible_results.append({
							'value': text,
							'rank': index + 1
						})
			else:
				qualifier_text = qualifier_texts[0]
				is_passed = True
				possible_results.append({
					'value': qualifier_text,
					'rank': 1
				})

		possible_results = sorted(possible_results, key=lambda result: result.get('rank'))
			
		return is_passed, possible_results


	def is_contains_alpha_and_num(self, unpacked_corpus):
	
		is_passed = False
		possible_results = list()

		alpha_num_values = list(filter(lambda text: bool(re.match('^(?=.*[0-9]$)(?=.*[a-zA-Z])', text)), unpacked_corpus))

		alpha_num_values = sorted(alpha_num_values, key=len, reverse=True)

		# print('\talphanumvalues', alpha_num_values)

		if alpha_num_values:
			is_passed = True
			possible_results = list(map(lambda text: {
					'value': text,
					'rank': 1
				}, alpha_num_values))
			
		return is_passed, possible_results		


	def is_large_number(self, unpacked_corpus):
	
		is_passed = False
		possible_results = list()

		LENGTH_THRESHOLD = 3

		numeric_values = list(filter(lambda text: text.isdigit() and len(text) > LENGTH_THRESHOLD, unpacked_corpus))

		numeric_values = sorted(numeric_values, key=len, reverse=True)

		# print('\tnumeric_values', numeric_values)

		if numeric_values:
			is_passed = True
			possible_results = list(map(lambda text: {
					'value': text,
					'rank': 1
				}, numeric_values))
			
		return is_passed, possible_results		
	

	def drop_alpha_from_text(self, text):
	
		try:
			
			text_chars = list(text)
			only_numbers = list(filter(lambda char: char == '.' or char.isdigit(), text_chars))
			return ''.join(only_numbers)

		except Exception as e:
			raise e	


class ReceiptNumber(InformationRetrievalUtils):


	def __init__(self, corpus):
		self.RECEIPT_NO_TAGS = self.make_tags(RECEIPT_NO_TAGS_META)
		self.corpus = self.remove_extra_spaces(corpus)

		# op: [['00', 'Put', 'ull', '73%'],['16:28'],['+'],['Driver', 'on', 'the', 'way'],['Lim', 'Choo', 'Tong'],['SLG67947', '•', 'Toyota', 'Prius']
		split_packed_corpus = list(map(lambda text: text.split(), self.corpus))		
		# op: ['00','Put','ull','73%','16:28','+','Driver','on','the','way','Lim','Choo','Tong','SLG67947']
		self.unpacked_corpus = list(itertools.chain.from_iterable(split_packed_corpus))


	def get_receipt_no(self):
		try:
			# print('\n', self.RECEIPT_NO_TAGS)
			# print('\n', self.corpus)

			success, results = self.is_excat_match(self.corpus, self.RECEIPT_NO_TAGS)
			
			if success:
				return results

			success, results = self.is_excat_match_with_some_extra_text(self.corpus, self.RECEIPT_NO_TAGS)
			
			if success:
				return results

			# ===============================

			success, alpha_results = self.is_contains_alpha_and_num(self.unpacked_corpus)

			success, num_results = self.is_large_number(self.unpacked_corpus)
			
			alpha_results.extend(num_results)

			if alpha_results:
				return alpha_results

			return list()	

		except Exception as e:
			raise e



class ReceiptAmount(InformationRetrievalUtils):

	def __init__(self, corpus):
		try:
			self.RECEIPT_AMOUNT_TAGS = self.make_tags(RECEIPT_AMOUNT_TAGS_META)
			self.corpus = self.remove_extra_spaces(corpus)

			# print(self.RECEIPT_AMOUNT_TAGS, self.corpus)

			split_packed_corpus = list(map(lambda text: text.split(), self.corpus))		
			self.unpacked_corpus = list(itertools.chain.from_iterable(split_packed_corpus))
		except Exception as e:
			print('error while initializing receipt amount instance')
			raise e

	def is_excat_match_amount(self):
		
		corpus = self.corpus
		tags = self.RECEIPT_AMOUNT_TAGS

		tag_names = list(map(lambda tag: tag[1], tags))

		is_passed = False
		possible_results = list()

		for index, corpus_text in enumerate(corpus):
			if corpus_text.lower() in tag_names:
					
				next_index = index + 1

				while next_index < len(corpus):
					# Handling this case => 'FARE\n$\n15.10'
					next_text = corpus[next_index]
					try:
						is_zero = len(next_text) == 1 and int(next_text) == 0

						if is_zero:
							next_index += 1
							continue

						next_text = float( ''.join(next_text.split()) )
						
						is_passed = True
						possible_results.append({
							'value': next_text,
							'rank': tags[index][0]
						})
						break

						next_index += 1
					
					except ValueError as e:

						try:
							# Handling this case => 'FARE\n$15.10'
							numeric_text = self.drop_alpha_from_text(next_text)
							numeric_text = float(numeric_text)

							is_passed = True
							possible_results.append({
								'value': numeric_text,
								'rank': tags[index][0]
							})
							break

						except ValueError as e:
							next_index += 1	


		# sorting by rank asc, by amt desc 
		possible_results = sorted( possible_results, key=lambda result: (result.get('rank'), -len( str( result.get('value') ) )) )			

		return is_passed, possible_results
		

	def get_receipt_amount(self):
	
		try:
			print('\n', self.RECEIPT_AMOUNT_TAGS)

			success, results = self.is_excat_match_amount()
			
			if success:
				return results

			return list()	

		except Exception as e:
			raise e	



class InformationRetrieval:


	def __init__(self, corpus):
		self.CORPUS = corpus.split('\n')


	def get_receipt_contents(self):
		try:
			receipt_no_data = ReceiptNumber(self.CORPUS).get_receipt_no()
			receipt_amt_data = ReceiptAmount(self.CORPUS).get_receipt_amount()

			return {
				'receipt_no': receipt_no_data,
				'receipt_amt': receipt_amt_data
			}

		except Exception as e:
			print('Some error while performing information retrieval: ', e)
			return {}
		



class InformationRetrievalTests:


	def perform_tests():

		try:
			test_data = [
				'CITYCAB PTE LTD\nSHC72925\nTRIP NO\n101120291\nSTART 11/10/2018 20:29\nEND 11/10/2018 20:49\nDISTANCE RUN 13.80 KM\nMETER FARE $\nCITY AREA SUR $\nPEAK HOUR 25% $\nTOTAL FARE $\n12.70\n3.00\n3.20\n18.90\nAMOUNT PAID\n$\n18.90\n',
				
				'00 Put ull 73%\n16:28\n+\nDriver on the way\nLim Choo Tong\nSLG67947 • Toyota Prius\nGrabShare\nFare: SGD 4.5\nVISA\nTag this trip as\nPersonal\nPromo\nTAKE5\n• 37 Jln Sempadan\nTerminal 2, Changi Airport\nCANCEL BOOKING\n',
				
				'SHIRT\nDAILINING\nDIAL-A-CAB\nTEL: 0555 8883\nart\nMonth\nwww\nSHB408C\nRECEIPT N. 6384\nFRM 02/10/19 22:38\nTO 02/10/18 22:54\nKM RUN\n8.6\nFARE\n9.40\nom\nAIRPORT\nPEAK 25\nTUTAL SS\n14.75\nHAVE A NICE DAY\n',
				
				'COMFORT TRANSPORTATION\nSH 8026G\nTRIP NO 523425914\nSTART 11/01/2018 20:00\nSH\nfaiye\nBA\n.\n1\n.\nha\nust\nFOR\nniverend\n',
				
				'Reg No.20-0304975-11\nTAXI NO.\nSHB85095\nRECEIPT NO. 4610190006\nSTART 19/10/2018 00:06\nEND 19/10/2018 00:15\nDISTANCE RUN\n7.6KM\nMETER FARE\nMIDNIGHT\nCHANGI AIRPORT\n$8.08\n$4.04\n$3.00\nTOTAL\n$1.5.12\nPAIDAMT\n$15.10\nCust Service 6476-3033\n',
				
				'COMFORT TRANSPORTATION\nSHD4062D\nTRIP NO 010408455\nSTART 04/01/2018 08:15\nEND 04/01/2018 09:01\nDISTANCE RUN 11.80 KM\nMETER FARE $\nERP\nPEAK HOUR 25% $\nTOTAL FARE\n10.45\n4.50\n2.60\n17.55\nAMOUNT PAID\n$\n17.55\n',
				
				'CITYCAB PTE LTD\nSHA8520M\nTRIP NO 010511564\nSTART 05/01/2018 11:56\nEND 05/01/2018 12:20\nDISTANCE RUN 2.80 KM\n$\nMETER FARE\nTOTAL FARE\n11.60\n11.60\nAMOUNT PAID\n$\n11.60\n',
				
				'B\nCOMFORT TRANSPORTATION\nSHA7375Y\n12\npl\nTRIP MO\n523369155\nSTART 11/01/2018 09:24\nEND 11/01/2018 09:42\nDISTANCE RUN 12.10 KM\neit.\nFLAT FARE\nTOTAL FARE\n$\n27.50\n27.50\nAMOUNT PAID\n$\n27.50\nCheck your cubpoint at\nhttps://cabrewards.\ncdytaxi com.sg\nhe\nlem\nF\n',
				
				'COMFORT TRANSPORTATION\nSH 8026G\nTRIP NO 523425914\nSTART 11/01/2018 20:00\nSH\nfaiye\nBA\n.\n1\n.\nha\nust\nFOR\nniverend\n',
				
				'@as ull 77%\n07:58\n€\n25 Oct 2017, 09:02AM\nBooking ID:\nADR-0459658-2-1787\nSJN4532\nGoh Guo Quan Edwin\nFare: SGD 7\nVISA\nTag this trip as\nPersonal\nPromo\nTAKE5\nDoor 3, T2 Arrivals, Changi Airport\nVilla Marina\nREPORT AN ISSUE\n',
				
				'CITYCAB PTE LTD\nSHA9200E\nTRIP NO 573116766\nSTART 09/01/2018 09:11\nEND 09/01/2018 09:34\nDISTANCE RUM 9.30 KM\nFLAT FARE\nTOTAL FARE\nAMOUNT PAID\n0\n18.50\n',
				
				'B\nCOMFORT TRANSPORTATION\nSHA7375Y\n12\npl\nTRIP MO\n523369155\nSTART 11/01/2018 09:24\nEND 11/01/2018 09:42\nDISTANCE RUN 12.10 KM\neit.\nFLAT FARE\nTOTAL FARE\n$\n27.50\n27.50\nAMOUNT PAID\n$\n27.50\nCheck your cubpoint at\nhttps://cabrewards.\ncdytaxi com.sg\nhe\nlem\nF\n',
				
				'...l StarHub\n1 18%O\n13:20\n10 Jan 2018, 09:25\nBOOKING ID\nIOS-2595014-3-721\nSLV3422M\nLim Kim Huat Clivee (Lin Jinfa)\nFARE: SGD 25\nVISA\nPromo\nTAKE4\nTag this trip as\nPersonal\n37 Jln Sempadan\nOmron Asia Pacific Pte Ltd - Asia Pacific Regional O...\nYou rated:\nEXCELLENT!\nREPORT AN ISSUE\n'
			]


			for data in test_data:
				print(data.split('\n'))
				contents = InformationRetrieval(data).get_receipt_contents()
				print('\n', contents)
				print('-'*25)

		except Exception as e:
			print('Unable to perform tests:', e)
