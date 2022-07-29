from flask import Flask
from flask import render_template, url_for, request
from PIL import Image
from math import floor
import re
import json

app = Flask(__name__)

with open("app/data/map.json", "r") as f:
    room_data = json.load(f)

rd_dict = {}
for room in room_data:
    rd_dict[room["id"]] = room
    if room.get("uid"):
        rd_dict[f'u{room["uid"][0]}'] = room

with open("app/data/updated_at", "r") as f:
    updated_at = f.read()


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")


@app.route("/")
def root():
    return render_template("404.html")


@app.route("/<int:room_id>")
@app.route("/u<int:room_id>")
def room_page(room_id):
    room_box = {"x": 0, "y": 0, "width": 0, "height": 0}
    is_uid = re.search("u[0-9]+\?$", request.full_path)
    if is_uid:
        room_id = f"u{room_id}"
    room = rd_dict.get(room_id)
    if not room:
        return render_template("404.html", noroom=True)
    orig_ratio = 1
    size_mod = 1
    new_width = new_height = False
    if room.get("image"):
        with Image.open("app/static/maps/" + room["image"]) as img:
            orig_width, orig_height = img.size
        orig_ratio = float(orig_height) / float(orig_width)
        new_width = 700
        new_height = floor(700 * orig_ratio)
        width_ratio = float(new_width) / float(orig_width)
        height_ratio = float(new_height) / float(orig_height)
    if room.get("image_coords"):
        room_box["x"] = floor(width_ratio * room["image_coords"][0])
        room_box["y"] = floor(height_ratio * room["image_coords"][1])
        box_width = floor(width_ratio * room["image_coords"][2]) - floor(
            width_ratio * room["image_coords"][0]
        )
        box_height = floor(height_ratio * room["image_coords"][3]) - floor(
            height_ratio * room["image_coords"][1]
        )
        room_box["width"] = box_width
        room_box["height"] = box_height
    image_dims = {"width": new_width, "height": new_height}
    room_json_pretty = json.dumps(room, indent=4, sort_keys=True)
    return render_template(
        "room.html",
        room=room,
        room_box=room_box,
        image_dimensions=image_dims,
        room_json_pretty=room_json_pretty,
        updated_at=updated_at,
    )
