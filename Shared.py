import asyncio
import discord
VoiceClients = {}
ActiveVoiceClientChannelIDs = {}
ActiveVoiceClientChannelNames = {}
Queues = {}
QueueTasks = {}

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
async def QueueWorker(Queue : Queuer):
    while True:
        try:
            triple = await Queue.Queue.get()
            finished = asyncio.Event()
            Queue.voiceclient.play(discord.FFmpegOpusAudio(triple[1]),after=lambda e: finished.set())
            await finished.wait()
            Queue.soundq.task_done()
        except Exception as e:
            print(e)

async def ClearQueue(GuildID : int):
    queue : asyncio.Queue = Queues[GuildID].Queue 
    try:
        queue.join()
        for x in queue.qsize:
            queue.get_nowait()
            queue.task_done()
    except Exception as e:
        return
async def ShutdownQueue(GuildID : int):
    Queues[GuildID].Queue.Shutdown()
    QueueTasks[GuildID].cancel()
    Queues.pop(GuildID)
    QueueTasks.pop(GuildID)

async def CreateTTSFile():
    pass