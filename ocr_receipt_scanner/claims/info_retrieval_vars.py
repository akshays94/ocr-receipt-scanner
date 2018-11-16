
no__alternatives = ['n', 'n.', 'no.', 'number', 'nmbr', '#', 'm', 'mo.', 'mo', 'id']

no__paid__alternatives = ['n', 'n.', 'no.', 'number', 'nmbr', '#', 'm', 'mo.', 'mo', 'id', 'paid']

RECEIPT_NO_TAGS_META = [
	{ 
		'rank': 1,  
		'name': 'trip no',
		'alternatives': {
			'trip': ['trp', 'tp', 't'],
			'no': no__alternatives
		}
	},
	{ 
		'rank': 1,  
		'name': 'receipt no',
		'alternatives': {
			'receipt': ['rcpt', 'rpt', 'rct', 'rc', 'r'],
			'no': no__alternatives
		}
	},
	{ 
		'rank': 1,  
		'name': 'transaction no',
		'alternatives': {
			'transaction': [],
			'no': no__alternatives
		}
	},
	{ 
		'rank': 1,  
		'name': 'bill no',
		'alternatives': {
			'bill': [],
			'no': no__alternatives
		}
	},
	{ 
		'rank': 1,  
		'name': 'invoice no',
		'alternatives': {
			'invoice': ['inv'],
			'no': no__alternatives
		}
	},
	{ 
		'rank': 1,  
		'name': 'booking no',
		'alternatives': {
			'booking': [],
			'no': no__alternatives
		}
	},
	{ 
		'rank': 1,  
		'name': 'receipt',
		'alternatives': {
			'receipt': ['rcpt', 'rpt', 'rct', 'rc', 'rcpt#', 'rpt#', 'rct#', 'rc#']
		}
	},
	{ 
		'rank': 1,  
		'name': 'booking',
		'alternatives': {
			'booking': []
		}
	},
	{ 
		'rank': 1,  
		'name': 'check',
		'alternatives': {
			'check': ['chk']
		}
	},
	{ 
		'rank': 1,  
		'name': 'slip no',
		'alternatives': {
			'slip': [],
			'no': no__alternatives
		}
	},
	{ 
		'rank': 1,  
		'name': 'slip',
		'alternatives': {
			'slip': []
		}
	},
	{ 
		'rank': 1,  
		'name': 'bill',
		'alternatives': {
			'bill': []
		}
	},
	{ 
		'rank': 1,  
		'name': 'invoice',
		'alternatives': {
			'invoice': []
		}
	}
]


RECEIPT_AMOUNT_TAGS_META = [
	{
		'rank': 1,
		'name': 'amount no',
		'alternatives': {
			'amount': ['amt'],
			'no': no__paid__alternatives
		}
	},
	{
		'rank': 1,
		'name': 'amount',
		'alternatives': {
			'amount': ['amt']
		}
	},
	{
		'rank': 1,
		'name': 'total amount',
		'alternatives': {
			'total': ['tot', 'paid', 'fare', 'tutal'],
			'amount': ['amt']
		}
	},
	{
		'rank': 2,
		'name': 'fare',
		'alternatives': {
			'fare': []
		}
	},
	{
		'rank': 2,
		'name': 'fare amount',
		'alternatives': {
			'fare': [],
			'amount': no__paid__alternatives
		}
	},
	{
		'rank': 1,
		'name': 'total',
		'alternatives': {
			'total': ['tot', 'tutal', 'totamt', 'tutalamt', 'tutal ss']
		}
	},
	{
		'rank': 1,
		'name': 'paid',
		'alternatives': {
			'paid': ['paidamt']
		}
	},
]

