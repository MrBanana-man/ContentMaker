import os
import re
import random
import tkinter as tk
from tkinter import ttk
from PIL import ImageGrab
from elevenlabs import save
from mutagen.mp3 import MP3
from elevenlabs.client import ElevenLabs
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips, AudioFileClip, concatenate_audioclips

client = ElevenLabs(
  api_key=""  # Replace with your actual API key
)

# Dictionary to map users to voices
user_voices = {
    "User 1": "Rachel",  # Replace with the voice you want for User 1
    "User 2": "Alice"    # Replace with the voice you want for User 2
}

# Predefined script as a list of tuples (sender, message)
script = [
    ("User 2", "Hello, how are you?"),
    ("User 2", "I'm good, thank you! How about you?"),
    ("User 1", "I'm doing well too."),
    ("User 2", "That's great to hear."),
    ("User 2", "This is a longer message to test the height adjustment."),
    ("User 1", "Yes, we need to make sure all the messages fit properly."),
    ("User 2", "and we need to make sure some messages fit properly"),
    ("User 1", "and we need to make sure some messages fit properly"),
    ("User 2", "and we need to make sure some messages fit properly"),
    ("User 1", "and we need to make sure some messages fit properly"),
    ("User 2", "and we need to make sure some messages fit properly"),
    ("User 1", "and we need to make sure some messages fit properly"),
    ("User 2", "and we need to make sure some messages fit properly"),
    ("User 1", "and we need to make sure some messages fit properly"),
]

# Directory paths
Vdirectory = r'C:\Programing\PYTHON\Projects\ContentMaker\Bvideo'
image_directory = r"C:\Programing\PYTHON\Projects\ContentMaker\Mpic"
audio_directory = r"C:\Programing\PYTHON\Projects\ContentMaker\Raudio"
FINAL_directory = r"C:\Programing\PYTHON\Projects\ContentMaker\FinishedOutput"

current_script_index = 0
ScreenShot_Loop = 0
messages_per_window = 6  # New window every 6 messages

def delete_files_in_folders(folder1, folder2, folder3):
    def delete_files_in_folder(folder_path):
        try:
            # List all files in the folder
            files = os.listdir(folder_path)
            
            for file in files:
                file_path = os.path.join(folder_path, file)
                # Check if it's a file (not a directory)
                if os.path.isfile(file_path):
                    os.remove(file_path)  # Delete the file
                    #print(f"Deleted: {file_path}")
                    
            print(f"All files deleted successfully from {folder_path}")
        
        except Exception as e:
            print(f"Error while processing {folder_path}: {e}")

    # Call the deletion function for both folders
    delete_files_in_folder(folder1)
    delete_files_in_folder(folder2)
    delete_files_in_folder(folder3)

def choose_random_file(directory):
    try:
        # Get a list of files in the directory
        files = [file for file in os.listdir(directory) if os.path.isfile(os.path.join(directory, file))]
        
        # Check if directory contains any files
        if not files:
            return "No files found in the directory."
        
        # Choose a random file from the list
        random_file = random.choice(files)
        full_name = f"{Vdirectory}\{random_file} "
        return full_name
    
    except FileNotFoundError:
        return "The specified directory does not exist."
    
def get_mp3_durations(directory):
    durations = []
    
    for filename in os.listdir(directory):
        if filename.lower().endswith(".mp3"):
            try:
                file_path = os.path.join(directory, filename)
                audio = MP3(file_path)
                duration = audio.info.length
                durations.append((filename, duration))
            except Exception as e:
                print(f"Could not process {filename}: {e}")
    
    return durations

def edit_video():
    
    video_path = choose_random_file(Vdirectory)
    print(video_path)
    
    # Load the video
    video = VideoFileClip(video_path)

    # Get MP3 durations
    mp3_durations = get_mp3_durations(audio_directory)

    # List to hold the final video clips
    final_clips = []

    # Get the list of image files
    image_files = [f for f in os.listdir(image_directory) if f.endswith(('.png', '.jpg', '.jpeg'))]

    # Custom sort function to sort by numeric values in filenames
    def sort_key(filename):
        numbers = re.findall(r'\d+', filename)
        return tuple(map(int, numbers))

    # Sort image and audio files
    image_files = sorted(image_files, key=sort_key)
    mp3_durations = sorted(mp3_durations, key=lambda x: sort_key(x[0]))

    # Ensure there are enough MP3 durations for the images
    if len(mp3_durations) < len(image_files):
        raise ValueError("Not enough MP3 files for the number of images. Please add more MP3 files.")

    # Initialize the start time for video
    start_time = 0

    # Iterate over the sorted list of images and MP3 durations
    for image_file, (audio_filename, audio_duration) in zip(image_files, mp3_durations):
        image_path = os.path.join(image_directory, image_file)
        image = ImageClip(image_path).resize(width=int(ImageClip(image_path).w * 1.5))

        image_display_duration = audio_duration
        image = image.set_duration(image_display_duration).set_position("center")
        
        # Create a clip that includes both the video and the image overlay for the duration of the image
        image_clip = CompositeVideoClip([video.subclip(start_time, start_time + image_display_duration), image])
        
        # Append this clip to the list of final clips
        final_clips.append(image_clip)
        
        # Update the start time for the next image
        start_time += image_display_duration

    # Concatenate all the image clips to create the final video
    final_video = concatenate_videoclips(final_clips)

    # Process audio files
    audio_files = [f for f in os.listdir(audio_directory) if f.endswith('.mp3')]
    audio_files = sorted(audio_files, key=sort_key)

    # List to hold the audio clips
    audio_clips = []

    # Iterate over the sorted list of audio files
    for audio_file in audio_files:
        audio_path = os.path.join(audio_directory, audio_file)
        audio_clip = AudioFileClip(audio_path)
        audio_clips.append(audio_clip)

    # Concatenate all audio clips into a single audio track
    final_audio = concatenate_audioclips(audio_clips)

    # Set the audio of the video to the final concatenated audio
    video_with_audio = final_video.set_audio(final_audio)

    # Write the result to a file
    video_with_audio.write_videofile("C:\Programing\PYTHON\Projects\ContentMaker\FinishedOutput\FINALOUTPUT.mp4", codec="libx264", fps=60)

    # Close clips
    video.close()
    final_audio.close()

def getRvoice():

    # Generate audio for each message in the script
    for i, (user, message) in enumerate(script):
        # Generate audio using the user's voice
        audio = client.generate(
            text=message,
            voice=user_voices.get(user, "Rachel")  # Default to Rachel if user not in the dictionary
        )
        
        # Save the audio file
        output_path = f"C:\Programing\PYTHON\Projects\ContentMaker\Raudio\output_message_{i + 1}.mp3"
        save(audio, output_path)
        #print(f"Saved {user}'s message: '{message}' to {output_path}")

#* DO NOT TOUCH
def take_screenshot(window, count):
    # Schedule the screenshot to be taken after a slight delay (500ms in this case)
    window.after(500, lambda: capture_screenshot(window, count))

def capture_screenshot(window, count):
    try:
        # Update to get current window dimensions after resizing
        window.update_idletasks()  # Ensure the window is updated
        x = window.winfo_rootx()
        y = window.winfo_rooty()
        width = window.winfo_width()
        height = window.winfo_height()

        # Capture the region specified by the window coordinates
        screenshot = ImageGrab.grab(bbox=(x, y, x + width - 20, y + height - 10))
    
        # Save the screenshot to a file
        screenshot.save(f"C:\Programing\PYTHON\Projects\ContentMaker\Mpic\screenshot{count}.png")
        print(f"Screenshot saved as screenshot{count}.png")

    except Exception as e:
        print(f"An error occurred: {e}")

def create_new_window():
    global current_script_index
    if current_script_index >= len(script):
        return  # Stop if all messages have been sent

    # Create a new window for the next set of messages
    window = tk.Tk()
    window.title(f"Messaging App Window {current_script_index // messages_per_window + 1}")
    window.configure(bg="#000000")

    chat_frame = tk.Frame(window, bg="#000000")
    chat_frame.grid(row=0, column=0, padx=0, pady=5)

    chat_canvas = tk.Canvas(chat_frame, bg="#000000", width=300, height=1080, bd=0, highlightthickness=0)
    chat_canvas.pack(side="left", fill="both", expand=True)

    def display_next_message():
        nonlocal window, chat_canvas
        global current_script_index, ScreenShot_Loop
        
        if current_script_index < len(script):
            sender, message = script[current_script_index]
            frame = tk.Frame(chat_canvas, bg="#000000")
            bubble_color = "#4CAF50" if sender == "User 1" else "#3E3E3E"
            text_color = "#FFFFFF"

            bubble_frame = tk.Frame(frame, bg=bubble_color, bd=5, padx=5, pady=2)
            bubble_frame.pack(side='right' if sender == "User 1" else 'left', anchor='e' if sender == "User 1" else 'w', padx=5, pady=5)

            message_label = tk.Label(bubble_frame, text=message, bg=bubble_color, fg=text_color, font=("Helvetica", 10), wraplength=200)
            message_label.pack()

            chat_canvas.create_window((10, chat_canvas.bbox("all")[3] + 20 if chat_canvas.bbox("all") else 10), window=frame, anchor='nw', width=chat_canvas.winfo_width() - 20)

            chat_canvas.config(scrollregion=chat_canvas.bbox("all"))
            chat_canvas.yview_moveto(1)

            current_script_index += 1
            ScreenShot_Loop += 1

            # Adjust window height dynamically
            adjust_window_height(window, chat_canvas)
            
                        
            # Check if 6 messages have been displayed; if so, close the window and create a new one
            if (current_script_index % messages_per_window == 0 or current_script_index >= len(script)):
                window.after(1000, lambda: (window.destroy(), create_new_window()))  # Delay before closing and creating new window
            else:
                window.after(1000, display_next_message)  # Continue displaying messages in the same window
    
    def adjust_window_height(window, chat_canvas):
        chat_frame.update_idletasks()
        canvas_height = chat_canvas.bbox("all")[3] + 20  # Get the total height of all messages and add padding
        window.geometry(f"{window.winfo_width()}x{canvas_height + 5}")  # Update the window height with extra padding
        take_screenshot(window, ScreenShot_Loop)

    # Start displaying messages in this window
    display_next_message()
    
    window.mainloop()


#* Start the first window 
#* create_new_window()
#* getRvoice()
#* edit_video()
#* delete_files_in_folders(image_directory, audio_directory, FINAL_directory)
