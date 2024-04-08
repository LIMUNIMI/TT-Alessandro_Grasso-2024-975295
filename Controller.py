from functions import *
from pythonosc import udp_client

ip = "127.0.0.1"
port = 9004
#port = 9001

database = [0,0,0,0,0,0,0,0,0]


def updateDatabase(db,eyelids_left,eyelids_right,mouth,left_eyebrows,left_eyebrows_ratio,x,y,mouse_state,other_click):
    db[0] = eyelids_left                                         #distanza_palpebre_sinistre
    db[1] = eyelids_right                                        #distanza_palpebre_destre
    db[2] = mouth                                                #apertura_bocca
    db[3] = left_eyebrows                                        #distanza_sopracciglia
    db[4] = left_eyebrows_ratio                                  #distanza_sopracciglia_ratio
    db[5] = x                                                    #x_mouse
    db[6] = y                                                    #y_mouse
    db[7] = int(mouse_state[0])                                  #stato_del_mouse
    db[8] = int(other_click)                                     #sopracciglia_alzate fare other_click[0]


def udp_sender(path, ip, port , value):
    sock = udp_client.SimpleUDPClient(ip, port)
    sock.send_message(path, value)



def facial_mouse_control_main(camera, screen_w, screen_h, face_mesh, coordinate_angoli, scelta, scelta_movimento):
    mouse_state = [False]
    mouse_state_right = [False]
    other_click = [False]

    screen_x1 = [0.0]
    screen_y1 = [0.0]

    max_eye_opening = 0
    max_eye_opening_right = 0
    max_mouth_opening = 0
    max_eyebrows_opening = [0.45]
    alfa = 0.3

    global max_rapporto_bocca

    #load scelta from file if not provided
    if not scelta:
        with open('scelta_occhio.json', 'r') as file:
            data = json.load(file)
            scelta = data

    if not scelta_movimento:
        with open('scelta_metodo.json', 'r') as file:
            scelta_movimento  = json.load(file)


    while True:
        frame, landmark_points, frame_h, frame_w = process_frame(camera, face_mesh)

        if landmark_points:
            landmarks = landmark_points[0].landmark
            left_eyebrows, left_eyebrows_ratio = distance(landmarks, landmarks[118], landmarks[105])
            max_eyebrows_opening = clickCheck(landmarks, landmarks[118], landmarks[105], max_eyebrows_opening, other_click, mouse_state, "", "")
            if scelta_movimento == "mov":
                x,y = movimento_facciale(frame, landmarks, frame_w, frame_h, screen_w, screen_h, coordinate_angoli, alfa, screen_x1, screen_y1)
                max_eye_opening,max_eye_opening_right, max_mouth_opening,palpebra_sinistra,palpebra_destra,apertura_bocca = click_facciale(landmarks, scelta, mouse_state, max_eye_opening, mouse_state_right, max_eye_opening_right, max_mouth_opening,other_click)
                updateDatabase(database, palpebra_sinistra,palpebra_destra, apertura_bocca,left_eyebrows,left_eyebrows_ratio,x,y,mouse_state,other_click[0])
            elif scelta_movimento == "rot":
                x,y = head_pose_estimation(coordinate_angoli, frame, landmarks, frame_h, frame_w, alfa, screen_x1, screen_y1)
                max_eye_opening,max_eye_opening_right, max_mouth_opening,palpebra_sinistra,palpebra_destra,apertura_bocca = click_facciale(landmarks,scelta, mouse_state, max_eye_opening, mouse_state_right,max_eye_opening_right, max_mouth_opening,other_click)
                updateDatabase(database, palpebra_sinistra, palpebra_destra, apertura_bocca, left_eyebrows,left_eyebrows_ratio,x,y, mouse_state,other_click[0])
        udp_sender("/aminclusivecontroller", ip, port,  database)
        print(database)
        #udp_sender("/juce/rotaryknob", ip, port, database)
        cv2.imshow("Faces", frame)
        if cv2.waitKey(1) == ord("q"):
            break
    camera.release()
    cv2.destroyAllWindows()



