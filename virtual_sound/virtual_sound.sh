sudo modprobe snd-aloop

while true; do
    aplay -D hw:Loopback,0,0 sound.wav
done