import subprocess

file = "/home/jetson/Bird-Song-Detector/runs/detect/predict/labels/AM1_20230511_060000.txt"
command = 'ffmpeg -i {} -af "atrim=start={}:end={}1,asetpts=PTS-STARTPTS" data/output_{}.wav'
total = 0
with open(file) as f:
    for i, line in enumerate(f):
        items = line.split()
        center = float(items[1])
        span = float(items[3])
        total += span*60
        start = round(60 * (center - span/2), 3)
        end = round(60 * (center + span/2), 3)
        print(i, start, end)
        trim_command = command.format("AM1_20230511_060000.wav", start, end, i)
        subprocess.run(trim_command, shell=True)
print(total)