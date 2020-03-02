from Robot import Robot, time
import numpy as np
from selenium.webdriver.common.keys import Keys
import os
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException


class robot_usabilidad(Robot):
    def __init__(self, DRIVER_PATH, default_download_dir = None):
        self.default_download_dir = default_download_dir
        super().__init__(DRIVER_PATH,default_download_dir)
        self.tipos_preguntas = ["match", "calculated", "multianswer", "multichoice", "truefalse"]

        logs_recalificacion_preguntas = [ "\n [-3] No ha sido posible crear el directorio temporal | EXCEPTION:  ",#6
                "\n [3] Respuestas encontradas satisfactoriamente  ",#7
                "\n [-5] Fallo al encontrar el tipo al que pertenece la pregunta | EXCEPTION: ",#8
                "\n [5] tipo al que pertenece la pregunta encontrados satisfactoriamente",#9
                "\n [-6] Fallo al recorrer preguntas del curso: ",#10
                "\n [6] pregunta a tratar: ",#11
                "\n [7] preguntatratada satisfactoriamente "]#11

        # LOGS en Robot tiene un tamaño de 6 logs
        # el primero que se añada a: logs_recalificacion_preguntas
        # tendrán de 
        self._LOGS = self._LOGS + logs_recalificacion_preguntas




    def tratamiento_curso(self,datos, variables_de_control):
        lista_archivos_anterior = set(os.listdir(self.default_download_dir))

        #Obtenemos el curso que estamos tratando para nombrar los archivos
        contador = variables_de_control[1]
        curso = datos[0][contador]

        # Encontramos los registros
        self.driver.find_element_by_xpath("//*[contains(text(),'Informes')]").click()
        self.driver.find_element_by_xpath(".//*[contains(text(),'Registros')]").click()
        self.driver.find_element_by_xpath("//input[@value='Conseguir estos registros']").click()
        
        #Descagamos los registros
        self.driver.find_element_by_xpath("*//label[contains(text(),'Descargar datos de tabla como')]").location_once_scrolled_into_view
        descargar = self.driver.find_element_by_xpath("//input[@value='Descargar']")
        descargar.find_element_by_xpath("..").location_once_scrolled_into_view
        self.driver.find_element_by_css_selector('body').send_keys(Keys.UP)
        time.sleep(1)
        descargar.click()
        time.sleep(1)
        lista_archivos_nueva = set(os.listdir(self.default_download_dir))


        lista_archivos_nueva = set(os.listdir(self.default_download_dir))
        nuevo_acrchivo = list(lista_archivos_nueva-lista_archivos_anterior)
        nuevo_acrchivo = nuevo_acrchivo[0]

        os.rename(self.default_download_dir+'/'+nuevo_acrchivo, self.default_download_dir+'/'+str(curso)+'.csv')


        #Si no ha saltado alguna excepción, se guarda que fue un curso exitoso
        self.log+=self._LOGS[4]

    


def eliminar_ultimo_espacio(cadena):
    while(' ' == cadena[-1]):
        cadena = cadena[:-1]
    return cadena