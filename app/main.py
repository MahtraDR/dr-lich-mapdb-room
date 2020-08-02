from flask import Flask 
from flask import render_template
import json

app = Flask(__name__) 

with open("app/data/map.json", "r") as f:
    room_data = json.load(f)

rd_dict = {}
for room in room_data:
    rd_dict[room['id']] = room

@app.route("/") 
def root():
    return f'hey, go to #{request.base_url}/<room id> to view a room'

@app.route("/<int:room_id>")
def room_page(room_id):
    room = rd_dict.get(room_id)
    if not room:
        return "Room not found"
    return render_template('room.html', room=room)
    
