import pyautogui
from PIL import Image
from typing import List, Tuple

# for whatever reason, the top left pixel of the unrevealed tiles has a little
# variance to it.
tolerance = 10

# tile class
class Tile:
    def __init__(self, grid_x: int, grid_y: int, top_left_pixel_x: int, top_left_pixel_y: int):
        # grid coords
        self.x = grid_x
        self.y = grid_y

        self.rel_tl_x = grid_x * 32
        self.rel_tl_y = grid_y * 32

        self.rel_cx   = self.rel_tl_x + 20
        self.rel_cy   = self.rel_tl_y + 23
        # actual pixel coordinates
        self.top_left_pixel_x = top_left_pixel_x
        self.top_left_pixel_y = top_left_pixel_y

        self.mid_x = top_left_pixel_x + 16
        self.mid_y = top_left_pixel_y + 16

        # state flags:
        self.is_revealed: bool = False
        self.number_value: int = 0    # 0 = empty, 1–8 numbered
        self.is_flagged: bool = False

        # will be filled in by GameState._build_neighbors()
        self.neighbors: List["Tile"] = []

   # helper to determine if two colors are very similar
    def colors_close(c1: Tuple[int,int,int], c2: Tuple[int,int,int], tol: int) -> bool:
        return all(abs(a - b) <= tol for a, b in zip(c1, c2))

    def update_state_frm_pxls(self, pix, color_to_number: dict, unrevealed_color: Tuple[int,int,int], empty_color: Tuple[int,int,int]):         
        # grab colors
        color_px = pix[self.rel_cx, self.rel_cy][:3]
        top_left = pix[self.rel_tl_x + 1, self.rel_tl_y + 1][:3]

        # still unrevealed?
        if Tile.colors_close(top_left, unrevealed_color, tolerance):
            # if it happens to be the little "face" pixel, mark specially
            if color_px == (0, 0, 0):
                self.number_value = 9
            self.is_revealed = False
            return

        # revealed
        self.is_revealed = True
        if color_px == empty_color:
            self.number_value = 0
            return

        # lookup 1–8
        self.number_value = color_to_number.get(color_px, 0)


# class to track the state of the game
class GameState:
    def __init__(self, top_left_x: int, top_left_y: int, tile_size: int, cols: int, rows: int, num_mines: int = None):
        self.top_left_x = top_left_x
        self.top_left_y = top_left_y
        self.tile_size  = tile_size
        self.cols = cols
        self.rows = rows
        self.num_mines = num_mines

        # 2d list of tiles
        self.grid: List[List[Tile]] = []
        for y in range(rows):
            row: List[Tile] = []
            for x in range(cols):
                px = top_left_x + x * tile_size 
                py = top_left_y + y * tile_size
                row.append(Tile(x, y, px, py))
            self.grid.append(row)

        self.track_neighbors()

        self.color_to_number = {
            (0, 0, 246): 1,
            (51, 120, 29): 2,
            (234, 51, 35): 3,
            (0, 0, 118): 4,
            (112, 19, 11): 5,
            (53, 121, 122): 6,
            (0, 0, 0): 7
            # no 8 because i never encountered it in my testing to get its RGB vals
        }
        self.empty_color = (189, 189, 189)
        self.unrevealed_color = (255, 255, 255)

    # keep track of each tiles neighbors
    def track_neighbors(self):
        for y in range(self.rows):
            for x in range(self.cols):
                t = self.grid[y][x]
                for dy in (-1, 0, +1):
                    for dx in (-1, 0, +1):
                        if dx == 0 and dy == 0: continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.cols and 0 <= ny < self.rows:
                            t.neighbors.append(self.grid[ny][nx])

    def update_game_state(self):
        # grab the board once
        img = pyautogui.screenshot(region=(self.top_left_x, self.top_left_y, self.cols * self.tile_size, self.rows * self.tile_size))
        # get fast pixel-access map
        pix = img.load()

        # update every tile from that screenshot
        for row in self.grid:
            for tile in row:
                tile.update_state_frm_pxls(pix, self.color_to_number, self.unrevealed_color, self.empty_color)
        

    # helper that places flags
    def flag(self, x: int, y: int):
        t = self.grid[y][x]
        pyautogui.rightClick(t.mid_x, t.mid_y)
        t.is_flagged = True

    # heler that reveals a tile
    def reveal(self, x: int, y: int):
        t = self.grid[y][x]
        pyautogui.click(t.mid_x, t.mid_y)

    # prints the board in a nice format
    def print_board(self):
        for row in self.grid:
            print(" ".join( "F" if t.is_flagged else "-" if not t.is_revealed else str(t.number_value) for t in row))
