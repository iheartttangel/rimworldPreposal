
import pygame
from pygame.locals import *
import random

pygame.init()

screen_width = 600
screen_height = 600

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Breakout')

font = pygame.font.SysFont('Constantia', 30)
small_font = pygame.font.SysFont('Constantia', 20)

bg = (234, 218, 184)
block_red = (242, 85, 96)
block_green = (86, 174, 87)
block_blue = (69, 177, 232)
paddle_col = (142, 135, 123)
paddle_outline = (100, 100, 100)
text_col = (78, 81, 139)
powerup_expand = (255, 215, 0)
powerup_slow = (147, 112, 219)
powerup_multi = (255, 140, 0)
powerup_life = (255, 105, 180)

cols = 6
rows = 6
clock = pygame.time.Clock()
fps = 60
live_ball = False
game_over = 0
lives = 3

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

class PowerUp():
    def __init__(self, x, y, type):
        self.type = type
        self.width = 30
        self.height = 30
        self.x = x
        self.y = y
        self.speed = 3
        self.rect = Rect(self.x, self.y, self.width, self.height)
        
        if self.type == 'expand':
            self.color = powerup_expand
            self.text = 'E'
        elif self.type == 'slow':
            self.color = powerup_slow
            self.text = 'S'
        elif self.type == 'multi':
            self.color = powerup_multi
            self.text = 'M'
        elif self.type == 'life':
            self.color = powerup_life
            self.text = '+1'
    
    def move(self):
        self.y += self.speed
        self.rect.y = self.y
        
        if self.y > screen_height:
            return True
        return False
    
    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, paddle_outline, self.rect, 2)
        draw_text(self.text, small_font, (0, 0, 0), self.x + 5, self.y + 5)

class wall():
    def __init__(self):
        self.width = screen_width // cols
        self.height = 50

    def create_wall(self):
        self.blocks = []
        block_individual = []
        for row in range(rows):
            block_row = []
            for col in range(cols):
                block_x = col * self.width
                block_y = row * self.height
                rect = pygame.Rect(block_x, block_y, self.width, self.height)
                if row < 2:
                    strength = 3
                elif row < 4:
                    strength = 2
                elif row < 6:
                    strength = 1
                block_individual = [rect, strength]
                block_row.append(block_individual)
            self.blocks.append(block_row)

    def draw_wall(self):
        for row in self.blocks:
            for block in row:
                if block[1] == 3:
                    block_col = block_blue
                elif block[1] == 2:
                    block_col = block_green
                elif block[1] == 1:
                    block_col = block_red
                pygame.draw.rect(screen, block_col, block[0])
                pygame.draw.rect(screen, bg, (block[0]), 2)

class paddle():
    def __init__(self):
        self.reset()
        self.expand_timer = 0

    def move(self):
        self.direction = 0
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
            self.direction = -1
        if key[pygame.K_RIGHT] and self.rect.right < screen_width:
            self.rect.x += self.speed
            self.direction = 1
        
        if self.expand_timer > 0:
            self.expand_timer -= 1
            if self.expand_timer == 0:
                self.reset_size()

    def draw(self):
        pygame.draw.rect(screen, paddle_col, self.rect)
        pygame.draw.rect(screen, paddle_outline, self.rect, 3)

    def expand(self):
        old_center = self.rect.centerx
        self.width = int(screen_width / cols) * 2
        self.rect.width = self.width
        self.rect.centerx = old_center
        self.expand_timer = 300
    
    def reset_size(self):
        old_center = self.rect.centerx
        self.width = int(screen_width / cols)
        self.rect.width = self.width
        self.rect.centerx = old_center

    def reset(self):
        self.height = 20
        self.width = int(screen_width / cols)
        self.x = int((screen_width / 2) - (self.width / 2))
        self.y = screen_height - (self.height * 2)
        self.speed = 10
        self.rect = Rect(self.x, self.y, self.width, self.height)
        self.direction = 0
        self.expand_timer = 0

class game_ball():
    def __init__(self, x, y):
        self.reset(x, y)
        self.slow_timer = 0

    def move(self):
        collision_thresh = 5

        wall_destroyed = 1
        row_count = 0
        for row in wall.blocks:
            item_count = 0
            for item in row:
                if self.rect.colliderect(item[0]):
                    if abs(self.rect.bottom - item[0].top) < collision_thresh and self.speed_y > 0:
                        self.speed_y *= -1
                    if abs(self.rect.top - item[0].bottom) < collision_thresh and self.speed_y < 0:
                        self.speed_y *= -1
                    if abs(self.rect.right - item[0].left) < collision_thresh and self.speed_x > 0:
                        self.speed_x *= -1
                    if abs(self.rect.left - item[0].right) < collision_thresh and self.speed_x < 0:
                        self.speed_x *= -1
                    if wall.blocks[row_count][item_count][1] > 1:
                        wall.blocks[row_count][item_count][1] -= 1
                    else:
                        block_rect = wall.blocks[row_count][item_count][0]
                        if random.randint(1, 4) == 1:
                            powerup_type = random.choice(['expand', 'slow', 'multi', 'life'])
                            powerup = PowerUp(block_rect.centerx - 15, block_rect.centery - 15, powerup_type)
                            powerups.append(powerup)
                        wall.blocks[row_count][item_count][0] = (0, 0, 0, 0)

                if wall.blocks[row_count][item_count][0] != (0, 0, 0, 0):
                    wall_destroyed = 0
                item_count += 1
            row_count += 1
        if wall_destroyed == 1:
            self.game_over = 1

        if self.rect.left < 0 or self.rect.right > screen_width:
            self.speed_x *= -1

        if self.rect.top < 0:
            self.speed_y *= -1
        if self.rect.bottom > screen_height:
            self.game_over = -1

        if self.rect.colliderect(player_paddle):
            if abs(self.rect.bottom - player_paddle.rect.top) < collision_thresh and self.speed_y > 0:
                self.speed_y *= -1
                self.speed_x += player_paddle.direction
                if self.speed_x > self.speed_max:
                    self.speed_x = self.speed_max
                elif self.speed_x < 0 and self.speed_x < -self.speed_max:
                    self.speed_x = -self.speed_max
            else:
                self.speed_x *= -1

        if self.slow_timer > 0:
            self.slow_timer -= 1
            if self.slow_timer == 0:
                self.reset_speed()

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        return self.game_over

    def draw(self):
        pygame.draw.circle(screen, paddle_col, (self.rect.x + self.ball_rad, self.rect.y + self.ball_rad), self.ball_rad)
        pygame.draw.circle(screen, paddle_outline, (self.rect.x + self.ball_rad, self.rect.y + self.ball_rad), self.ball_rad, 3)

    def slow(self):
        self.speed_x = self.speed_x // 2 if abs(self.speed_x) > 1 else (1 if self.speed_x > 0 else -1)
        self.speed_y = self.speed_y // 2 if abs(self.speed_y) > 1 else (1 if self.speed_y > 0 else -1)
        self.slow_timer = 300

    def reset_speed(self):
        self.speed_x = 4 if self.speed_x > 0 else -4
        self.speed_y = -4 if self.speed_y < 0 else 4

    def reset(self, x, y):
        self.ball_rad = 10
        self.x = x - self.ball_rad
        self.y = y
        self.rect = Rect(self.x, self.y, self.ball_rad * 2, self.ball_rad * 2)
        self.speed_x = 4
        self.speed_y = -4
        self.speed_max = 5
        self.game_over = 0
        self.slow_timer = 0

wall = wall()
wall.create_wall()

player_paddle = paddle()

ball = game_ball(player_paddle.x + (player_paddle.width // 2), player_paddle.y - player_paddle.height)

balls = [ball]
powerups = []

run = True
while run:

    clock.tick(fps)
    
    screen.fill(bg)

    wall.draw_wall()
    player_paddle.draw()
    
    for b in balls:
        b.draw()
    
    for powerup in powerups:
        powerup.draw()

    draw_text(f'Lives: {lives}', small_font, text_col, 10, screen_height - 30)

    if live_ball:
        player_paddle.move()
        
        balls_to_remove = []
        for b in balls:
            game_over = b.move()
            if game_over != 0:
                if game_over == -1:
                    balls_to_remove.append(b)
                else:
                    live_ball = False
        
        for b in balls_to_remove:
            balls.remove(b)
        
        if len(balls) == 0:
            lives -= 1
            if lives > 0:
                live_ball = False
            else:
                game_over = -1
                live_ball = False
        
        powerups_to_remove = []
        for powerup in powerups:
            if powerup.move():
                powerups_to_remove.append(powerup)
            
            if powerup.rect.colliderect(player_paddle.rect):
                if powerup.type == 'expand':
                    player_paddle.expand()
                elif powerup.type == 'slow':
                    for b in balls:
                        b.slow()
                elif powerup.type == 'multi':
                    for i in range(2):
                        new_ball = game_ball(balls[0].rect.centerx, balls[0].rect.centery)
                        new_ball.speed_x = balls[0].speed_x + random.choice([-2, 2])
                        new_ball.speed_y = balls[0].speed_y
                        balls.append(new_ball)
                elif powerup.type == 'life':
                    lives += 1
                
                powerups_to_remove.append(powerup)
        
        for powerup in powerups_to_remove:
            if powerup in powerups:
                powerups.remove(powerup)

    if not live_ball:
        if game_over == 0:
            draw_text('CLICK ANYWHERE TO START', font, text_col, 100, screen_height // 2 + 100)
        elif game_over == 1:
            draw_text('YOU WON!', font, text_col, 240, screen_height // 2 + 50)
            draw_text('CLICK ANYWHERE TO START', font, text_col, 100, screen_height // 2 + 100)
        elif game_over == -1:
            draw_text('YOU LOST!', font, text_col, 240, screen_height // 2 + 50)
            draw_text('CLICK ANYWHERE TO START', font, text_col, 100, screen_height // 2 + 100)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and live_ball == False:
            live_ball = True
            ball.reset(player_paddle.x + (player_paddle.width // 2), player_paddle.y - player_paddle.height)
            balls = [ball]
            powerups = []
            player_paddle.reset()
            wall.create_wall()
            if game_over != 0:
                lives = 3
                game_over = 0

    pygame.display.update()

pygame.quit()
