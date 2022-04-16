import platform
import time
from pyvirtualdisplay import Display

if platform.system() == "Linux" :
    print("Starting virtual display")
    _display = Display(visible=0, size=(1920, 1200))  
    _display.start()
else:
    print("Virtual display is only supported on Linuxes because it uses xvfb, continuing with real display...")

while True:
    time.sleep(5)
