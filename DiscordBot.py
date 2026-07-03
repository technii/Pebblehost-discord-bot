import discord
from discord import app_commands
import json
import mysql.connector
from mutagen.mp3 import MP3
import Shared

jsonfile = open("token.json")
jsondict : dict = json.load(jsonfile)
allowedcontenttypes = ["audio/mpeg3"]
intents = discord.Intents.default()

audiofp = "Sounds/"
ttsfp = "TTS/"
sqlforuploadingsounds = "INSERT INTO SOUNDPOINTERS (GUILDID,FILENAME,LENGTH,USERID,SOUNDNAME,FileID) VALUES (%s,%s,%s,%s,%s,%s) "
sqlforgettingsoundnames = "select SOUNDNAME, LENGTH from SOUNDPOINTERS where GUILDID = %s"
sqlforplayingsound = "select FILENAME,GUILDID,LENGTH from `SOUNDPOINTERS` where SOUNDNAME = %s AND GUILDID = %s"

"""
Database Map

Guilds - ID(autoincrement), GuildID (int(255)), GuildName (varchar(255)), VoiceChannelIDs (varchar(255)) [save this in the following format (data,moredata,evenmoredata)], VoiceChannelNames (varchar(255)) [save this in the following format (data,moredata,evenmoredata]) 
SoundFiles - FileID (autoincrement), SoundName (varchar(255)), FIleName (varchar(255)), UploadGuild (int(255)), FilePath (varchar(255)), Length (varchar(255)), UploaderID (varchar(255))
Users - ID (autoincrement), Name (varchar(255)), CurrentGuilds (varchar(255)) [save this in the following format (data,moredata,evenmoredata)], UploadedSoundIDS [save this in the following format (data,moredata,evenmoredata)],UserID (int(255)),Permissions (int(255)) [Basic = 0, Admin = 1] 

"""
audiofp = "Sounds/"
ttsfp = "TTS/"
sqlforuploadingsounds = "INSERT INTO SoundFiles (UploadGuild,FileName,Length,UploaderID,SoundName) VALUES (%s,%s,%s,%s,%s,%s) "
sqlforgettingsoundnames = "select SOUNDNAME, LENGTH from SOUNDPOINTERS where GUILDID = %s"
sqlforplayingsound = "select FILENAME,GUILDID,LENGTH from `SOUNDPOINTERS` where SOUNDNAME = %s AND GUILDID = %s"



db = mysql.connector.connect(
    host=jsondict.get("SQLHost"),
    port = jsondict.get("SQLPort"),
    user = jsondict.get("SQLUsername"),
    password = jsondict.get("SQLPassword"),
    database = jsondict.get("SQLUsername"),
    connection_timeout = 10
)
sqlcursor = db.cursor()

class sclient(discord.Client):
    def __init__(self) -> None:
        super().__init__(intents=discord.Intents.default())
        self.tree = discord.app_commands.CommandTree(self)
    async def setup_hook(self) -> None:
        await self.tree.sync()

        print(f"we have signed in as {client.user}")
        
client = sclient()


@client.tree.command(name="joinvc")
@app_commands.allowed_contexts(guilds=True)
async def _joinvc(interaction : discord.Interaction, channel : discord.VoiceChannel):
    try:
        Shared.VoiceClients[interaction.guild.id] = await channel.connect()
        Shared.ActiveVoiceClientChannelIDs[interaction.guild.id] = channel.id
        Shared.ActiveVoiceClientChannelNames[interaction.guild.id] = channel.name
        await interaction.response.send_message(f"Joined {channel.name}")
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
        pass
    except Exception as e:
        await interaction.response.send_message(e,ephemeral=True)

@client.tree.command(name="playtts")
@app_commands.allowed_contexts(guilds=True)
async def _playtts(interaction : discord.Interaction, text : str, speaker : str):
    try:
        pass
    except Exception as e:
        await interaction.response.send_message(e,ephemeral=True)

@client.tree.command(name="stop")
@app_commands.allowed_contexts(guilds=True)
async def _stop(interaction : discord.Interaction):
    try:
        pass
    except Exception as e:
        await interaction.response.send_message(e,ephemeral=True)

@client.tree.command(name="pause")
@app_commands.allowed_contexts(guilds=True)
async def _pause(interaction : discord.Interaction):
    try:
        pass
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
        pass
    except Exception as e:
        await interaction.response.send_message(e,ephemeral=True)

@client.tree.command(name="uploadsound")
@app_commands.allowed_contexts(guilds=True)
async def _uploadsound(interaction : discord.Interaction, sound : discord.Attachment, soundname : str):
    try:
        if sound.content_type in allowedcontenttypes:
            sqlcursor.execute("SELECT `FileID` FROM SOUNDPOINTERS ORDER BY FileID DESC LIMIT 1")
            currentfileid : int  = int(str(sqlcursor.fetchone()).removeprefix("(").removesuffix(",)")) + 1
            await sound.save(fp=audiofp + str(interaction.guild.id) + str(currentfileid)+ ".mp3")
            vals = (str(interaction.guild.id),audiofp + str(interaction.guild.id) + str(currentfileid)+ ".mp3",str(MP3(audiofp + str(interaction.guild.id) + str(currentfileid)+ ".mp3").info.length),str(interaction.user.id),soundname,currentfileid)
            sqlcursor.execute(sqlforuploadingsounds,vals)
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