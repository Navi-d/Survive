import pygame
from support import import_csv_layout, import_cut_graphics
from settings import tile_size, screen_height, screen_width
from tile import Tile, StaticTile, AnimatedTile
from player import Player


#from game_data import levels

import sys


class Level:
    def __init__(self, level_data, surface, over, change_coin, change_health):
        self.display_surface = surface
        self.world_shift = 0
        self.over = over
        self.coins = 0

        # terrain setup
        terrain_layout = import_csv_layout(level_data['terrain'])
        self.terrain_sprites = self.create_tile_group(
            terrain_layout, 'terrain')

        player_layout = import_csv_layout(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(player_layout, change_health)

        self.change_coin = change_coin

        background_layout = import_csv_layout(level_data['background'])
        self.background_sprites = self.create_tile_group(
            background_layout, 'background')
        coins_layout = import_csv_layout(level_data['coins'])
        self.coins_sprites = self.create_tile_group(coins_layout, 'coins')
        enemy_layout = import_csv_layout(level_data['enemy'])
        self.enemy_sprites = self.create_tile_group(enemy_layout, 'enemy')
        heal_layout = import_csv_layout(level_data['heal'])
        self.heal_sprites = self.create_tile_group(heal_layout, 'heal')
        #self.sky = Sky(8)
        #level_width = len(terrain_layout[0]) * tile_size
        #self.water = Water(screen_height - 30, level_width)
        #self.clouds = Clouds(400, level_width, 20)

    def create_tile_group(self, layout, type):
        sprite_group = pygame.sprite.Group()

        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                if val != '-1':
                    x = col_index * tile_size
                    y = row_index * tile_size

                    if type == 'terrain':
                        terrain_tile_list = import_cut_graphics(
                            'graphics/terrain/asset_pierre.png')
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)
                    if type == 'background':
                        background_tile_list = import_cut_graphics(
                            'graphics/sky/storm cloud.png')
                        tile_surface = background_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)
                    if type == 'coins':
                        coins_tile_list = import_cut_graphics(
                            'graphics/coins/coin_tiles.png')
                        tile_surface = coins_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)
                    if type == 'enemy':
                        if val == '0':
                            sprite = AnimatedTile(
                                tile_size, x, y, 'graphics/enemy/left')
                        if val == '1':
                            sprite = AnimatedTile(
                                tile_size, x, y, 'graphics/enemy/right')
                    if type == 'heal':
                        heal_tile_list = import_cut_graphics(
                            'graphics/heal/fruits_itch.png')
                        tile_surface = heal_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)
                    sprite_group.add(sprite)

        return sprite_group

    def player_setup(self, layout, change_health):
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size
                if val == '0':
                    sprite = Player((x, y), change_health)
                    self.player.add(sprite)
                if val == '1':
                    hat_surface = pygame.image.load(
                        'graphics/character/hat.png').convert_alpha()
                    sprite = StaticTile(tile_size, x, y, hat_surface)
                    self.goal.add(sprite)

    def horizontal_movement_collision(self):
        player = self.player.sprite
        player.rect.x += player.direction.x * player.speed

        for sprite in self.terrain_sprites.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right
                    player.on_left = True
                    self.current_x = player.rect.left
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left
                    player.on_right = True
                    self.current_x = player.rect.right
        if player.on_left and (player.rect.left < self.current_x or player.direction.x >= 0):
            player.on_left = False
        if player.on_right and (player.rect.right < self.current_x or player.direction.x <= 0):
            player.on_right = False

    def vertical_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()

        for sprite in self.terrain_sprites.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True
        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False
        if player.on_ceiling and player.direction.y > 0:
            player.on_ceiling = False

    def scroll(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x

        if player_x < screen_width / 3 and direction_x < 0:
            self.world_shift = 8
            player.speed = 0
        elif player_x > screen_width - (screen_width / 3) and direction_x > 0:
            self.world_shift = -8
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = 8

    def change_coin_collisions(self):
        collided_coins = pygame.sprite.spritecollide(
            self.player.sprite, self.coins_sprites, True)
        if collided_coins:
            for coin in collided_coins:
                self.change_coin(1)

    def check_enemy_collisions(self):

        enemy_collitions = pygame.sprite.spritecollide(
            self.player.sprite, self.enemy_sprites, False)
        if enemy_collitions:

            for enemy in enemy_collitions:
                enemy_center = enemy.rect.centery
                enemy_top = enemy.rect.top
                player_bottom = self.player.sprite.rect.bottom
                if enemy_top < player_bottom < enemy_center and self.player.sprite.direction.y >= 0:
                    self.player.sprite.direction.y = -15
                    enemy.kill()
                else:
                    self.player.sprite.get_damage()

    def check_player_healed(self):
        heal_collitions = pygame.sprite.spritecollide(
            self.player.sprite, self.heal_sprites, True)
        if heal_collitions:
            for heal in heal_collitions:
                self.player.sprite.get_healed()

    def check_over(self):

        if self.player.sprite.rect.top > screen_height:
            self.over()

    def run(self):

        self.coins_sprites.update(self.world_shift)
        self.coins_sprites.draw(self.display_surface)

        self.heal_sprites.update(self.world_shift)
        self.heal_sprites.draw(self.display_surface)

        self.terrain_sprites.update(self.world_shift)
        self.terrain_sprites.draw(self.display_surface)

        self.enemy_sprites.update(self.world_shift)
        self.enemy_sprites.draw(self.display_surface)

        self.player.update()
        self.horizontal_movement_collision()
        self.vertical_movement_collision()
        self.scroll()

        self.player.draw(self.display_surface)
        self.goal.update(self.world_shift)
        self.goal.draw(self.display_surface)

        self.change_coin_collisions()
        self.check_enemy_collisions()
        self.check_player_healed()

        self.check_over()
