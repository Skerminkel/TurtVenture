"""
Side scrolling Game

This program creates a simple side scrolling game using the Turtle library. The game features a player that can move
left and right and jump over objects that spawn at the bottom of the screen. The game ends when the player's
hit points reach zero.
"""
import turtle
import random

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
PLAYER_SIZE = 100
OBJECT_SIZE = SCREEN_HEIGHT // 5
OBSTACLE_SIZE = 3
WALL = -SCREEN_WIDTH // 2 + round(1 / 3 * SCREEN_WIDTH)
GRAVITY = 1
PLAYER_SPEED = 15
OBJECT_SPEED = 6
FPS = 45
BUFFER = 20  # A small buffer to make collision detection less strict
HITPOINTS = 5


class GameObject(turtle.Turtle):
    """Base class for all game objects."""

    def __init__(self, shape, x, y):
        super().__init__()
        self.shape(shape)
        self.penup()
        self.goto(x, y)
        self.shapesize(2)


class Player(GameObject):
    """Player object."""

    def __init__(self, x, y):
        super().__init__('turtle', x, y)
        self.color('black', 'green')
        self.dy = 0
        self.hitpoints = HITPOINTS

    def move_left(self):
        """Move player to the left."""
        if self.xcor() - OBJECT_SIZE // 2 > - SCREEN_WIDTH // 2:
            self.goto(self.xcor() - PLAYER_SPEED, self.ycor())

    def move_right(self):
        """Move player to the right."""
        if self.xcor() + 0.5 * OBJECT_SIZE < WALL:
            self.goto(self.xcor() + PLAYER_SPEED, self.ycor())

    def jump(self):
        """Make the player jump."""
        if self.ycor() <= -SCREEN_HEIGHT // 2 + PLAYER_SIZE // 2:
            self.dy = 15

    def fall(self):
        """Apply gravity to the player."""
        self.goto(self.xcor(), self.ycor() + self.dy)
        self.dy -= GRAVITY

        if self.ycor() <= -SCREEN_HEIGHT // 2 + PLAYER_SIZE // 2:
            self.dy = 0
            self.goto(self.xcor(), -SCREEN_HEIGHT // 2 + PLAYER_SIZE // 2)

    def damage(self):
        """Flashes red when player takes damage"""
        return self.color('black', 'red')


class Obstacle(GameObject):
    """Obstacle object."""

    def __init__(self, x, y):
        super().__init__('arrow', x, y)
        self.color('grey', 'black')
        self.width_multiplier = random.uniform(0.5, 1.5)  # Multiplier for width
        self.height_multiplier = random.uniform(max(self.width_multiplier + 0.5, 0.1),
                                                self.width_multiplier + 1.5)  # Multiplier for height, ensuring height > width

        self.shapesize(OBSTACLE_SIZE * self.width_multiplier, OBSTACLE_SIZE * self.height_multiplier, 2)
        self.counted = False

    def move(self):
        """Move the obstacle."""
        self.goto(self.xcor() - OBJECT_SPEED, self.ycor())

    def is_out_of_screen(self):
        """Check if the obstacle is out of the screen."""
        return self.xcor() < -SCREEN_WIDTH // 2 - OBJECT_SIZE // 2


class Pickup(GameObject):
    """Pickup object."""

    def __init__(self, x, y):
        super().__init__('circle', x, y)
        self.color('yellow', 'orange')
        self.speed = OBJECT_SPEED

    def move(self):
        """Move the pickup."""
        self.speed = random.uniform(OBJECT_SPEED // 4, OBJECT_SPEED)
        wobble = random.uniform(-2, 2)  # Make the pickup move up and down randomly
        self.goto(self.xcor() - self.speed, self.ycor() + wobble)

    def is_out_of_screen(self):
        """Check if the pickup is out of the screen."""
        return self.xcor() < -SCREEN_WIDTH // 2 - OBJECT_SIZE // 2


class SidescrollingGame:
    """Side scrolling game."""

    def __init__(self):
        # Initialize screen
        self.screen = turtle.Screen()
        self.screen.setup(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.screen.tracer(0)
        try:
            self.screen.bgpic('Full-Background.png')
        except turtle.TurtleGraphicsError:
            print("Error: Cannot open background image.")
            self.screen.bgcolor('black')

        # Player
        self.player = Player(-SCREEN_WIDTH // 3, -SCREEN_HEIGHT // 2 + PLAYER_SIZE // 2)

        # Objects
        self.waiting_obstacles = [self.create_obstacle() for _ in range(10)]
        self.in_play_obstacles = []
        self.waiting_pickups = [self.create_pickup() for _ in range(10)]
        self.in_play_pickups = []

        # Score and hitpoints
        self.score = 0
        self.score_writer = self.create_writer(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, 'Score: 0', 'black')
        self.hitpoints_writer = self.create_writer(-SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT // 2 - 50,
                                                   f'Hitpoints: {self.player.hitpoints}', 'black')

        # Start game loop
        self.obstacle_timer = 0
        self.pickup_timer = 15
        self.screen.onkeypress(self.player.jump, 'space')
        self.game_loop()

    def create_obstacle(self):
        """Create a new obstacle."""
        obstacle = Obstacle(SCREEN_WIDTH + OBJECT_SIZE // 2, -SCREEN_HEIGHT // 2 + OBJECT_SIZE // 4)
        obstacle.left(90)
        return obstacle

    def create_pickup(self):
        """Create a new pickup."""
        return Pickup(SCREEN_WIDTH + OBJECT_SIZE // 2,
                      random.randint(-SCREEN_HEIGHT // 2 + round(OBJECT_SIZE * 1.5), -OBJECT_SIZE // 2 - 45))

    def create_writer(self, x, y, text, color):
        """Create a new writer."""
        writer = turtle.Turtle()
        writer.hideturtle()
        writer.penup()
        writer.goto(x, y)
        writer.color(color)
        writer.write(text, align='center', font=('Deja Vu Sans Mono', 24, 'bold'))
        return writer

    def update_score(self):
        """Update the score."""
        self.score_writer.clear()
        self.score_writer.write(f'Score: {self.score}', align='center', font=('Deja Vu Sans Mono', 24, 'bold'))

    def update_hitpoints(self):
        """Update the hitpoints."""
        self.hitpoints_writer.clear()
        self.hitpoints_writer.write(f'Hitpoints: {self.player.hitpoints}', align='center',
                                    font=('Deja Vu Sans Mono', 24, 'bold'))

    def check_collision(self, obj):
        """Check if the player has collided with an object."""

        return (abs(obj.xcor() - self.player.xcor()) < OBJECT_SIZE // 2 - BUFFER
                and abs(obj.ycor() - self.player.ycor()) < OBJECT_SIZE // 2 - BUFFER)

    def handle_obstacle(self, obstacle):
        """Handle an obstacle."""
        if obstacle.is_out_of_screen():
            self.reset_obstacle(obstacle)
        elif self.check_collision(obstacle):
            self.player.color('black', 'red')
            self.screen.update()
            self.player.hitpoints -= 1
            self.update_hitpoints()
            self.reset_obstacle(obstacle)
            self.screen.ontimer(self.player.damage(), 20)
            self.player.color('black', 'green')
        elif obstacle.xcor() < self.player.xcor() and not obstacle.counted:
            self.score += 1
            self.update_score()
            obstacle.counted = True

    def handle_pickup(self, pickup):
        """Handle a pickup."""
        if pickup.is_out_of_screen():
            self.reset_pickup(pickup)
        elif self.check_collision(pickup):
            self.score += 5
            self.update_score()
            self.reset_pickup(pickup)

    def reset_obstacle(self, obstacle):
        """Reset an obstacle."""
        self.in_play_obstacles.remove(obstacle)
        self.waiting_obstacles.append(obstacle)
        obstacle.goto(SCREEN_WIDTH + OBJECT_SIZE // 2, -SCREEN_HEIGHT // 2 + OBJECT_SIZE // 4)
        obstacle.counted = False

    def reset_pickup(self, pickup):
        """Reset a pickup."""
        self.in_play_pickups.remove(pickup)
        self.waiting_pickups.append(pickup)
        pickup.goto(SCREEN_WIDTH + OBJECT_SIZE // 2,
                    random.randint(-SCREEN_HEIGHT // 2 + OBJECT_SIZE // 2, -OBJECT_SIZE // 2))

    def game_over(self):
        """Check if the game is over."""
        return self.player.hitpoints <= 0

    def show_game_over_screen(self):
        """Show the game over screen."""
        self.screen.clear()
        self.screen.bgcolor('black')
        game_over_turtle = turtle.Turtle()
        game_over_turtle.hideturtle()
        game_over_turtle.penup()
        game_over_turtle.goto(0, 50)
        game_over_turtle.color('white')
        game_over_turtle.write('Game Over', align='center', font=('Deja Vu Sans Mono', 24, 'bold'))
        game_over_turtle.goto(0, -50)
        game_over_turtle.write(f'Final score: {self.score}', align='center', font=('Deja Vu Sans Mono', 24, 'bold'))

    def game_loop(self):
        """The main game loop."""
        if not self.game_over():
            self.obstacle_timer += 1
            self.pickup_timer += 1
            if (self.obstacle_timer >= 30 and len(self.in_play_obstacles) < 10
                    and len(self.waiting_obstacles) > 0 and random.random() <= 0.5):
                if self.waiting_obstacles:
                    obstacle = self.waiting_obstacles.pop(0)
                    self.in_play_obstacles.append(obstacle)
                self.obstacle_timer = 0
            if (self.pickup_timer >= 12 and len(self.in_play_pickups) < 1
                    and len(self.waiting_pickups) > 0 and random.random() < 0.2):
                if self.waiting_pickups:
                    pickup = self.waiting_pickups.pop(0)
                    self.in_play_pickups.append(pickup)
                self.pickup_timer = 0

            self.screen.listen()
            self.screen.onkeypress(self.player.move_left, 'a')
            self.screen.onkeypress(self.player.move_right, 'd')

            self.player.fall()

            for obstacle in self.in_play_obstacles:
                obstacle.move()
                self.handle_obstacle(obstacle)

            for pickup in self.in_play_pickups:
                pickup.move()
                self.handle_pickup(pickup)

            self.screen.update()
            self.screen.ontimer(self.game_loop, FPS)
        else:
            self.show_game_over_screen()


game = SidescrollingGame()
turtle.done()
