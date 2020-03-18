from robot_gui import robot_gui, tk
from usabilidad import robot_usabilidad 
from leer_usabilidad import leer_datos_usabilidad
import os
DEBUG = True
class robot_usabilidad_gui(robot_gui):
    def __init__(self):
        super().__init__()
        self.root.title("Robot para adquirir datos para de la usabilidad de la plataforma")

        if(DEBUG):
            self.file_path = "/home/david-norato/Documentos/EXPERTIC/usabilidad/datos/datos_usabilidad.xlsx"
            self.input_user_entry.insert(0,"exper-tic")
            self.input_pass_entry.insert(0,"exper-tic")
            self.archivo_cargado = True
        

        try:
            dir_path = os.path.dirname(os.path.realpath(__file__))
        
            self.tempDownDir = os.path.join(dir_path, "tempDownDir")
            if not os.path.exists(self.tempDownDir):
                os.mkdir(self.tempDownDir)
        except Exception as e:
            self.log += "\n [-3] No ha sido posible crear el directorio temporal | EXCEPTION:  " + str(e)#5
        self.root.mainloop()
        


    def pre_run_especifico(self):
        # Lemos los datos del archivo xlsx
        leer_datos = leer_datos_usabilidad()
        datos = leer_datos.lectura_especifica(self.file_path)
        if(len(leer_datos.get_log())<1): # Si no hay algún error al leer los datos
            # Se pasan los datos y la opción de la tarea del robot
            # elección = 0 ya que no hay elecciín
            self.run_robot(datos,0)
        else:
            # Si hay por lo menos un error lo imprime en el label de la GUI
            self.log += leer_datos.get_log()
            self.label_logs_result.config(text = leer_datos.get_log())

    def get_robot(self,driver_path):
        return robot_usabilidad(driver_path, self.tempDownDir)

    def run_robot_especifico(self,datos, tipo_tarea):

        # Tarea siempre va a ser 0
        tipo_recalificacion = tipo_tarea

        # Corre el robot
        self.robot.recorrer_cursos(datos, tipo_recalificacion)


    def revisar_log(self):

        log = self.robot.log
        salida = ''


        cursos_procesados = log.count("[1]")
        cursos_exitosos = log.count("[4]")
        cursos_fallidos = log.count("[-6]")
        salida += "Total cursos procesados: "+ str(cursos_procesados) + '\n'
        salida += "Total cursos recorridos exitosamente: "+ str(cursos_exitosos) + '\n'
        salida += "archivos descargados incorrectamente: "+ str(cursos_fallidos) + '\n'
        
        return salida