import cv2
from cvzone.HandTrackingModule import HandDetector


class Button:
    def __init__(self, pos, width, height, value):
        self.pos = pos
        self.width = width
        self.height = height
        self.value = value

    def draw(self, img):
        cv2.rectangle(img, self.pos, (self.pos[0] + self.width, self.pos[1] + self.height),
                      (225, 225, 225), cv2.FILLED)
        cv2.rectangle(img, self.pos, (self.pos[0] + self.width, self.pos[1] + self.height),
                      (50, 50, 50), 3)
        cv2.putText(img, self.value, (self.pos[0] + 40, self.pos[1] + 60), cv2.FONT_HERSHEY_PLAIN,
                    2, (50, 50, 50), 2)

    def checkClick(self, x, y):

        # compares the value of the index finger (x,y)
        # if it falls under the button block (self.pos) trigger it

        if self.pos[0] < x < self.pos[0] + self.width and \
                self.pos[1] < y < self.pos[1] + self.height:
            cv2.rectangle(img, (self.pos[0] + 3, self.pos[1] + 3),
                          (self.pos[0] + self.width - 3, self.pos[1] + self.height - 3),
                          (255, 255, 255), cv2.FILLED)
            cv2.putText(img, self.value, (self.pos[0] + 25, self.pos[1] + 80), cv2.FONT_HERSHEY_PLAIN,
                        5, (0, 0, 0), 5)
            return True
        else:
            return False



# Webcam input
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # makes the image big
detector = HandDetector(detectionCon=0.8, maxHands=1)

# Buttons
buttonListValues = [['7', '8', '9', '*'],
                    ['4', '5', '6', '-'],
                    ['1', '2', '3', '+'],
                    ['0', '/', 'C', '=']]
buttonList = []
for x in range(4):
    for y in range(4):
        xpos = x*100 + 150
        ypos = y*100 + 150
        buttonList.append(Button((xpos,ypos),100,100,buttonListValues[y][x]))

# Variables
myEquation = ""
delayCounter = 0

# program loop
while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    # Detection of hand (using mediapipe)
    hands, img = detector.findHands(img, flipType=False)

    # calculator display area
    cv2.rectangle(img, (150,50), (150 + 400, 70 + 100),
                  (225, 225, 225), cv2.FILLED)
    cv2.rectangle(img, (150,50), (150+400,70+100),
                  (50, 50, 50), 3)

    # clear button area
    #cv2.rectangle(img, (450, 110), (100, 100),
                  #(225, 225, 225), cv2.FILLED)

    #cv2.putText(img, "X", (490, 120), cv2.FONT_HERSHEY_PLAIN,
                #3, (50, 50, 50), 3)

    # Draw interface buttons
    for button in buttonList:
        button.draw(img)

    ### math processing

    # 1 check for hand
    if hands:
        # Find distance between index [8] and middle [12] fingers
        lmList = hands[0]['lmList']
        indexFingerX = lmList[8][0]
        indexFingerY = lmList[8][1]

        middleFingerX = lmList[12][0]
        middleFingery = lmList[12][1]

        length, _, img = detector.findDistance((indexFingerX,indexFingerY),
                                               (middleFingerX,middleFingery),
                                               img)

        # if length < 50 detect it as a click for the interface
        if length < 35:
            for i, button in enumerate(buttonList):      #enum for counting how many buttons were clicked
                if button.checkClick(indexFingerX,indexFingerY) and delayCounter == 0:

                    #specific check for cancel

                    # get's the latest button user clicked on
                    myValue = buttonListValues[int(i%4)][int(i/4)]
                    # ex. 7%4 = 3 (3rd row) 7/4 = 1 (1st column)

                    # update current equation
                    if myValue == "C":
                        myEquation = ""

                    elif myValue == "=":
                        myEquation = str(eval(myEquation))

                    else:
                        myEquation += myValue

                    delayCounter = 1


    # avoiding duplicate entries
    if delayCounter != 0:
        delayCounter += 1
        if delayCounter > 10:
            delayCounter = 0



    ### Display result
    cv2.putText(img, myEquation, (160, 120), cv2.FONT_HERSHEY_PLAIN,
                3, (50, 50, 50), 3)

    # display
    cv2.imshow("Image", img)
    cv2.waitKey(1)

    key = cv2.waitKey(1)

    if key == ord('c'):
        myEquation = ''