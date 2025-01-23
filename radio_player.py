import os
import subprocess
import streamlink
from streamlink.exceptions import PluginError, NoPluginError

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
        print("1. Play Radio Station")
        print("2. Exit")
        choice = input("Enter choice (1 or 2): ")
        print(f"User choice: {choice}")  # Debug print
        
        if choice == '1':
            url = input("Enter Radio Station URL: ")
            print(f"User URL: {url}")  # Debug print
            play_online_radio(url)
            break
        elif choice == '2':
            print("Exiting...")
            exit()
        else:
            print("Invalid choice. Try again.")
        
if __name__ == '__main__':
    while True:
        menu()