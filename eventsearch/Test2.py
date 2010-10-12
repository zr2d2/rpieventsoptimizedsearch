#This tests the capability to parse the events.rpi.edu RSS Feed
#Items are seperated by URL, Title, and Description just like
#the google results.

#References
#http://wiki.python.org/moin/RssLibraries
#http://www.ibm.com/developerworks/webservices/library/ws-pyth11.html

from RSS import ns, CollectionChannel, TrackingChannel

#Create a tracking channel, which is a data structure that
#Indexes RSS data by item URL
tc = TrackingChannel()

#Returns the RSSParser instance used, which can usually be ignored
tc.parse("http://events.rpi.edu/webcache/v1.0/rssRange/20101001/20101031/list-rss/no--filter.rss")

RSS10_TITLE = (ns.rss10, 'title')
RSS10_DESC = (ns.rss10, 'description')

#You can also use tc.keys()
items = tc.listItems()
for item in items:
    #Each item is a (url, order_index) tuple
    url = item[0]
    print "URL:", url
    #Get all the data for the item as a Python dictionary
    item_data = tc.getItem(item)
    print "Title:", item_data.get(RSS10_TITLE, "(none)")
    print "Description:", item_data.get(RSS10_DESC, "(none)")
