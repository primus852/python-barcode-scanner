import cv2
from PIL import Image
import zbar
import pprint
import beep as b
import requests
import csv
import keyboard
import sqlite3
import os

if __name__ == "__main__":

    # Debug
    pp = pprint.PrettyPrinter(indent=4)

    # Create a SQLite Database
    location = "data.db"
    table = "movies"

    # Connect to DB
    conn = sqlite3.connect(location)
    c = conn.cursor()

    # Create Table
    sql = 'create table if not exists ' + table + ' (ean NUMERIC PRIMARY KEY ASC, title TEXT, price NUMERIC)'
    c.execute(sql)
    conn.commit()

    # Select CaptureDevice (0 first, 1 second,...)
    cap = cv2.VideoCapture(0)

    # Set Camera Width
    cap.set(3, 1280)

    # Set Camer Height
    cap.set(4, 720)

    # Init Scan Images
    scanner = zbar.ImageScanner()
    old = None
    new = None

    # Set Font for CV Output
    font = cv2.FONT_HERSHEY_PLAIN

    # Init Vars
    found = False
    title = ''
    settings = 'Press \'s\' for Settings, \'c\' to create a csv from DB, \'w\' to wipe the db and \'q\' to quit'
    mlist = []

    while True:

        # Capture frame-by-frame
        ret, frame = cap.read()

        # Our operations on the frame come here
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        pil = Image.fromarray(gray)
        width, height = pil.size
        raw = pil.tobytes()

        # Settings menu Text
        cv2.putText(gray, settings, (20, 20), font, 1, (255, 255, 255), 1, cv2.LINE_AA)

        # Print Text to Frame if found/not found
        if found:
            cv2.putText(gray, title, (20, 700), font, 3, (255, 255, 255), 1, cv2.LINE_AA)

        # create a reader
        image = zbar.Image(width, height, 'Y800', raw)
        scanner.scan(image)

        # extract results
        for symbol in image:

            # do something useful with results
            new = symbol.data
            if new != old:

                # Toggle vars
                found = True
                old = new

                # Debug
                print 'decoded', symbol.type, 'symbol', '"%s"' % symbol.data

                # Spawn Thread For Beep
                beep = b.MakeBeep('default')
                beep.start()

                url = "https://api.barcodable.com/api/v1/ean/" + symbol.data
                r = requests.get(url)
                j = r.json()
                if j['status'] == 200:
                    if 'item' in j:
                        if 'matched_items' in j['item']:
                            if j['item']['matched_items']:
                                if 'title' in j['item']['matched_items'][0]:

                                    # Check if it exists in DB
                                    c.execute('select * from ' + table + ' where ean=\'' + j['item']['ean'] + '\'')
                                    rows = c.fetchone()

                                    if rows is not None:

                                        # Debug
                                        print ('EAN in DB')

                                        title = 'EAN already in DB'

                                        # Spawn Thread
                                        beep = b.MakeBeep('duplicate')
                                        beep.start()

                                    else:

                                        # Debug
                                        print ('EAN new')

                                        title = j['item']['matched_items'][0]['title'].replace('[Import allemand]', '')
                                        price = 0
                                        if 'used_price' in j['item']['matched_items'][0]:
                                            price = j['item']['matched_items'][0]['used_price']

                                        # Insert into DB
                                        c.execute('insert into ' + table + '(ean, title, price) values(?,?,?)',
                                                  (symbol.data, title, price))
                                        conn.commit()

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

                # Debug
                print "Result: " + title

        # Display the resulting frame
        cv2.imshow("BarCodeScanner", gray)

        # Write to csv on 'c'
        if cv2.waitKey(1) & keyboard.is_pressed('c'):

            # Check if it exists in DB
            c.execute('select * from ' + table)
            rows = c.fetchall()

            with open('movies.csv', 'wb') as movies:
                wr = csv.writer(movies, quoting=csv.QUOTE_ALL)
                for row in rows:

                    # Debug
                    print ('Writing line...')
                    wr.writerow(row)

            os.startfile('movies.csv')

        # Open Camera Settings on 's'
        if cv2.waitKey(1) & keyboard.is_pressed('s'):
            cap.set(37, 0)

        # Wipe db on 'w'
        if cv2.waitKey(1) & keyboard.is_pressed('w'):
            c.execute('delete from ' + table)

        # Exit on 'q'
        if cv2.waitKey(1) & keyboard.is_pressed('q'):
            break

    # When everything done, release the capture
    cap.release()

    # Close DB
    conn.close()

    # Close all
    cv2.destroyAllWindows()
