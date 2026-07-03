import threading
from DiscordBot import run_bot
from waitress import serve
from FlaskAPI import app
import Shared

bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()
print("Started the server on 0.0.0.0 at port 8054")

serve(app, host="0.0.0.0", port=8054) 