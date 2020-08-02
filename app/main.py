from flask import Flask 
from flask import render_template, url_for, request
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
    room_box = {'x': 0, 'y': 0, 'width': 0, 'height': 0}
    room = rd_dict.get(room_id)
    if room.get("image_coords"):
        room_box['x'] = room['image_coords'][0]
        room_box['y'] = room['image_coords'][1]
        room_box['width'] = room['image_coords'][2] - room['image_coords'][0]
        room_box['height'] =  room['image_coords'][3] - room['image_coords'][1]
    if not room:
        return "Room not found"
    return render_template('room.html', room=room, room_box=room_box)
    
