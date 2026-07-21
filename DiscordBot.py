import discord
from discord import app_commands
import json
import mysql.connector
from mutagen.mp3 import MP3
import Shared
import SQLcursor
import datetime

jsonfile = open("token.json")
jsondict : dict = json.load(jsonfile)
allowedcontenttypes = ["audio/mpeg3"]
intents = discord.Intents.default()

db = SQLcursor.db
sqlcursor = SQLcursor.sqlcursor
"""
Database Map

Guilds - ID(autoincrement), GuildID (int(255)), GuildName (varchar(255)), VoiceChannelIDs (varchar(255)) [save this in the following format (data,moredata,evenmoredata)], VoiceChannelNames (varchar(255)) [save this in the following format (data,moredata,evenmoredata]) 
SoundFiles - FileID (autoincrement), SoundName (varchar(255)), FIleName (varchar(255)), UploadGuild (int(255)), FilePath (varchar(255)), Length (varchar(255)), UploaderID (varchar(255))
Users - ID (autoincrement), Name (varchar(255)), CurrentGuilds (varchar(255)) [save this in the following format (data,moredata,evenmoredata)], UploadedSoundIDS [save this in the following format (data,moredata,evenmoredata)],UserID (int(255)),Permissions (int(255)) [Basic = 0, Admin = 1] 

"""
audiofp = "Sounds/"
ttsfp = "TTS/"
sqlforuploadingsounds = SQLcursor.sqlqueries.upload
sqlforgettingsoundnames = SQLcursor.sqlqueries.getallguildsounds
sqlforplayingsound = SQLcursor.sqlqueries.play





class sclient(discord.Client):
    def __init__(self) -> None:
        super().__init__(intents=discord.Intents.default())
        self.tree = discord.app_commands.CommandTree(self)
    async def setup_hook(self) -> None:
        await self.tree.sync()

        print(f"we have signed in as {client.user}")
        
        guildss = []
        async for guild in client.fetch_guilds():
            guildss.append(guild.name)
        print(f"Running on {len(guildss)} servers called {guildss}")
        
client = sclient()


@client.tree.command(name="joinvc")
@app_commands.allowed_contexts(guilds=True)
async def _joinvc(interaction : discord.Interaction, channel : discord.VoiceChannel):
    try:
        Shared.VoiceClients[interaction.guild.id] = await channel.connect()
        Shared.ActiveVoiceClientChannelIDs[interaction.guild.id] = channel.id
        Shared.ActiveVoiceClientChannelNames[interaction.guild.id] = channel.name
        Shared.GuildsWithbotInVC.append(interaction.guild.id)
        await Shared.CreateQueue(interaction.guild.id)
        await interaction.response.send_message(f"Joined {channel.name}", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(e,ephemeral=True)

@client.tree.command(name="leavevc")
@app_commands.allowed_contexts(guilds=True)
async def _leavevc(interaction : discord.Interaction):
    try:
        await Shared.VoiceClients[interaction.guild.id].disconnect()
        print(interaction.guild.voice_channels)
        await interaction.response.send_message(f"left {Shared.ActiveVoiceClientChannelNames[interaction.guild.id]}")
    except Exception as e:
        await interaction.response.send_message(e,ephemeral=True)

@client.tree.command(name="playsound")
@app_commands.allowed_contexts(guilds=True)
async def _playsound(interaction : discord.Interaction, soundname : str):
    try:
        sqlcursor.execute(sqlforplayingsound,(soundname,interaction.guild.id))
        resp = sqlcursor.fetchall()
        print(resp[0][0])
        print(Shared.GuildsWithbotInVC)

        if interaction.guild.id in Shared.GuildsWithbotInVC:
            await Shared.PlaySound(interaction.guild.id,resp[0][0],resp[0][1])
        else:
            await interaction.response.send_message("Not In A VC :(", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(e,ephemeral=True)

@client.tree.command(name="playtts")
@app_commands.allowed_contexts(guilds=True)
async def _playtts(interaction : discord.Interaction, text : str, speaker : Shared.TTSVoices):
    try:
        if interaction.guild.id in Shared.GuildsWithbotInVC:
            await interaction.response.send_message("Done",ephemeral=True)
            await Shared.PlayTTS(interaction.guild.id,speaker,text)
        else:
            await interaction.response.send_message("Not In A VC :(", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(e,ephemeral=True)

@client.tree.command(name="pause")
@app_commands.allowed_contexts(guilds=True)
async def _pause(interaction : discord.Interaction):
    try:
        await Shared.PauseQueue(interaction.guild.id)
        await interaction.response.send_message("Paused!",ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(e,ephemeral=True)
@client.tree.command(name="resume")
@app_commands.allowed_contexts(guilds=True)
async def _resume(interaction : discord.interactions):
    try:
        await Shared.UnpauseQueue(interaction.guild.id)
        await interaction.response.send_message("Resumed!",ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(e,ephemeral=True)
@client.tree.command(name="showqueue")
@app_commands.allowed_contexts(guilds=True)
async def _showqueue(interaction : discord.Interaction):
    try:
        pass
    except Exception as e:
        await interaction.response.send_message(e,ephemeral=True)

@client.tree.command(name="skip")
@app_commands.allowed_contexts(guilds=True)
async def _skip(interaction : discord.Interaction):
    try:
        await Shared.StopSound(interaction.guild.id)
        await interaction.response.send_message("Skipped",ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(e,ephemeral=True)

@client.tree.command(name="uploadsound")
@app_commands.allowed_contexts(guilds=True)
async def _uploadsound(interaction : discord.Interaction, sound : discord.Attachment, soundname : str):
    try:
        if sound.content_type in allowedcontenttypes:
            filepath = audiofp + str(interaction.guild.id) + str(datetime.datetime.now(datetime.timezone.utc))+ ".mp3"
            await sound.save(fp=filepath)
            vals = (str(interaction.guild.id),filepath,str(MP3(filepath).info.length),str(interaction.user.id),soundname)
            sqlcursor.execute(SQLcursor.sqlqueries.upload,vals)
            db.commit()
            await interaction.response.send_message("SAVED", ephemeral=True)
            
        else:
            await interaction.response.send_message("Must be a .mp3", ephemeral=True)


    except Exception as e:
        await interaction.response.send_message(e,ephemeral=True)

@client.tree.command(name="soundlist")
@app_commands.allowed_contexts(guilds=True)
async def _soundlist(interaction : discord.Interaction):
    try:
        pass
    except Exception as e:
        await interaction.response.send_message(e,ephemeral=True)




def run_bot():
    client.run(jsondict.get("token"))