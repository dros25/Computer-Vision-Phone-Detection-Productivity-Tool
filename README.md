# Computer-Vision-Phone-Detection-Productivity-Tool

I know a big problem for many people (including myself) is how much time we spend on our phones. I decided to engineer a productivity device that would take the feed from my computer's webcam to detect if I am using my phone and play an alarm if it does. It uses YOLOv8 to detect the presence of my phone and triggers a physical audio alarm wired through an Arduino to annoy me enough to put it down. This helps me have more focused and productive work sessions while avoiding the urge to pick up my phone and distract myself. 

## How it works 
- YOLOv8 (pre trained) runs real time object detection on the live webcam feed from my computer via OpenCV, looking for the "cell phone" class
- When detected, it tells the Arduino over serial communication via PySerial
- The Arduino then drives the buzzer to sound the physical alert noise

## Tech Stack
- **Vision** Python, OpenCV, Ultralytics, YOLOv8
- **Hardware bridge** PySerial
- **Firmware** Arduino (C++)

## Setup
\`\`\`bash
pip install opencv-python ultralytics pyserial
python detect.py
\`\`\`
Upload `firmware/alert.ino` to your Arduino via the Arduino IDE.

I'm hoping to try this out with other physical applications as well, like having it trigger a servo motor or a little fan 
