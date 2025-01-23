import os
import subprocess
import streamlink
from streamlink.exceptions import PluginError, NoPluginError

# Predefined Stations (can include WebSDR streams)
stations = {
    "WebSDR Example": "http://websdr.ewi.utwente.nl:8901/",
    "Study High (Chill)": "https://study-high.rautemusik.fm/",
    "Another Music Project (IDM)": "https://radio.anothermusicproject.com:8443/idm",
    "Epic Piano": "https://stream.epic-piano.com/chillout-piano",
    "Radio Science": "https://radio-science.stream.laut.fm/radio-science"
}

# Stream Online Radio
def play_online_radio(url):
    print(f"Connecting to {url}...")
    try:
        streams = streamlink.streams(url)
        if 'best' in streams:
            stream_url = streams['best'].url
            # Use ffmpeg to play audio
            subprocess.call(['ffplay', '-nodisp', '-autoexit', stream_url])
        else:
            print("No stream available for this URL.")
    except NoPluginError:
        print("Streamlink cannot handle this URL. Trying ffplay directly...")
        try:
            subprocess.call(['ffplay', '-nodisp', '-autoexit', url])
        except Exception as e:
            print(f"Error: {e}")
    except PluginError as e:
        print(f"Error: {e}")

# CLI Menu
def menu():
    while True:
        print("Radio Station Player")
        print("Select a station:")
        for idx, (name, url) in enumerate(stations.items(), start=1):
            print(f"{idx}. {name}")
        print("A. Add a custom station")
        print("X. Exit")
        
        choice = input("Enter choice (number, A, or X): ").strip().lower()
        
        if choice == 'x':
            print("Exiting...")
            exit()
        elif choice == 'a':
            add_custom_station()
        else:
            try:
                choice = int(choice)
                station_name = list(stations.keys())[choice - 1]
                station_url = stations[station_name]
                print(f"Playing {station_name}...")
                play_online_radio(station_url)
            except (ValueError, IndexError):
                print("Invalid choice. Try again.")
            
def add_custom_station():
    name = input("Enter station name: ").strip()
    url = input("Enter station URL: ").strip()
    if name and url:
        stations[name] = url
        print(f"Added {name} to stations.")
    else:
        print("Invalid name or URL. Station not added.")
        
if __name__ == '__main__':
        menu()
        
# def menu():
#     while True:
#         print("Radio Station Player")
#         print("1. Play Radio Station")
#         print("2. Exit")
#         choice = input("Enter choice (1 or 2): ")
#         print(f"User choice: {choice}")  # Debug print
        
#         if choice == '1':
#             url = input("Enter Radio Station URL: ")
#             print(f"User URL: {url}")  # Debug print
#             play_online_radio(url)
#             break
#         elif choice == '2':
#             print("Exiting...")
#             exit()
#         else:
#             print("Invalid choice. Try again.")
        
# if __name__ == '__main__':
#     while True:
#         menu()