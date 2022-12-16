# main.py runs after boot.py

from display import disp  # import even if not used in main to instantiate disp
import wifi
import time
from lights_controller import LightsController


# Only connect to wifi when main.py is first executed, and
# not when importing
#
if __name__ == "__main__":
    pass
#     wifi.home_wifi()
#     time.sleep(10)
    LightsController().control_lights()

    # change this only
    #        |
    #        |
    #       \|/
    #        V
#     import scratch
#     from binhex import run
    
#     run()
