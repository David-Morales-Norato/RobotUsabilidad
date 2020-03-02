from read_files import leer_datos,pd

class leer_datos_usabilidad(leer_datos):
    def __init__(self):
        self.NOMBRES_HOJAS = ["CURSOS","PREGUNTAS"]
        super().__init__()

    def lectura_especifica(self,file_path):
        try:

            archivo_excel = pd.read_excel(file_path, sheet_name=None)
            datos = self.lectura_historal_preguntas(archivo_excel)
            return datos
        except Exception as e:
            self.log += str(e)
            return None

    def lectura_historal_preguntas(self, archivo_excel):
        # Leemos las hojas
        cursos_hoja = archivo_excel[self.NOMBRES_HOJAS[0]]

        # Leemos cursos y actividades
        cursos= self.leer_columna(cursos_hoja,"CURSOS_ID")

        
        return [cursos]

    def get_log(self):
        return self.log