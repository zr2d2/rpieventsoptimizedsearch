#Zach Rowe, Dan Souza, Phil Sarid
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
    keywords = {}
    domains = []
    locations = []
    query = None
    eventdate = datetime.date.today()

    DATE_HEURISTIC = 5
    DOMAIN_HEURISTIC = 1
    LOCATION_HEURISTIC = 2

    months = {1:["January","Jan"],2:["February","February"],3:["March","Mar"],4:["April","Apr"],5:["May"],6:["June","Jun"],7:["July","Jul"],8:["August","Aug"],9:["September","Sep"],10:["October","Oct"],11:["November","Nov"],12:["December","Dec"]}
    def search(self, query, rpp):
        self.results = super(EventsSearch, self).search(query, rpp)
        #self.printResults()
	self.query = query
    def printResults(self):
        for res in self.results:
            print res.title#.encode("utf8")
            print res.desc#.encode("utf8")
            print res.url#.encode("utf8")
            print
    #Creates a URL for an RSS feed from the span of dates
    #Currently filters College Fairs
    def createURL(self, start, end):
	url = "http://events.rpi.edu/webcache/v1.0/rssRange/"+ str(start.year) + str(start.month)+ str(start.day)+"/"+ str(end.year)+str(end.month)+ str(end.day)+"/list-rss/(catuid!%3D'00f18254-27ff9c18-0127-ff9c19ce-00000020').rss"#no--filter.rss"
	#print url
	return url
    def addRSS(self):
	#Indexes RSS data by item URL
	tc = TrackingChannel()
	StartDate = self.eventdate - datetime.timedelta(days=3)
	EndDate = self.eventdate + datetime.timedelta(days=5)
	
	#Returns the RSSParser instance used, which can usually be ignored
	tc.parse(self.createURL(StartDate,EndDate))

	RSS10_TITLE = (ns.rss10, 'title')
	RSS10_DESC = (ns.rss10, 'description')

	#You can also use tc.keys()
	items = tc.listItems()
	for item in items:
	    #Each item is a (url, order_index) tuple
	    url = item[0]
	    #print "URL:", url
	    #Get all the data for the item as a Python dictionary
	    item_data = tc.getItem(item)
	    title = item_data.get(RSS10_TITLE, "(none)")
	    desc = item_data.get(RSS10_DESC, "(none)").replace("<br/>","").replace("\n","").replace("\r","").replace("  "," ")
	    #print "Title:", item_data.get(RSS10_TITLE, "(none)")
	    #print "Description:", item_data.get(RSS10_DESC, "(none)")
	    for q in self.query.split():
		if(title.lower().find(q.lower()) >= 0):# or desc.lower().find(q.lower())):
			self.results.append(SearchResult(title, url, desc))
			#print q
			break

    def initLocations(self):
	#one location per line
	location_file = open("locations.txt",'r')
	for line in location_file:
		self.locations.append(line.strip('\r\n'))

    def addLocationValue(self, res):
	for location in self.locations:
		if self.query.find(location) >= 0:
			return 2
		if res.desc.find(location) >= 0:
			return 1
	return 0

    def initDomains(self):
	domain_file = open("domains.txt",'r')
	for line in domain_file:
		for domain in line.split():
			self.domains.append(domain)

    def addDomainValue(self, res):
	for domain in self.domains:
		if res.url.find(domain) >= 0:
			return 1
	return 0
    def addDateValue(self,res):
	yearscale = 1
	for year in xrange(1990, self.eventdate.year + 1):
		if res.title.find(str(year)) >= 0 or res.desc.find(str(year)) >= 0:
			if self.eventdate.year == year:
				yearscale = 1.0
				continue
			else:
				yearscale = 1.0/abs(year - self.eventdate.year)
	for i in xrange(1,len(self.months)):
		for month in self.months[i]:
			if res.title.find(month) >= 0 or res.desc.find(month) >= 0:
				#print (12.0 - abs(i - self.eventdate.month)) / 12
				return (12.0 - abs(i - self.eventdate.month)) / 12
	return 0
    def initDictionary(self):
        key_file = open("keywords.txt",'r')
        count = 1
        for line in key_file:
            for word in line.split():
                self.keywords[word]=count
                count = count+1

    def reorder(self):
        self.initDictionary()
	self.initDomains()
	self.initLocations()
	self.addRSS()
        value = 0
        orders = []
        pair = ()
        
        #search titles and descriptions for keywords
	#this doesn't work, needs to be fixed or removed
        for res in self.results:
	    value += (self.addDomainValue(res) * self.DOMAIN_HEURISTIC)
	    value += (self.addLocationValue(res) * self.LOCATION_HEURISTIC)
	    value += (self.addDateValue(res) * self.DATE_HEURISTIC)
            pair = res, value
            orders.append(pair)
            pair = ()
            value = 0

        #order results based on values
        def cmpfun(a,b):
            return cmp(b[1],a[1])
        orders.sort(cmpfun)

        for i in orders:
            print i[0].title, "RANK = ", i[1]
            print i[0].desc
	    print i[0].url
            print

        

