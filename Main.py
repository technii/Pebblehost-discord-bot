import threading
from DiscordBot import run_bot
from waitress import serve
from FlaskAPI import app
from SQLcursor import main

sql_thread = threading.Thread(target=main, daemon=True)
sql_thread.start()
#bot_thread = threading.Thread(target=run_bot, daemon=True)
#bot_thread.start()
print("Bot Started")
print("SqlCursor Started")
print("Started the server on 0.0.0.0 at port 8054")
serve(app, host="0.0.0.0", port=8054) 