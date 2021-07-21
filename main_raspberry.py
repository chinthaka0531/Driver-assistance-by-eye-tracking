import cv2
from gaze_tracking import GazeTracking
import time
from gpiozero import LED

sleep_time=2 #sleep detection time
not_center_time = 2 # not center looking time

led = LED(17) # LED pin
buz = LED(18) # Buzzer pin

gaze = GazeTracking() # Creating the eye tracking object
webcam = cv2.VideoCapture(0) # Creating the webcam object with a camera device. You can replace "0" with "1" to change the device

blink_count = 0 #number of blinks are going to be stored in this variable
blink_mem=[0]*3 # This array is used to have a blinking memory. this can be used to detect eye blinks more accurately
blink_mem1 = [0]*(10*sleep_time) # this one also used to have a closed eye memory. this can be used to detect sleepy.
t=time.time() # This is for timing calculation
text="Looking center" #this variable udes to store the detection result
sleep=0 # If person sleepy. This become TRUE
not_center_mem = [0]*(not_center_time*10)


###This loop is for iterate ove the frames that are coming from the camera device###
t0=time.time()

while True:
    # We get a new frame from the webcam
    _, frame = webcam.read()

    # We send this frame to GazeTracking to analyze it
    gaze.refresh(frame)

    frame = gaze.annotated_frame() # this returns annotated frame.(Face bounding box and eye bounding boxes)
    sleep=0
    blink=0
    blink_mem.append(gaze.is_blinking()) # updating blink memory
    blink_mem.pop(0)# removing oldest element from blink memory. this is to stop ram overflow
    blink_mem1.append(gaze.is_blinking())# updating sleepy memory
    blink_mem1.pop(0)# removing oldest element from sleepy memory. this is to stop ram overflow
    if gaze.is_blinking():# If eyes are closed gaze.is_blinking() become true
        blink = 1
        if (time.time()-t)>0.2 and sum(blink_mem)<2: #if previous two frames are with closed eyes count it as a eye blink.here (time.time()-t)>0.2 part using to stop continues eye blinks when person closed his eyes for a long time
            blink_count=blink_count+1
            t = time.time()
        if (sum(blink_mem1)/len(blink_mem1))>0.9:# If this blink_mem1 array has filled with 1, It assumed that person is sleepy.
            led.on()
            buz.on()


    elif gaze.is_right(): # if person looking right
        text = "Looking right"
        not_center_mem.pop(0)  # removing oldest element from not center memory. this is to stop ram overflow
        not_center_mem.append(1)  # updating not center memory

    elif gaze.is_left():#if person looking left
        text = "Looking left"
        not_center_mem.pop(0)  # removing oldest element from not center memory. this is to stop ram overflow
        not_center_mem.append(1)  # updating not center memory

    elif gaze.is_center():#if person looking center
        text = "Looking center"
        not_center_mem.pop(0)  # removing oldest element from not center memory. this is to stop ram overflow
        not_center_mem.append(0)  # updating not center memory
        led.off()
        buz.off()

    else:
        text = "Looking center" # if it fails to recognize eye balls. it assumes person looking center
        not_center_mem.pop(0)  # removing oldest element from not center memory. this is to stop ram overflow
        not_center_mem.append(0)  # updating not center memory
        led.off()
        buz.off()

    if (sum(not_center_mem)==len(not_center_mem))>0.9:
        led.on()
        buz.on()
    else:
        led.off()
        buz.off()

    #followigs are for visualization
    cv2.putText(frame, text, (20, 20), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2)
    cv2.putText(frame, "Blink count:" + str(blink_count), (20, 50), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2)
    if sleep:
        cv2.putText(frame, "You are sleepy..", (20, 80), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Demo", frame)

    Time_diff = time.time()-t0
    t0=time.time()
    print("FPS: ",(1/Time_diff))

    if cv2.waitKey(1) == 27:
        break

webcam.release()
cv2.destroyAllWindows()
