
import pygame
import random
import sys

# Use this to play a very trimmed down version of Galaga.
# Move your ship using the arrow keys and space to fire
# Kill all of the ships and you win!
# Lose all your lives and you lose!
# Made using pygame
# @author: Tristan James
# @version: COVID-19


# Shows the overlay for the game, the score and number of lives
class Overlay(pygame.sprite.Sprite):
    # Constructor that sets up hit boxes and sets initial overlay
    def __init__(self):
        super(pygame.sprite.Sprite, self).__init__()
        self.image = pygame.Surface((800, 20))
        self.rect = self.image.get_rect()
        self.font = pygame.font.Font('freesansbold.ttf', 18)
        self.render("Score: 0        Lives: 5")

    # Renders text onto overlay
    def render(self, text):
        self.text = self.font.render(text, True, (255, 255, 255))
        self.image.blit(self.text, self.rect)

    # Blits the overlay on argued screen
    def draw(self, screen):
        screen.blit(self.text, (0, 0))

    # Updates the overlay with specified screen and new socre and lives
    def update(self, screen, score, lives):
        self.render("Score: " + str(score) + "        Lives: " + str(lives)) 

# Ship that you get to play as
class Ship(pygame.sprite.Sprite):
    # Constructor that sets image, start postion, and hit box of ship
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("assets/PNG/playerShip1_green.png")
        self.rect = self.image.get_rect()
        self.rect.x = 450
        self.rect.y = 800

    #Blits the ship when you move on argued screen
    def draw(self, screen):
        screen.blit(self.image, self.rect)

# Projectiles that all ships and enemies use
class Projectile(pygame.sprite.Sprite):
    # Constructor that sets image and sounds. enemy determines if it was
    # fired by an enemy
    def __init__(self, enemy):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("assets/PNG/Lasers/laserBlue15.png")
        self.rect = self.image.get_rect()
        self.vector = [ 0, 0 ]
        self.enemy = enemy
        self.hit_sound = pygame.mixer.Sound('assets/thud.wav')
        self.fire_sound = pygame.mixer.Sound('assets/DStar-Gun4.wav')
        self.fire_sound.play()

    # Updates projectiles, and causes sprite changes based on collisions with enemies or ship
    def update(self, game, enemies, ship):
        # removes from group if off screen
        if self.rect.y > ship.rect.y or self.rect.y <= 0:
            self.kill()
        hitEnemy = pygame.sprite.spritecollideany(self, enemies)
        if hitEnemy and self.enemy == False: #enemy hit and fired by player
            self.hit_sound.play()
            hitEnemy.kill()
            game.score += 5
            expl = Explosion()
            expl.rect.x = hitEnemy.rect.x
            expl.rect.y = hitEnemy.rect.y
            game.explosions.add(expl)
            self.kill()
        if pygame.sprite.collide_rect(self, ship) and self.enemy == True:
            self.hit_sound.play()
            pygame.event.post(game.death_event)
            self.kill()
        self.rect.y += self.vector[1]

# Base Enemy class
class Enemy(pygame.sprite.Sprite):
    # Constructor that set image to argument, to create different looking enemies
    def __init__(self, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()

    # Moves enemies in pattern. left determines whether to move left or not
    def update(self, left):
        if left:
            self.rect.x -= 5
        else:
            self.rect.x += 5

# Base explosion, created when enemy is destroyed
class Explosion(pygame.sprite.Sprite):
    # Constructor sets image
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("assets/PNG/Damage/playerShip1_damage3.png")
        self.rect = self.image.get_rect()

# Game class that handles gameplay loop and updates of everything
class Game:
    # Constructor that sets enemies up, sounds, screen, and events
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(50)
        pygame.mixer.music.load('assets/loop.wav')
        pygame.mixer.music.play(-1)
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((1100, 900))
        self.enemies = pygame.sprite.Group()
        # Sets enemies up like in galaga with different enemies on different rows
        for i in range(0, 5):
            if i < 1:
                for j in range(3, 7):
                    enemy = Enemy("assets/PNG/Enemies/enemyBlue1.png")
                    enemy.rect.x = (j * 100) + 50
                    enemy.rect.y = i * 100
                    self.enemies.add(enemy)
            elif i < 3:
                for j in range(1, 9):
                    enemy = Enemy("assets/PNG/Enemies/enemyRed2.png")
                    enemy.rect.x = (j * 100) + 50
                    enemy.rect.y = i * 100
                    self.enemies.add(enemy)
            else:    
                for j in range(0, 10):
                    enemy = Enemy("assets/PNG/Enemies/enemyGreen5.png")
                    enemy.rect.x = (j * 100) + 50
                    enemy.rect.y = i * 100
                    self.enemies.add(enemy)
        self.ship = Ship()
        self.death_event = pygame.event.Event(pygame.USEREVENT + 1)
        self.projectiles = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.overlay = Overlay()
        self.screen.fill((0, 0, 0))
        self.enemy_fire_event = pygame.event.Event(pygame.USEREVENT + 2)
        pygame.time.set_timer(self.enemy_fire_event.type, random.randint(1000, 10000), True) # random enemy firing
        self.enemy_move = pygame.event.Event(pygame.USEREVENT + 3)
        pygame.time.set_timer(self.enemy_move.type, 500) # enemies move often
        self.ready = True
        self.score = 0
        self.lives = 5
        self.left = False
        self.move_count = 10 # for moving enemies 
        self.fire_count = 0 # for not letting player win really easy with mega laser

    # Gameplay loop, checks for events and handles all keypresses
    def run(self):
        self.done = False
        while not self.done:
            self.screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == self.death_event.type: # if you get hit
                    self.lives -= 1
                    if self.lives <= 0:
                        pygame.quit()
                        sys.exit(0)
                if event.type == self.enemy_fire_event.type and len(self.enemies) > 0: # enemy fires
                    enemy_fired = self.enemies.sprites()[random.randint(0, len(self.enemies) - 1)]
                    proj = Projectile(True)
                    proj.rect.x = enemy_fired.rect.x + 45
                    proj.rect.y = enemy_fired.rect.y
                    proj.vector = [ 0, 10 ]
                    pygame.time.set_timer(pygame.USEREVENT + 2, random.randint(1000, 2000), True) # set another random interval for enemy to fire
                    self.projectiles.add(proj)
                if len(self.enemies) <= 0:
                    pygame.quit()
                    sys.exit(0)
                if event.type == self.enemy_move.type: # moves enemies 20 times left or right
                    if self.left:
                        self.enemies.update(True)
                        self.move_count += 1
                        if self.move_count > 20:
                            self.move_count = 0
                            self.left = False
                    else:
                        self.enemies.update(False)
                        self.move_count += 1
                        if self.move_count > 20:
                            self.move_count = 0
                            self.left = True
                    self.explosions.empty()
                if event.type == pygame.QUIT:
                    self.done = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.ready:
                        proj = Projectile(False)
                        proj.rect.x = self.ship.rect.x + 45
                        proj.rect.y = self.ship.rect.y
                        proj.vector = [ 0, -10 ]
                        self.projectiles.add(proj)
                        self.ready = False
                        self.fire_count = 0
                    if event.key == pygame.K_LEFT:
                        self.ship.rect.x -= 5
                        if self.ship.rect.x <= 0:
                            self.ship.rect.x = 0
                    if event.key == pygame.K_RIGHT:
                        self.ship.rect.x += 5
                        if self.ship.rect.x >= 1000:
                            self.ship.rect.x = 1000
            if self.ready == False: # after fire_count is 0 player can fire again
                self.fire_count += 1
                if self.fire_count > 50:
                    self.ready = True
            self.projectiles.update(self, self.enemies, self.ship)
            self.overlay.update(self.screen, self.score, self.lives)
            self.projectiles.draw(self.screen)
            self.explosions.draw(self.screen)
            self.ship.draw(self.screen)
            self.enemies.draw(self.screen)
            self.overlay.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()