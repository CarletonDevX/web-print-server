import pickle, requests, re, datetime

printerPages = {}
session = requests.session()
endpoint = 'https://print.ads.carleton.edu:9192/app'

loginInfo = {
    'service': 'direct/1/Home/$Form$0',
    'sp': 'S0',
    'Form0': '$Hidden$0,$Hidden$1,inputUsername,inputPassword,$PropertySelection$0,$Submit$0',
    '$Hidden$0': 'true',
    '$Hidden$1': 'X',
    '$PropertySelection$0': 'en',
    '$Submit$0': 'Log in'
  }

def login(u, p):
	
	loginInfo['inputUsername'] = u
	loginInfo['inputPassword'] = p
	session.get(endpoint)
	session.post(endpoint, loginInfo)

def navigateToPage():
	print "navigating to page"
	session.get(endpoint + '?service=page/UserWebPrint')
	session.get(endpoint + '?service=action/1/UserWebPrint/0/$ActionLink')

def storePrinterInfo(attempt):
	if attempt <= 3:
		print "Storing info on page " + str(attempt)
		url = endpoint + '?service=direct/1/UserWebPrintSelectPrinter/table.tablePages.linkPage&sp=AUserWebPrintSelectPrinter%2Ftable.tableView&sp=' + str(attempt)
		response = session.get(url)
		lines = response.text.split('<label')
		regex = '.*value=\"[0-9]+\".*\n(.*).*'
		for line in lines:
			matches = re.findall(regex, line)
			if matches:
				printerPages[str(matches[0])] = attempt

		storePrinterInfo(attempt + 1)


def main():

	printerPages["updated"] = str(datetime.datetime.utcnow())

	with open("creds.txt", "r") as file:
		u, p = file.read().splitlines()
	if not u or not p:
		print "Please include credentials"
		return

	login(u, p)
	navigateToPage()
	storePrinterInfo(1)
	pickle.dump(printerPages, open("/var/www/web-print-server/web-print-server/printerPages.p", "wb"))

if __name__ == '__main__':
	main()
