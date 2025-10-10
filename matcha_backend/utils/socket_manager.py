from flask import current_app, g



class SocketManager:
    def __init__(self):
        self.socketio = None

    def init_app(self):
        self.socketio = current_app.config.get("socketio")

    def emit_event(self, event, data, room=None):
        if self.socketio:
            self.socketio.emit(event, data, room=room)
        else:
            raise RuntimeError("SocketIO not initialized. Call init_app first.")
        

socket_manager = SocketManager()