import threading
import beep as b
import requests
import pprint
import csv


class GetJson(threading.Thread):

    def __init__(self, ean):
        threading.Thread.__init__(self)
        self.ean = ean

    def run(self):

        # Debug
        pp = pprint.PrettyPrinter(indent=4)

        # Title var
        title = None

        url = "https://api.barcodable.com/api/v1/ean/" + self.ean
        r = requests.get(url)
        j = r.json()
        if j['status'] == 200:
            if 'item' in j:
                if 'matched_items' in j['item']:
                    if j['item']['matched_items']:
                        if 'title' in j['item']['matched_items'][0]:
                            title = j['item']['matched_items'][0]['title'].replace('[Import allemand]', '')
                            price = 0
                            if 'used_price' in j['item']['matched_items'][0]:
                                price = j['item']['matched_items'][0]['used_price']
                            mlist = [title, price, self.ean]

                            with open('filme.csv', 'ab') as movies:
                                wr = csv.writer(movies, quoting=csv.QUOTE_ALL)
                                wr.writerow(mlist)

                            # Spawn Thread
                            beep = b.MakeBeep('success')
                            beep.start()

                        else:
                            pp.pprint(j)
                    else:
                        title = 'Not found'

                        # Spawn Thread For Beep
                        beep = b.MakeBeep('fail')
                        beep.start()
                else:
                    pp.pprint(j)
            else:
                pp.pprint(j)
        else:
            pp.pprint(j)

        print "Result: " + title
