import os
import subprocess
import streamlink
from streamlink.exceptions import PluginError, NoPluginError
from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

# Global process variable for stopping playback
current_process = None

# Load stations from a JSON file
STATION_FILE = "stations.json"

def load_stations():
    if not os.path.exists(STATION_FILE):
        with open(STATION_FILE, "w") as f:
            json.dump({}, f)
    with open(STATION_FILE, "r") as f:
        return json.load(f)

def save_stations(stations):
    with open(STATION_FILE, "w") as f:
        json.dump(stations, f, indent=4)

stations = load_stations()

def get_stream_metadata(url):
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format_tags", "-of", "json", url],
            capture_output=True,
            text=True,
            timeout=10
        )
        metadata = json.loads(result.stdout)
        return metadata.get("format", {}).get("tags", {})
    except subprocess.TimeoutExpired:
        return {"error": "Metadata extraction timed out"}
    except Exception as e:
        return {"error": str(e)}

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
            metadata = get_stream_metadata(stream_url)  # Extract metadata after starting playback
            return {"message": f"Playing {url}", "metadata": metadata}, 200
        else:
            return {"error": "No stream available for this URL"}, 404
    except NoPluginError:
        try:
            current_process = subprocess.Popen(['ffplay', '-nodisp', '-autoexit', url])
            metadata = get_stream_metadata(url)
            return {"message": f"Playing {url}", "metadata": metadata}, 200
        except Exception as e:
            return {"error": f"Error: {e}"}, 500
    except PluginError as e:
        return {"error": f"Error: {e}"}, 500


@app.route('/stations', methods=['GET'])
def get_stations():
    search_query = request.args.get('search', '').lower()
    if search_query:
        filtered_stations = {
            name: url for name, url in stations.items() if search_query in name.lower()
        }
        return jsonify(filtered_stations)
    return jsonify(stations)

@app.route('/stations', methods=['POST'])
def add_station():
    data = request.json
    name = data.get('name')
    url = data.get('url')
    if not name or not url:
        return jsonify({"error": "Name and URL are required"}), 400

    stations[name] = url
    save_stations(stations)
    return jsonify({"message": f"Station {name} added successfully"}), 201

@app.route('/stations/<name>', methods=['DELETE'])
def delete_station(name):
    if name not in stations:
        return jsonify({"error": "Station not found"}), 404

    del stations[name]
    save_stations(stations)
    return jsonify({"message": f"Station {name} deleted successfully"}), 200

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
