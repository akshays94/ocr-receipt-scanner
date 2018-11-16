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
			# print('\n', self.RECEIPT_AMOUNT_TAGS)

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
				# 'CITYCAB PTE LTD\nSHC72925\nTRIP NO\n101120291\nSTART 11/10/2018 20:29\nEND 11/10/2018 20:49\nDISTANCE RUN 13.80 KM\nMETER FARE $\nCITY AREA SUR $\nPEAK HOUR 25% $\nTOTAL FARE $\n12.70\n3.00\n3.20\n18.90\nAMOUNT PAID\n$\n18.90\n',
				
				# '00 Put ull 73%\n16:28\n+\nDriver on the way\nLim Choo Tong\nSLG67947 • Toyota Prius\nGrabShare\nFare: SGD 4.5\nVISA\nTag this trip as\nPersonal\nPromo\nTAKE5\n• 37 Jln Sempadan\nTerminal 2, Changi Airport\nCANCEL BOOKING\n',
				
				# 'SHIRT\nDAILINING\nDIAL-A-CAB\nTEL: 0555 8883\nart\nMonth\nwww\nSHB408C\nRECEIPT N. 6384\nFRM 02/10/19 22:38\nTO 02/10/18 22:54\nKM RUN\n8.6\nFARE\n9.40\nom\nAIRPORT\nPEAK 25\nTUTAL SS\n14.75\nHAVE A NICE DAY\n',
				
				# 'COMFORT TRANSPORTATION\nSH 8026G\nTRIP NO 523425914\nSTART 11/01/2018 20:00\nSH\nfaiye\nBA\n.\n1\n.\nha\nust\nFOR\nniverend\n',
				
				# 'Reg No.20-0304975-11\nTAXI NO.\nSHB85095\nRECEIPT NO. 4610190006\nSTART 19/10/2018 00:06\nEND 19/10/2018 00:15\nDISTANCE RUN\n7.6KM\nMETER FARE\nMIDNIGHT\nCHANGI AIRPORT\n$8.08\n$4.04\n$3.00\nTOTAL\n$1.5.12\nPAIDAMT\n$15.10\nCust Service 6476-3033\n',
				
				# 'COMFORT TRANSPORTATION\nSHD4062D\nTRIP NO 010408455\nSTART 04/01/2018 08:15\nEND 04/01/2018 09:01\nDISTANCE RUN 11.80 KM\nMETER FARE $\nERP\nPEAK HOUR 25% $\nTOTAL FARE\n10.45\n4.50\n2.60\n17.55\nAMOUNT PAID\n$\n17.55\n',
				
				# 'CITYCAB PTE LTD\nSHA8520M\nTRIP NO 010511564\nSTART 05/01/2018 11:56\nEND 05/01/2018 12:20\nDISTANCE RUN 2.80 KM\n$\nMETER FARE\nTOTAL FARE\n11.60\n11.60\nAMOUNT PAID\n$\n11.60\n',
				
				# 'B\nCOMFORT TRANSPORTATION\nSHA7375Y\n12\npl\nTRIP MO\n523369155\nSTART 11/01/2018 09:24\nEND 11/01/2018 09:42\nDISTANCE RUN 12.10 KM\neit.\nFLAT FARE\nTOTAL FARE\n$\n27.50\n27.50\nAMOUNT PAID\n$\n27.50\nCheck your cubpoint at\nhttps://cabrewards.\ncdytaxi com.sg\nhe\nlem\nF\n',
				
				# 'COMFORT TRANSPORTATION\nSH 8026G\nTRIP NO 523425914\nSTART 11/01/2018 20:00\nSH\nfaiye\nBA\n.\n1\n.\nha\nust\nFOR\nniverend\n',
				
				# '@as ull 77%\n07:58\n€\n25 Oct 2017, 09:02AM\nBooking ID:\nADR-0459658-2-1787\nSJN4532\nGoh Guo Quan Edwin\nFare: SGD 7\nVISA\nTag this trip as\nPersonal\nPromo\nTAKE5\nDoor 3, T2 Arrivals, Changi Airport\nVilla Marina\nREPORT AN ISSUE\n',
				
				# 'CITYCAB PTE LTD\nSHA9200E\nTRIP NO 573116766\nSTART 09/01/2018 09:11\nEND 09/01/2018 09:34\nDISTANCE RUM 9.30 KM\nFLAT FARE\nTOTAL FARE\nAMOUNT PAID\n0\n18.50\n',
				
				# 'B\nCOMFORT TRANSPORTATION\nSHA7375Y\n12\npl\nTRIP MO\n523369155\nSTART 11/01/2018 09:24\nEND 11/01/2018 09:42\nDISTANCE RUN 12.10 KM\neit.\nFLAT FARE\nTOTAL FARE\n$\n27.50\n27.50\nAMOUNT PAID\n$\n27.50\nCheck your cubpoint at\nhttps://cabrewards.\ncdytaxi com.sg\nhe\nlem\nF\n',
				
				# '...l StarHub\n1 18%O\n13:20\n10 Jan 2018, 09:25\nBOOKING ID\nIOS-2595014-3-721\nSLV3422M\nLim Kim Huat Clivee (Lin Jinfa)\nFARE: SGD 25\nVISA\nPromo\nTAKE4\nTag this trip as\nPersonal\n37 Jln Sempadan\nOmron Asia Pacific Pte Ltd - Asia Pacific Regional O...\nYou rated:\nEXCELLENT!\nREPORT AN ISSUE\n',

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







			]


			for data in test_data:
				print(data.split('\n'))
				contents = InformationRetrieval(data).get_receipt_contents()
				print('\n', contents)
				print('-'*25)

		except Exception as e:
			print('Unable to perform tests:', e)
