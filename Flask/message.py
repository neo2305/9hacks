from scipy.spatial import distance
import cv2
import numpy as np
import dlib

# Creating face detection and landmark predictor objects using dlib
face_detect = dlib.get_frontal_face_detector()
landmark_predict = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')


# Returning a tuple for bounding box
def ret_to_bb(face_rect):
    x = face_rect.left()
    y = face_rect.top()
    w = face_rect.right() - x
    h = face_rect.bottom() - y
    return (x, y, w, h)

def get_right_eye(landmarks, dtype = "int"):

    cords = np.zeros((6,2),dtype = dtype)
    for i in range(36,42):
        cords[i-36] = (landmarks.part(i).x , landmarks.part(i).y)
    return cords


def get_left_eye(landmarks, dtype = "int"):

    cords = np.zeros((6,2),dtype = dtype)
    for i in range(42,48):
        cords[i-42] = (landmarks.part(i).x , landmarks.part(i).y)
    return cords

def calc_ear(eye):
    a = distance.euclidean(eye[1],eye[5])
    b = distance.euclidean(eye[2],eye[4])

    c = distance.euclidean(eye[0],eye[3])

    ear = (a+b)/(2.0*c)

    return ear


# Creating a video capture object
cap = cv2.VideoCapture(0)


EAR_Tresh = 0.25


EYE_Consec_frames = 4
counter = 0
total = 0

while True:
    # Reading from the webcam
    ret, frame = cap.read() 


    if ret == True:
        # Flipping the camera view horizontally to avoid mirror view
        frame = cv2.flip(frame, 1)
        # Converting the color image to grayscale for faster computation
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_copy = frame.copy()
        # Detecting the faces on the grayscale image and getting the co-ordinates
        faces = face_detect(gray)
        if len(faces) == 1:
            for (i, face) in enumerate(faces):
            # Getting landmark co-ordinates over the detected faces
                landmarks = landmark_predict(gray, face)
                right_eye = get_right_eye(landmarks)
                left_eye = get_left_eye(landmarks)

                for(x,y) in right_eye:
                    cv2.circle(frame, (x, y), 2, (0,0,255), -1)
                    hull = cv2.convexHull(right_eye)
                    cv2.drawContours(frame, [hull], -1, (255,255,255), 1)
                for(x,y) in left_eye:
                    cv2.circle(frame, (x, y), 2, (0,0,255), -1)
                    hull = cv2.convexHull(left_eye)
                    cv2.drawContours(frame, [hull], -1, (255,255,255), 1)
                right_ear = calc_ear(right_eye)
                left_ear = calc_ear(left_eye)
                ear =(right_ear + left_ear) / 2.0


                if ear < EAR_Tresh:
                    counter+=1

                else:
                    if counter >= EYE_Consec_frames:
                        total  +=1
                    counter = 0
                cv2.putText(frame, "You're drowsy for: {} many frames".format(total), (left_eye[0][1],left_eye[0][1]),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
                
                # for (x,y) in left_eye:
                cv2.putText(frame,"EAR: {:.2f}".format(ear), (left_eye[0][1],left_eye[0][1]-15),  #(x-75,y-125) wala part miyamura
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        elif len(faces) > 1:
            z = 0
            for f in faces:
                face = faces[z]
                for (i, face) in enumerate(faces):
                # Getting landmark co-ordinates over the detected faces
                    landmarks = landmark_predict(gray, face)
                    right_eye = get_right_eye(landmarks)
                    left_eye = get_left_eye(landmarks)
                    for(x,y) in right_eye:
                        cv2.circle(frame, (x, y), 2, (0,0,255), -1)
                        hull = cv2.convexHull(right_eye)
                        cv2.drawContours(frame, [hull], -1, (255,255,255), 1)
                    for(x,y) in left_eye:
                        cv2.circle(frame, (x, y), 2, (0,0,255), -1)
                        hull = cv2.convexHull(left_eye)
                        cv2.drawContours(frame, [hull], -1, (255,255,255), 1)
                    right_ear = calc_ear(right_eye)
                    left_ear = calc_ear(left_eye)
                    ear =(right_ear + left_ear) / 2.0


                    if ear < EAR_Tresh:
                        counter+=1

                    else:
                        if counter >= EYE_Consec_frames:
                            total  +=1
                        counter = 0
                    cv2.putText(frame, "You're drowsy for: {} many frames".format(total), (left_eye[0][1],left_eye[0][1]),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
                    
                    # for (x,y) in left_eye:  
                    cv2.putText(frame,"EAR: {:.2f}".format(ear), (left_eye[0][1],left_eye[0][1]-25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)




    cv2.imshow('Face-Landmarking', frame)

    k = cv2.waitKey(1) & 0xff
    # Pressing escape to end the program
    if k == 27:
        break
cap.release()
cv2.destroyAllWindows()