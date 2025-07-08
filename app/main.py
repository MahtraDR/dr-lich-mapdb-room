from flask import Flask
from flask import render_template, url_for, request, redirect
from PIL import Image
from math import floor
import re
import json
from os import environ as osenv

app = Flask(__name__)
try:
	app.config['SECRET_KEY'] = osenv.get('FLASK_SECRET_KEY')
except KeyError:
	from os import secrets
	app.config['SECRET_KEY'] = secrets.token_hex(16)

with open("app/data/map.json", "r") as f:
    room_data = json.load(f)

rd_dict = {}
for room in room_data:
    rd_dict[room["id"]] = room
    room_uids = room.get("uid")
    if room_uids and type(room_uids) == list:
        for room_uid in room_uids:
            rd_dict[f'u{room_uid}'] = room

with open("app/data/updated_at", "r") as f:
    updated_at = f.read()


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")


@app.route("/")
def root():
    return render_template("404.html")


@app.route("/u<int:simu_id>")
@app.route("/<int:room_id>")
def room_page(room_id = None, simu_id = None):
    room_box = {"x": 0, "y": 0, "width": 0, "height": 0}
    is_uid = re.search("u[0-9]+\?$", request.full_path)
    if is_uid:
        room_id = f"u{simu_id}"
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
        original_x = floor(width_ratio * room["image_coords"][0])
        original_y = floor(height_ratio * room["image_coords"][1])
        original_width = floor(width_ratio * room["image_coords"][2]) - floor(
            width_ratio * room["image_coords"][0]
        )
        original_height = floor(height_ratio * room["image_coords"][3]) - floor(
            height_ratio * room["image_coords"][1]
        )
        
        # Apply minimum dimensions while maintaining center point
        min_size = 10
        final_width = max(original_width, min_size)
        final_height = max(original_height, min_size)
        
        # Calculate position adjustment to maintain center
        width_adjustment = (final_width - original_width) / 2
        height_adjustment = (final_height - original_height) / 2
        
        room_box["x"] = original_x - width_adjustment
        room_box["y"] = original_y - height_adjustment
        room_box["width"] = final_width
        room_box["height"] = final_height
    image_dims = {"width": new_width, "height": new_height}
    room_json_pretty = json.dumps(room, indent=4, sort_keys=True)
    
    # Get rooms on the same image as current room and collect their tags
    same_image_rooms = []
    image_tags = set()
    if room.get("image"):
        for room_info in room_data:
            if room_info.get("image") == room["image"] and room_info.get("image_coords"):
                same_image_rooms.append(room_info)
                if room_info.get("tags"):
                    image_tags.update(room_info["tags"])
    
    image_tags = sorted(list(image_tags))
    
    return render_template(
        "room.html",
        room=room,
        room_box=room_box,
        image_dimensions=image_dims,
        room_json_pretty=room_json_pretty,
        updated_at=updated_at,
        image_tags=image_tags,
        same_image_rooms=same_image_rooms,
    )

@app.route("/search", methods=('GET', 'POST'))
def search():
	if request.method == 'POST':
		search = request.form['search'].strip().lower()
		overflow = False
		try:
			room = rd_dict.get(int(search))
			return redirect(url_for('room_page', room_id=search))
		except ValueError:
			room = rd_dict.get(search)
			if room:
				return redirect(url_for('room_page', simu_id=search.replace("u", "")))
		room_list = {}
		for rinfo in room_data:
			rid = rinfo.get("id", "wut")
			if search in rinfo.get('tags', []):
				room_list[rid] = rinfo
		if not room_list:
			for rinfo in room_data:
				rid = rinfo.get('id', "wut")
				if len(room_list) >= 100:
					overflow = True
					break
				for title in rinfo.get('title', {}):
					title_check = re.search(search, title, re.IGNORECASE)
					if title_check:
						room_list[rid] = rinfo
						break
				if room_list.get(rid):
					continue
				for desc in rinfo.get('description', {}):
					desc_check = re.search(search, desc, re.IGNORECASE)
					if desc_check:
						room_list[rid] = rinfo
						break
		if len(room_list) == 1:
			return redirect(url_for('room_page', room_id=list(room_list.keys())[0]))
		return render_template('search.html', results=room_list, overflow=overflow)
	else:
		return render_template('search.html', results=None, overflow=False)
