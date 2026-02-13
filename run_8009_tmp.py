import platform
import app
use_reloader = False if platform.system().lower().startswith('win') else True
app.socketio.run(app.app, host='127.0.0.1', port=8009, debug=True, use_reloader=use_reloader)

