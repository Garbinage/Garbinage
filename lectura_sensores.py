#-------------------------------------Garbinage----------------------------------------------------
#--------------------------Pontificia Universidad Javeriana----------------------------------------
#---------------------------IoT: Fundamentos y Aplicaciones----------------------------------------
#--------Dorymar Gómez Chin, Cristhiam Felipe González, Santiago Humberto Ramirez Martinez---------

#----------------------------------Bibliotecas usadas------------------------------------------------------ 
import Adafruit_DHT 
import time
from datetime import datetime
from RPi import GPIO
from HX711.hx711 import HX711

#-----------------------------Definición de pines y variables-----------------------------------------------
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

pinHUMEDAD=4 #pin para el sensor de humedad 
pinABIERTA = 18 #pin para el sensor FC-51 IR

GPIO_TRIGGER = 23 #pin para el sensor HC-SR04 (Trigger)
GPIO_ECHO = 24   #pin para el sensor HC-SR04 (Echo)

sensor= Adafruit_DHT.DHT11 #Digo a la función Adafruit que voy a usar el sensor DHT11
GPIO.setup(pinABIERTA, GPIO.IN) #Defino pinABIERTA como entrada
GPIO.setup(GPIO_TRIGGER, GPIO.OUT) #Defino GPIO_TRIGGER como salida 
GPIO.setup(GPIO_ECHO, GPIO.IN) #Defino GPIO_ECHO como entrada
hx = HX711(dout_pin=21, pd_sck_pin=20) #Defino los pines para el módulo Hx711

now=datetime.now()
datos_basura={'Año:':[],'Mes:':[], 'Día:':[],'Hora:':[],'Humedad:':[],'Estado:':[],'Nivel:':[],'Peso:':[]}

#--------------------------------Creación de funciones--------------------------------------------------------------

#------------------------------Función de toma de humedad------------------------------------------------------------
def humedad (sensor,pin):

    humedad,temperatura = Adafruit_DHT.read_retry(sensor,pinHUMEDAD) #Extraigo los datos de la función Adafruit_DHT
    if humedad is not None and temperatura is not None:
        t=temperatura
        h=humedad
    else:
        print('No se pudo establecer conexión, intente de nuevo')
    return (t,h) #Retorno los datos de temperatura y humedad, aunque solo nos interesa el dato de humedad

#------------------------------Función para el sensor FC-51 IR: Estado de la caneca (abierto o cerrado)----------------------------------------------------------------
def abierta (pin):
    
     estado=GPIO.input(pinABIERTA) #Asigno el estado del pin a la variable estado 
     if estado is 1:
         cestado='Abierta'  #Si nada me obstaculiza el sensor es porque la caneca está abierta 
     else:
         cestado='Cerrada' #Si algo me obstaculiza el sensor es porque está cerrado 
        
     return (cestado) #retorno el estado de la caneca
    
#------------------------------Función para el sensor HC-SR04: Nivel de la caneca---------------------------------------------------------------------------------
def nivel():

    GPIO.output(GPIO_TRIGGER, True) #Prendo el trigger para enviar la señal 
    time.sleep(0.00001) #Espero un momento
    GPIO.output(GPIO_TRIGGER, False) #Apago 
    inicio = time.time() #Guardo el tiempo 
    parada = time.time() #Guardo el tiempo 
    while GPIO.input(GPIO_ECHO) == 0: #si no ha retornado el eco
        inicio = time.time() #Asigno este tiempo al inicio, porque aún no hay eco, lo cual indica que está iniciando
    while GPIO.input(GPIO_ECHO) == 1: #si retornó el eco
        parada = time.time() #Asigno este tiempo a la parada, porque ya hay un eco

    Tiempot = parada - inicio #Este es el tiempo que se demoró mi eco
    distancia = (Tiempot * 34300) / 2 #Con ese tiempo defino la distancia 
    
    dist = distancia
    
    if dist>167: #el sensor me da datos de 0 a 400, pero solo me los da bien precisos de 0 a 200 
        Nivel = ("Hay espacio en la caneca, mas del 50%")
    if dist<=167 and dist>=80:
        Nivel = ("La caneca  se está llenando, 50%")
    if dist <80:
        Nivel = ("La caneca está llena, menos del 50%")
    return Nivel

#--------------------------------Función para el modulo Hx711 conectado a la celda de carga: Peso de la basura--------------------------------------------------------------------
def peso():
    
    leyendo = hx.get_data_mean() #me lee un valor de la celda de carga para calibrar 
    pesoconocido = 50 #asigno un peso conocido que tengo puesto en la cerla de carga en gramos 
    valor = float(pesoconocido) #vuelvo el valor anterior flotante 
    ratio = leyendo / valor  #divide el valor que lee sobre el valor que es realmente 
    hx.set_scale_ratio(ratio) #paso ese valor a la función de la biblioteca
    Peso = int(hx.get_weight_mean(20)) #la función me devuelve el peso y se lo asigno a la variable peso 
    return Peso 
    

     


while True:
    
    datos_basura['Año:'].append(now.year) #Agrego año al diccionario 
    datos_basura['Mes:'].append(now.month) #Agrego mes al diccionario
    datos_basura['Día:'].append(now.day) #Agrego día al diccionario 
    datos_basura['Hora:'].append([now.hour, now.minute]) #Agrego hora al diccionario
    
#-------------------------------Leo los datos de las funciones-------------------------------------------------------
    
    temp,hum = humedad(sensor,pinHUMEDAD)  
    Caneca_estado = abierta(pinABIERTA)
    Niv=nivel()
    pes=peso()
    
#----------------------------------Agrego los datos leidos al diccionario-----------------------------------------------

    datos_basura['Humedad:'].append(hum)
    datos_basura['Estado:'].append(Caneca_estado)
    datos_basura['Nivel:'].append(Niv)
    datos_basura['Peso:'].append(pes)
    
#----------------------------------Recorro el diccionario imprimiendo los datos-------------------------------------------
    
    for key in datos_basura:
        print(key,':',datos_basura[key])
    print("\n")
    
#----------------------------------Guardo todos los datos en un archivo de texto--------------------------------------------------
    
    with open("datossensor.txt","w") as datossensor:
        for nombre, valor in datos_basura.items():
            datossensor.write("%s %s\n" %(nombre,valor))
    

    
    



