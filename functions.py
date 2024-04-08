
import threading
import mediapipe as mp
import cv2
import pyautogui
import json
import math
import numpy as np
import time


face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
screen_w, screen_h = pyautogui.size()
max_rapporto_bocca = 0



def map_segment(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
# Prepara la telecamera

def process_frame(camera, face_mesh):
    ret, frame = camera.read()
    if not ret:
        print("Error: Unable to capture frame from the camera.")
        return None, None, None, None  # or handle the error accordingly

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = face_mesh.process(rgb_frame)
    landmark_points = output.multi_face_landmarks
    frame_h, frame_w, _ = frame.shape
    return frame, landmark_points, frame_h, frame_w

def salva_su_file_json(scelta, nome_file):
    with open(nome_file, 'w') as file:
        json.dump(scelta, file)
def coordinate(frame, land, frame_h, frame_w):
    x = int(land.x * frame_w)
    y = int(land.y * frame_h)
    cv2.circle(frame, (x, y), 3, (0, 255, 255))
    return x, y
def euclidean_distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
def distance(landmarks, landmark1, landmark2):
    landmark_distance = euclidean_distance(landmark1.x, landmark1.y, landmark2.x, landmark2.y)
    face_width = euclidean_distance(landmarks[234].x, landmarks[234].y, landmarks[454].x, landmarks[454].y)
    ratio = landmark_distance / face_width

    return landmark_distance,ratio



def clickCheck(landmarks, landmark1, landmark2,max_ratio,other_click,mouse_state,scelta,click):
    value, ratio = distance(landmarks, landmark1, landmark2)

    if scelta == "":
        if float(ratio) > max_ratio[0]:
            if not other_click[0]:
                other_click[0] = True
        else:
            if other_click[0]:
                other_click[0] = False

    elif scelta == "m":
        if ratio > max_ratio:
            max_ratio = ratio

        mapped_ratio = map_segment(ratio, 0, max_ratio, 0, 1)
        if mapped_ratio <= (max_ratio * 0.5):
            if not mouse_state[0]:
                pyautogui.mouseDown(button=click)
            mouse_state[0] = True

        else:
            if mouse_state[0]:
                pyautogui.mouseUp(button=click)
            mouse_state[0] = False
    return max_ratio


# Si occupa del click effettuato con la bocca, occhio sinistro  e bocca. Nel caso della bocca, effettua il click solamente nel caso in cui i landmarks passati corrispondono a quelli della bocca
# altrimenti si limita a dire se le sopracciglia sono alzate o meno.
def gestione_eventi_mouse(landmarks, landmark1, landmark2, max_ratio, mouse_state,mouse_state_right, click, scelta, other_click):
    if scelta == "sx" or scelta == "dx":
        value_distance, ratio = distance(landmarks, landmark1, landmark2)
        if value_distance > max_ratio:
            max_ratio = value_distance

        if scelta == "sx":
            if value_distance < (max_ratio * 0.5):
                if not mouse_state[0]:
                    pyautogui.mouseDown(button=click)
                mouse_state[0] = True
            else:
                if mouse_state[0]:
                    pyautogui.mouseUp(button=click)
                mouse_state[0] = False
        elif scelta == "dx":
            if value_distance < (max_ratio * 0.5):
                if not mouse_state_right[0]:
                    pyautogui.mouseDown(button=click)
                mouse_state_right[0] = True
            else:
                if mouse_state_right[0]:
                    pyautogui.mouseUp(button=click)
                mouse_state_right[0] = False
    else:
        max_ratio = clickCheck(landmarks, landmark1, landmark2, max_ratio, other_click, mouse_state, scelta, click)

    return max_ratio


def click_facciale( landmarks, scelta, mouse_state, max_eye_opening, mouse_state_right,max_eye_opening_right, max_mouth_opening,other_click):
    left = [landmarks[145], landmarks[159]]
    right = [landmarks[374], landmarks[386]]
    mouth = [landmarks[12], landmarks[15]]
    if scelta == 'sx':
        max_eye_opening = gestione_eventi_mouse(landmarks, left[0], left[1], max_eye_opening, mouse_state,mouse_state_right, 'left',scelta,other_click)
        max_eye_opening_right = gestione_eventi_mouse(landmarks, right[0],right[1], max_eye_opening_right,mouse_state,mouse_state_right, 'right',scelta,other_click)


    elif scelta == 'dx':
        max_eye_opening = gestione_eventi_mouse(landmarks, right[0], right[1], max_eye_opening, mouse_state,mouse_state_right,'left',scelta,other_click)
        max_eye_opening_right = gestione_eventi_mouse(landmarks, left[0],left[1], max_eye_opening_right,mouse_state, mouse_state_right,'right',scelta,other_click)

    elif scelta == "m":
        max_mouth_opening = gestione_eventi_mouse(landmarks, mouth[0], mouth[1],max_mouth_opening, mouse_state,mouse_state_right,'left',scelta,other_click)

    palpebra_sinistra, _ = distance(landmarks, left[0], left[1])
    palpebra_destra,   _ = distance(landmarks, right[0], right[1])
    _,    apertura_bocca = distance(landmarks, mouth[0], mouth[1])

    return max_eye_opening, max_eye_opening_right, max_mouth_opening,palpebra_sinistra,palpebra_destra,apertura_bocca
def movimento_facciale(frame, landmarks, frame_w, frame_h, screen_w, screen_h, coordinate_angoli, alfa, screen_x1, screen_y1):
    #for id, landmark in enumerate(landmarks[474:478]):
    for id, landmark in enumerate(landmarks[4:220]):
        x, y = coordinate(frame, landmark, frame_h, frame_w)
        if id == 0:
            screen_x = screen_w / frame_w * x
            screen_y = screen_h / frame_h * y
            if len(coordinate_angoli) != 0:
                screen_x = map_segment(screen_x, coordinate_angoli[0][0], coordinate_angoli[1][0], 0, pyautogui.size()[0])
                screen_y = map_segment(screen_y, coordinate_angoli[0][1], coordinate_angoli[1][1], 0, pyautogui.size()[1])

                alfa = max(0, min(alfa, 1))

                x_pesato = (alfa * screen_x) + ((1 - alfa) * screen_x1[0])
                y_pesato = (alfa * screen_y) + ((1 - alfa) * screen_y1[0])
                pyautogui.moveTo(x_pesato, y_pesato)
                screen_x1[0], screen_y1[0] = x_pesato, y_pesato
                return x_pesato,y_pesato

            else:
                pyautogui.moveTo(screen_x, screen_y)
                return screen_x,screen_y
def head_pose_estimation(coordinate_angoli,frame, landmarks, frame_h, frame_w, alfa, screen_x1, screen_y1):

    face_2d = []
    face_3d = []


    for idx, lm in enumerate(landmarks):
        if idx == 33 or idx == 263 or idx == 1 or idx == 61 or idx == 291 or idx == 199:
            if idx == 1:
                nose_2d = (lm.x * frame_w, lm.y * frame_h)
                nose_3d = (lm.x * frame_w, lm.y * frame_h, lm.z * 3000)

            x, y = int(lm.x * frame_w), int(lm.y * frame_h)
            # Get 2D coordinates
            face_2d.append([x, y])

            # Get 3D coordinates
            face_3d.append([x, y, lm.z])

    # Convert to NumPy array
    face_2d = np.array(face_2d, dtype=np.float64)
    face_3d = np.array(face_3d, dtype=np.float64)

    # Camera matrix
    focal_length = 1 * frame_w

    cam_matrix = np.array([[focal_length, 0, frame_h / 2], [0, focal_length, frame_w / 2], [0, 0, 1]])

    # Distortion parameters
    dist_matrix = np.zeros((4, 1), dtype=np.float64)

    # Solve PnP
    success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)

    # Get rotational matrix
    rmat, jac = cv2.Rodrigues(rot_vec)

    # Get angles
    angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)

    # Get the y rotation degree
    x = angles[0] * 360
    y = angles[1] * 360
    z = angles[2] * 360

    # Display the nose direction
    nose_3d_projection, jacobian = cv2.projectPoints(nose_3d, rot_vec, trans_vec, cam_matrix, dist_matrix)

    p1 = [int(nose_2d[0]), int(nose_2d[1])]
    p2 = [int(nose_2d[0] + y * 10), int(nose_2d[1] - x * 10)]

    if len(coordinate_angoli) != 0:
        newx = map_segment(p1[0], coordinate_angoli[0][0], coordinate_angoli[1][0], 0,pyautogui.size()[0])
        newy = map_segment(p1[1], coordinate_angoli[0][1], coordinate_angoli[1][1], 0,
pyautogui.size()[1])

        alfa = max(0, min(alfa, 1))

        x_pesato = (alfa * newx) + ((1 - alfa) * screen_x1[0])
        y_pesato = (alfa * newy) + ((1 - alfa) * screen_y1[0])
        pyautogui.moveTo(x_pesato, y_pesato)
        cv2.line(frame, p1, p2, (255, 0, 0), 3)
        screen_x1[0], screen_y1[0] = x_pesato, y_pesato
        return x_pesato,y_pesato
    else:
        pyautogui.moveTo(p2[0],p2[1])
        return p2[0],p2[1]
