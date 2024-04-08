from functions import *
from Controller import facial_mouse_control_main,udp_sender,ip,port
from calibratore import avvia_calibratore
from tkinter import *
import tkinter

screen_w, screen_h = pyautogui.size()
max_rapporto_bocca = 0
coordinate_angoli = []





def run_gui():
    root = tkinter.Tk()
    root.geometry("700x300")
    root.resizable(False, False)
    app = Selector_GUI(root)
    root.mainloop()


class Selector_GUI:
    def __init__(self, root):
        # ------------------ costanti per il controllo della disposizione
        larghezza_pulsanti = 11
        imb_pulsantex = "2m"
        imb_pulsantey = "1m"
        imb_quadro_pulsantix = "3m"
        imb_quadro_pulsantiy = "2m"
        imb_int_quadro_pulsantix = "3m"
        imb_int_quadro_pulsantiy = "1m"
        # ------------------------------------------------------------------
        self.root = root
        self.root.title("Main GUI")
        self.selected_eye = ""
        self.selected_method = ""

        self.quadro_pulsanti = Frame(root)
        self.quadro_pulsanti.pack(
            ipadx=imb_int_quadro_pulsantix,
            ipady=imb_int_quadro_pulsantiy,
            padx=imb_quadro_pulsantix,
            pady=imb_quadro_pulsantiy,
        )

        # Pulsante di avvio --------------------------------------------------------------------------------------------------------------
        self.start = tkinter.Button(self.quadro_pulsanti, text="Avvia ", bg="white", fg="black", command=self.start_facial_mouse_control)

        self.start.configure(
            width=larghezza_pulsanti,
            padx=imb_pulsantex,
            pady=imb_pulsantey
        )

        self.start.grid(row=0, column=0, padx=(0, 10), pady=(10, 0))
        #---------------------------------------------------------------------------------------------------------------------------------

        # Pulsante per la calibrazione----------------------------------------------------------------------------------------------------
        self.cal = tkinter.Button(self.quadro_pulsanti, text="Calibratore", background="white",command=self.start_calibrator)

        self.cal.configure(
            width=larghezza_pulsanti,
            padx=imb_pulsantex,
            pady=imb_pulsantey
        )

        self.cal.grid(row=0, column=2, padx=(10, 0), pady=(10, 0))
        #---------------------------------------------------------------------------------------------------------------------------------
        self.info = Label(self.quadro_pulsanti, text="Scegli quale metodo usare per controllare il movimento del puntatore del mouse", fg="black")
        self.info.grid(row=1, column=1)
        # Selezione movimento testa ------------------------------------------------------------------------------------------------------
        self.head_movement = tkinter.Button(self.quadro_pulsanti, text="Movimento testa", bg="white", fg="black",command=lambda: self.select_method("mov"))

        self.head_movement.configure(
            width=larghezza_pulsanti,
            padx=imb_pulsantex,
            pady=imb_pulsantey
        )

        self.head_movement.grid(row=1, column=0, padx=(0, 10), pady=(60, 0))
        #--------------------------------------------------------------------------------------------------------------------------------

        # Selezione rotazione testa -----------------------------------------------------------------------------------------------------
        self.head_rotation = tkinter.Button(self.quadro_pulsanti, text="Rotazione testa", background="white",command=lambda: self.select_method("rot"))
        self.head_rotation.configure(
            width=larghezza_pulsanti,
            padx=imb_pulsantex,
            pady=imb_pulsantey
        )

        self.head_rotation.grid(row=1, column=2, padx=(10, 0), pady=(60, 0))
        #--------------------------------------------------------------------------------------------------------------------------------

        self.info = Label(self.quadro_pulsanti, text="Scegli quale gesto associare al click del tasto sinistro del mouse", fg="black")
        self.info.grid(row=2, column=1)


        # Selezione occhi ----------------------------------------------------------------------------------------------------------------
        self.eyes = tkinter.Button(self.quadro_pulsanti, text="Occhiolino", bg="white", fg="black",command=self.toggle_eye_buttons)

        self.eyes.configure(
            width=larghezza_pulsanti,
            padx=imb_pulsantex,
            pady=imb_pulsantey
        )
        self.eyes.grid(row=3, column=0, padx=(0, 10), pady=(10, 0))
        #---------------------------------------------------------------------------------------------------------------------------------

        # Selezione bocca ----------------------------------------------------------------------------------------------------------------
        self.mouth = tkinter.Button(self.quadro_pulsanti, text="Chiusura bocca", background="white",command=self.hide_eye_buttons)

        self.mouth.configure(
            width=larghezza_pulsanti,
            padx=imb_pulsantex,
            pady=imb_pulsantey
        )

        self.mouth.grid(row=3, column=2, padx=(10, 0), pady=(10, 0))
        # ---------------------------------------------------------------------------------------------------------------------------------

        self.frame_occhi = Frame(root)

        # occhio sinistro------------------------------------------------------------------------------------------------------------------
        self.left_eye = tkinter.Button(self.frame_occhi, text="Occhio sinistro", bg="white",fg="black", command=lambda: self.select_eye("sx"))

        self.left_eye.configure(
            width=larghezza_pulsanti,
            padx=imb_pulsantex,
            pady=imb_pulsantey
        )

        # occhio destro ----------------------------------------------------------------------------------------------------------------
        self.right_eye = tkinter.Button(
            self.frame_occhi,
            text="Occhio destro",
            background="white",
            command=lambda: self.select_eye("dx")
        )

        self.right_eye.configure(
            width=larghezza_pulsanti,
            padx=imb_pulsantex,
            pady=imb_pulsantey
        )

        self.label_eye_selection = Label(self.frame_occhi, text="Quale occhio vuoi usare per controllare click?",fg="black")



    def start_facial_mouse_control(self):
        camera = cv2.VideoCapture(0)
        facial_thread = threading.Thread(target=facial_mouse_control_main, args=(camera, screen_w, screen_h, face_mesh, coordinate_angoli, self.selected_eye, self.selected_method))
        facial_thread.start()

    def start_calibrator(self):
        calibrator_thread = threading.Thread(target=avvia_calibratore,args=(self.selected_method,))
        calibrator_thread.start()

    def select_method(self, selected_method):
        self.selected_method = selected_method
        salva_su_file_json(selected_method, 'scelta_metodo.json')
        if selected_method == "mov":
            self.head_movement.configure(bg="lightblue")  # Set the desired color
            self.head_rotation.configure(bg="white")  # Reset the other button's color
        elif selected_method == "rot":
            self.head_rotation.configure(bg="lightblue")  # Set the desired color
            self.head_movement.configure(bg="white")  # Reset the other button's color

    def toggle_eye_buttons(self):
        if self.frame_occhi.winfo_ismapped():
            self.hide_eye_buttons()

        else:
            self.show_eye_buttons()

    def show_eye_buttons(self):
        self.mouth.configure(bg="white")
        self.label_eye_selection.pack(pady=(0, 20))
        self.left_eye.pack(side=tkinter.LEFT, padx=(7, 20))
        self.right_eye.pack(side=tkinter.RIGHT, padx=(0, 28))
        self.frame_occhi.pack()  # Mostra il frame degli occhi

    def hide_eye_buttons(self):
        self.select_eye("m")
        self.mouth.configure(bg="lightblue")  # Set the desired color
        self.left_eye.pack_forget()
        self.right_eye.pack_forget()
        self.label_eye_selection.pack_forget()
        self.frame_occhi.pack_forget()  # Nasconde il frame degli occhi

    def select_eye(self, selected_eye):
        self.selected_eye = selected_eye
        salva_su_file_json(selected_eye, 'scelta_occhio.json')
        if selected_eye == "sx":
            self.left_eye.configure(bg="lightblue")  # Set the desired color
            self.right_eye.configure(bg="white")  # Reset the other button's color
            self.mouth.configure(bg="white")
        elif selected_eye == "dx":
            self.right_eye.configure(bg="lightblue")  # Set the desired color
            self.left_eye.configure(bg="white")  # Reset the other button's color
            self.mouth.configure(bg="white")
        else:
            # Reset the background color for other cases if needed
            self.left_eye.configure(bg="white")
            self.right_eye.configure(bg="white")


if __name__ == "__main__":
    file = open("coordinate_calibrazione2.json")
    data = json.load(file)
    for i in data:
        coordinate_angoli.append(data[i])
    file.close()



    udp_sender("/aminclusivecontroller/getNumberOfAuxPads", ip, port, None)
    udp_sender("/aminclusivecontroller/getNumberOfPages", ip, port, None)
    udp_sender("/aminclusivecontroller/page/1", ip, port, None)
    run_gui()


