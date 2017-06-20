"""
pong.py - A python Pong clone.

Example from chapter 1 of the book "Python Game Programming by Example":
https://www.packtpub.com/game-development/python-game-programming-example
"""
import tkinter as tk


class GameObject(object):
    """
    Defines behavior common for all game objects.

    All objects in the game - ball, paddle and bricks - inherit from this class.
    """
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        """
        Get the object position.

        :return: x and y coordinates
        """
        return self.canvas.coords(self.item)

    def move(self, x_coordinate, y_coordinate):
        """
        Move the object by an offset.

        :param x_coordinate: horizontal offset, left to right
        :param y_coordinate: vertical offset, top to bottom
        :return:
        """
        self.canvas.move(self.item, x_coordinate, y_coordinate)

    def delete(self):
        """
        Remove the object.

        :return:
        """
        self.canvas.delete(self.item)


class Ball(GameObject):
    """
    This class contains movement, collision speed, size and color properties for the ball.
    """
    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [1, -1]
        self.speed = 10
        item = canvas.create_oval(x-self.radius, y-self.radius,
                                  x+self.radius, y+self.radius,
                                  fill='white')
        super(Ball, self).__init__(canvas, item)

    def update(self):
        """
        Update ball position and change movement direction if out of bounds.

        Get the current position of the ball, and width of the canvas.
        Changes direction when the position collides with the canvas border.
        Direction vector is scaled by the ball's speed.
        :return:
        """
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1
        x_coordinate = self.direction[0] * self.speed
        y_coordinate = self.direction[1] * self.speed
        self.move(x_coordinate, y_coordinate)

    def collide(self, game_objects):
        """
        Checks collision with paddle and bricks.

        :param game_objects: Checks if the object hit is a brick, and calls Brick.hit() if it is.
        :return:
        """
        coords = self.get_position()
        x_coordinate = (coords[0] + coords[2]) * 0.5
        if len(game_objects) > 1:
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            coords = game_object.get_position()
            if x_coordinate > coords[2]:
                self.direction[0] = 1
            elif x_coordinate < coords[0]:
                self.direction[0] = -1
            else:
                self.direction[1] *= -1

        for game_object in game_objects:
            if isinstance(game_object, Brick):
                game_object.hit()


class Paddle(GameObject):
    """
    Contains the paddle properties and movement.

    Also puts the ball on the paddle.
    """
    def __init__(self, canvas, x, y):
        self.width = 80
        self.height = 10
        self.ball = None
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='blue')
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball):
        """
        Puts the ball on the paddle when the game starts and after lost balls

        :param ball: Reference to the ball in play.
        :return:
        """
        self.ball = ball

    def move(self, offset):  # pylint: disable=arguments-differ
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)
            if self.ball is not None:
                self.ball.move(offset, 0)


class Brick(GameObject):
    """
    Defines the brick size, color and hit points.
    """
    COLORS = {1: '#999999', 2: '#555555', 3: '#222222'}

    def __init__(self, canvas, x, y, hits):
        self.width = 75
        self.height = 20
        self.hits = hits
        color = Brick.COLORS[hits]
        item = canvas.create_rectangle(x - self.width / 2, y - self.height / 2,
                                       x + self.width / 2, y + self.height / 2,
                                       fill=color, tags='brick')
        super(Brick, self).__init__(canvas, item)

    def hit(self):
        """
        Removes destroyed bricks, and weakens bricks that take more than one hit.

        :return:
        """
        self.hits -= 1
        if self.hits == 0:
            self.delete()
        else:
            self.canvas.itemconfig(self.item, fill=Brick.COLORS[self.hits])


class Game(tk.Frame):
    """
    Contains gameplay logic and main loop.

    Creates canvas, bricks, paddle and ball.
    Draws text on screen to communicate with user.
    """
    # pylint: disable=too-many-ancestors
    # pylint: disable=too-many-instance-attributes

    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3
        self.width = 610
        self.height = 400
        self.canvas = tk.Canvas(bg='#aaaaff', width=self.width, height=self.height)
        self.canvas.pack()
        self.pack()

        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width/2, 326)
        self.items[self.paddle.item] = self.paddle
        for x_position in range(5, self.width - 5, 75):
            self.add_brick(x_position + 37.5, 50, 2)  # top row of bricks
            self.add_brick(x_position + 37.5, 70, 1)
            self.add_brick(x_position + 37.5, 90, 1)

        self.hud = None
        self.setup_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>', lambda _: self.paddle.move(-10))
        self.canvas.bind('<Right>', lambda _: self.paddle.move(10))

    def setup_game(self):
        """
        Get game ready and display instructions to start.

        :return:
        """
        self.add_ball()
        self.update_lives_text()
        self.text = self.draw_text(300, 200, 'Press Space to start')
        self.canvas.bind('<space>', lambda _: self.start_game())

    def add_ball(self):
        """
        Adds a ball on top of the paddle at current position.

        :return:
        """
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x_coordinate = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x_coordinate, 310)
        self.paddle.set_ball(self.ball)

    def add_brick(self, x_coordinate, y_coordinate, hits):
        """
        Add a brick to the canvas.

        :param x_coordinate: Horizontal position
        :param y_coordinate: Vertical position
        :param hits: Brick hit points
        :return:
        """
        brick = Brick(self.canvas, x_coordinate, y_coordinate, hits)
        self.items[brick.item] = brick

    def draw_text(self, x_coordinate, y_coordinate, text, size='40'):
        """
        Draw text on the canvas.

        :param x_coordinate: X position.
        :param y_coordinate: Y position.
        :param text: The text to display.
        :param size: The text size.
        :return:
        """
        font = ('Helvetica', size)
        return self.canvas.create_text(x_coordinate, y_coordinate, text=text, font=font)

    def update_lives_text(self):
        """
        Displays number of lives left.

        :return:
        """
        text = 'Lives: %s' % self.lives
        if self.hud is None:
            self.hud = self.draw_text(50, 20, text, 15)
        else:
            self.canvas.itemconfig(self.hud, text=text)

    def start_game(self):
        """
        Starts the game, and makes sure 'space' is no longer capable of starting the game.

        :return:
        """
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_loop()

    def game_loop(self):
        """
        The main game loop. Checks for collisions on each tick. Checks for win/lose condition.

        :return:
        """
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0:
            self.ball.speed = None
            self.draw_text(300, 200, 'You win!')
            self.draw_text(500, 200, 'Press Space to play again')
            self.canvas.bind('<space>', lambda _: self.start_game())
        elif self.ball.get_position()[3] >= self.height:
            self.ball.speed = None
            self.lives -= 1
            if self.lives < 0:
                self.draw_text(300, 200, 'Game over!')
            else:
                self.after(1000, self.setup_game)
        else:
            self.ball.update()
            self.after(50, self.game_loop)

    def check_collisions(self):
        """
        Check if the ball's current position overlaps with any other game objects.

        :return:
        """
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items \
                   if x in self.items]
        self.ball.collide(objects)


if __name__ == '__main__':
    # pylint: disable=invalid-name
    root = tk.Tk()
    root.title('Hello, Pong!')
    game = Game(root)
    game.mainloop()
