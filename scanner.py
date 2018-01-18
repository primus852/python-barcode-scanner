import cv2
from PIL import Image
import zbar
import pprint
import beep as b
import api as ac


if __name__ == "__main__":

    # Debug
    pp = pprint.PrettyPrinter(indent=4)

    # Select CaptureDevice (0 first, 1 second,...)
    cap = cv2.VideoCapture(0)

    # Open Camera Settings
    # cap.set(37, 0)

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
    mlist = []

    while True:

        # Capture frame-by-frame
        ret, frame = cap.read()

        # Our operations on the frame come here
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        pil = Image.fromarray(gray)
        width, height = pil.size
        raw = pil.tobytes()

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

                # Spawn Thread for API Call (and wait for it)
                apiCall = ac.GetJson(symbol.data)
                apiCall.start()
                apiCall.join()

        # Display the resulting frame
        cv2.imshow("BarCodeScanner", gray)

        # Close on q
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()

    # Close all
    cv2.destroyAllWindows()
