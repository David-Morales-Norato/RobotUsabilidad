from Robot import Robot, time
import numpy as np
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException

class robot_hist_pregunta(Robot):
    def __init__(self, DRIVER_PATH):
        super().__init__(DRIVER_PATH)

        self.tipos_preguntas = ["match", "calculated", "multianswer", "multichoice", "truefalse"]

        logs_recalificacion_preguntas = [ "\n [-3] Fallo en encontrar respuestas para el tipo de pregunta:  ",#6
                "\n [3] Respuestas encontradas satisfactoriamente  ",#7
                "\n [-5] Fallo al encontrar el tipo al que pertenece la pregunta | EXCEPTION: ",#8
                "\n [5] tipo al que pertenece la pregunta encontrados satisfactoriamente",#9
                "\n [-6] Fallo al recorrer preguntas del curso: ",#10
                "\n [6] pregunta a tratar: ",#11
                "\n [7] preguntatratada satisfactoriamente "]#11

        self.datos_recopilados.append(["ID_CURSO", "NOMBRE_ACTIVIDAD", "ID_PREGUNTA", "NOMBRE_ESTUDIANTE", "NOTA", "RESPUESTA", "LINK_RESPUESTA", "LINK_RESULTADOS_DE_ACTIVIDAD"])
        # LOGS en Robot tiene un tamaño de 6 logs
        # el primero que se añada a: logs_recalificacion_preguntas
        # tendrán de 
        self._LOGS = self._LOGS + logs_recalificacion_preguntas
        # Texto para recalificar una pregunta
        self.__RESCORE_STRING = "Escribir comentario o corregir la calificación"

    def tratamiento_curso(self,datos, variables_de_control):
        #Obtenemos el curso que estamos tratando
        contador = variables_de_control[1]
        curso = datos[0][contador]

        try:
            # Se listan las resultados_de_actividades de cada curso
            resultados_de_actividades = self.driver.find_elements_by_xpath("//td[@class='cell c3 lastcol']//a")



        except Exception as e:
            # En caso de no ser encontrado se captura la excepción y  se registra en el log
            self.log +=self._LOGS[2]+ str(e)
        

        main_window = self.driver.current_window_handle

        for intento_actividad in resultados_de_actividades:
            # Hallamos la intento_actividad
            intento_actividad.location_once_scrolled_into_view
            href = intento_actividad.get_attribute('href')
            if href:
                self.driver.execute_script('window.open(arguments[0]);', href)

            new_window = self.driver.window_handles[-1]
            self.driver.switch_to.window(new_window)

            # Para sacar estadísticas.
            # Preparación para llegar a la tabla
            table = self.driver.find_element_by_id("attempts")

            self.recorrer_preguntas(table, new_window, curso, href)

            self.driver.close()
            self.driver.switch_to.window(main_window)
            
        #Si no ha saltado alguna excepción, se guarda que fue un curso exitoso
        self.log+=self._LOGS[4]
            

    def recorrer_preguntas(self, table, main_window, curso, link_actividad):
        try: 
            nombre_actividad = self.driver.find_element_by_xpath("//nav//*//a[@title='Cuestionario']").text
            # Buscamos todas las preguntas que han sido respondidas por estudiantes
            questions = table.find_elements_by_xpath(".//*[@title = 'Revisar respuesta']")

            # Se va a revisar cada pregunta
            for question in questions:
                puntaje = question.text
                if(puntaje == "-"):
                    puntaje = None
                elif("/" in puntaje):
                    puntaje = puntaje.split("/")[1].replace(",",".")
                else:
                    puntaje = puntaje.replace(",",".")
                
                question.click()

                # Cambiamos a la nueva ventana que es la preunta
                handles = self.driver.window_handles
                self.driver.switch_to.window(handles[-1])
                quest_id_title = str(self.driver.title).split(" pregunta ")[1].split(" en ")[0]
                # Nombre de la persona
                nombre = str(self.driver.title.split(" por ")[1])
                self.log += self._LOGS[11] + quest_id_title

                # Link de la respuesta del estudiante
                link_quest = self.driver.current_url
                # Encontrar respuestas
                respuestas = self.encontrar_respuestas(quest_id_title)

                # id_curso, nombre actividad, id_ pregunta, nombre estudiante, puntaje en la respuesta, respuesta del estudiante, link a la respuesta, link a resultados del curso
                self.datos_recopilados.append([curso,nombre_actividad,quest_id_title,nombre,puntaje,respuestas,link_quest, link_actividad])


                self.log += self._LOGS[12]

                # Si es o no es la pregunta solicitada, cierra y vuelve a la ventana original
                self.driver.close()
                self.driver.switch_to.window(main_window)

        except Exception as e:
            # Si hay algún error guarda el fallo
            self.log += self._LOGS[10] + curso + " | Exception:  " + str(e)

    def encontrar_respuestas(self, title):
        tipo = self.encontrar_tipo_pregunta()
        # Si la pregunta si la podemos tratar 
        if tipo != None:
            # Encontrar respuesta
            
            respuestas = self.recoger_respuestas_por_tipo(tipo)
        else:
            respuestas = "--tipo de pregunta no soportada--"
        # Si encontró las respuestas las retorna
        # Si no es un tipo de pregunta tratable retorna None
        if(tipo != None and respuestas == None):
            respuestas = "--pregunta no respondida--"
                   
        return respuestas
                


    def encontrar_tipo_pregunta(self):
        try:
            encontrado = False
            for tipo in self.tipos_preguntas:
                string_tipos_preguntas = ("//*[@class='que " +tipo + " deferredfeedback incorrect' or "
                "@class='que "+tipo+ " deferredfeedback correct' or "
                "@class='que "+tipo+ " deferredfeedback partiallycorrect' or "
                "@class='que "+tipo+ " deferredfeedback notanswered' or "
                "@class='que "+tipo+ " deferredfeedbackexplain incorrect' or "  
                "@class='que "+tipo+ " deferredfeedbackexplain partiallycorrect' or "
                "@class='que "+tipo+ " deferredfeedbackexplain correct' or"
                "@class='que "+tipo+ " deferredfeedbackexplain notanswered']")
                encontrados = self.driver.find_elements_by_xpath(string_tipos_preguntas)
                if len(encontrados) >=1:
                    # Tipo de pregunta
                    self.log +=  self._LOGS[9]
                    return tipo
            if(not encontrado): 
                raise Exception(" Tipo de pregunta no soportado por el robot ")
        except Exception as e:
            self.log += self._LOGS[8] + str(e)
            return None

    
    def recoger_respuestas_por_tipo(self, tipo):

        try:
            # si es tipo match
            if(tipo == self.tipos_preguntas[0] ):
                # Encontramos la tabla de las respuestas
                tabla  = self.driver.find_elements_by_xpath("//table[@class='answer']//tbody//tr")
                # para cada fila en la tabla
                cont = 0
                respuestas = {}
                for tr in tabla:
                    tds = tr.find_elements_by_xpath(".//td")
                    enun = tds[0].find_element_by_xpath(".//p").text
                    seleccion = tds[1].find_element_by_xpath(".//select//option[@selected='selected']").text
                    respuestas[cont] = [enun, seleccion]
                    cont +=1
                

            # si es tipo calculated
            elif(tipo == self.tipos_preguntas[1] ):

                # Encontramos el span de la respuesta
                ans  = self.driver.find_element_by_xpath("//span[@class='answer']")
                # El input del usuario
                respuestas = ans.find_element_by_xpath(".//input").get_attribute("value")
                # Las unidades
                unidades =  ans.find_element_by_xpath(".//select//option[@selected='selected']").text
                unidades = unidades.replace("[","").replace("]","")
                # Se guardan para ser recuperadas
                respuestas = {0:[respuestas, unidades]}

            # si es tipo multianswer
            elif(tipo == self.tipos_preguntas[2] ):
                opciones_seleccionadas = self.driver.find_elements_by_xpath("//select")
                cont = 0
                respuestas = {}
                for seleccion in opciones_seleccionadas:
                    enun = seleccion.find_element_by_xpath("..").find_element_by_xpath("..").text
                    sele = seleccion.find_element_by_xpath(".//option[@selected='selected']").text
                    
                    enun = enun.split("\n")[0]
                    respuestas[cont] = [enun,sele]
                    cont +=1

            # si es tipo multichoice 
            elif(tipo == self.tipos_preguntas[3] ):
                # Se encuentra el seleccionado
                respuestas = self.driver.find_element_by_xpath("//div[@class='answer']//div//input[@checked='checked']")
                respuestas = respuestas.find_element_by_xpath("..//label").text
                # Se guardan para ser recuperadas
                respuestas = {0: respuestas}

            # si es tipo truefalse
            elif(tipo == self.tipos_preguntas[4] ):
                respuestas = self.driver.find_element_by_xpath("//input[@checked='checked']").find_element_by_xpath("..").find_element_by_xpath(".//label").text
                respuestas = {0: respuestas}
            else:
                raise Exception(" Tipo de pregunta no soportado ")
        except Exception as e:
            self.log +=  self._LOGS[6] + str(tipo) + " | Exception: " + str(e)
            return None

        self.log +=  self._LOGS[7]
        return respuestas

def eliminar_ultimo_espacio(cadena):
    while(' ' == cadena[-1]):
        cadena = cadena[:-1]
    return cadena