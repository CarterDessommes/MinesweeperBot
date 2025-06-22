import random
import time
import pyautogui
from mss import mss

# initial testing program to get pyauto gui and all the pixels lined up.
# feel free to play around with this also!

# set for https://minesweeperonline.com/, with display settings set to left and zoom
# at 200%.

top_left_x, top_left_y = 260, 258
tile_size = 32

grid_w, grid_h = 16, 16

# loss-detector coords & target RGB
frown_x, frown_y = 509, 214 # small 397, 214 #large #732
frown_rgb = (64, 64, 21)

# win-detector coords & target RGB
shades_x, shades_y = 516, 201 # small 404, 201 
shades_rgb = (0, 0, 0)


def click_randomly(duration_seconds):
    start = time.time()
    games = 1
    with mss() as sct:  # instantiate once :contentReference[oaicite:2]{index=2}
        while time.time() - start < duration_seconds:
            # click a random cell
            rx = random.randint(top_left_x, top_left_x + tile_size * grid_w - 1)
            ry = random.randint(top_left_y, top_left_y + tile_size * grid_h - 1)
            cx, cy = rx + tile_size // 2, ry + tile_size // 2
            pyautogui.click(cx, cy)

            # loss detection: grab exactly one pixel :contentReference[oaicite:3]{index=3}
            shot = sct.grab({'top': frown_y, 'left': frown_x, 'width': 1, 'height': 1})
            if shot.pixel(0, 0) == frown_rgb:  # ScreenShot.pixel returns (R,G,B) :contentReference[oaicite:4]{index=4}
                games += 1
                pyautogui.click(frown_x, frown_y)
                print(f"{games}")
                continue

            # win detection: another 1×1 grab
            shot = sct.grab({'top': shades_y, 'left': shades_x, 'width': 1, 'height': 1})
            if shot.pixel(0, 0) == shades_rgb:
                print("winner!!!!!!!")
                break