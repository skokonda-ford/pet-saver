import argparse
import cv2
import time
import imutils
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=False,
	help="path to the input image")
ap.add_argument("-c", "--cascade",
                default="haar_cascade_catfrontal.xml",
                help="path to cat detector haar cascade")
args = vars(ap.parse_args())

if args.get("video", None) is None:
    camera = cv2.VideoCapture('videoplayback1.mp4')
    time.sleep(0.25)

# otherwise, we are reading from a video file
else:
    camera = cv2.VideoCapture(args["video"])



while True:
    # grab the current frame and initialize the occupied/unoccupied
    # text
    (grabbed, frame) = camera.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    detector = cv2.CascadeClassifier("haar_cascade_catfrontal.xml")
    rects = detector.detectMultiScale(gray, scaleFactor=1.3,minNeighbors=10, minSize=(75, 75))
# loop over the cat faces and draw a rectangle surrounding each
    for (i, (x, y, w, h)) in enumerate(rects):
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.putText(frame, "Cat #{}".format(i + 1), (x, y - 10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)

# show the detected cat faces
    cv2.imshow("Cat Faces", frame)
    key = cv2.waitKey(10) & 0xFF

    # if the `q` key is pressed, break from the lop
    if key == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()