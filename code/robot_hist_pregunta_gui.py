from robot_gui import robot_gui, tk
from robot_hist_pregunta import robot_hist_pregunta
from leer_hist_pregunta import leer_datos_historial_pregunta
DEBUG = True
class robot_hist_pregunta_gui(robot_gui):
    def __init__(self):
        super().__init__()
        self.root.title("Robot para ver historial preguntas")

        if(DEBUG):
            self.file_path = "/home/david-norato/Documentos/EXPERTIC/historia_por_pregunta/datos/datos_recalificar_todo.xlsx"
            self.input_user_entry.insert(0,"exper-tic")
            self.input_pass_entry.insert(0,"exper-tic")
            self.archivo_cargado = True
        self.root.mainloop()


    def pre_run_especifico(self):
        # Lemos los datos del archivo xlsx
        leer_datos = leer_datos_historial_pregunta()
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
        return robot_hist_pregunta(driver_path)

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
        fallos_camino = log.count("[-2]")
        cursos_fallidos = log.count("[-4]")
        salida += "Total cursos procesados: "+ str(cursos_procesados) + '\n'
        salida += "Total cursos recorridos exitosamente: "+ str(cursos_exitosos) + '\n'
        salida += "Total cursos recorridos incorrectamente: "+ str(cursos_fallidos) + '\n'
        salida += "Total cursos con fallo en el camino a resultados: "+ str(fallos_camino) + '\n'
        
        preguntas_procesadas = log.count("[2]")
        preguntas_fallidas = log.count("[-3]")
        salida += "Total preguntas procesadas: "+ str(preguntas_procesadas) + '\n'
        salida += "Total preguntas fallidas a procesar: "+ str(preguntas_fallidas) + '\n'
        return salida