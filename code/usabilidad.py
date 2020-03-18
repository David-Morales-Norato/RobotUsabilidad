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

        logs_recalificacion_preguntas = [ "\n [-3] Fallo en encontrar los registros | Exception: ",#6
                                          "\n [-5] Fallo al encontrar botón de descargar | Exception: ",#7
                                          "\n [-6] Fallo al descargar el archivo del curso: | Exception: ",#8
                                          "\n [3] Registros encontrados correctamente ",#9
                                          "\n [5] Botón de descarga encontrado correctamente ",#10
                                          "\n [6] Archivo descargado correctamente "]#11

        # LOGS en Robot tiene un tamaño de 6 logs
        # el primero que se añada a: logs_recalificacion_preguntas
        # tendrán de 
        self._LOGS = self._LOGS + logs_recalificacion_preguntas




    def tratamiento_curso(self,datos, variables_de_control):
        #lista_archivos_anterior = set(os.listdir(self.default_download_dir))

        #Obtenemos el curso que estamos tratando para nombrar los archivos
        contador = variables_de_control[1]
        curso = datos[0][contador]

        try: 
            self.driver.find_element_by_xpath("//input[@value='Conseguir estos registros']").click()
        
            self.log += self._LOGS[9]
            try:
                #Descagamos los registros
                self.driver.find_element_by_xpath("*//label[contains(text(),'Descargar datos de tabla como')]").location_once_scrolled_into_view
                descargar = self.driver.find_element_by_xpath("//input[@value='Descargar']")
                descargar.find_element_by_xpath("..").location_once_scrolled_into_view
                self.driver.find_element_by_css_selector('body').send_keys(Keys.UP)
                self.log += self._LOGS[10]
                try: 

                    time.sleep(1)
                    nuevo_archivo = self.getDownLoadedFileName(descargar)
                    if(nuevo_archivo == None):
                        self.log += self._LOGS[8]
                    else:
                        print(nuevo_archivo)
                        #lista_archivos_nueva = set(os.listdir(self.default_download_dir))


                        #lista_archivos_nueva = set(os.listdir(self.default_download_dir))
                        #nuevo_acrchivo = list(lista_archivos_nueva-lista_archivos_anterior)
                        #nuevo_acrchivo = nuevo_acrchivo[0]

                        os.rename(self.default_download_dir+'/'+nuevo_archivo, self.default_download_dir+'/'+str(curso)+'.csv')
                        self.log += self._LOGS[11]
                except Exception as e:
                    self.log += self._LOGS[8] + str(e)
            except Exception as e:
                self.log += self._LOGS[7] + str(e)
        except Exception as e:
            self.log += self._LOGS[6] + str(e)

        #Si no ha saltado alguna excepción, se guarda que fue un curso exitoso
        self.log+=self._LOGS[4]

    


    # method to get the downloaded file name
    def getDownLoadedFileName(self,descargar, waitTime = 20):
        descargar.click()
        self.driver.execute_script("window.open()")
        # switch to new tab
        current_window = self.driver.current_window_handle
        self.driver.switch_to.window(self.driver.window_handles[-1])
        # navigate to chrome downloads
        self.driver.get('chrome://downloads')
        # define the endTime
        
        endTime = time.time()+waitTime
        while True:
            try:
                # get downloaded percentage
                name = self.driver.execute_script("return document.querySelector('downloads-manager').shadowRoot.querySelector('#downloadsList downloads-item').shadowRoot.querySelector('div#content  #file-link').text")
                print(name)

                # downloadPercentage = self.driver.execute_script("return document.querySelector('downloads-manager').shadowRoot.querySelector('#downloadsList downloads-item').shadowRoot.querySelector('#progress').value")
                # # check if downloadPercentage is 100 (otherwise the script will keep waiting)
                # if downloadPercentage == 100:
                #     name = self.driver.execute_script("return document.querySelector('downloads-manager').shadowRoot.querySelector('#downloadsList downloads-item').shadowRoot.querySelector('div#content  #file-link').text")
                #     # return the file name once the download is completed
                    
                #     self.driver.close()
                #     self.driver.switch_to_window(current_window)

                return name
            except Exception as e:
                self.driver.close()
                self.driver.switch_to_window(current_window)
                print(e)
                return None
            time.sleep(1)
            if time.time() > endTime:
                return None
                
        