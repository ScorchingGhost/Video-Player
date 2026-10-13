
# import necessary modules
import json
import os
import shutil
import subprocess
from pathlib import Path
from threading import Timer

from flask import Flask, jsonify, send_file, send_from_directory


# static paths
app = Flask(__name__, static_folder="Style", static_url_path="/Style")
index_file = Path(__file__).with_name("index.php")
media_directory = Path(__file__).with_name("Media")
config_file = Path(__file__).with_name("config.json")


@app.get("/")
def index():
    return send_file(index_file, mimetype="text/html")


@app.get("/Media/<path:filename>")
def media(filename: str):
	return send_from_directory(media_directory, filename)

# load configuration from config.json
def load_config() -> dict:
	with config_file.open(encoding="utf-8") as config:
		return json.load(config)

# serve the public configuration for the buttons
@app.get("/config.json")
def public_config():
	buttons = load_config().get("buttons")
	if not isinstance(buttons, list):
		raise ValueError("'buttons' must be a list.")

	public_buttons = []
	for index, button in enumerate(buttons):
		if not isinstance(button, dict):
			raise ValueError(f"Button configuration at index {index} must be an object.")
		if not isinstance(button.get("label"), str) or not isinstance(button.get("class"), str):
			raise ValueError(f"Button configuration at index {index} needs a label and class.")
		label_class = button.get("label_class")
		if label_class is not None and not isinstance(label_class, str):
			raise ValueError(f"'label_class' for button {index} must be a string.")

		public_button = {
			"label": button["label"],
			"class": button["class"],
			"video": f"/configured-video/{index}",
		}
		if label_class:
			public_button["label_class"] = label_class
		public_buttons.append(public_button)

	return jsonify({"buttons": public_buttons})


@app.get("/configured-video/<int:button_index>")
def configured_video(button_index: int):
	buttons = load_config().get("buttons")
	if not isinstance(buttons, list) or button_index >= len(buttons):
		return {"error": "No configured button exists at this index."}, 404

	settings = buttons[button_index]
	if not isinstance(settings, dict):
		raise ValueError(f"Button configuration at index {button_index} must be an object.")

	directory = settings.get("video_directory")
	filename = settings.get("video_filename")
	if not isinstance(directory, str) or not directory.strip():
		raise ValueError(f"'video_directory' for button {button_index} must be a non-empty path.")
	if not isinstance(filename, str) or not filename.strip():
		raise ValueError(f"'video_filename' for button {button_index} must be a non-empty filename.")

	video_directory = Path(directory)
	if not video_directory.is_absolute():
		video_directory = Path(__file__).parent / video_directory

	return send_from_directory(video_directory, filename)


@app.get("/Script/video.js")
def video_script():
	return send_from_directory(Path(__file__).parent / "Script", "video.js")


def open_edge(url: str) -> None:
	install_roots = (
		os.environ.get("PROGRAMFILES(X86)"),
		os.environ.get("PROGRAMFILES"),
		os.environ.get("LOCALAPPDATA"),
	)

	executable = None
	for root in install_roots:
		if not root:
			continue

		candidate = Path(root) / "Microsoft" / "Edge" / "Application" / "msedge.exe"
		if candidate.is_file():
			executable = candidate
			break

	if executable is None:
		executable = shutil.which("msedge")
	if executable is None:
		raise FileNotFoundError("Microsoft Edge executable was not found.")

	command = [str(executable), "--kiosk", url, "--edge-kiosk-type=fullscreen"]
	subprocess.Popen(command)


# serve the application and open Microsoft Edge in kiosk mode
if __name__ == "__main__":
    url = "http://127.0.0.1:5001/"
    Timer(1, open_edge, args=(url,)).start()
    app.run(host="127.0.0.1", port=5001)