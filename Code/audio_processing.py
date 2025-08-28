# Import libraries
import pandas as pd
import librosa
import os
import matplotlib.pyplot as plt
import numpy as np
from pydub import AudioSegment
from PIL import Image
from ultralytics.utils.ops import Profile

@Profile()
def save_spectrogram_from_audio(audio_file):
    """
    Generate a spectrogram image from an audio file and save it to the Images folder."
    """

    y, sr = librosa.load(audio_file, sr=16000)
    
    # Create the output path for the image
    output_image_path = audio_file.replace('Audios', 'Images').replace(".WAV", ".PNG")
    output_image_path = audio_file.replace('Audios', 'Images').replace(".wav", ".PNG")
    
    # Ensure the output folder exists
    os.makedirs(os.path.dirname(output_image_path), exist_ok=True)
    
    # Define the frequency range
    fmin = 1
    fmax = 16000

    fig, ax = plt.subplots(figsize=(12, 6))  # Set the background color to black
    D = librosa.amplitude_to_db(librosa.stft(y), ref=np.max)
    librosa.display.specshow(D, sr=sr, x_axis="time", y_axis="log", fmin=fmin, fmax=fmax, ax=ax)  # Specify frequency range
    ax.axis('off')  # Remove axes

    # Save the figure using the output_image_path
    fig.savefig(output_image_path, bbox_inches='tight', pad_inches=0, transparent=True)
    
    # Close the figure to release memory resources
    plt.close(fig)

    return output_image_path

@Profile()
def transform_coordinates_to_seconds(audio_path, prediccion_txt_path):
    image_path = audio_path.replace('Audios', 'Images').replace(".WAV", ".PNG")
    image_path = audio_path.replace('Audios', 'Images').replace(".wav", ".PNG")
    # Read image size
    with Image.open(image_path) as img:
        WIDTH, _ = img.size
    
    # Read predictions file
    with open(prediccion_txt_path, 'r') as file:
        predictions = file.readlines()
    
    # Load original audio
    audio = AudioSegment.from_wav(audio_path)
    
    # Audio duration in ms
    audio_duration_ms = len(audio)
    # To seconds
    audio_duration_sec = audio_duration_ms / 1000
    
    # Process each prediction
    for i, line in enumerate(predictions):
        _, x_center, _, width, _, score = map(float, line.split())
        
        # Denormalize coordinates
        x_center_desnorm = x_center * WIDTH
        width_desnorm = width * WIDTH

        # Convert image coordinates to audio seconds
        start_sec = (x_center_desnorm - width_desnorm / 2) * 60 / WIDTH
        end_sec = (x_center_desnorm + width_desnorm / 2) * 60 / WIDTH
        
        # Ensure the segment is within the audio duration
        start_sec = max(0, min(start_sec, audio_duration_sec))
        end_sec = max(0, min(end_sec, audio_duration_sec))

        print(f"Detection {i+1}: From {start_sec:.2f} to {end_sec:.2f} seconds ({score:.2f})")

@Profile()
def transform_predictions_save_segment(audio_path, prediccion_txt_path):
    image_path = audio_path.replace('Audios', 'Images').replace(".WAV", ".PNG")
    image_path = audio_path.replace('Audios', 'Images').replace(".wav", ".PNG")
    # Read image size
    with Image.open(image_path) as img:
        WIDTH, _ = img.size
    
    # Read predictions file
    with open(prediccion_txt_path, 'r') as file:
        predictions = file.readlines()
    
    # Load original audio
    audio = AudioSegment.from_wav(audio_path)
    
    # Audio duration in ms
    audio_duration_ms = len(audio)
    # To seconds
    audio_duration_sec = audio_duration_ms / 1000
    
    # Process each prediction
    for i, line in enumerate(predictions):
        _, x_center, _, width, _, score = map(float, line.split())
        
        # Denormalize coordinates
        x_center_desnorm = x_center * WIDTH
        width_desnorm = width * WIDTH

        # Convert image coordinates to audio seconds
        start_sec = (x_center_desnorm - width_desnorm / 2) * 60 / WIDTH
        end_sec = (x_center_desnorm + width_desnorm / 2) * 60 / WIDTH
        
        # Ensure the segment is within the audio duration
        start_sec = max(0, min(start_sec, audio_duration_sec))
        end_sec = max(0, min(end_sec, audio_duration_sec))

        # To ms
        start_msec = start_sec * 1000
        end_msec = end_sec * 1000
        
        # Segment audio
        segment = audio[start_msec:end_msec]

        output_path = audio_path.replace('Audios', 'Segments').replace(".WAV", f"_{start_sec:.2f}_{end_sec:.2f}_{score:.2f}.WAV")
        output_path = audio_path.replace('Audios', 'Segments').replace(".wav", f"_{start_sec:.2f}_{end_sec:.2f}_{score:.2f}.wav")
        output_folder = os.path.dirname(output_path)

        # If output_folder does not exist, create it
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        # Save the segment
        segment.export(output_path, format="wav")

        print(f"Detection {start_sec:.2f} - {end_sec:.2f} seconds ({score:.2f}) saved as {output_path}")
        
        # print(f"Saved segment {i}: {output_path} ({start_sec:.2f}s - {end_sec:.2f}s)")