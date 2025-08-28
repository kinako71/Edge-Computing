import subprocess
from datetime import datetime
import time  # Add this to control the loop timing
from multiprocessing import Process

def upload():
    subprocess.run(["bash", "upload.sh"])

def upload_file(filename):
    subprocess.run(["bash", "upload_file.sh", filename])

def move_file(filename):
    filename_new = filename.replace("_temp", "").replace("wav", "flac")
    print(filename, filename_new)
    subprocess.run(["bash", "convert.sh", filename, filename_new])
    # filename_new = filename.replace("_temp", "")
    # subprocess.run(["mv", filename, filename_new])

minutes = 30
while True:
    for i in range(minutes):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"data_temp/Audios/{timestamp}.wav"

        command = [
            "arecord",
            "--device", "hw:Loopback,1,0",
            "--rate", "32000",
            "--format", "S16_LE",
            "--channels", "1",
            "--duration", "60",
            filename
        ]

        # command = [
        #     "arecord",
        #     "--device", "hw:0,0",
        #     "--rate", "44100",
        #     "--format", "S16_LE",
        #     "--channels", "2",
        #     "--duration", "60",
        #     filename
        # ]

        subprocess.run(command)
        # p = Process(target=move_file, args=(filename,))
        # p.start()
        
    # p = Process(target=upload, args=())
    # p.start()


    
