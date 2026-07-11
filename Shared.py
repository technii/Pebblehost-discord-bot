import asyncio
import discord
from piper import PiperVoice
from enum import StrEnum
import wave
import random
import os
import mysql.connector
import json
from werkzeug import datastructures
from mutagen.mp3 import MP3
import SQLcursor

jsonfile = open("token.json")
jsondict : dict = json.load(jsonfile)



allowedcontenttypes = ["audio/mpeg"]
VoiceClients = {}
ActiveVoiceClientChannelIDs = {}
ActiveVoiceClientChannelNames = {}
Queues = {}
QueueTasks = {}
GuildsWithbotInVC = []
audiofp = "Sounds/"
Sql = SQLcursor.sqlqueries
sqlcursor = SQLcursor.sqlcursor
db = SQLcursor.db
CanceledItems = {}
QueuedItems = {}

class TTSVoices(StrEnum):
    alan ="TTSvoices/en_GB-alan-medium.onnx"
    cori ="TTSvoices/en_GB-cori-medium.onnx"
    southwoman = "TTSvoices/en_GB-southern_english_female-low.onnx"
    VCTK = "TTSvoices/en_GB-vctk-medium.onnx"
    lessac = "TTSvoices/en_US-lessac-medium.onnx"
    norman = "TTSvoices/en_US-norman-medium.onnx"

"""
queue Template tuple ref = (FilePath,Duration)
"""

class Queuer():
    def __init__(self,GuildID: int ,VoiceClient : discord.voice_client):
        self.VoiceClient = VoiceClient
        self.GuildID = GuildID
        self.Queue = asyncio.Queue()


async def CreateQueue(GuildID : int):
    Queues[GuildID] = Queuer(GuildID,VoiceClients[GuildID])
    QueueTasks[GuildID] = asyncio.create_task(QueueWorker(Queues[GuildID]))
    QueuedItems[GuildID] = []
async def QueueWorker(Queue : Queuer):
    while True:
        try:
            triple = await Queue.Queue.get()
            finished = asyncio.Event()
            Queue.VoiceClient.play(discord.FFmpegOpusAudio(triple[0]),after=lambda e: finished.set())
            await finished.wait()
            if triple[2] == 1:
                os.remove(triple[0])
            print("poped")
            QueuedItems[Queue.GuildID].pop(0)
            Queue.Queue.task_done()
            
        except Exception as e:
            print(e)

async def ClearQueue(GuildID : int):
    queue : asyncio.Queue = Queues[GuildID].Queue 
    try:
        queue.join()
        for x in queue.qsize:
            queue.get_nowait()
            queue.task_done()
            QueuedItems[GuildID].pop(0)
    except Exception as e:
        return
async def ShutdownQueue(GuildID : int):
    Queues[GuildID].Queue.Shutdown()
    QueueTasks[GuildID].cancel()
    Queues.pop(GuildID)
    QueueTasks.pop(GuildID)

async def GetQueuedItems(GuildID: int):
    
    return QueuedItems.get(GuildID)

async def PlaySound(GuildID: int, SoundFileLocation : str, Duration : str):
    Queue: asyncio.Queue = Queues[GuildID].Queue
    triple = (SoundFileLocation,Duration,0)
    try:
        QueuedItems[GuildID].append(triple)
        await Queue.put(triple)
        
    except Exception as e:
        raise "no active queue"

async def StopSound(GuildID: int):
    Queue: asyncio.Queue = Queues[GuildID].Queue
    try:
        Queue.task_done()
        QueuedItems[GuildID].pop(0)
    except Exception as e:
        raise e

async def PlayTTS(GuildID: int,Voice:str,Text : str):
    voice = PiperVoice.load(Voice)
    filename =  "TTS/"+ str(GuildID) + str(random.randint(0,100000)) + ".wav"
    with wave.open(filename, "wb") as wav_file:
        voice.synthesize_wav(Text, wav_file)
    await Queues[GuildID].Queue.put((filename,GuildID,1))

async def GenerateTTS(GuildID: int,Voice:str,Text : str):
    voice = PiperVoice.load(Voice)
    filename =  "TTS/"+ str(GuildID) + random.randint(0,100000) + ".wav"
    with wave.open(filename, "wb") as wav_file:
        voice.synthesize_wav(Text, wav_file)
    return filename


async def UploadSound(File: datastructures.FileStorage,SoundName: str, GuildID : int, UserID : int):
    try:
        print(File.mimetype)
        if File.mimetype in allowedcontenttypes:
            print("True")
            filepath = audiofp + str(GuildID) + str(random.randint(0,100000))+ ".mp3"
            File.save(filepath)
            vals = (str(GuildID),filepath,str(MP3(filepath).info.length),str(UserID),SoundName)
            sqlcursor.execute(Sql.upload,vals)
            db.commit()
            return 1
        else:
            raise "Not an MP3"

    except Exception as e:
        return e