import random
import time
import pygame
import shelve
from os import path

pygame.init()
pygame.font.init()

# save data
high_score = "highscore.txt"
s = shelve.open("Save Data")

width = 650
height = 650
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Primal")

# load image
spaceship_1 = pygame.image.load("venv/images/battleship .png")

# enemy ship
aircraft = pygame.image.load("venv/images/aircraft.png")
aircraft_1 = pygame.image.load("venv/images/aircraft1.png")
aircraft_2 = pygame.image.load("venv/images/aircraft2.png")
aircraft_3 = pygame.image.load("venv/images/aircraft3.png")

# laser
bullet_3 = pygame.image.load("venv/images/fire.png")
bullet_4 = pygame.image.load("venv/images/gear.png")

# background
background = pygame.transform.scale(pygame.image.load("venv/images/background.png"), (650, 650))


class Game:
    discontinue = 30  # because the fps is 60, it takes half a second

    def __init__(self, x, y, health=100, score=0):
        self.x = x
        self.y = y
        self.health = health
        self.object_img = None
        self.bullet_img = None
        self.lasers = []
        self.stop = 0
        self.heal = 0
        self.score = score
        self.max_health = 100
        self.health_ratio = self.health / self.max_health
        self.load_data()

    def load_data(self):
        # load high score
        self.dir = path.dirname(__file__)
        with open(path.join(self.dir, high_score), 'r+') as d:
            try:
                self.highscore = int(d.read())
            except:
                self.highscore = 0

    def draw(self, window):
        window.blit(self.object_img, (self.x, self.y))
        for bullet in self.lasers:
            bullet.draw(window)

    def stop_bullet(self):
        if self.stop >= self.discontinue:
            self.stop = 0
        elif self.stop > 0:
            self.stop += 1

    def add_bullets(self):
        if self.stop == 0:
            bullet = Bullet(self.x + 20, self.y, self.bullet_img)
            self.lasers.append(bullet)
            self.stop = 1

    def shoot_player(self, vel, obj):
        self.stop_bullet()
        for bullet in self.lasers:
            bullet.move_bullet(vel)
            if bullet.off_screen(height):
                self.lasers.remove(bullet)
            elif bullet.collision(obj):
                obj.health -= 10
                self.lasers.remove(bullet)

    def get_width(self):
        return self.object_img.get_width()

    def get_height(self):
        return self.object_img.get_height()


# making player appear


class Player(Game):
    def __init__(self, x, y, health=100):

        # super method uses parent class ship to initialize things
        super().__init__(x, y, health)
        self.object_img = spaceship_1
        self.bullet_img = bullet_3
        self.mask = pygame.mask.from_surface(self.object_img)
        self.max_health = health

    def fire(self, velocity, objs):
        self.stop_bullet()
        for bullet in self.lasers:
            bullet.move_bullet(velocity)
            if bullet.off_screen(height):
                self.lasers.remove(bullet)
            else:
                for obj in objs:
                    if bullet.collision(obj):
                        self.score += 1
                        objs.remove(obj)
                        if bullet in self.lasers:
                            self.lasers.remove(bullet)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)
        self.scorebar(window)
        self.hsbar(window)

    # x, y, width and height of rectangle

    def healthbar(self, window):
        pygame.draw.rect(window, (144, 144, 144),
                         (self.x, self.y + self.object_img.get_height() + 4, self.object_img.get_width(), 4))
        pygame.draw.rect(window, (255, 0, 0), (
            self.x, self.y + self.object_img.get_height() + 4,
            self.object_img.get_width() * (self.health / self.max_health), 4))

    def scorebar(self, window):
        score_text = pygame.font.SysFont("commissars", 25)
        score_screen = score_text.render(f"Score: {self.score}", True, (144, 144, 144))
        window.blit(score_screen, (90, 10))
        if self.score > self.highscore:
            self.highscore = self.score
            with open(path.join(self.dir, high_score), "w") as d:
                d.write(str(self.score))
        else:
            self.highscore = self.highscore

    def hsbar(self, window):
        hs_score_text = pygame.font.SysFont("commissars", 25)
        hs_screen = hs_score_text.render(f"Highest Score: {str(self.highscore)}", True, (144, 144, 144))
        window.blit(hs_screen, (200, 10))


'''f the objects are overlapping within the distance we have given, objects collide'''


def collide(obj1, obj2):
    distance_x = obj2.x - obj1.x
    distance_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (distance_x, distance_y)) is not None


class Enemy(Game):
    enemy_ship = {"red": (aircraft, bullet_4),
                  "black": (aircraft_1, bullet_4),
                  "grey": (aircraft_2, bullet_4),
                  "white": (aircraft_3, bullet_4)}

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        # obtaining images from enemy_ship dictionary
        self.object_img, self.bullet_img = self.enemy_ship[color]
        self.mask = pygame.mask.from_surface(self.object_img)

    def move(self, speed):
        # to move ship downwards
        self.y += speed

    def add_bullets(self):
        if self.stop == 0:
            bullet = Bullet(self.x, self.y, self.bullet_img)
            self.lasers.append(bullet)
            self.stop = 1


class Bullet(Game):
    def __init__(self, x, y, img):
        super().__init__(x, y)
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move_bullet(self, velocity):
        self.y += velocity

    def off_screen(self, height):
        return not (height >= self.y >= 0)

    def collision(self, obj):
        return collide(obj, self)


def main():
    running = True
    fps = 60
    # setting the clock speed
    clock = pygame.time.Clock()
    level = 0
    lives = 3
    lives_text = pygame.font.SysFont("commissars", 25)
    level_text = pygame.font.SysFont("commissars", 25)
    over_text = pygame.font.SysFont("commissars", 40)

    # moving the player by pixels
    player_speed = 7
    player = Player(300, 540)

    # bullet
    bullet_speed = 3

    # for game over
    game_over = False
    over_count = 0

    # for enemies
    enemies = []
    num_of_enemies = 3
    enemy_speed = 1

    def draw_bg():

        screen.blit(background, (0, 0))

        # display lives and level

        lives_screen = lives_text.render(f"Lives: {lives}", True, (144, 144, 144))
        level_screen = level_text.render(f"Level: {level}", True, (144, 144, 144))

        screen.blit(lives_screen, (10, 10))
        screen.blit(level_screen, (width - level_screen.get_width() - 10, 10))

        # draw player on the screen
        player.draw(screen)

        for alien in enemies:
            alien.draw(screen)

        # display game over

        if game_over:
            gameover_text = over_text.render("Game Over!!", True, (255, 255, 255))
            screen.blit(gameover_text, (width / 2 - gameover_text.get_width() / 2, 350))

        pygame.display.update()

    while running:
        clock.tick(fps)
        draw_bg()

        # for game over
        if lives <= 0 or player.health <= 0:
            game_over = True
            over_count += 1

        if game_over:
            if over_count > fps * 3:
                running = False
            else:
                continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # moving enemies

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and player.x - player_speed > 0:
            player.x -= player_speed
        if keys[pygame.K_RIGHT] and player.x + player_speed + player.get_width() < width:
            player.x += player_speed
        if keys[pygame.K_UP] and player.y - player_speed > 0:
            player.y -= player_speed
        if keys[pygame.K_DOWN] and player.y + player_speed + player.get_width() < height:
            player.y += player_speed
        if keys[pygame.K_SPACE]:
            player.add_bullets()

        if len(enemies) == 0:
            level += 1
            num_of_enemies += 5
            for i in range(num_of_enemies):
                # to make random enemy ships appear
                enemy = Enemy(random.randrange(50, 600), random.randrange(-1000, -100),
                              random.choice(["red", "black", "grey", "white"]))

                enemies.append(enemy)

        for enemy in enemies:
            enemy.move(enemy_speed)
            enemy.shoot_player(bullet_speed, player)

            if random.randrange(0, 2 * 60) == 1:
                enemy.add_bullets()

            if enemy.y + enemy.get_height() > height:
                lives -= 1
                enemies.remove(enemy)

        player.fire(-bullet_speed, enemies)


def start():
    start_text = pygame.font.SysFont("commissars", 40)
    hs_text = pygame.font.SysFont("commissars", 30)
    running = True
    with open("highscore.txt", "r") as t:
        a = t.read()
    while running:
        screen.blit(background, (0, 0))
        start_display = start_text.render("Press space bar to begin...", True, (255, 255, 255))
        hs_display = hs_text.render(f"High Score: {a}", True, (255, 255, 255))
        screen.blit(start_display, (width / 2 - start_display.get_width() / 2, 350))
        screen.blit(hs_display, (width/2 - hs_display.get_width()/2, 300))
        pygame.display.update()
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if keys[pygame.K_SPACE]:
                main()
    pygame.quit()


start()
