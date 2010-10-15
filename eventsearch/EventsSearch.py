#Zach Rowe, Phil Sarid, Dan Souza
#FA2010
#Event Search

import abc
from SearchBase import SearchBase
from xgoogle.search import SearchResult
from RSS import ns, CollectionChannel, TrackingChannel

import time
import datetime

class EventsSearch(SearchBase):
    results = None
    domains = []
    locations = []
    query = None
    eventdate = datetime.date.today()
    rpp = 50
    DATE_HEURISTIC = 3
    DOMAIN_HEURISTIC = 1
    LOCATION_HEURISTIC = 4
    TITLE_HEURISTIC = 3
    DESC_HEURISTIC = .1

    months = {1:["January","Jan"],2:["February","February"],3:["March","Mar"],4:["April","Apr"],5:["May"],6:["June","Jun"],7:["July","Jul"],8:["August","Aug"],9:["September","Sep"],10:["October","Oct"],11:["November","Nov"],12:["December","Dec"]}
    def search(self, query, rpp):
        self.results = super(EventsSearch, self).search(query, rpp)
	self.query = query
	self.rpp = rpp
	self.reorder()
	self.printResults()

    #print results
    def printResults(self):
	total = 0
	for res in self.results:
		print res.title.encode("utf-8")
		print res.desc.encode("utf-8")
		print res.url.encode("utf-8")
		print
		total += 1
		if(total > self.rpp):
			return

    #Creates a URL for an RSS feed from the span of dates
    #Currently filters College Fairs
    def createURL(self, start, end):
	if(start.day < 10):
		startday = "0" + str(start.day)
	else:
		startday = str(start.day)
	if(start.month < 10):
		startmonth = "0" + str(start.month)
	else:
		startmonth = str(start.month)
	if(end.day < 10):
		endday = "0" + str(end.day)
	else:
		endday = str(end.day)
	if(end.month < 10):
		endmonth = "0" + str(end.month)
	else:
		endmonth = str(end.month)
	url = "http://events.rpi.edu/webcache/v1.0/rssRange/"+ str(start.year) + startmonth + startday +"/"+ str(end.year) + endmonth + endday+"/list-rss/(catuid!%3D'00f18254-27ff9c18-0127-ff9c19ce-00000020').rss"#no--filter.rss"
	return url

    #Add RSS results to the google results
    def addRSS(self):
	#Indexes RSS data by item URL
	tc = TrackingChannel()
	StartDate = self.eventdate - datetime.timedelta(days=3)
	EndDate = self.eventdate + datetime.timedelta(days=7)
	
	#Returns the RSSParser instance used, which can usually be ignored
	tc.parse(self.createURL(StartDate,EndDate))

	RSS10_TITLE = (ns.rss10, 'title')
	RSS10_DESC = (ns.rss10, 'description')

	#You can also use tc.keys()
	items = tc.listItems()
	for item in items:
	    #Each item is a (url, order_index) tuple
	    url = item[0]
	    #Get all the data for the item as a Python dictionary
	    item_data = tc.getItem(item)
	    title = item_data.get(RSS10_TITLE, "(none)")
	    desc = item_data.get(RSS10_DESC, "(none)").replace("<br/>","").replace("\n","").replace("\r","").replace("  "," ")
	    for q in self.query.split():
		if(title.lower().find(q.lower()) >= 0 or desc.lower().find(q.lower())):
			if(len(self.results) <= self.rpp):
				self.results.append(SearchResult(title.decode("utf-8"), url.decode("utf-8"), desc.decode("utf-8")))
				break

    #Sets eventdate
    #Determine if a month or year is present within the query
    #Otherwise, use today's date as a metric
    def initEventDate(self):
	for i in xrange(1,len(self.months) + 1):
		for month in self.months[i]:
			if self.query.find(month) >= 0:
				self.eventdate = datetime.date(self.eventdate.year,i,self.eventdate.day)
				self.query = self.query.replace(month,"")
	for year in xrange(1990, self.eventdate.year + 2):
		if self.query.find(str(year)) >= 0:
			self.eventdate = datetime.date(year,self.eventdate.month,self.eventdate.day)
			self.query = self.query.replace(str(year),"")

    #Create a list of campus locations
    def initLocations(self):
	#one location per line
	location_file = open("locations.txt",'r')
	for line in location_file:
		self.locations.append(line.strip('\r\n'))

    #Adds a value between 0-1 if a campus location is in the result description
    def addLocationValue(self, res):
	for location in self.locations:
		if res.desc.find(location) >= 0:
			if self.query.find(location) >= 0:
				return 1
			else:
				return 0
			
	return 0

    #Initialize the Whitelisted Domains List
    def initDomains(self):
	domain_file = open("domains.txt",'r')
	for line in domain_file:
		for domain in line.split():
			self.domains.append(domain)

    #Returns 1 if a whitelisted domain is present in the result url
    #Otherwise returns 0
    def addDomainValue(self, res):
	for domain in self.domains:
		if res.url.find(domain) >= 0:
			return 1
	return 0

    #Returns a value between 0-1
    #based on the difference between month and year of eventdate 
    #and the first date found within the result description
    def addDateValue(self,res):
	yearscale = 1
	for year in xrange(1990, self.eventdate.year + 1):
		if res.title.find(str(year)) >= 0 or res.desc.find(str(year)) >= 0:
			if self.eventdate.year == year:
				yearscale = 1.0
				continue
			else:
				yearscale = 1.0/abs(year - self.eventdate.year)
				continue
	for i in xrange(1,len(self.months) + 1):
		for month in self.months[i]:
			if res.title.find(month) >= 0 or res.desc.find(month) >= 0:
				#print (12.0 - abs(i - self.eventdate.month)) / 12
				return ((12.0 - abs(i - self.eventdate.month)) / 12) * yearscale
	return 0
    #returns a value between 0-1 depending on how many of the
    #words in the search query are present in the title
    def addTitleValue(self,res):
	found = 0.0
	for term in self.query.split():
		if res.title.find(term) >= 0:
			found +=1
	if len(self.query.split()) > 0:
		return found / len(self.query.split())
	else:
		return 0

    #returns a value between 0-1 depending on how many of the
    #words in the search query are present in the description
    def addDescriptionValue(self,res):
	found = 0.0
	for term in self.query.split():
		if res.title.find(term) >= 0:
			found +=1
	if len(self.query.split()) > 0:
		return found / len(self.query.split())
	else:
		return 0

    #Reorders the search results
    def reorder(self):
	#Initialize Domain, Location lists
	self.initDomains()
	self.initLocations()
	#Determine event date range
	self.initEventDate()
	#Add results from events.rpi.edu RSS Feed
	self.addRSS()
        value = 0
        orders = []
        pair = ()
        
        #search titles and descriptions for keywords
        for res in self.results:
	    #add to rank if URL contains whitelisted domain
	    value += (self.addDomainValue(res) * self.DOMAIN_HEURISTIC)
	    #add to rank if the query location or a campus location is in the description
	    value += (self.addLocationValue(res) * self.LOCATION_HEURISTIC)
	    #determine the month/date distance to the eventdate
	    value += (self.addDateValue(res) * self.DATE_HEURISTIC)
	    value += (self.addTitleValue(res) * self.TITLE_HEURISTIC)
	    value += (self.addDescriptionValue(res) * self.DESC_HEURISTIC)
            pair = res, value
            orders.append(pair)
            pair = ()
            value = 0
	    
        #order results based on values
        def cmpfun(a,b):
            return cmp(b[1],a[1])
        orders.sort(cmpfun)
	self.results = []
	for i in orders:
		self.results.append(i[0])
