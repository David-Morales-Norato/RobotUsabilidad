
from abc import ABC,abstractmethod
import pandas as pd
import tkinter as tk
import tkinter.filedialog
import os
from sys import platform
from sys import maxsize as msBits

class robot_gui():
    def __init__(self):
        #Inicializaciones
        # Errores que pueden salir 
        self.LOGS = ["\n No ha sido posible cargar el archivo: ",
                     "\n Ingrese usuario y contraseña antes de correr el robot",
                     "\n Cargue el archivo primero antes de correr el robot",
                     "\n Error de autenticación ",
                     "\n Elija una opción de"]
        self.log = ''

        # Variable de control, para verificar cuando hayan cargado un archivo existente
        self.archivo_cargado = False

        #Es necesaria una verificación en que plataforma se corre para cargar driver
        self.DRIVER_PATH = self.get_path_driver()
        

        self.file_path = ''


        #Ventana principal.
        self.root = tk.Tk()
        m = self.root.maxsize()
        self.root.geometry('{}x{}+0+0'.format(*m))

        #Frame donde van a estar ubicados las entradas de usuario y contraseña.
        self.frame_left = tk.Frame(self.root)
        self.frame_left.pack(side = "left")

        #Botón para cargar los datos del xlsx
        button_cargar_datos = tk.Button(self.frame_left, text = "Cargar datos.",comman = lambda:self.open_file()) 
        button_cargar_datos.grid(row = 0, column = 1) 

        #Labels para describir
        tk.Label(self.frame_left, text="Nombre de usuario: ").grid(row=1,column=0) 
        tk.Label(self.frame_left, text="Contraseña: ").grid(row=2,column=0)

        #Campo de texto que guarda el input de el usuario.
        self.input_user_entry = tk.Entry(self.frame_left) 
        self.input_user_entry.grid(row = 1, column =1, pady = 20)

        #Campo de texto que guarda el input de la contraseña.
        self.input_pass_entry = tk.Entry(self.frame_left) 
        self.input_pass_entry.grid(row = 2, column = 1, pady = 20)

        #Label para describir que es importante
        tk.Label(self.frame_left, text="*", fg='red').grid(row=0,column=2)
        tk.Label(self.frame_left, text="*", fg='red').grid(row=1,column=2) 
        tk.Label(self.frame_left, text="*", fg='red').grid(row=2,column=2)

        #Botón para correr el robot
        button_run_robot = tk.Button(self.frame_left, text = "Correr robot.",comman = lambda:self.pre_run()) 
        button_run_robot.grid(row = 3, column = 1) 

        #Frame derecho
        self.frame_right = tk.Frame(self.root)
        self.frame_right.pack(side = "right")

        #Label donde se van a imprimir las estadísticas
        self.label_logs_result = tk.Label(self.frame_right, text="",anchor = "center")  # Label para escribir mensajes
        self.label_logs_result.grid(row = 0, column = 0)

        # Botón que imprime estadísticas del proceso realizado.
        # Se activa una vez que se haya terminado de ejecutar el robot
        self.button_log = tk.Button(self.frame_right, text = "Revisar estadisticas",state="disabled",comman = lambda:self.imprimir_estadisticas()) 
        self.button_log.grid(row = 1, column = 0) 
        
        # Botón que guardará el log puro para ser analizado en un arvhivo plano
        # Se activa una vez que se haya terminado de ejecutar el robot
        self.button_guardar = tk.Button(self.frame_right, text = "Guardar log",state="disabled",comman = lambda:self.save_file()) 
        self.button_guardar.grid(row = 2, column = 0) 

        # Botón que guardará los datos recopilados durante la recalificación.
        # Se activa una vez que se haya terminado de ejecutar el robot
        self.button_guardar_datos = tk.Button(self.frame_right, text = "Guardar datos obtenidos",state="disabled",comman = lambda:self.save_datos_recopilados()) 
        self.button_guardar_datos.grid(row = 3, column = 0) 

        # En caso de que se quieran colocar varias opciones
        self.opcion = None

    def get_path_driver(self):

        carpeta_drivers = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/chromedriver/"
        if platform == "linux" or platform == "linux2":
            chrome_driver_path = 'Linux/'
        elif platform == "darwin":
            chrome_driver_path = 'OSX/'
        elif platform == "win32":
            chrome_driver_path = 'Win32/'

        return carpeta_drivers+ chrome_driver_path+'chromedriver'


    def pre_run(self):
            log = ''

            # Si hay un menú de opciones y si no se ha escogido ninguna opción
            if(self.opcion != None and self.opcion.get() <1):
                log += self.LOGS[4]

            # Si No ha ingresado nada como usuario o contraseña
            if(len(self.input_user_entry.get()) == 0 or len(self.input_pass_entry.get()) == 0):
                log += self.LOGS[1]
                
            # Si no ha cargado ningún archivo
            if(not self.archivo_cargado):
                log += self.LOGS[2]
                
            # Imprime los errores en el label de la GUI
            self.label_logs_result.config(text = log)

            # Si ha salido algún error no ejecuta el robot
            if(len(log)>1): 
                return

            else:
                self.pre_run_especifico()

    @abstractmethod
    def pre_run_especifico(self):
        pass

    @abstractmethod
    def get_robot(self,driver_path):
        pass

    @abstractmethod
    def run_robot_especifico(self,datos, tipo_tarea):
        pass

    def run_robot(self,datos,tipo_tarea):
        try:
            # intenta cargar el driver del navegador
            self.robot = self.get_robot(self.DRIVER_PATH)
            
        except Exception as e: # Si hay algún problema cancela correr el robot e imprime un error
            self.log += "\n" + str(e)
            self.label_logs_result.config(text = "Problema al cargar el driver de Google \n"+str(e))
            return

        # Autenticación en tic-uis
        self.robot.autenticacion_tic(self.input_user_entry.get(),self.input_pass_entry.get())
        log = self.robot.log

        # Si ha existido algún error en la autenticación
        # cierra el robot y el navegador, e imprime el error
        if(len(log)>1):
            self.cerrar_driver()
            self.log += log
            self.label_logs_result.config(text = log)
            return

        self.run_robot_especifico(datos, tipo_tarea)

        # Activa el botón para ver las estadísticas
        self.button_log.config(state="normal")
        self.button_guardar.config(state="normal")
        self.button_guardar_datos.config(state = 'normal')
        self.label_logs_result.config(text = "Terminado!")

        # Cierra el robot y el navegador
        self.cerrar_driver()
        pass


    def open_file(self):
        # Obtiene el path del archivo selexionado por el usuario
        file_path = tk.filedialog.askopenfilename(filetypes =(("Archivo xlsx", "*.xlsx"),("Todos los archivos","*.*")),
                           title = "Escoge el archivo .xlsx")
        try:
            #Intenta abrirlo
            # Si existe puede procegir a otras verificaciones
            with open(file_path,'r'):
                self.file_path = file_path
                self.archivo_cargado = True

        # Si no existe el archivo crea error
        except:
            self.archivo_cargado = False
            self.log += self.LOGS[0] + str(self.file_path)
            self.label_logs_result.config(text = self.LOGS[0])

    def save_file(self):
        try:
            # Obtiene el path del archivo selexionado por el usuario
            f = tkinter.filedialog.asksaveasfile(mode = 'w', defaultextension=".txt")
            if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
                return

            robot_log = self.robot.log
            gui_log = self.log
            path_save_file = f.name
            with open(path_save_file,'w') as f:
                f.write("Robot LOG: \n")
                f.write(robot_log)
                f.write("\nGUI LOG: \n")
                f.write(gui_log)
                self.label_logs_result.config(text = "Archivo guardado exitosamente")

                #Si no existe el archivo crea error
        except Exception as e:
            self.log += "|No se pudo guardar el archivo  |Exeption: "+ str(e)
            self.label_logs_result.config(text = "|No se pudo guardar el archivo  |Exeption: "+ str(e))

    def save_datos_recopilados(self):
        try:
            # Obtiene el path del archivo selexionado por el usuario
            f = tkinter.filedialog.asksaveasfile(mode = 'w', defaultextension=".csv")
            if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
                return

            robot_datos = self.robot.datos_recopilados
            path_save_file = f.name
            pd.DataFrame(robot_datos).to_csv(path_save_file, index=False, header=False)

                #Si no existe el archivo crea error
        except Exception as e:
            self.log += "|No se pudo guardar el archivo  |Exeption: "+ str(e)
            self.label_logs_result.config(text = "|No se pudo guardar el archivo  |Exeption: "+ str(e))


    @abstractmethod
    def revisar_log(self):
        pass

    def imprimir_estadisticas(self):
        # Imprime las estadísticas en el label de la GUI
        self.label_logs_result.config(text = self.revisar_log())

    def cerrar_driver(self):
        #Cierra el driver
        self.robot.cerrar()


        


