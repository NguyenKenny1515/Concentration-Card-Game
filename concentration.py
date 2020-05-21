# ----------------------------------------------------------------------
# Name:        concentration
# Purpose:     Implement a single player matching game
#
# Author(s): Kenny Nguyen
# ----------------------------------------------------------------------
"""
A single player matching game.

usage: matchit.py [-h] [-f] {blue,green,magenta} image_folder
positional arguments:
  {blue,green,magenta}  What color would you like for the player?
  image_folder          What folder contains the game images?

optional arguments:
  -h, --help            show this help message and exit
  -f, --fast            Fast or slow game?
"""
import tkinter
import os
import random
import argparse


class MatchGame(object):
    """
    GUI Game class for a matching game.

    Arguments:
    parent: the root window object
    player_color (string): the color to be used for the matched tiles
    folder (string): the folder containing the images for the game
    delay (integer) how many milliseconds to wait before flipping a tile

    Attributes:
    canvas (tkinter.Canvas): the widget defining the area to be painted
    score (integer): the player's score
    turns (integer): total number of turns player has made
    image_names (list): contains image names corresponding to folder
    image_dict (dictionary): key is image name, value is its PhotoImage
    delay (integer): how many milliseconds to wait before flipping a tile
    remaining_tiles (integer): number of remaining tiles
    """

    def __init__(self, parent, player_color, folder, delay):
        self.turns = 0
        self.delay = 1000 if delay else 3000
        self.remaining_tiles = 16
        self.color = player_color

        parent.title('Match it!')

        # Get image names and map each image name to a PhotoImage object
        folder_images = [name for name in os.listdir(folder) if
                         os.path.splitext(name)[-1] == ".gif"]
        self.image_names = 2 * folder_images
        self.image_dict = {name: tkinter.PhotoImage(file=os.path.join(
            folder, name)) for name in folder_images}

        random.shuffle(self.image_names)

        # Create RESTART button
        restart_button = tkinter.Button(parent, text="RESTART", width=7,
                                        command=self.restart)
        restart_button.grid()

        # Create Canvas and Tiles
        self.canvas = tkinter.Canvas(parent, width=600, height=600)
        for row in range(0, 600, 150):
            for col in range(0, 600, 150):
                self.canvas.create_rectangle(col, row, col + 150, row + 150,
                                             outline=self.color,
                                             fill="yellow")
        self.canvas.grid()

        # Associate every image with the tag "image"
        for name in self.image_dict:
            self.canvas.itemconfig(name, tag="image")

        # Associate every tile with an image
        img_iterator = iter(self.image_names)
        for tile in self.canvas.find_all():
            self.canvas.itemconfig(tile, tag=next(img_iterator))

        # Create score label
        self.score = 100
        self.score_text = tkinter.StringVar()
        self.score_text.set(f"Score: {self.score}")
        score_label = tkinter.Label(parent, textvariable=self.score_text)
        score_label.grid()

        # Allow player to click on tile
        self.canvas.bind("<Button-1>", self.play)

    def restart(self):
        """
        This method is invoked when player clicks on the RESTART button.
        It shuffles and reassigns the images and resets the GUI and the
        score.
        :return: None
        """
        # Delete current image selected if any
        if self.prev_image:
            self.canvas.after(0, self.disappear, self.prev_image)
        self.canvas.delete("image")

        # Shuffle the images
        random.shuffle(self.image_names)

        # Reinstantiate each tile with new img and recolor squares
        img_iterator = iter(self.image_names)
        for tile in self.canvas.find_all():
            self.canvas.itemconfig(tile, tag=next(img_iterator), fill="yellow")

        # Reset all changeable values
        self.score = 100
        self.turns = 0
        self.remaining_tiles = 16
        self.score_text.set(f"Score: {self.score}")
        self.canvas.bind("<Button-1>", self.play)

    def play(self, event):
        """
        This method is invoked when the user clicks on a square.
        It implements the basic controls of the game.
        :param event: event (Event object) describing the click event
        :return: None
        """
        # Get the current tile
        tile = self.canvas.find_withtag(tkinter.CURRENT)
        image_name = self.canvas.gettags(tile)[0]

        # Update turns and if more than 13 turns begin deducting score
        # First tile always chosen on odd turn; second tile on even turn
        self.turns += .5
        if self.turns > 13 and self.turns % 1 == 0:
            self.score -= 10
            self.score_text.set(f"Score: {self.score}")

        # If first tile, doesn't disappear until after 2nd tile chosen
        if self.turns % 1 != 0:
            self.prev_image = self.appear(tile, image_name)
            self.prev_name = image_name
            self.prev_tile = tile
        else:  # If second tile
            # Don't let player choose another tile
            self.canvas.unbind("<Button-1>")

            curr = self.appear(tile, image_name)

            # If tiles match, remove their images and change their color
            if image_name == self.prev_name:
                self.remaining_tiles -= 2
                self.canvas.after(self.delay, self.disappear, curr)
                self.canvas.after(self.delay, self.disappear, self.prev_image)
                self.canvas.after(self.delay, self.change_color, tile,
                                  self.color)
                self.canvas.after(self.delay, self.change_color,
                                  self.prev_tile, self.color)
            else:  # If tiles don't match, remove their images
                self.canvas.after(self.delay, self.disappear, curr)
                self.canvas.after(self.delay, self.disappear, self.prev_image)

            # If game is over, disable clicking & print out game stats
            if not self.remaining_tiles:
                self.canvas.unbind("<Button-1>")
                self.canvas.after(self.delay, self.score_text.set, f"Game "
                    f"over!\nScore: {self.score}\nNumber of tries: "
                    f"{int(self.turns)}")
            else:
                # Rebind to allow player to click again
                self.canvas.after(self.delay, self.canvas.bind,
                                  "<Button-1>", self.play)

    def change_color(self, tile, color):
        """
        Change the tile's color when two tiles match
        :param tile: the tile whose color will be changed
        :param color: color tile will be changed to
        :return: None
        """
        self.canvas.itemconfigure(tile, fill=color)

    def appear(self, tile, image_name):
        """
        Make the image appear on the tile
        :param tile: (rectangle) tile for image to appear on
        :param image_name: (string) name of the image to be created
        :return: id of the image
        """
        x1, y1, x2, y2 = self.canvas.coords(tile)
        image_id = self.canvas.create_image((x1 + x2) / 2, (y1 + y2) / 2,
                                            image=self.image_dict[image_name],
                                            tag=image_name)
        return image_id

    def disappear(self, image_id):
        """
        Remove the image from the tile
        :param image_id: id of image to be removed
        :return: None
        """
        self.canvas.delete(image_id)


def get_arguments():
    """
    Parse and validate the command line arguments.
    :return: tuple containing the color (string), image folder (local
    directory) and fast option (boolean)
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("color", help="What color would you like for the "
                                      "player?", choices=["blue", "green",
                                                          "magenta"])
    parser.add_argument("image_folder", help="What folder contains the game "
                                             "images?", type=validate_images)
    parser.add_argument("-f", "--fast", help="Fast or slow game?",
                        action="store_true")
    arguments = parser.parse_args()
    color = arguments.color
    image_folder = arguments.image_folder
    fast = arguments.fast
    return color, image_folder, fast


def validate_images(image_folder):
    """
    Validate that the folder is a valid directory and it contains 8 gif
    :param image_folder: (file directory) folder containing the images
    :return: (file directory) folder containing the images if it's valid
    """
    if not os.path.exists(image_folder):
        raise argparse.ArgumentTypeError(f'{image_folder} is not a valid '
                                         f'folder')

    names = [name for name in os.listdir(image_folder) if os.path.splitext(
        name)[-1] == ".gif"]
    if len(names) < 8:
        raise argparse.ArgumentTypeError(f'{image_folder} must contain at '
                                         f'least 8 gif images')

    return image_folder


def main():
    color, image_folder, fast = get_arguments()
    root = tkinter.Tk()
    match_game = MatchGame(root, color, image_folder, fast)
    root.mainloop()


if __name__ == '__main__':
    main()
