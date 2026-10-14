
# import necessary modules
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from threading import Timer

from flask import Flask, jsonify, send_file, send_from_directory
from waitress import serve


# static paths
app_directory = (
    Path(sys.executable).resolve().parent
    if getattr(sys, "frozen", False)
    else Path(__file__).resolve().parent
)
app = Flask(
    __name__,
    static_folder=str(app_directory / "Style"),
    static_url_path="/Style",
)
index_file = app_directory / "index.php"
media_directory = app_directory / "Media"
script_directory = app_directory / "Script"
config_file = app_directory / "config.json"


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


def get_server_address() -> tuple[str, int]:
	server = load_config().get("server", {})
	if not isinstance(server, dict):
		raise ValueError("'server' must be an object.")

	host = server.get("host", "0.0.0.0")
	port = server.get("port", 5001)
	if not isinstance(host, str) or not host.strip():
		raise ValueError("'server.host' must be a non-empty string.")
	if isinstance(port, bool) or not isinstance(port, int) or not 1 <= port <= 65535:
		raise ValueError("'server.port' must be an integer between 1 and 65535.")

	return host, port


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

# serve the configured video for a specific button index
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
		video_directory = app_directory / video_directory

	return send_from_directory(video_directory, filename)

# serve the video.js script
@app.get("/Script/video.js")
def video_script():
	return send_from_directory(script_directory, "video.js")

# open Microsoft Edge in kiosk mode with the URL
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
    server_host, server_port = get_server_address()
    url = f"http://127.0.0.1:{server_port}/"
    Timer(1, open_edge, args=(url,)).start()
    serve(app, host=server_host, port=server_port)