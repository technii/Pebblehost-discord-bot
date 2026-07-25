from flask import Flask, request, jsonify, render_template, make_response, redirect
import Shared
from SQLcursor import db,sqlcursor,sqlqueries
from datetime import datetime, timezone
import datetime as dt
import requests
import json
app = Flask(__name__)
Discordapi = "https://discord.com/api/v10"
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024
REDIRECT_URI = "https://api.dizzybot.online/handleoauth2loginpc"
LOCALREDIRECT_URI = "http://localhost:8054/handleoauth2loginpc"
clientid = "1510230840662167644"
clientsecret = "kHtfCh23tzsiSvIf8xLb0OLMy7hLMv4c"
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/GetQueue", methods=["GET"])
async def GetQueue():
    if "GuildID" in request.form:
        return await Shared.GetQueuedItems(int(request.form.get("GuildID")))
    else:
        return {"code":400,"Reason":"No Guild ID"}

@app.route("/PlaySoundByName", methods=["POST"])
async def PlaySoundByName():
    try:
        if "GuildID" in request.form:
            GuildID = int(request.form.get("GuildID"))
            if "SoundName" in request.form:
                if GuildID in Shared.GuildsWithbotInVC:
                    try:
                        sqlcursor.execute(sqlqueries.play,(request.form.get("SoundName"),GuildID))
                        resp = sqlcursor.fetchall()
                        print(resp[0][0])
                        await Shared.PlaySound(GuildID,resp[0][0],resp[0][1])
                        return {"Code": 200,"Resp": resp}
                    except Exception as e:
                        return {"Code":400,"Reason":"No Data"}
                else:
                    return {"Code":400,"Reason":"Not In VC"}
            else:
                return {"Code":400,"Reason":"No SoundName"}
        else:
            return {"Code":400,"Reason":"No GuildID"}
    except Exception as e:
        return {"Code":400,"Reason":"No Data"}
@app.route("/UploadSound",methods=["POST"])
async def UploadSound():
    try:
        print(request.form.keys())
        if "GuildID" in request.form:
            if "UserID" in request.form:
                if "SoundName" in request.form:
                    if "SoundFile" in request.files:
                        print("Hit")
                        w = await Shared.UploadSound(request.files.get("SoundFile"),request.form.get("SoundName"),request.form["GuildID"],request.form["UserID"])
                        return {"code":200,"R":str(w)}
                    else:
                        return {"Code": 400,"Reason": "Missing SoundFile"}
                else:
                    return {"Code": 400,"Reason": "Missing SoundName"}
            else:
                return {"Code": 400,"Reason": "Missing UserID"}
        else:
            return {"Code": 400,"Reason": "Missing GuildID"}
       
    except Exception as e:
        print(e)
        return {"Code":-1,"Reason": "missing all data"}

@app.route("/GetSoundDataByName",methods=["GET"])
def GetSoundByName():
    if "SoundName" in request.form:
        a = (request.form.get("SoundName"),)
        sqlcursor.execute(sqlqueries.getsounddatabyname,a)
        data = sqlcursor.fetchall()
        return {"Code": 200,"Data": data}
    else:
        return {"Code": 400, "Reason": "Missing SoundName"}
    
@app.route("/GetActiveVoiceClient",methods=["GET"])
def GetVoiceClient():
    if "GuildID" in request.form:
        GuildID = int(request.form.get("GuildID"))
        if GuildID in Shared.GuildsWithbotInVC:
            data = {"GuildID": GuildID,"VoiceClientChannelID":Shared.ActiveVoiceClientChannelIDs[GuildID],"VoiceClientChannelName":Shared.ActiveVoiceClientChannelNames[GuildID]}
            return {"Code":200, "Data":data}
    else:
        return {"Code": 400,"Reason": "Missing GuildID"}

@app.route("/handleoauth2loginpc")
def HandleOauth2loginpc():
    
    code = request.args.get("code")
    creds : dict = getcreds(code)
    resp = make_response(render_template("ForcedOauthRedirect.html",fragment = json.dumps(creds)))
    return resp
    
def getcreds(code):
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    r = requests.post('%s/oauth2/token' % Discordapi, data=data, headers=headers, auth=(clientid, clientsecret))
    r.raise_for_status()
    return r.json()

@app.route("/localhandleoauth2loginpc")
def LocalHandleOauth2loginpc():
    try:
        code = request.args.get("code")
        creds : dict = localgetcreds(code)
        resp = make_response(render_template("ForcedOauthRedirect.html",fragment = json.dumps(creds)))
        return resp
    except Exception as e:
        return render_template("errorpage.html",error = e)
def localgetcreds(code):
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': LOCALREDIRECT_URI
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    r = requests.post('%s/oauth2/token' % Discordapi, data=data, headers=headers, auth=(clientid, clientsecret))
    r.raise_for_status()
    return r.json()



"""
{
  "access_token": "6qrZcUqja7812RVdnEKjpzOL4CvHBFG",
  "token_type": "Bearer",
  "expires_in": 604800,
  "refresh_token": "D43f5y0ahjqew82jZ4NViEr2YafMKhue",
  "scope": "identify"
}
"""