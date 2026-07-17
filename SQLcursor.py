import mysql.connector
import json
import asyncio
from enum import StrEnum
jsonfile = open("token.json")
jsondict : dict = json.load(jsonfile)

db = mysql.connector.connect(
    host=jsondict.get("SQLHost"),
    port = jsondict.get("SQLPort"),
    user = jsondict.get("SQLUsername"),
    password = jsondict.get("SQLPassword"),
    database = jsondict.get("SQLUsername"),
    connection_timeout = 10
)
sqlcursor = db.cursor()

class sqlqueries(StrEnum):
    upload = "INSERT INTO SoundFiles (GuildID,FileName,Length,UploaderID,SoundName) VALUES (%s,%s,%s,%s,%s) "
    getallguildsounds = "select SOUNDNAME, LENGTH from SOUNDPOINTERS where GUILDID = %s"
    play = "select FileName,Length from `SoundFiles` where SoundName = %s AND GuildID = %s"
    getsounddatabyname = "select * from SoundFiles where SoundName = %s "


def main():
    while True:
        pass

