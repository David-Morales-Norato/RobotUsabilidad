import pandas as pd
from abc import ABC,abstractmethod
class leer_datos(ABC):
    def __init__(self):
        self.log = ''
    
    def leer_columna(self,data_frame, nombre_columna):
        try:
            # Intenta encontrar la columna 

            columna = data_frame[nombre_columna].dropna().tolist()

            if(len(columna) == 0):# Si no encuentra bota error 
                raise Exception(nombre_columna)
            else:
                pass
        except Exception as e:
            self.log += "Fallo al leer columna: " + str(e) + "\n"
            columna = None

        
        return columna

    def lectura_cursos_actividad(self,data):

        # Leemos los id del curso
        cursos = self.leer_columna(data,"CURSOS_ID")

        # Leemos las actividades para cada curso
        actividad = self.leer_columna(data,"ACTIVIDAD")

        # Se retornan los datos con el log
        return [cursos, actividad]

    @abstractmethod
    def lectura_especifica(self,path,tipo):
        pass

    @abstractmethod
    def get_log(self):
        pass