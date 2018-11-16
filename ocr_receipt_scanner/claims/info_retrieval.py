from ocr_receipt_scanner.claims.info_retrieval_vars import *

def get_trip_no():
	try:
		pass
	except Exception as e:
		raise e

def get_receipt_date():
	try:
		pass
	except Exception as e:
		raise e

def get_receipt_amount():
	try:
		pass
	except Exception as e:
		raise e


def get_receipt_contents():
	try:
		# find text for trip no

		# find text for receipt date
		
		# find text for receipt amount
		pass
	except Exception as e:
		print('Some error while performing information retrieval', e)
		return {}
	

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
			print('-'*25)
			print(data.split('\n'))

	except Exception as e:
		print('Unable to perform tests:', e)
