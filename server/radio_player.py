import os
import subprocess
import streamlink
from streamlink.exceptions import PluginError, NoPluginError
from flask import Flask, request, jsonify
from flask_cors import CORS
import signal

app = Flask(__name__)
CORS(app)

# Global process variable for stopping playback
current_process = None

stations = {
    "Study High": "https://study-high.rautemusik.fm/",
    "IDM Project": "https://radio.anothermusicproject.com:8443/idm",
    "Chillout Piano": "https://stream.epic-piano.com/chillout-piano",
    "Radio Science": "https://radio-science.stream.laut.fm/radio-science",
}

# Stream Online Radio
def play_online_radio(url):
    global current_process

    # Stop any existing ffplay processes
    if current_process:
        try:
            current_process.terminate()
            current_process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            current_process.kill()
        current_process = None

    # Ensure no other ffplay processes are lingering
    if os.name == "nt":  # Windows
        subprocess.call(["taskkill", "/F", "/IM", "ffplay.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:  # Unix-based systems
        subprocess.call(["pkill", "-f", "ffplay"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Start the new process
    try:
        streams = streamlink.streams(url)
        if 'best' in streams:
            stream_url = streams['best'].url
            current_process = subprocess.Popen(['ffplay', '-nodisp', '-autoexit', stream_url])
            return {"message": f"Playing {url}"}, 200
        else:
            return {"error": "No stream available for this URL"}, 404
    except NoPluginError:
        try:
            current_process = subprocess.Popen(['ffplay', '-nodisp', '-autoexit', url])
            return {"message": f"Playing {url}"}, 200
        except Exception as e:
            return {"error": f"Error: {e}"}, 500
    except PluginError as e:
        return {"error": f"Error: {e}"}, 500

    
# API Endpoints
@app.route('/stations', methods=['GET'])
def get_stations():
    search_query = request.args.get('search', '').lower()
    if search_query:
        filtered_stations = {
            name: url for name, url in stations.items() if search_query in name.lower()
        }
        return jsonify(filtered_stations)
    return jsonify(stations)
   
@app.route('/play', methods=['POST'])
def api_play():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400
    response, status_code = play_online_radio(url)
    return jsonify(response), status_code

@app.route('/stop', methods=['POST'])
def api_stop():
    global current_process
    if current_process:
        try:
            # Terminate the process if it exists
            current_process.terminate()
            current_process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            current_process.kill()
        current_process = None

    # Ensure all ffplay processes are stopped
    if os.name == "nt":  # Windows
        subprocess.call(["taskkill", "/F", "/IM", "ffplay.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:  # Unix-based systems
        subprocess.call(["pkill", "-f", "ffplay"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return jsonify({"message": "Playback stopped"}), 200

@app.route('/health', methods=['GET'])
def api_health():
    return jsonify({"status": "running"}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
