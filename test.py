# import the necessary packages
import argparse
import datetime
import imutils
import time
import cv2

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
args = vars(ap.parse_args())
tempThrushold = 40
ppmThrushold = 200
currentTemp = 30
currentPpm = 100
start_time = time.clock()
isAlertSent = False

# if the video argument is None, then we are reading from webcam
if args.get("video", None) is None:
    camera = cv2.VideoCapture(0)
    time.sleep(0.25)

# otherwise, we are reading from a video file
else:
    camera = cv2.VideoCapture(args["video"])

# initialize the first frame in the video stream
firstFrame = None

innerlooptime=0
Timestamp = 0
# loop over the frames of the video
while True:
    # grab the current frame and initialize the occupied/unoccupied
    # text
    (grabbed, frame) = camera.read()
    frame = cv2.flip(frame, -1)
    text = "Unoccupied"

    # if the frame could not be grabbed, then we have reached the end
    # of the video
    if not grabbed:
        break

    # resize the frame, convert it to grayscale, and blur it
    frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # if the first frame is None, initialize it
    if firstFrame is None:
        firstFrame = gray
        continue
    currentTime = int(time.clock() - start_time)
    innerlooptime = int(time.clock() - Timestamp)
    if currentTime % 2 == 0 and innerlooptime / 2 == 1 and currentTemp <= 45:
        Timestamp = 0
        currentTemp = currentTemp + 1
        currentPpm = currentPpm + 10
        Timestamp = time.clock()
    # compute the absolute difference between the current frame and
    # first frame
    frameDelta = cv2.absdiff(firstFrame, gray)
    thresh = cv2.threshold(frameDelta, 75, 255, cv2.THRESH_BINARY)[1]

    # dilate the thresholded image to fill in holes, then find contours
    # on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=2)
    _,cnts, _= cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                 cv2.CHAIN_APPROX_SIMPLE)

    # loop over the contours
    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < args["min_area"]:
            continue

        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    if currentTemp >= tempThrushold or currentPpm >= ppmThrushold:
        if not (isAlertSent):
            gcm = GCM("AIzaSyBiDFz1AUZh0sSTXOTBiAsmzK7TLTHhwr8")
            body = ""
            if currentTemp >= tempThrushold:
                body = "High Temperature"
            else:
                body = "Poor Air Quality"
            data = {"body": body, "title": "Warning !! Pet in danger"}
            reg_id = 'dMjW83MD3mw:APA91bHe_wXIJ6PAaGD7ThlcPiSCq9tea77X360E7m3FzdI061QUVtDjNehTlW4yTcnH1pq2T0G0FH1htXfoJh3yX4M6GvaTnUxJhbQ-hB4h2iXsHdDbN-ELnci0z-QvheBRhOZ1heu4';
            gcm.plaintext_request(registration_id=reg_id, data=data)

            isAlertSent = True
        cv2.putText(frame, "Temperature: {}".format(currentTemp) + " Celcius", (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                    (250, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
        cv2.putText(frame, "Air Quality PPM: {}".format(currentPpm), (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    else:
        cv2.putText(frame, "Temperature: {}".format(currentTemp) + " Celcius", (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                    (250, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
        cv2.putText(frame, "Air Quality PPM: {}".format(currentPpm), (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    if isAlertSent:
        cv2.putText(frame, 'Alert Sent', (10, 200), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2, cv2.LINE_AA)

    # show the frame and record if the user presses a key
    cv2.imshow("Security Feed", frame)
    #cv2.imshow("Thresh", thresh)
    #cv2.imshow("Frame Delta", frameDelta)
    key = cv2.waitKey(50) & 0xFF

    # if the `q` key is pressed, break from the lop
    if key == ord("q"):
        break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
