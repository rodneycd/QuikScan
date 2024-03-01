import pytesseract
import re
import cv2
from datetime import datetime as dt
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


#Image input
image_path = 'data/workschedule.jpg'
img = cv2.imread(image_path)

#Dictionary to store all 
shifts_dict = {}

# Convert the image to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Use pytesseract to perform OCR on the grayscale image
custom_config = r'--oem 3 --psm 6'
text = pytesseract.image_to_string(gray, config=custom_config)

# Split the OCR output into words
words = text.split()

# Initialize variables to track the current date, start time, and end time
current_date = None
current_start_time = None
current_end_time = None

#Converts standard date time to military/24hr clock time
def convert(time):
    if time == None:
        pass
    else:
        if re.search('a.m.', time): #Checks if the meridiem a.m. is within the string
            convertedTime = re.sub('a.m.', '', time) #removes the meridiem so now left with just time value

            #Checking if time is in format HH:MM, if so, return the time value
            if re.search('(1[0-2]):[0-5][0-9]', convertedTime):
                return convertedTime 
           
            #Checking if time is in format H:MM, if so, add 0 before the H
            if re.search('[1-9]:[0-5][0-9]', convertedTime):
                return '0' + convertedTime
            
            #Checking if time is in format HH, if so, add trailing :00
            if re.search('(1[0-2])', convertedTime):
                return convertedTime + ':00' 
            
            #Checking if time is in format H, if so, add trailing :00
            if re.search('[1-9]', convertedTime):
                return '0' + convertedTime + ':00' 
        #The code below is now formatting like above, but for p.m. times instead
        if re.search('p.m.', time): #Checks if the meridiem p.m. is within the string
                convertedTime = re.sub('p.m.', '', time) #removes the meridiem so now left with just time value
                
                if re.search('[1-9]:[0-5][0-9]', convertedTime): #If format in H:MM
                    x = convertedTime.split(':') #Split string at colon : so that way 12 can be added to the hours alone
                    hoursMins = str(int(x[0]) + 12)
                    convertedTime = hoursMins + ":" + x[1]
                    return convertedTime
                
                if re.search('[1-9]', convertedTime): #If format in H alone, 3pm is 3 for example. 
                    hoursMins = str(int(convertedTime) + 12)
                    convertedTime = hoursMins + ":00"
                    return convertedTime
                if re.search('(1[0-2]):[0-5][0-9]', convertedTime): #If format in HH:MM
                    if '12' in convertedTime: #If HH:MM hour value is 12, then return converted time
                        return convertedTime
                    x = convertedTime.split(':')
                    hoursMins = str(int(x[0]) + 12)
                    convertedTime = hoursMins + ":" + x[1]
                    return convertedTime
                if re.search('(1[0-2])', convertedTime):
                    if '12' in convertedTime:
                        return convertedTime + ':00'
                    hoursMins = str(int(convertedTime) + 12)
                    convertedTime = hoursMins + ':00'
                    return convertedTime 
                    
                

# Combine relevant components
combined_times = []
current_time = ""
for word in words:
    #print(word)
    if not re.match(r'\d{1,2}/\d{1,2}', word) and any(char.isdigit() for char in word) or word.lower() in ["a.m.", "p.m."]:
        current_time += word
    else:
        if current_time:
            combined_times.append(current_time.strip())
            current_time = ""
    if re.match(r'\d{1,2}/\d{1,2}', word):
        combined_times.append(word)

#print(combined_times)

for time in combined_times:
    if not re.match(r'\d{1,2}/\d{1,2}', time):
        if not current_start_time:
            current_start_time = time
        else:
            current_end_time = time
    else:
        current_date = time + "/2024"
        shifts_dict[current_date] = convert(current_start_time), convert(current_end_time)

        current_start_time = None
        current_end_time = None
   
print(shifts_dict)

for date,time in zip(shifts_dict.keys(), shifts_dict.values()):
    None #print(date,time[0])



#GOOGLE API

SCOPES = ["https://www.googleapis.com/auth/calendar"]

'''
def main():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
    
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)
        
        for key in shifts_dict:

            event = {
                'summary': 'Cashier',
                'location': 'Publix Super Market at Lake Ella Plaza, 1700 N Monroe St, Tallahassee, FL 32303, USA',
                'description': 'Break: ',
            }






    except HttpError as error:
        print("An error occurerd: ", error)
'''