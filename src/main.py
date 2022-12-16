# main.py runs after boot.py

from display import disp  # import even if not used in main to instantiate disp
from lights_controller import LightsController


if __name__ == "__main__":
    LightsController().control_lights()
