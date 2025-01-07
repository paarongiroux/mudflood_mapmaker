import tkinter as tk
import json

GRID_SIZE = 16  # Number of rows and columns
TILE_SIZE = 30  # Size of each tile in pixels
WALL_HEIGHT = 5  # Height of the wall

directionCodes = {
    "north": 0,
    "east": 1,
    "south": 2,
    "west": 3
}

class CheckerboardApp:
    def __init__(self, root):
        self.root = root

        # Add side panel for wall direction selection
        self.side_panel = tk.Frame(root)
        self.side_panel.pack(side=tk.RIGHT, fill=tk.Y)

        self.wall_direction = tk.StringVar(value="north")  # Default direction

        # Radio buttons for wall direction
        directions = ["north", "east", "south", "west", "full"]
        for direction in directions:
            rb = tk.Radiobutton(self.side_panel, text=direction.capitalize(), variable=self.wall_direction, value=direction)
            rb.pack(anchor="w")

        # Buttons for save and load
        self.save_button = tk.Button(self.side_panel, text="Save Map", command=self.save_map)
        self.save_button.pack(pady=5)

        self.load_button = tk.Button(self.side_panel, text="Load Map", command=self.load_map)
        self.load_button.pack(pady=5)

        self.load_button = tk.Button(self.side_panel, text="Clear Map", command=self.clear_map)
        self.load_button.pack(pady=5)

        # Canvas for the checkerboard
        self.canvas = tk.Canvas(root, width=GRID_SIZE * TILE_SIZE, height=GRID_SIZE * TILE_SIZE)
        self.canvas.pack(side=tk.LEFT)

        self.tiles = {}  # To store references to tile rectangles

        self.create_checkerboard()

    def create_checkerboard(self):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x1 = col * TILE_SIZE
                y1 = row * TILE_SIZE
                x2 = x1 + TILE_SIZE
                y2 = y1 + TILE_SIZE
                color = "white" if (row + col) % 2 == 0 else "black"

                tile = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")
                self.tiles[tile] = {"row": row, "col": col, "walls": {"north": False, "east": False, "south": False, "west": False}, "full": False}

                self.canvas.tag_bind(tile, "<Button-1>", lambda event, t=tile: self.on_tile_click(t))

    def on_tile_click(self, tile):
        tile_data = self.tiles[tile]
        row, col = tile_data["row"], tile_data["col"]

        direction = self.wall_direction.get()

        x1 = col * TILE_SIZE
        y1 = row * TILE_SIZE
        x2 = x1 + TILE_SIZE
        y2 = y1 + TILE_SIZE

        if direction == "full":
            if tile_data["full"]:
                self.canvas.itemconfig(tile, fill="white" if (row + col) % 2 == 0 else "black")
                tile_data["full"] = False
            else:
                self.canvas.itemconfig(tile, fill="red")
                tile_data["full"] = True
            return

        # Handle wall placement or removal
        wall = tile_data["walls"].get(direction)
        if wall:
            # Wall exists, remove it
            self.canvas.delete(wall)
            tile_data["walls"][direction] = None
        else:
            # Draw the wall
            if direction == "north":
                wall = self.canvas.create_rectangle(x1, y1, x2, y1 + WALL_HEIGHT, fill="red", outline="red")
            elif direction == "east":
                wall = self.canvas.create_rectangle(x2 - WALL_HEIGHT, y1, x2, y2, fill="red", outline="red")
            elif direction == "south":
                wall = self.canvas.create_rectangle(x1, y2 - WALL_HEIGHT, x2, y2, fill="red", outline="red")
            elif direction == "west":
                wall = self.canvas.create_rectangle(x1, y1, x1 + WALL_HEIGHT, y2, fill="red", outline="red")
            tile_data["walls"][direction] = wall

    def coordsToInt(self, coords):
        return coords[0] * GRID_SIZE + coords[1]
    
    def intToCoords(self, num):
        return [num // GRID_SIZE, num % GRID_SIZE]

    def save_map(self):
        map_data = {}
        for tile, data in self.tiles.items():
            coords = [data["row"], data["col"]]
            
            wallsData = data["walls"]
            itemsList = []
            if data["full"]:
                itemsList.append(4)
            else:
                if wallsData["north"]:
                    itemsList.append(0)
                if wallsData["east"]:
                    itemsList.append(1)
                if wallsData["south"]:
                    itemsList.append(2)
                if wallsData["west"]:
                    itemsList.append(3)
                
            if len(itemsList) > 0:
                map_data[self.coordsToInt(coords)] = itemsList

        with open("map_data.json", "w") as file:
            json.dump(map_data, file)
        print("Map saved to map_data.json")

    def clear_map(self):
        for tile in self.tiles.keys():
            tile_data = self.tiles[tile]
            if tile_data["full"]:
                self.canvas.itemconfig(tile, fill="white" if tile % 2 == 0 else "black")
                tile_data["full"] = False
            walls = tile_data["walls"]
            for wallKey in walls.keys():
                wall = walls[wallKey]
                if wall:
                    self.canvas.delete(wall)
                    tile_data["walls"][wallKey] = False

    def load_map(self):
        self.clear_map()

        try:
            with open("map_data.json", "r") as file:
                map_data = json.load(file)

            for tile, data in self.tiles.items():
                row, col = data["row"], data["col"]
                tile_key = str(self.coordsToInt([row, col]))
                if tile_key in map_data:
                    tile_info = map_data[tile_key]

                    # Update tile full state
                    tileFull = False
                    if 4 in tile_info:
                        self.canvas.itemconfig(tile, fill="red")
                        tileFull = True
                        

                    data["full"] = tileFull

                    tile_data = self.tiles[tile]
                    tile_data["full"] = tileFull
                    
                    # Update walls
                    for direction in tile_info:
                        if direction == 0:
                            data["walls"]["north"] = True
                        elif direction == 1:
                            data["walls"]["east"] = True
                        elif direction == 2:
                            data["walls"]["south"] = True
                        elif direction == 3:
                            data["walls"]["west"] = True
                        else: 
                            continue
                        
                        x1 = col * TILE_SIZE
                        y1 = row * TILE_SIZE
                        x2 = x1 + TILE_SIZE
                        y2 = y1 + TILE_SIZE
                
                        wall = tile_data["walls"].get(direction)
                        if direction == 0: #north
                            wall = self.canvas.create_rectangle(x1, y1, x2, y1 + WALL_HEIGHT, fill="red", outline="red")
                            tile_data["walls"]["north"] = wall
                        elif direction == 1: #east
                            wall = self.canvas.create_rectangle(x2 - WALL_HEIGHT, y1, x2, y2, fill="red", outline="red")
                            tile_data["walls"]["east"] = wall
                        elif direction == 2: # south
                            wall = self.canvas.create_rectangle(x1, y2 - WALL_HEIGHT, x2, y2, fill="red", outline="red")
                            tile_data["walls"]["south"] = wall
                        elif direction == 3: # west
                            wall = self.canvas.create_rectangle(x1, y1, x1 + WALL_HEIGHT, y2, fill="red", outline="red")
                            tile_data["walls"]["west"] = wall

                        # tile_data["walls"][direction] = wall
            print("Map loaded from map_data.json")
        except FileNotFoundError:
            print("No saved map found.")

if __name__ == "__main__":
    root = tk.Tk()
    app = CheckerboardApp(root)
    root.mainloop()
