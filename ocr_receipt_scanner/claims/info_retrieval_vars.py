

TRIP_TAGS_META = [
	{ 
		'rank': 1,  
		'name': 'trip no',
		'alternatives': {
			'trip': ['trp', 'tp', 't'],
			'no': ['n']
		}
	},
	{ 
		'rank': 1,  
		'name': 'receipt no',
		'alternatives': {
			'receipt': ['rcpt', 'rpt', 'rct', 'rc', 'r'],
			'no': ['n']
		}
	},
	{ 
		'rank': 1,  
		'name': 'trip',
		'alternatives': {
			'trip': ['trp', 'tp']
		}
	},
	{ 
		'rank': 1,  
		'name': 'receipt',
		'alternatives': {
			'receipt': ['rcpt', 'rpt', 'rct', 'rc', 'r']
		}
	}
]

def foo():
	try:

		TRIP_TAGS = list()
		for meta_data in TRIP_TAGS_META:
			TRIP_TAGS.append( (meta_data['rank'], meta_data['name']) )
			
			main_tag_name = meta_data['name']

			for text, alternatives in meta_data['alternatives'].items():
				print(text, alternatives)
				for alternative in alternatives:
					new_tag_name = main_tag_name.replace(text, alternative)
					TRIP_TAGS.append( (meta_data['rank'], new_tag_name) )

		print(TRIP_TAGS)			

	except Exception as e:
		print(e)


# AMOUNT_TAGS = [
# 	(1, 'paid'),
# 	(1, 'amount paid'),
# 	(1, 'total paid'),
# 	(2, 'fare'),
# 	(2, 'total fare'),
# 	(2, 'paid fare'),
# 	(2, 'amount fare'),
# 	(2, 'amt fare'),
# 	(2, 'fare')
# ]