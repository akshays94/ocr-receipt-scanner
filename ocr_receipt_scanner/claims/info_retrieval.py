import re
import itertools

from dateparser.search import search_dates
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
		try:
			return list(map(lambda text: ' '.join(text.split()), corpus))	
		except Exception as e:
			print('Error while removing extra spaces:', e)
			raise e


	def is_excat_match(self, corpus, tags):
		
		try:			
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
		except Exception as e:
			print('Error in is_excat_match:', e)
			raise e


	def is_excat_match_with_some_extra_text_with_spaces(self, corpus, tags):
			
		try:
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

		except Exception as e:
			print('Error in is_excat_match_with_some_extra_text_with_spaces:', e)
			raise e


	def is_contains_alpha_and_num(self, unpacked_corpus):
	
		try:
			
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

		except Exception as e:
			print('Error in is_contains_alpha_and_num:', e)
			raise e


	def is_large_number(self, unpacked_corpus):
	
		try:
			
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

		except Exception as e:
			print('error in is_large_number', e)
			raise e


	def drop_alpha_from_text(self, text):
	
		try:
			
			text_chars = list(text)
			only_numbers = list(filter(lambda char: char == '.' or char.isdigit(), text_chars))
			return ''.join(only_numbers)

		except Exception as e:
			print('Error in drop_alpha_from_text', e)
			raise e	


	def is_excat_match_with_some_extra_text_without_spaces(self, packed_corpus, unpacked_corpus, tags):
		try:
			
			is_passed = False
			possible_results = list()

			tag_names = list(map(lambda tag: tag[1], tags))

			# print('unpacked_corpus', unpacked_corpus)

			for text in itertools.chain(unpacked_corpus, packed_corpus):

				for tag_name in tag_names:

					found_start_index = text.lower().find(tag_name)

					# print('ttagf', text, tag_name, found_start_index)

					if not found_start_index == -1:

						contained_value_start_index = found_start_index + len(tag_name)

						contained_value = text[contained_value_start_index:]

						LENGTH_THRESHOLD = 3

						has_minimum_length = len(contained_value) > LENGTH_THRESHOLD

						if has_minimum_length:
							is_passed = True
							possible_results.append({
								'value': contained_value,
								'rank': 1
							})

			possible_results = sorted( possible_results, key=lambda result: (result.get('rank'), len( result.get('value') )) )				

			return is_passed, possible_results

		except Exception as e:
			print('Error in is_excat_match_with_some_extra_text_with_spaces:', e)
			raise e		
			

class ReceiptNumber(InformationRetrievalUtils):


	def __init__(self, corpus):

		try:			
			self.RECEIPT_NO_TAGS = self.make_tags(RECEIPT_NO_TAGS_META)
			self.corpus = self.remove_extra_spaces(corpus)

			# op: [['00', 'Put', 'ull', '73%'],['16:28'],['+'],['Driver', 'on', 'the', 'way'],['Lim', 'Choo', 'Tong'],['SLG67947', '•', 'Toyota', 'Prius']
			split_packed_corpus = list(map(lambda text: text.split(), self.corpus))		
			# op: ['00','Put','ull','73%','16:28','+','Driver','on','the','way','Lim','Choo','Tong','SLG67947']
			self.unpacked_corpus = list(itertools.chain.from_iterable(split_packed_corpus))
		except Exception as e:
			print('Error while creating ReceiptNumber instance', e)
			raise e


	def get_receipt_no(self):
		try:
			# print('\n', self.RECEIPT_NO_TAGS)
			# print('\n', self.corpus)

			success, results = self.is_excat_match(self.corpus, self.RECEIPT_NO_TAGS)
			
			if success:
				return results

			success, with_spaces_results = self.is_excat_match_with_some_extra_text_with_spaces(self.corpus, self.RECEIPT_NO_TAGS)

			success, without_spaces_results= self.is_excat_match_with_some_extra_text_without_spaces(self.corpus, self.unpacked_corpus, self.RECEIPT_NO_TAGS)

			# print('with_spaces_results', with_spaces_results)
			# print('without_spaces_results', without_spaces_results)
		
			with_spaces_results.extend(without_spaces_results)

			if with_spaces_results:
				return with_spaces_results

			# ===============================

			success, alpha_results = self.is_contains_alpha_and_num(self.unpacked_corpus)

			success, num_results = self.is_large_number(self.unpacked_corpus)
			
			alpha_results.extend(num_results)

			if alpha_results:
				return alpha_results

			return list()	

		except Exception as e:
			print('error in get_receipt_no', e)
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
			
		try:
			
			corpus = self.corpus
			tags = self.RECEIPT_AMOUNT_TAGS

			tag_names = list(map(lambda tag: tag[1], tags))

			is_passed = False
			possible_results = list()

			for index, corpus_text in enumerate(corpus):
				
				AMOUNT_THRESHOLD = 1000000 # 1 million

				# if excat match
				if corpus_text.lower() in tag_names:
						
					next_index = index + 1

					# keep finding till you reach a number
					while next_index < len(corpus):
						# Handling this case => 'FARE\n$\n15.10'
						next_text = corpus[next_index]
						try:
							is_zero = len(next_text) == 1 and int(next_text) == 0

							if is_zero:
								next_index += 1
								continue

							next_text = float( ''.join(next_text.split()) )
							
							if next_text < AMOUNT_THRESHOLD:
								is_passed = True
								possible_results.append({
									'value': next_text,
									'rank': tags[index][0]
								})
							# break

							next_index += 1
						
						except ValueError as e:

							try:
								# Handling this case => 'FARE\n$15.10'
								numeric_text = self.drop_alpha_from_text(next_text)
								numeric_text = float(numeric_text)
								
								if numeric_text < AMOUNT_THRESHOLD:
									is_passed = True
									possible_results.append({
										'value': numeric_text,
										'rank': tags[index][0]
									})
									# break

								next_index += 1

							except ValueError as e:
								next_index += 1	


			# sorting by rank asc, by amt desc 
			possible_results = sorted( possible_results, key=lambda result: (result.get('rank'), -result.get('value') ) )			

			return is_passed, possible_results
		except Exception as e:
			print('error in is_excat_match_amount', e)
			raise e

		

	def get_receipt_amount(self):
	
		try:
			# print('\n', self.RECEIPT_AMOUNT_TAGS)

			success, results = self.is_excat_match_amount()
			
			if success:
				return results

			return list()	

		except Exception as e:
			print('error in get_receipt_amount', e)
			raise e	



class InformationRetrieval:


	def __init__(self, corpus):
		self.CORPUS = corpus.split('\n')


	def get_receipt_contents(self):
		try:
			print(self.CORPUS)

			receipt_no_data = ReceiptNumber(self.CORPUS).get_receipt_no()

			receipt_no_data = list(map(lambda item: item.get('value'), receipt_no_data))

			receipt_amt_data = ReceiptAmount(self.CORPUS).get_receipt_amount()

			receipt_amt_data = list(map(lambda item: item.get('value'), receipt_amt_data))

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

				'...l StarHub\n1 18%O\n13:20\n10 Jan 2018, 09:25\nBOOKING ID\nIOS-2595014-3-721\nSLV3422M\nLim Kim Huat Clivee (Lin Jinfa)\nFARE: SGD 25\nVISA\nPromo\nTAKE4\nTag this trip as\nPersonal\n37 Jln Sempadan\nOmron Asia Pacific Pte Ltd - Asia Pacific Regional O...\nYou rated:\nEXCELLENT!\nREPORT AN ISSUE\n',

				# go1
				'Catalunya\nCatalunya Pte Ltd\n82 Colyer Quay,\nSingapore 049327\nReg/Gst Number: 201128706C\nSlip : 0000000T02000001977\nStaff : Pol\nTrans: 10106637\nDate : 11/05/12 9:05:39 PM\nTable:\n10\n** COPY **\nDescription\nAmount\nPANNA BOTTLE\nSCRAMBLED EGGS CHORI SER\nBIKINI SERVING\nSUCKLING PIG (TAPA) SERV\nTASMANIAN TXULETA (2 SER\nMASHED POTATO SERVING\nAUBERGINES SERVING\nPASIANS FAVOURITE 40 ML\nSTELLA ARTOIS BOTTLE\nWARM ALMOND TART SERVING\nTORRIJA SERVING\n9.00\n16.00\n18.00\n18.00\n100.00\n10.00\n12.00\n21.00\n18.00\n12.00\n12.00\n246.00\nSubtotal\nServices Charge\nGST\n24.60\n18.94\nTotal SGD\nVisa\n289.54\n-289.54\n',

				'1\nres\nBak\nwww.drips.com.sg\nTiong Bahru Estate\n82 Tiong Poh Road #01-05\nSingapore 160082\nTel: 6222 0400\nRCT# 4452\nTERMINAL# 1\nONLINE\n20/08/12(MON) 12:46\nSTAFF: Alfred\nLatte\n$9.60\n&gt; SKINNY.B2\nBlackberry Almond lart\n1 $7.50\nCrumbly Apple Crumble Tail\n$7.50\nDessert Of The Day\n$7.80\n| &gt; CHO PORT\nCinnamon Pear Tarl\n$7.50\nSUB TOTAL\n$39.90\n$39.90\nTOTAL(5 Qty)\nVISA\nTOTAL TENDERED\nCHANGE\nHave a nice day\nThank you\nSee you soon\n$39.90\n$0.00\n',

				'SHOTS\nESPRESSO BAR\nwww. shots, con se\nJABLZ0B2CHE\nPax: 1\nOP:Cashier 1\nPOS Title POS001\nCashier 1\nPUS: POS001\nRept# 11000035434 31/12/2011 22:12\n1 Cafe Mocha\n1 Cold Cafe Mocha\n$5.80\n$6.20\nSUBTOTAL\n$12.00\nInc. 7% GST\n$0.79\nTOTAL\n$12.00\nCASH\n$50.00\nChange\n$38.00\nClosed Bill\n- 31/12/2011 22:13---\n8 Ann Siang Hill\nS(069788)\nTel: 52248502\nemail: infushots.com.sg\n*XXXXXXXXXXX\nThank You\nPlease Come Again\n',

				'COOK BOOK ASIA\nGST No: 200910135R\nChangi Business Park Ave 1\nLevel 1. Unit: #01-24 Bussiness Park1\nUE BizHub EAST 468017\nPH: 65427057\n10 COUNTER1\n1021 CASHIER\nPrint Cnt: 1\n1021 CASHIER\nCover:0\nCheck: 12693\n05 Dec 12 12:04:06\nTAG:15 / 1\n1 Curry Chicken Rice\n1 Ice Lemon Tea\n1 Signature Laksa\n1 Mineral Water\n5.90\n1.90\n5.90\n1.90\nSub Total:\n15.60\nTotal:\n15.60\nPay:\n20.00\nCASH\n20.00\nChange Due:\n4.40\nGST Inc\n1.02\n--1021 CLOSED 05 Dec 12 12:04:41---\nThank You For Coming !\nSee You Soon!\n',

				'SANYS CURRY RESTAURANT PTE LTD\nBLK 25 DEMPSEY ROAD S249670 TEL:64722080\nGST NO: 1996021650\nVisit us www.samycurry.com\nBILL NUMBER: 181368 Date:2015-08-23\nTABLE NUMBER: 10 Time: 11:44.02\nNo.of Pax: 2\nQTY DESCRIPTION PRICE AMOUNT\n1\n1\n4\n1\n3\n2\nCurry Mutton Small\nBlack Squid Small\nFish Cutlet\nTandoori Chicken\nWhite Rice with Veg\nLime Juice BIG\n10.00\n9.00\n2.10\n6.50\n3.00\n3.20\n10.00\n9.00\n8.40\n6.50\n9.00\n6.40\nSUBTOTAL\nGST 7%\nGRAND AMOUNT\n49.30\n3.45\n52.75\nServed By : SURESH\nTime:\n',

				'Secret Recipe\n#03-18 PLAZA SINGAPURA\n68 ORCHARD ROAD SINGAPORE 238839\nTEL: 6341 9909 FAX: 6341 9949\nGST REG NO: 199901752Z\n1971\nINVOICE\nTable #\n11\n11\n11\nGuest\n1 CHOC BANANA (S)\n1 ICED MOCHA\n10%-SR CARD\n2\n5.50\n5.90\n-1.14\n10% SERVICE\n7% GST\n2 Total\nSUBTOTAL\n1.03\n0.79\n12.00\n10.26\nDINERS\n12.00\nSaturday 16- 2-2013 18:00:01\n#265578 L0001 KASIMA\nTHANK YOU\nFOR YOUR VISIT\n',

				'Leron &amp; Heros Rotisserie\n6 Chargi Business Park Ave 1\n#01-34\nSingapore 486017\nPrinted: 2013-02-06 12:04:25\nTerminal: LemonandHerb Clerk: Marilyn\nBill No: 201302050009\n1X Grilled Boneless Chix 10.50\nTX Mineral Water Dasani 2.00\n1x Chicken Schnitzel 12.00\n1X Homenade Iced Leuon T 2.50\n1x Mineral Water Dasant 2.00\n10.50\n2.00\n12.00\n2.50\n2.00\n29.00\nSubtotal:\nTotal:\nCash:\nReceived:\nCHANGE:\n29.00\n100.00\n100.00\n71.00\n',

				'Tax Involce\nTian Tian Hainanese Chicken Rice\nStall No. 10 &amp; 11\nMaxwell Food Centre\nSingapore 069184\nTel: 9691 4852\n26 Jan 2018 11:58:49 AM\nReceipt no:OR18012600010200\nQueue: 0200\nQty\nCashier: ET\n1 Stm CR (L) - Std\n1 Stm CR (M) - Std\nTOTAL\nCASH\n*GST included. So 84\nTotal\n$7.80\n$5.00\n$12.80\n$12.80\nTTCRM (MW) Pte Ltd\nGST no 2009202345R\nThank you. Please come again.\nQueue: 0200\nET\n26/01/2018\n11:58\nQtv\n',

				'SARI RATU\nRestaurant &amp; Catering PTE LTD\n20 Pahang Street\nSingapore 198617\nTel : 62949983 Fax : 62949913\n24/12/2014 18:00 Tm: ToolShift201412241\nTable Svr:Cashier 001\nBill:A076070\n5.00\n1 Alpokat Juice\n1 Ayam Kg. Panggang\n2 WHITE RICE\n1 Telur Dadar\n1 Sambal Grg\n1 Sambal Hij/Merah\n1 Sayur Lodeh\n5.00\n2.00\n2.00\n2.50\n1.50\n2.50\nTOTAL\nVISA\n20.50\n50.50\n7093\n',

				'SETAN\nSINGAPORE\nJURONG EAST\nCO.REG.NO. : 197001177H\nGST REG. NO. : M2-0011480-9\nTEL NO. : 6896-7777\nCOUNTER:6713\n01/05/2015 (Fri) 15:24\n60-SWEETS\nS#7316509\nCHATERAISE\n4.70\nS#7316509\nCHATERAISE\n1.90\nTOTAL\nGST ON GDS\n6.60\n0.43\nVISA\n(************2459.67130198)\n6.60\nRECEIPT:0198/006093CL\nTHANK YOU\n2 ITEMS\nNO I-POINTS ENTITLED FOR\nPURCHASE FROM BAKERY.\nLIQUOR AND CIGARETTES\n'


				# go11

				'COMFORT TRANSPORTATION\nSHC2231B\nTRIP NO\n333470794\nSTART 25/05/2011 23:47\nEND 26/05/2011 00:04\nDISTANCE RUN 17.7 KM\nMETER FARE $\nCURR BOOKING $\nLATE NIGHT 507$\n12.60\n2.50\n1.10\nTOTAL\n$\n16.20\n',

				'TAXI RECEIPT\nНАСК\nMED #\nTRIPS\nDATE:\nSTART TIME\nEND TIME\nRATE NO.\nSTAND.\nMILES R1\nFARE 1\nSURCHARGE\nTOTAL\nTIP/OTHER\nGR. TOTAL\n12345\n8P69\n57896\n11/11/2014\n15:10\n15:30\nCITY RATE\n03\n1.48\n$8.10\n$1.00\n$9.10\n$2.00\n$11.10\nTHANK YOU\n',

				'COMFORT TRANSPORTATION\nSHC19482\nTRIP NO 021600270\nSTART 16/02/2015 00:27\nEND 16/02/2015 00:54\nDISTANCE RUN 18.6 KM\nMETER FARE $\nLATE NIGHT 50%$\nTOTAL FARES\n15.95\n8.00\n23.95\nAMOUNT PAID\n$\n23.95\n',

				'COMFORT TRANSPORTATION\nSHB42141\nTRIP NO 02210106\nSTART 21/02/2014 01:06\nEND 21/02/2014 01:24\nDISTANCE RUN 16.6 KM\nMETER FARE S\nCHANGI AIRPORTS\nLATE NIGHT 507$\nTOTAL FARE $\n13.50\n3.00\n6.75\n23.25\nAMOUNT PAID\n$\n23.25\n',

				'COMFORT TRANSPORTATION\nSHC22502\nTRIT NO\n153074744\nSTART 11/04/2016 08:05\nEND 11/04/2016 08:12\nDISTANCE RUN 2.8 KM\nMETER FARE\nERP\nADU BOOKING\nPEAK HOUR 25%. $\nTOTAL FARE\n4.95\n2.00\n8.00\n1.25\n16.20\nAMOUNT PAID\n$\n15.20\n',

				'COMFORT TRANSPORTATION\nSHA3374B\nTRIP NO 072519151\nSTART 25/07/2016 19:15\nEND 25/07/2016 19:46\nDISTANCE RUN 24,50 KM\nMETER FARE $\nPEAK HOUR 25% $\nTOTAL FARE $\n19.95\n5.00\n24.95\nAMOUNT PAID\n$\n24.95\n',

				'COMFORT TRANSPORTATION\nSH 7919L\nTRIP NO\n032119370\nSTART 21/03/2014 19:37\nEND 21/03/2014 19:49\nDISTANCE RUN 3.4 KM\nMETER FARE\nCITY AREA SUR $\nPTE BOOKING\nPEAK HOUR 25%. $\nTOTAL FARE\n6.70\n3.00\n4.00\n1.70\n15.40\nAMOUNT PAID\n$\n15.40\n',

				'200 Vetore tre 405 Bugis Junction\nSingapore 101021\nTel: 6330135 Fax: 6338 0116\n**Duplicate copy-1**\nReceipt:0014163\nTable No : 16\nSI PANCAKE\nSI PANCAKE\n20.00\n20.00\nSUBTOTAL\nSRVCH 10x\nGST 7%\nRound\nTOTAL\n40.00\n4.00\n3.08\n0.02\n47.10\nVISA S6$\n47.10\nItem Qty:2\nSve Oty:0\nTerm: 1 No:0000043\nCashier:1\nDate: Jul-28-2016 02:58 PM\n',

				'Onion Restaurant &amp; Bar Pte Ltd\nSEASONAL SALAD BAR\n1 Lower Kent Road\n#04-18/19/20 One@kentRidge\nSingapore 119082\nTel: +65 6734 2652\nFax: +65 6734 2671\nUEN/GST : 201131116K\n12/10/2016 12:03 T001\nTable 24\nPax\n201610121\n3 A050810\n1\n1\n(L) TCM Steak w/SSB\nDisc - 100%(ENTERTAINER)\n(L) TCM Steak W/SSB\n(L) PEPPER Sirloin Ste\ncPPCR Sirloin Ste\nSUBTTL\n10% SVC CHG\n7% GST\n19.95\n-19.95\n19.95\n21.95\n41.90\n4.19\n3.23\nTOTAL\n49.32\nSEASONAL SALAD BAR\nPresent your receipt\non your next visit and enjoy\n10% Discount!\n(with minimum spending of $200)\n*Not applicable with any other\nPromotions, Discounts &amp; Vouchers\n*Terms and Conditions Apply\nThank You\nSee You Again!\nCustomer Signature:\n',

				'TRIP NO\nSTART 07/06/2011 00:37\n747216941\nEND 07/06/2011 00:53\nDISTANCE RUN 17.1 KM\nNETS\n111638864000 63886457\nPURCHASE SAU\nDBS BANK\n07 JUN, 2011 00:54:35\nAPPROVAL 595270\nSTAN\n004152\nMETER FARE $\nLATE NIGHT 50%$\nFEE (GST INCL.)$\n12.60\n6.30\n0.30\nTOTAL\n$\n19.20\n',

				'a 18-2006\nas\n2 Shyan\nChk 5546\nJOT16 12:50PM\nFor Here\n1 Latte Eng F-T\nCash\n5.70\n0.37 7% GST\nTotal\nPaynent\nChange Due\n** Thank You +++\n** Plaase Come Again\n+\n+\nPrice payable includes GST.\nGST is not payable for purchase\nor loading of the Starbucks Card\n',

				'Starbucks Coffee\nWELCOME TO STARBUCKS COFFEE\nSTARBUCKS OFFICE CENTRAL WORLD\n(02) 2645076-7\nHAVE A GRANDE DAY\n12 NATKAMOL\nChk 9788 Dec01\'12 04:25PM\n1 TB SS MILLER 16\n1 RED FOX 8 OZ\n1150.00\n1 XMAS GIFTBAG\n380.00\n1 VIA COL 12CT\n0.00\n100 %\n350.00\n1000 FREEVIA\n1 g. I/TOFFEE NUT\n350.00 -\nCup Dis 10B\n155.00\n0001121201162659\n10.00-\nSbux Redeem\n0001121201162713\n500.00\nSbux Redeem\n0001121201162717\n425.00\nSbux Redeem\n500.00\n0001121201162811\nSbux Redeen\n250.00\nTotal\n1675.00\nPayment\n1675.00\n109.58 VAT TTL 1675.00\nNet TTL\n1565.42\nTAX INVOICE (ABB) 121201-02-51440\nTAX# 0105541008688\nPOS#\n-------12 Check Closed--\n----\n-----Dec01\'12 04:28PM---\n',

				'delete\nSTARBUCKS Store #7475\n405 Route 10 East\nEast Hanover, NJ (973) 599-0100\nCHK 657461\n12/17/2014 03:01 PM\n1186448 Drawer: 1 Reg: 2\nTurky Pesto Panini\nTI Pasntgo Icd Tea\nSbux Card\nXXXXXXXXXXXX7801\n5.95\n1.75\n8.24\nSubtotal\nTax 7%\nTotal\nChange Due\n$7.70\n$0.54\n$8.24\n$0.00\nCheck Closed\n',

				'STARBUCKS Store #7222\n330 Madison Ave\nNew York, NY (212) 682-1880\nCHK 716062\n03/28/2018 07:17 AM\n2179818 Drawer: 1 Reg: 1\nVt Latte\nBlueberry Muffin\nMastercard\nXXXXXXXXXXXX1445\n4.75\n2.65\n7.82\nSubtotal\nTax 8.875%\nTotal\nChange Due\n$7.40\n$0.42\n$7.82\n$0.00\n-- Check Closed ---\n03/28/2018 07:17 AM\n',

				'PIZZA HUT\n### ALL PRINTER ###\n10 COUNTER1\n103 TRICA\nTBL\nCust. Count: 1\n----- Take Out\n1 Pnt Reg Shrm Dit\n1 Pnt Reg ved Lur\n-REG ONIONS\nCheck #: 118009\n12 Oct 14 17:47:18\nDue Time 18:01\n',

				'.... Singtel 46\n7:49 AM\n&lt;\n19 Nov 2016, 07:01AM\nBOOKING ID\nIOS-1109625-2-137\nSLF705B\nBurhanuden Bin Razali\nFARE: SGD 12\nCASH\nNotes to driver\nBus interchange side\nTag this trip as\nPersonal\nPunggol MRT/LRT Interchange (NE17/PTC)\n|| Changi Airport Terminal 2\nYou rated:\nVERY BAD\nREPORT AN ISSUE\n',

				'Mastellae\nOST Reno:201504766Z\n36 BEACH ROAD\n#02-02 SIPORE 189756\nTABLE = BARS\nPaxei OP:ANG XIUTING RACHEL\nPOS Title:OrderStation\nPOS:P0501\nRept#:A17000015474 19/07/2017 20:39\n1 Guac n Chips\n$11.00\n1 Fish Tacos (2)\n$12.00\n1 Classic Frozen\n$23.00\nSUBTOTAL\n$46.00\n10% Svr Chrg\n$4.60\n7% GST\n$3.54\nTOTAL\n$54.14\nThank you\nSee you again!\nPresettlement Bill\n19/07/2017 21:20\n',
   	      
				'BLIS\nP UI\nTUUUU\nTel : 65099698 Fax : 65091996\nGST NO.: M2-0117072-9\nTABLE: 4 Check: 134175\nDate : 09 Jul, 13 Time: 12:58\nStaff: Linda Foo Cover: 6\nPrint: 1\n1\n2\n1\nSprite-Can\nDF Seafood Platter\nGrilFishFillet/Fries\nBK Rice/Pork Chop\nSpaghetti/FishFillet\nSpaghetti/Porkchop\nRice/ChknP.Ssg&amp;Mush\nSet Lunch Add $4\n2.60\n31.60\n9.80\n9.80\n10.80\n9.80\n7.80\n4.00\n1\n1\nSubtot\nS.C. (10%)\n86.20\n8.62\nLLA\n'
			]

			print('='*30)
			print('RUNNING TESTS ON {} SAMPLES'.format(len(test_data)))
			print('='*30)

			for data in test_data:
				print(data.split('\n'))
				contents = InformationRetrieval(data).get_receipt_contents()
				print('\n', contents)
				print('-'*25)

			# for data in test_data:
			# 	print('-'*25)
			# 	print(data)
			# 	try:
			# 		result = search_dates(data)
			# 		print(result)
			# 	except Exception as e:
			# 		continue
			# 		print('-'*25)

			# 	print('-'*25)

		except Exception as e:
			print('Unable to perform tests:', e)


#  import datefinder                                                                                                                                 

# In [3]: for data in test_data: 
#    ...:     matches = datefinder.find_dates(data) 
#    ...:     print('_'*25) 
#    ...:     print(data) 
#    ...:     print('_'*25) 
#    ...:     for match in matches: 
#    ...:         print('\t', match) 
#    ...:     print('='*25) 