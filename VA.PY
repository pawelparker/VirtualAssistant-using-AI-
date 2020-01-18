import pyttsx3 
import speech_recognition as sr
import datetime
import wikipedia 
import webbrowser
import os
import smtplib
from elasticsearch import Elasticsearch 
from elasticsearch.helpers import bulk


engine = pyttsx3.init('nsss') #for windows use 'sapi5'
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)


def search_es(query):
    res = es.search(index="voice_assistant", doc_type="text", body={                     
    "query" :{
        "match": {
            "voice_command": {
                "query": query,
                "fuzziness": 2
            }
            }
        },
    })
    return res['hits']['hits'][0]['_source']['sys_command']

def speak(audio):
    engine.say(audio)
    engine.runAndWait()


def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour>=0 and hour<12:
        speak("Good Morning!")

    elif hour>=12 and hour<18:
        speak("Good Afternoon!")   

    else:
        speak("Good Evening!") 

    speak("How may I help you?")       

def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
        transcript = r.recognize_google(audio)
        print(transcript)

    try:
        print("Recognizing...")   
        query = r.recognize_google(audio, language='pt',show_all=True)
        print(f"User said: {query}\n")

    except Exception as e:
        # print(e)   
        print("Say that again please...") 
        return "None"
    return query

def sendEmail(to, content):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login('youremail@gmail.com', 'your-password')
    server.sendmail('youremail@gmail.com', to, content)
    server.close()

if __name__ == "__main__":
    wishMe()
    while True:
        query = takeCommand()
        if 'wikipedia' in query:
            speak('Searching Wikipedia...')
            query = query.replace("wikipedia", "")
            results = wikipedia.summary(query, sentences=2)
            speak("According to Wikipedia")
            print(results)
            speak(results)

        elif 'open youtube' in query:
            webbrowser.open("youtube.com")

        elif 'open google' in query:
            webbrowser.open("google.com")

        elif 'open facebook' in query:
            webbrowser.open("facebook.com")   

        elif 'the time' in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")   
            speak(f"Sir, the time is {strTime}")

        elif 'email to pawel' in query:
            try:
                speak("What should I say?")
                content = takeCommand()
                to = "pawel.pavi@gmail.com"   
                sendEmail(to, content)
                speak("Email has been sent!")
            except Exception as e:
                print(e)
                speak("Sorry !!! I am not able to send this email")   
        
        else:
            es = Elasticsearch(['localhost:9200'])
            d = '/Applications'
            records = []
            apps = os.listdir(d)
            for app in apps:
              record = {}
              record['voice_command'] = 'open ' + app.split('.app')[0]
              record['sys_command'] = 'open ' + d +'/%s' %app.replace(' ','\ ')
              records.append(record)
            bulk(es, records, index='voice_assistant', doc_type='text', raise_on_error=True)
            sys_command = search_es(query)
            os.system(sys_command)
            speak("I opened that application for you") 

