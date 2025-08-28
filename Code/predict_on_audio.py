"""
This script performs bird song detection on an audio file by converting the audio to a spectrogram image,
running the Bird Song Detector from BIRDeep project YOLO model to detect bird songs, and then transforming the predictions to time segments.

Workflow:
1. Load the YOLO model for bird song detection.
2. Clean the output folder to ensure no previous results interfere.
3. Convert the input audio file to a spectrogram image.
4. Perform detection on the spectrogram image using the YOLO model.
5. Read the predictions from the output folder.
6. Transform the predictions to time segments and save the results.

Variables:
- model: The YOLO model loaded with pre-trained weights for bird song detection.
- audio_path: Path to the input audio file.
- audio_name: Name of the audio file without the extension.
- image_path: Path to the saved spectrogram image.
- predictions_txt: Path to the text file containing the YOLO model predictions.
"""

# Import libraries
from ultralytics import YOLO
import os
import numpy as np
import pandas as pd
from ultralytics.utils.ops import Profile
from audio_processing import save_spectrogram_from_audio, transform_coordinates_to_seconds, transform_predictions_save_segment
import librosa
import soundfile as sf
from zipfile import ZipFile
import tempfile
import sys
import time 
import glob

import subprocess
from multiprocessing import Process

model = YOLO("./Bird-Song-Detector/Models/Bird Song Detector/weights/best.pt")
brank = np.zeros((320, 640, 3), dtype=np.uint8)
_ = model(brank)
# model.to("cuda")
print("Model device:", next(model.model.parameters()).device)

def extract_segments_and_save_zip_from_txt(audio_path: str, segments_txt_path: str, output_zip_path: str = None):
    """
    Extracts audio segments based on a .txt file containing start_second, end_second, class, and confidence.
    Saves all extracted segments as .wav files in a zip archive.

    Args:
        audio_path (str): Path to the original audio file.
        segments_txt_path (str): Path to the TXT file with transformed predictions.
        output_zip_path (str, optional): Path to the output ZIP file. Defaults to <audio_name>_segments.zip.
    """
    if not os.path.exists(audio_path):
        print(f"Audio file not found: {audio_path}")
        return
    if not os.path.exists(segments_txt_path):
        print(f"Prediction TXT file not found: {segments_txt_path}")
        return

    audio_name = os.path.basename(audio_path).rsplit('.', 1)[0]
    output_zip_path = output_zip_path or f"./runs/detect/predict/{audio_name}_segments.zip"

    # Load audio
    y, sr = librosa.load(audio_path, sr=None)

    # Read segments
    segments = []
    with open(segments_txt_path, 'r') as f:
        for idx, line in enumerate(f):
            parts = line.strip().split()
            if len(parts) < 4:
                continue  # Skip malformed lines
            start, end, cls, conf = map(float, parts[:4])
            segments.append((idx, start, end, int(cls), conf))

    if not segments:
        print("No valid segments found.")
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        wav_paths = []
        for idx, start, end, cls, conf in segments:
            segment = y[int(start * sr):int(end * sr)]
            filename = f"{audio_name}_segment_{idx}_class{cls}_conf{conf:.2f}.wav"
            out_path = os.path.join(tmpdir, filename)
            sf.write(out_path, segment, sr)
            wav_paths.append(out_path)

        with ZipFile(output_zip_path, 'w') as zipf:
            for wav_file in wav_paths:
                zipf.write(wav_file, os.path.basename(wav_file))

    print(f"Extracted {len(wav_paths)} segments and saved to: {output_zip_path}")

def run(audio_path):
    # Load model (Bird Song Detector from BIRDeep)
    
    # Clean the output folder
    import shutil

    # Clean the output folder
    shutil.rmtree('runs', ignore_errors=True)

    audio_name = os.path.basename(audio_path).replace(".wav", "")
    # Audio has to be converted to spectrogram and saved as image
    with Profile() as dt:
        image_path = save_spectrogram_from_audio(audio_path)
    print("Spectrogram extraction: ",dt)

    with Profile() as dtmodel:
        model(image_path, save_txt=True, save_conf=True)
    print("Model extraction: ",dtmodel)
    # Read txt in the output folder
    predictions_txt = f"./runs/detect/predict/labels/{audio_name}.txt"

    if os.path.exists(predictions_txt):
        # Convert to start_second, end_second, class, confidence score:
        transform_predictions_save_segment(audio_path, predictions_txt)
        extract_segments_and_save_zip_from_txt(audio_path, predictions_txt)

    else:
        print(f"No detections for {audio_path}")

def upload():
    subprocess.run(["bash", "./upload.sh"])

def move_file(filename):
    filename_new = filename.replace("_temp", "").replace("Segments/", "").replace("wav", "flac")
    print(filename, filename_new)
    subprocess.run(["bash", "convert.sh", filename, filename_new])

if __name__ == "__main__":
    target_dir = "./data_temp/Audios/"
    result_dir = "./data_temp/Segments/"

    count = 10
    while True:
        if count > 9:
            count = 0
            p = Process(target=upload, args=())
            p.start()
        
        files = os.listdir(target_dir)
        if len(files) == 1:
            print("Now recording...")
            time.sleep(30)
            continue
        
        files = [file for file in files if file.endswith(".wav")]
        files.sort()

        files = files[:-1] # remove the last file
        for file in files:
            file = os.path.join(target_dir, file)
            run(file)
            delete_files = glob.glob(file.replace(".wav", "*"))
            for delete_file in delete_files:
                os.remove(delete_file)
            print("Process finished of", file)
            os.remove(file.replace("Audios", "Images").replace("wav", "PNG"))
            count += 1

        files = os.listdir(result_dir)
        for file in files:
            print(result_dir + file)
            p = Process(target=move_file, args=(result_dir + file,))
            p.start()
        
        time.sleep(1)

        

    # if len(sys.argv) > 1:
    #     run(sys.argv[1])
    # else:
    #     # run("/home/jetson/Bird-Song-Detector/Data/Audios/AM1_20230511_060000.wav")
    #     # run("/home/jetson/Bird-Song-Detector/Data/Audios/AM1_20230510_073000.wav")
    #     run("/home/jetson/record/AM1_20230511_060000.wav")
