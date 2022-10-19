import cv2
import numpy as np
import serial
import time
from tkinter import *

arduinoData= serial.Serial('COM6',9600)
arduinoData.write_timeout=2     
totalImage=0 

def userInterface(tur,area):

    global totalImage 
    totalImage+=1 

    arayuz=Tk()
    pencere=Canvas(arayuz,height=400,width=400)
    pencere.pack() 
    cerceve1=Frame(arayuz, bg='#add8e6')
    cerceve1.place(relx=0.08, rely=0.08, relwidth=0.42, relheight=0.84)
    cerceve2=Frame(arayuz, bg='#add8e6')
    cerceve2.place(relx=0.50, rely=0.08, relwidth=0.42, relheight=0.84)
   
    sekilTurLabel=Label(cerceve1,bg='#add8e6',text='SEKİL : ', font='Verdana 12 bold').pack(anchor=NW, padx=15, pady=50 )
    sekilAlanLabel=Label(cerceve1,bg='#add8e6',text='SEKLİN ALANI : ', font='Verdana 12 bold').pack(anchor=NW, padx=15, pady=0 )
    toplamSekilLabel=Label(cerceve1,bg='#add8e6',text='TOPLAM SEKİL : ', font='Verdana 12 bold').pack(anchor=NW, padx=15, pady=50) 
       
    sekilTur=Label(cerceve2,bg='#add8e6',text=tur, font='Verdana 12 bold').pack(anchor=NW, padx=25, pady=50 )
    sekilAlan=Label(cerceve2,bg='#add8e6',text=area, font='Verdana 12 bold').pack(anchor=NW, padx=25, pady=0 )
    toplamSekil=Label(cerceve2,bg='#add8e6',text=totalImage, font='Verdana 12 bold').pack(anchor=NW, padx=25, pady=50 )

    arayuz.mainloop()

def nothing(x):pass
buton = [20,60,100,200]
def pushButton(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN: 
        if y > buton[0] and y < buton[1] and x > buton[2] and x < buton [3]:
            imageProcessing(1)
            
cv2.namedWindow("Ayar")
cv2.createTrackbar("Low-H", "Ayar", 0, 180, nothing)
cv2.createTrackbar("Low-S", "Ayar", 0, 255, nothing)
cv2.createTrackbar("Low-V", "Ayar", 0, 255, nothing)
cv2.setMouseCallback("Ayar", pushButton)  

controlImage = np.zeros((80,300), np.uint8)
controlImage[buton[0]:buton[1],buton[2]:buton[3]] = 180
cv2.putText(controlImage, 'RUN',(120,50),cv2.FONT_HERSHEY_PLAIN, 2,(0),3)
cv2.imshow("Ayar", controlImage)

video=cv2.VideoCapture(1) 

while True:
    _, image = video.read() 
    
    imageBlur=cv2.GaussianBlur(image,(7,7),1)
    hsvImage=cv2.cvtColor(imageBlur, cv2.COLOR_RGB2HSV)
 
    l_h=cv2.getTrackbarPos("Low-H","Ayar")
    l_s=cv2.getTrackbarPos("Low-S","Ayar")
    l_v=cv2.getTrackbarPos("Low-V","Ayar")
    # Yukarıda oluşturdugumuz trackbar'ların degerlerini alt esik degeri olarak belirledik.
   
    lowerLimit=np.array([l_h, l_s, l_v])
    upperLimit=np.array([180, 255, 255])
    # Esik degerlerimizin alt ve ust degerlerini belirledik

    mask=cv2.inRange(hsvImage, lowerLimit, upperLimit)   
    contours , hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) 

    def imageProcessing(buton):        

        if buton==1:
            for cnt in contours:
                imageArea=cv2.contourArea(cnt)
                print('alan: ',imageArea)

            if imageArea>3000:  
                contourPerimeter = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, 0.02* contourPerimeter, True)            
                x = approx.ravel()[0]
                y = approx.ravel()[1] - 5

                if len(approx) == 3:                    
                    data=("3").strip()                    
                    arduinoData.write(data.encode())
                    arduinoData.write_timeout=2
                    userInterface(tur=('UCGEN'),area=(imageArea))
            
                elif len(approx) == 4 :
                    x, y , w, h = cv2.boundingRect(approx)
                    aspectRatio = float(w)/h
                    if aspectRatio >= 0.95 and aspectRatio < 1.05:                        
                        data=("4").strip()
                        arduinoData.write(data.encode())
                        arduinoData.write_timeout=2                        
                        userInterface(tur=('KARE'),area=(imageArea))                
                
                    else:                        
                        data=("2").strip()
                        arduinoData.write(data.encode())
                        arduinoData.write_timeout=2
                        print('dikdortgen')
                        userInterface(tur=('DİKDÖRTGEN'),area=(imageArea))                

                elif len(approx) == 5 :                    
                    data=("5").strip()
                    arduinoData.write(data.encode())
                    arduinoData.write_timeout=2
                    userInterface(tur=('BESGEN'),area=(imageArea))
            
                else: 
                    data=("0").strip()
                    arduinoData.write(data.encode())
                    arduinoData.write_timeout=2                    
                    userInterface(tur=('DAİRE'),area=(imageArea))
            else:                
                print('Şekil algılanmadı..') 
    
    cv2.imshow("GORUNTU",image)
    cv2.imshow("MASK",mask)
    key=cv2.waitKey(5) & 0xFF
    if key==27:
        break
cv2.destroyAllWindows()
video.release()

