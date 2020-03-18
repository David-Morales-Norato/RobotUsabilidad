
"""
By David Morales Norato (2019)

Coming soon
"""
from abc import ABC,abstractmethod
from selenium import webdriver
import time
import pandas as pd
import glob

class Robot(ABC):
    
    def __init__(self, CHROME_DRIVER_PATH, download_deafult_path):
        ## Inicializaciones

        # Link que lleva a los cuestionarios, falta el id del curso al final del link
        self.__QUESTION_LINK = "https://tic.uis.edu.co/ava/report/log/index.php?id="
        
        self.log = ''
        self.download_deafult_path = download_deafult_path
        if(self.download_deafult_path == None):
            # El driver del robot
            self.driver = webdriver.Chrome(executable_path = CHROME_DRIVER_PATH)
        else:
            chromeOptions = webdriver.ChromeOptions()
            prefs = {"download.default_directory" : self.download_deafult_path}
            chromeOptions.add_experimental_option("prefs",prefs)
            # El driver del robot
            self.driver = webdriver.Chrome(executable_path = CHROME_DRIVER_PATH, chrome_options=chromeOptions)

        # Link de autenticación de tic-uis
        self.__autentication_link = 'https://tic.uis.edu.co/ava/login/index_ingreso.php'

        # Errores
        self._LOGS = ["\n [-1] Fallo Al hacer autenticación| EXCEPTION: ",#0
                        "\n [1] Curso a procesar: ",#1
                        "\n [-2] Error al encontrar la actividad| Exception: ",#2
                        "\n [2] Se va a procesar: ",#3
                        "\n [4] Curso terminado satisfactoriamente",#4
                        "\n [-4] Error al procesar curso: "]#5

        self.datos_recopilados = []


    def autenticacion_tic(self, nickName, password):
        try:
            # Tiempo de dejar cargar chrome
            time.sleep(1)
            # Carga la página inicial de tic-uis
            self.driver.get(self.__autentication_link)
            self.driver.maximize_window() 
            # Tiempo para dejar que cargue la página
            time.sleep(3)

            # da click en pregrado
            pregrado = self.driver.find_element_by_id('pregrado-head')
            pregrado.click()

            # Encuentra usuario y contraseña
            userName = self.driver.find_element_by_name('username')
            passWord = self.driver.find_element_by_name('password')
            
            # Escribe las credenciales
            userName.send_keys(nickName)
            passWord.send_keys(password)

            # Encuentra botón para enviar información
            login_attempt = self.driver.find_element_by_xpath("//*[@id='send']")
            login_attempt.submit()
            
            # Si hay un fallo en la autenticación se muestra como un errorcode en el link
            if('?' in self.driver.current_url and "errorcode" in self.driver.current_url.split("?")[1]):
                raise Exception("Error usuario o contraseña")

        except Exception as e:
            self.log += self._LOGS[0]+ str(e)

    def recorrer_cursos(self,datos, eleccion):

        id_cursos = datos[0]
        # Va a indicar el curso actual que se está tratando
        contador = 0
        for id in id_cursos: # Para cada curso de los que se proporcionaron Obtenemos el id del curso
            id = str(id)
            link_question = self.__QUESTION_LINK+id # links a los cuestionarios de ese curso
            try:
                self.log += self._LOGS[1] + id # Registramos curso a procesar
                self.driver.get(link_question) # se dirige a ese link

                # Esta tupla es el argumento donde irán las variables de control
                # La elección indica que tipo de tarea se va a realizar
                # El contador indica que fila de los datos se está tratando
                variables_de_control = [eleccion,contador]
                # Hacemos el debido tratamiento para el cual está recorriendo cursos
                self.tratamiento_curso(datos,variables_de_control)
                contador +=1
            except Exception as e:
                # Si ocurre un error se guarda el fallo
                self.log+=self._LOGS[5]+id +"| EXCEPTION: "+ str(e)

        self.pre_procesar_datos()

    @abstractmethod
    def tratamiento_curso(self,datos,variables_de_control):
        pass
        
    def cerrar(self):
        self.driver.quit()

    def pre_procesar_datos(self):
        all_data = pd.DataFrame()

        for f in glob.glob(self.download_deafult_path +"/*.csv"):
            df = pd.read_csv(f)
            all_data = all_data.append(df,ignore_index=True)

        self.datos_recopilados = all_data