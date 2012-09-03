import sfml as sf
import pickle
import zlib
from base64 import b64encode, b64decode

PLAYER_UPDATE = 0
CHAT_MESSAGE = 1

class Message(object):

    def __init__(self, payload, type):
        self.payload = payload
        self.type = type

    def encode(self):
        return b64encode(zlib.compress(pickle.dumps(self)))

    @classmethod
    def decode(self, msg):
        message = pickle.loads(zlib.decompress(b64decode(msg)))
        return message

class ChatMessage(Message):
    def __init__(self, message, from_player, to_player = None):
        self.message = message
        self.from_player = from_player
        self.to_player = to_player
        self.type = Message.CHAT_MESSAGE

class PlayerUpdateMessage(Message):
    def __init__(self, player_id, coords, heading, state, action):
        self.player_id = player_id
        self.map = map
        self.coords = coords
        self.heading = heading
        self.state = state
        self.action = action
        self.type = Message.PLAYER_UPDATE
