import pygame
import sys
from settings import screen_width, screen_height, tile_size
from game_data import level_1
from level import Level
from ui import UI

from player import Player


class Button():
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(
            image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self):
        action = False

        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):

            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action


class Game:
    def __init__(self):
        self.max_health = 100
        self.cur_health = 100
        self.coins = 0
        self.ui = UI(screen)
        self.level = Level(
            level_1, screen, self.over, self.change_coin, self.change_health)
        self.alive = True

    def change_coin(self, amount):
        self.coins += amount

    def change_health(self, amount):
        self.cur_health += amount

    def check_game_over(self):

        if self.cur_health <= 0:
            self.over()

    def caption_icon(self):
        pygame.display.set_caption("Survive")
        icon = pygame.image.load("graphics/character/icon.png")
        pygame.display.set_icon(icon)

    def background(self):
        #back_ground = pygame.image.load('graphics/sky/sky.jpg')
        #screen.blit(back_ground, (0, 0))
        screen.fill('#ffffe0', (0, 0, screen.get_width(),
                    screen.get_height() - 220))
        screen.fill('#FAD6A5', (0, 484, screen.get_width(),
                    screen.get_height() - 200))
        screen.fill('#696969', (0, 504, screen.get_width(),
                    screen.get_height()))

        # DCDCDC

    def over(self):
        self.alive = False
        screen.fill((0, 0, 0))
        start_img = pygame.image.load('graphics/buttons/button_start (2).png')
        start_button = Button(
            525, 322, start_img, 1)

        if start_button.draw():
            self.cur_health = 100
            self.coins = 0
            self.level = Level(
                level_1, screen, self.over, self.change_coin, self.change_health)
            self.alive = True

    def run(self):
        self.background()
        self.level.run()
        self.check_game_over()
        self.caption_icon()


pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()

game = Game()
while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    game.run()
    if game.alive == True:

        game.ui.show_coins(game.coins)
        game.ui.show_health(game.cur_health, game.max_health)

    pygame.display.update()
    clock.tick(60)
