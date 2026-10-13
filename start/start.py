
# import necessary modules
import os
import shutil
import subprocess
from pathlib import Path
from threading import Timer

from flask import Flask, send_file, send_from_directory


# static paths
app = Flask(__name__, static_folder="Style", static_url_path="/Style")
index_file = Path(__file__).with_name("index.php")
media_directory = Path(__file__).with_name("Media")


@app.get("/")
def index():
    return send_file(index_file, mimetype="text/html")


@app.get("/Media/<path:filename>")
def media(filename: str):
	return send_from_directory(media_directory, filename)


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