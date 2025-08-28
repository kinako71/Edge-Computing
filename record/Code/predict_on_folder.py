"""
This script performs bird song detection on audio files in a folder by converting the audio to spectrogram images,
running the Bird Song Detector from BIRDeep project YOLO model to detect bird songs, and then transforming the predictions to time segments.

Workflow:
1. Load the YOLO model for bird song detection.
2. Clean the output folder to ensure no previous results interfere.
3. Convert the input audio files to spectrogram images.
4. Perform detection on the spectrogram images using the YOLO model.
5. Read the predictions from the output folder.
6. Transform the predictions to time segments and save the results.

Variables:
- model: The YOLO model loaded with pre-trained weights for bird song detection.
- audio_folder: Path to the folder containing input audio files.
- audio_name: Name of the audio file without the extension.
- image_path: Path to the saved spectrogram image.
- predictions_txt: Path to the text file containing the YOLO model predictions.
"""

# Import libraries
from ultralytics import YOLO
from ultralytics.utils.ops import Profile
import os
import pandas as pd

from audio_processing import save_spectrogram_from_audio, transform_coordinates_to_seconds, transform_predictions_save_segment

# Load model (Bird Song Detector from BIRDeep)
model = YOLO("/home/FYP/mohor001/Bird-Song-Detector/Models/Bird Song Detector/weights/best.pt")
# Clean the output folder
import shutil

# Clean the output folder
shutil.rmtree('runs', ignore_errors=True)

# Path to the folder containing audio files
audio_folder = "/home/FYP/mohor001/Bird-Song-Detector/Data/Audios/"

# Iterate over all audio files in the folder
for audio_file in os.listdir(audio_folder):
    if audio_file.endswith(".WAV"):
        audio_path = os.path.join(audio_folder, audio_file)
        audio_name = os.path.basename(audio_path).replace(".WAV", "")
        
        # Audio has to be converted to spectrogram and saved as image
        with Profile() as dt:
            image_path = save_spectrogram_from_audio(audio_path)
        print("Spectrogram extraction: ",dt)
        # Perform detection on the spectrogram image using the model
        model(image_path, save_txt=True, save_conf=True)
        
        # Read txt in the output folder
        predictions_txt = f"/home/FYP/mohor001/Bird-Song-Detector/Code/runs/detect/predict/labels/{audio_name}.txt"
        
        if os.path.exists(predictions_txt):
            # Convert to start_second, end_second, class, confidence score:
            transform_predictions_save_segment(audio_path, predictions_txt)
        else:
            print(f"No detections for {audio_file}")
