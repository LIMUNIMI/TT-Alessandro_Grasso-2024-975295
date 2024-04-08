from Controller import *
import time
import winsound
import tkinter
from tkinter import messagebox

click = 0
mouse_state = "up"
max_eye_opening = 0
corners = {'top_left_c': (0, 0), 'bottom_right_c': (0, 0)}


def on_click(app, x, y):
    global click
    if click < 2:
        update_square_corners(x, y, click)
        click += 1
    if click == 2:
        app.calibration_complete()

def mouse_move(app,metodo,camera):
    global max_eye_opening, mouse_state, click
    while True:
        frame, landmark_points, frame_h, frame_w = process_frame(camera, face_mesh)
        if landmark_points:
            landmarks = landmark_points[0].landmark
            if metodo == 'mov':
                screen_x,screen_y = movimento_facciale(frame, landmarks, frame_w, frame_h, screen_w, screen_h, [], 0,0,0)
            else:
                screen_x, screen_y = head_pose_estimation([], frame, landmarks, frame_h, frame_w,  0, 0, 0)

            right = [landmarks[374], landmarks[386]]
            for landmark in right:
                x,y = coordinate(frame, landmark, frame_h, frame_w)
                eye_opening = euclidean_distance(right[0].x, right[0].y, right[1].x, right[1].y)
                if eye_opening > max_eye_opening:
                    max_eye_opening = eye_opening
                if eye_opening < (max_eye_opening * 0.5):  # treshold fisso
                    if mouse_state == "up":
                        mouse_state = "down"
                        on_click(app, screen_x, screen_y)
                        winsound.Beep(400, 100)
                    elif mouse_state == "down":
                        mouse_state = "up"
                        time.sleep(1)
            app.update_coordinates_label(f"X: {screen_x:.2f}, Y: {screen_y:.2f}")
        if click == 2:
            break

    camera.release()
    cv2.destroyAllWindows()
def update_square_corners(x, y, click):
    if click == 0:
        corners['top_left_c'] = (x, y)
    elif click == 1:
        corners['bottom_right_c'] = (x, y)

    json_object = json.dumps(corners)
    with open('coordinate_calibrazione2.json', 'w') as file:
        file.write(json_object)


class MouseCoordinatesApp:
    def __init__(self, calibrator_root, x, y,metodo):
        self.calibrator_root = calibrator_root
        self.metodo = metodo
        self.mouse_coordinates = tkinter.StringVar()
        self.calibrator_root.attributes("-fullscreen", True)

        self.calibrator_root.title("Calibratore")

        self.calibrated_label = tkinter.Label(self.calibrator_root, text="")
        self.calibrated_label.pack()

        self.coordinates_label = tkinter.Label(self.calibrator_root, textvariable=self.mouse_coordinates)
        self.coordinates_label.pack()

        self.label = tkinter.Label(self.calibrator_root, text="clicca in corrispondenza dell'angolo più in alto a sinistra e l'angolo più in basso a destra che riesci a raggiungere ")
        self.label.pack()

        self.canvas = tkinter.Canvas(self.calibrator_root, width=x - 400, height=y - 400)
        self.canvas.pack()

        self.canvas.create_oval(10, 10, 20, 20, fill="black", outline="black")
        self.canvas.create_oval(x - 410, y - 410, x - 400, y - 400, fill="black", outline="black")

        self.mouse = tkinter.Button(self.calibrator_root, text="Avvia calibrazione", command=self.mouse_starter)
        self.mouse.pack()

        self.update_coordinates()

        self.pulsante_chiusura = tkinter.Button(self.calibrator_root, text="Chiudi calibratore", command=self.chiudi)
        self.pulsante_chiusura.pack()

    def chiudi(self):
        self.calibrator_root.destroy()

    def mouse_starter(self):
        camera = cv2.VideoCapture(0)
        mouse_thread = threading.Thread(target=mouse_move, args=(self,self.metodo,camera))
        mouse_thread.start()

    def calibration_complete(self):
        self.calibrated_label.config(text="Calibrato")

    def update_coordinates(self):
        if click < 2:
            self.coordinates_label.after(100, self.update_coordinates)

        else:
            self.coordinates_label.config(text="Calibrato")

    def update_coordinates_label(self, coordinates):
        self.mouse_coordinates.set(coordinates)


def avvia_calibratore(metodo):

    calibrator_root = tkinter.Tk()
    app = MouseCoordinatesApp(calibrator_root, screen_w, screen_h,metodo)
    app.calibrator_root.mainloop()


