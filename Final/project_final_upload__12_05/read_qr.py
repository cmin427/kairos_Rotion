import cv2
import pyzbar.pyzbar as pyzbar
from playsound import playsound
import requests
from bs4 import BeautifulSoup


cap=cv2.VideoCapture(0)

while True:
    ret,frame=cap.read()
    
    if not ret:
        pass
    
    for obj in pyzbar.decode(frame):
        goodsID = obj.data.decode('utf-8')
        print("ID: ", goodsID)
        
       
    

