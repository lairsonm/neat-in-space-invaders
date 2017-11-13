# Space Invaders
# Created by Lee Robinson

#!/usr/bin/env python
from pygame import *
import sys
from random import shuffle, randrange, choice
from datetime import datetime

#           R    G    B
WHITE 	= (255, 255, 255)
GREEN 	= (78, 255, 87)
YELLOW 	= (241, 255, 0)
BLUE 	= (80, 255, 239)
PURPLE 	= (203, 0, 255)
RED 	= (237, 28, 36)

SCREEN_DISPLAY 		= display.set_mode((800,600))
FONT = "fonts/space_invaders.ttf"
IMG_NAMES 	= ["ship", "ship", "mystery", "enemy1_1", "enemy1_2", "enemy2_1", "enemy2_2",
                "enemy3_1", "enemy3_2", "explosionblue", "explosiongreen", "explosionpurple", "laser", "enemylaser"]
IMAGES 		= {name: image.load("SpaceInvaders/images/{}.png".format(name)).convert_alpha()
                for name in IMG_NAMES}

class Ship(sprite.Sprite):
    def __init__(self, individual):
        sprite.Sprite.__init__(self)
        self.image = IMAGES["ship"]
        self.rect = self.image.get_rect(topleft=(375, 540))
        self.speed = 5
        self.individual = individual


    def update(self, keys, *args):
        X = []
        X.append(self.rect.x)
        activation = self.individual.predict(X)
        #print "esquerda" + str(activation[0])
        #print "direita" + str(activation[1])
        #print "tiro" + str(activation[2])
        if activation[0] == True  and self.rect.x > 10:
            self.rect.x -= self.speed
        if activation[1] == True and self.rect.x < 740:
            self.rect.x += self.speed
        if keys[K_LEFT] and self.rect.x > 10:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < 740:
            self.rect.x += self.speed


        SCREEN.blit(self.image, self.rect)


class Bullet(sprite.Sprite):
    def __init__(self, xpos, ypos, direction, speed, filename, side):
        sprite.Sprite.__init__(self)
        self.image = IMAGES[filename]
        self.rect = self.image.get_rect(topleft=(xpos, ypos))
        self.speed = speed
        self.direction = direction
        self.side = side
        self.filename = filename

    def update(self, keys, *args):
        SCREEN.blit(self.image, self.rect)
        self.rect.y += self.speed * self.direction
        if self.rect.y < 15 or self.rect.y > 600:
            self.kill()


class Enemy(sprite.Sprite):
    def __init__(self, row, column):
        sprite.Sprite.__init__(self)
        self.row = row
        self.column = column
        self.images = []
        self.load_images()
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.direction = 1
        self.rightMoves = 15
        self.leftMoves = 30
        self.moveNumber = 0
        self.moveTime = 600
        self.firstTime = True
        self.movedY = False
        self.columns = [False] * 10
        self.aliveColumns = [True] * 10
        self.addRightMoves = False
        self.addLeftMoves = False
        self.numOfRightMoves = 0
        self.numOfLeftMoves = 0
        self.timer = time.get_ticks()

    def update(self, keys, currentTime, killedRow, killedColumn, killedArray):
        self.check_column_deletion(killedRow, killedColumn, killedArray)
        if currentTime - self.timer > self.moveTime:
            self.movedY = False
            if self.moveNumber >= self.rightMoves and self.direction == 1:
                self.direction *= -1
                self.moveNumber = 0
                self.rect.y += 35
                self.movedY = True
                if self.addRightMoves:
                    self.rightMoves += self.numOfRightMoves
                if self.firstTime:
                    self.rightMoves = self.leftMoves
                    self.firstTime = False
                self.addRightMovesAfterDrop = False
            if self.moveNumber >= self.leftMoves and self.direction == -1:
                self.direction *= -1
                self.moveNumber = 0
                self.rect.y += 35
                self.movedY = True
                if self.addLeftMoves:
                    self.leftMoves += self.numOfLeftMoves
                self.addLeftMovesAfterDrop = False
            if self.moveNumber < self.rightMoves and self.direction == 1 and not self.movedY:
                self.rect.x += 10
                self.moveNumber += 1
            if self.moveNumber < self.leftMoves and self.direction == -1 and not self.movedY:
                self.rect.x -= 10
                self.moveNumber += 1

            self.index += 1
            if self.index >= len(self.images):
                self.index = 0
            self.image = self.images[self.index]

            self.timer += self.moveTime
        SCREEN.blit(self.image, self.rect)

    def check_column_deletion(self, killedRow, killedColumn, killedArray):
        if killedRow != -1 and killedColumn != -1:
            killedArray[killedRow][killedColumn] = 1
            for column in range(10):
                if all([killedArray[row][column] == 1 for row in range(5)]):
                    self.columns[column] = True

        for i in range(5):
            if all([self.columns[x] for x in range(i + 1)]) and self.aliveColumns[i]:
                self.leftMoves += 5
                self.aliveColumns[i] = False
                if self.direction == -1:
                    self.rightMoves += 5
                else:
                    self.addRightMoves = True
                    self.numOfRightMoves += 5

        for i in range(5):
            if all([self.columns[x] for x in range(9, 8 - i, -1)]) and self.aliveColumns[9 - i]:
                self.aliveColumns[9 - i] = False
                self.rightMoves += 5
                if self.direction == 1:
                    self.leftMoves += 5
                else:
                    self.addLeftMoves = True
                    self.numOfLeftMoves += 5

    def load_images(self):
        images = {0: ["1_2", "1_1"],
                  1: ["2_2", "2_1"],
                  2: ["2_2", "2_1"],
                  3: ["3_1", "3_2"],
                  4: ["3_1", "3_2"],
                 }
        img1, img2 = (IMAGES["enemy{}".format(img_num)] for img_num in images[self.row])
        self.images.append(transform.scale(img1, (40, 35)))
        self.images.append(transform.scale(img2, (40, 35)))


class Blocker(sprite.Sprite):
    def __init__(self, size, color, row, column):
       sprite.Sprite.__init__(self)
       self.height = size
       self.width = size
       self.color = color
       self.image = Surface((self.width, self.height))
       self.image.fill(self.color)
       self.rect = self.image.get_rect()
       self.row = row
       self.column = column

    def update(self, keys, *args):
        SCREEN.blit(self.image, self.rect)


class Mystery(sprite.Sprite):
    def __init__(self):
        sprite.Sprite.__init__(self)
        self.image = IMAGES["mystery"]
        self.image = transform.scale(self.image, (75, 35))
        self.rect = self.image.get_rect(topleft=(-80, 45))
        self.row = 5
        self.moveTime = 25000
        self.direction = 1
        self.timer = time.get_ticks()
        #self.mysteryEntered = mixer.Sound('sounds/mysteryentered.wav')
        #self.mysteryEntered.set_volume(0.3)
        #self.playSound = True

    def update(self, keys, currentTime, *args):
        resetTimer = False
        #if (currentTime - self.timer > self.moveTime) and (self.rect.x < 0 or self.rect.x > 800) and self.playSound:
            #self.mysteryEntered.play()
            #self.playSound = False
        if (currentTime - self.timer > self.moveTime) and self.rect.x < 840 and self.direction == 1:
            #self.mysteryEntered.fadeout(4000)
            self.rect.x += 2
            SCREEN.blit(self.image, self.rect)
        if (currentTime - self.timer > self.moveTime) and self.rect.x > -100 and self.direction == -1:
            #self.mysteryEntered.fadeout(4000)
            self.rect.x -= 2
            SCREEN.blit(self.image, self.rect)
        if (self.rect.x > 830):
            #self.playSound = True
            self.direction = -1
            resetTimer = True
        if (self.rect.x < -90):
            #self.playSound = True
            self.direction = 1
            resetTimer = True
        if (currentTime - self.timer > self.moveTime) and resetTimer:
            self.timer = currentTime


class Explosion(sprite.Sprite):
    def __init__(self, xpos, ypos, row, ship, mystery, score):
        sprite.Sprite.__init__(self)
        self.isMystery = mystery
        self.isShip = ship
        if mystery:
            self.text = Text(FONT, 20, str(score), WHITE, xpos+20, ypos+6)
        elif ship:
            self.image = IMAGES["ship"]
            self.rect = self.image.get_rect(topleft=(xpos, ypos))
        else:
            self.row = row
            self.load_image()
            self.image = transform.scale(self.image, (40, 35))
            self.rect = self.image.get_rect(topleft=(xpos, ypos))
            SCREEN.blit(self.image, self.rect)

        self.timer = time.get_ticks()

    def update(self, keys, currentTime):
        if self.isMystery:
            if currentTime - self.timer <= 200:
                self.text.draw(SCREEN)
            if currentTime - self.timer > 400 and currentTime - self.timer <= 600:
                self.text.draw(SCREEN)
            if currentTime - self.timer > 600:
                self.kill()
        elif self.isShip:
            if currentTime - self.timer > 300 and currentTime - self.timer <= 600:
                SCREEN.blit(self.image, self.rect)
            if currentTime - self.timer > 900:
                self.kill()
        else:
            if currentTime - self.timer <= 100:
                SCREEN.blit(self.image, self.rect)
            if currentTime - self.timer > 100 and currentTime - self.timer <= 200:
                self.image = transform.scale(self.image, (50, 45))
                SCREEN.blit(self.image, (self.rect.x-6, self.rect.y-6))
            if currentTime - self.timer > 400:
                self.kill()

    def load_image(self):
        imgColors = ["purple", "blue", "blue", "green", "green"]
        self.image = IMAGES["explosion{}".format(imgColors[self.row])]


class Life(sprite.Sprite):
    def __init__(self, xpos, ypos):
        sprite.Sprite.__init__(self)
        self.image = IMAGES["ship"]
        self.image = transform.scale(self.image, (23, 23))
        self.rect = self.image.get_rect(topleft=(xpos, ypos))

    def update(self, keys, *args):
        SCREEN.blit(self.image, self.rect)


class Text(object):
    def __init__(self, textFont, size, message, color, xpos, ypos):
        self.font = font.Font(textFont, size)
        self.surface = self.font.render(message, True, color)
        self.rect = self.surface.get_rect(topleft=(xpos, ypos))

    def draw(self, surface):
        surface.blit(self.surface, self.rect)


class SpaceInvaders(object):
    def __init__(self, individual):
        global SCREEN, FPSCLOCK
        mixer.pre_init(44100, -16, 1, 512)
        init()
        self.caption = display.set_caption('Space Invaders')
        SCREEN = SCREEN_DISPLAY
        self.background = image.load('images/background.jpg').convert()
        self.startGame = False
        self.mainScreen = True
        self.gameOver = False
        # Initial value for a new game
        self.enemyPositionDefault = 65
        # Counter for enemy starting position (increased each new round)
        self.enemyPositionStart = self.enemyPositionDefault
        # Current enemy starting position
        self.enemyPosition = self.enemyPositionStart
        FPSCLOCK = time.Clock()
        #SCREEN = pygame.display.set_mode((512, 512))
        self.score = 0
        self.crash_info = []
        self.individual = individual

        #"""  CREATE PLAYER """
        #self.movementInfo = tools.load_and_initialize()
            #self.ships = [Bird(self.movementInfo, neural_network, i) for i, neural_network in enumerate(neural_networks)]
        #""" CREATE PIPES """
        #if REPEATING_PIPES:
        #    self.pipes = Pipes(PIPE_PATTERN)
        #else:
        #    self.pipes = Pipes()

        #""" CREATE BASE """
        #self.base = Base(self.movementInfo['basex'])




    def reset(self, score, lives, newGame=False):
        self.player = Ship(self.individual)
        self.playerGroup = sprite.Group(self.player)
        self.explosionsGroup = sprite.Group()
        self.bullets = sprite.Group()
        self.mysteryShip = Mystery()
        self.mysteryGroup = sprite.Group(self.mysteryShip)
        self.enemyBullets = sprite.Group()
        self.reset_lives(lives)
        self.enemyPosition = self.enemyPositionStart
        self.make_enemies()
        # Only create blockers on a new game, not a new round
        if newGame:
            self.allBlockers = sprite.Group(self.make_blockers(0), self.make_blockers(1), self.make_blockers(2), self.make_blockers(3))
        self.keys = key.get_pressed()
        self.clock = time.Clock()
        self.timer = time.get_ticks()
        self.noteTimer = time.get_ticks()
        self.shipTimer = time.get_ticks()
        self.score = score
        self.lives = 0
        self.create_audio()
        self.create_text()
        self.killedRow = -1
        self.killedColumn = -1
        self.makeNewShip = False
        self.shipAlive = True
        self.killedArray = [[0] * 10 for x in range(5)]

    def make_blockers(self, number):
        blockerGroup = sprite.Group()
        for row in range(4):
            for column in range(9):
                blocker = Blocker(10, GREEN, row, column)
                blocker.rect.x = 50 + (200 * number) + (column * blocker.width)
                blocker.rect.y = 450 + (row * blocker.height)
                blockerGroup.add(blocker)
        return blockerGroup

    def reset_lives(self, lives):
        self.lives = lives

    def create_audio(self):
        self.sounds = {}
        for sound_name in ["shoot", "shoot2", "invaderkilled", "mysterykilled", "shipexplosion"]:
            self.sounds[sound_name] = mixer.Sound("sounds/{}.wav".format(sound_name))
            self.sounds[sound_name].set_volume(0.2)

        self.musicNotes = [mixer.Sound("sounds/{}.wav".format(i)) for i in range(4)]
        for sound in self.musicNotes:
            sound.set_volume(0.5)

        self.noteIndex = 0

    def play_main_music(self, currentTime):
        moveTime = self.enemies.sprites()[0].moveTime
        if currentTime - self.noteTimer > moveTime:
            self.note = self.musicNotes[self.noteIndex]
            if self.noteIndex < 3:
                self.noteIndex += 1
            else:
                self.noteIndex = 0

            self.note.play()
            self.noteTimer += moveTime

    def create_text(self):
        self.titleText = Text(FONT, 50, "Space Invaders", WHITE, 164, 155)
        self.titleText2 = Text(FONT, 25, "Press any key to continue", WHITE, 201, 225)
        self.gameOverText = Text(FONT, 50, "Game Over", WHITE, 250, 270)
        self.nextRoundText = Text(FONT, 50, "Next Round", WHITE, 240, 270)
        self.enemy1Text = Text(FONT, 25, "   =   10 pts", GREEN, 368, 270)
        self.enemy2Text = Text(FONT, 25, "   =  20 pts", BLUE, 368, 320)
        self.enemy3Text = Text(FONT, 25, "   =  30 pts", PURPLE, 368, 370)
        self.enemy4Text = Text(FONT, 25, "   =  ?????", RED, 368, 420)
        self.scoreText = Text(FONT, 20, "Score", WHITE, 5, 5)
        self.livesText = Text(FONT, 20, "Lives ", WHITE, 640, 5)

 # DA ONDE SAI OS TIROS
    def check_input(self):
        self.keys = key.get_pressed()
        X = []
        X.append(self.player.rect.x)
        activation = self.individual.predict(X)
        #for e in event.get():
        #    if e.type == QUIT:
        #        sys.exit()
            #if e.type == KEYDOWN:
                #if e.key == K_SPACE:
        if activation[2] == True:
            if len(self.bullets) == 0 and self.shipAlive:
                if self.score < 1000:
                    bullet = Bullet(self.player.rect.x+23, self.player.rect.y+5, -1, 15, "laser", "center")
                    self.bullets.add(bullet)
                    self.allSprites.add(self.bullets)
                    #self.sounds["shoot"].play()
                else:
                    leftbullet = Bullet(self.player.rect.x+8, self.player.rect.y+5, -1, 15, "laser", "left")
                    rightbullet = Bullet(self.player.rect.x+38, self.player.rect.y+5, -1, 15, "laser", "right")
                    self.bullets.add(leftbullet)
                    self.bullets.add(rightbullet)
                    self.allSprites.add(self.bullets)
                    #self.sounds["shoot2"].play()

    def make_enemies(self):
        enemies = sprite.Group()
        for row in range(5):
            for column in range(10):
                enemy = Enemy(row, column)
                enemy.rect.x = 157 + (column * 50)
                enemy.rect.y = self.enemyPosition + (row * 45)
                enemies.add(enemy)

        self.enemies = enemies
        self.allSprites = sprite.Group(self.player, self.enemies, self.mysteryShip)

    def make_enemies_shoot(self):
        columnList = []
        for enemy in self.enemies:
            columnList.append(enemy.column)

        columnSet = set(columnList)
        columnList = list(columnSet)
        shuffle(columnList)
        column = columnList[0]
        enemyList = []
        rowList = []

        for enemy in self.enemies:
            if enemy.column == column:
                rowList.append(enemy.row)
        row = max(rowList)
        for enemy in self.enemies:
            if enemy.column == column and enemy.row == row:
                if (time.get_ticks() - self.timer) > 700:
                    self.enemyBullets.add(Bullet(enemy.rect.x + 14, enemy.rect.y + 20, 1, 5, "enemylaser", "center"))
                    self.allSprites.add(self.enemyBullets)
                    self.timer = time.get_ticks()

    def calculate_score(self, row):
        scores = {0: 30,
                  1: 20,
                  2: 20,
                  3: 10,
                  4: 10,
                  5: choice([50, 100, 150, 300])
                 }

        score = scores[row]
        self.score += score
        return score

    def create_main_menu(self):
        self.enemy1 = IMAGES["enemy3_1"]
        self.enemy1 = transform.scale(self.enemy1 , (40, 40))
        self.enemy2 = IMAGES["enemy2_2"]
        self.enemy2 = transform.scale(self.enemy2 , (40, 40))
        self.enemy3 = IMAGES["enemy1_2"]
        self.enemy3 = transform.scale(self.enemy3 , (40, 40))
        self.enemy4 = IMAGES["mystery"]
        self.enemy4 = transform.scale(self.enemy4 , (80, 40))
        SCREEN.blit(self.enemy1, (318, 270))
        SCREEN.blit(self.enemy2, (318, 320))
        SCREEN.blit(self.enemy3, (318, 370))
        SCREEN.blit(self.enemy4, (299, 420))
# COMECAR NOVO JOGO
        for e in event.get():
            if e.type == QUIT:
                sys.exit()
            if e.type == KEYUP:
                self.startGame = True
                self.mainScreen = False

    def update_enemy_speed(self):
        if len(self.enemies) <= 10:
            for enemy in self.enemies:
                enemy.moveTime = 400
        if len(self.enemies) == 1:
            for enemy in self.enemies:
                enemy.moveTime = 200

    def check_collisions(self):
        collidedict = sprite.groupcollide(self.bullets, self.enemyBullets, True, False)
        if collidedict:
            for value in collidedict.values():
                for currentSprite in value:
                    self.enemyBullets.remove(currentSprite)
                    self.allSprites.remove(currentSprite)

        enemiesdict = sprite.groupcollide(self.bullets, self.enemies, True, False)
        if enemiesdict:
            for value in enemiesdict.values():
                for currentSprite in value:
                    #self.sounds["invaderkilled"].play()
                    self.killedRow = currentSprite.row
                    self.killedColumn = currentSprite.column
                    score = self.calculate_score(currentSprite.row)
                    explosion = Explosion(currentSprite.rect.x, currentSprite.rect.y, currentSprite.row, False, False, score)
                    self.explosionsGroup.add(explosion)
                    self.allSprites.remove(currentSprite)
                    self.enemies.remove(currentSprite)
                    self.gameTimer = time.get_ticks()
                    break

        mysterydict = sprite.groupcollide(self.bullets, self.mysteryGroup, True, True)
        if mysterydict:
            for value in mysterydict.values():
                for currentSprite in value:
                    #currentSprite.mysteryEntered.stop()
                    #self.sounds["mysterykilled"].play()
                    score = self.calculate_score(currentSprite.row)
                    explosion = Explosion(currentSprite.rect.x, currentSprite.rect.y, currentSprite.row, False, True, score)
                    self.explosionsGroup.add(explosion)
                    self.allSprites.remove(currentSprite)
                    self.mysteryGroup.remove(currentSprite)
                    newShip = Mystery()
                    self.allSprites.add(newShip)
                    self.mysteryGroup.add(newShip)
                    break
#TIRO INIMIGO ATINGIU O JOGADOR
        bulletsdict = sprite.groupcollide(self.enemyBullets, self.playerGroup, True, False)
        if bulletsdict:
            for value in bulletsdict.values():
                for playerShip in value:
                    if self.lives == 0:
                        self.gameOver = True
                        self.startGame = False
                    #self.sounds["shipexplosion"].play()
                    explosion = Explosion(playerShip.rect.x, playerShip.rect.y, 0, True, False, 0)
                    self.explosionsGroup.add(explosion)
                    self.allSprites.remove(playerShip)
                    self.playerGroup.remove(playerShip)
                    self.makeNewShip = True
                    self.shipTimer = time.get_ticks()
                    self.shipAlive = False
# INVADER ATINGIU O JOGADOR
        if sprite.groupcollide(self.enemies, self.playerGroup, True, True):
            self.gameOver = True
            self.startGame = False

        sprite.groupcollide(self.bullets, self.allBlockers, True, True)
        sprite.groupcollide(self.enemyBullets, self.allBlockers, True, True)
        sprite.groupcollide(self.enemies, self.allBlockers, False, True)
        for enemy in self.enemies:
            if not enemy.rect.y > 1:
                print("error")

    def create_new_ship(self, createShip, currentTime):
        if createShip and (currentTime - self.shipTimer > 900):
            self.player = Ship()
            self.allSprites.add(self.player)
            self.playerGroup.add(self.player)
            self.makeNewShip = False
            self.shipAlive = True
# tela de game over
    def create_game_over(self, currentTime):
        SCREEN.blit(self.background, (0,0))
        if currentTime - self.timer < 750:
            self.gameOverText.draw(SCREEN)
        if currentTime - self.timer > 750 and currentTime - self.timer < 1500:
            SCREEN.blit(self.background, (0,0))
        if currentTime - self.timer > 1500 and currentTime - self.timer < 2250:
            self.gameOverText.draw(SCREEN)
        if currentTime - self.timer > 2250 and currentTime - self.timer < 2750:
            SCREEN.blit(self.background, (0,0))
        if currentTime - self.timer > 3000:
            self.mainScreen = True

        for e in event.get():
            if e.type == QUIT:
                sys.exit()
# main do jogo
    def main(self):
        while True:
            if self.mainScreen:
                self.reset(0, 3, True)
                SCREEN.blit(self.background, (0,0))
                self.titleText.draw(SCREEN)
                self.titleText2.draw(SCREEN)
                self.enemy1Text.draw(SCREEN)
                self.enemy2Text.draw(SCREEN)
                self.enemy3Text.draw(SCREEN)
                self.enemy4Text.draw(SCREEN)
                self.create_main_menu()
                if datetime.now().second % 2 == 0:
                    self.mainScreen = False
                    self.startGame = True

            elif self.startGame:
                if len(self.enemies) == 0:
                    currentTime = time.get_ticks()
                    if currentTime - self.gameTimer < 3000:
                        SCREEN.blit(self.background, (0,0))
                        self.scoreText2 = Text(FONT, 20, str(self.score), GREEN, 85, 5)
                        self.scoreText.draw(SCREEN)
                        self.scoreText2.draw(SCREEN)
                        self.nextRoundText.draw(SCREEN)
                        self.livesText.draw(SCREEN)
                        self.check_input()
                    if currentTime - self.gameTimer > 3000:
                        # Move enemies closer to bottom
                        self.enemyPositionStart += 35
                        self.reset(self.score, self.lives)
                        self.make_enemies()
                        self.gameTimer += 3000
                else:
                    currentTime = time.get_ticks()
                    #self.play_main_music(currentTime)
                    SCREEN.blit(self.background, (0,0))
                    self.allBlockers.update(SCREEN)
                    self.scoreText2 = Text(FONT, 20, str(self.score), GREEN, 85, 5)
                    self.scoreText.draw(SCREEN)
                    self.scoreText2.draw(SCREEN)
                    self.livesText.draw(SCREEN)
                    self.check_input()
                    self.allSprites.update(self.keys, currentTime, self.killedRow, self.killedColumn, self.killedArray)
                    self.explosionsGroup.update(self.keys, currentTime)
                    self.check_collisions()
                    self.create_new_ship(self.makeNewShip, currentTime)
                    self.update_enemy_speed()

                    if len(self.enemies) > 0:
                        self.make_enemies_shoot()
# acao de game over
            elif self.gameOver:
                currentTime = time.get_ticks()
                # Reset enemy starting position
                self.enemyPositionStart = self.enemyPositionDefault
                self.create_game_over(currentTime)
                print self.score
                return self.score



            display.update()
            self.clock.tick(60)


                
'''               
class SpaceInvadersApp(object):

    def __init__(self, neural_networks):
        global SCREEN, FPSCLOCK

        pygame.init()
        FPSCLOCK = pygame.time.Clock()
        SCREEN = pygame.display.set_mode((512, 512))
        pygame.display.set_caption('SpaceInvaders')

        self.score = 0
        self.crash_info = []
        self.num_organisms = len(neural_networks)

        """  CREATE PLAYER """
        self.movementInfo = tools.load_and_initialize()
        self.ships = [Bird(self.movementInfo, neural_network, i) for i, neural_network in enumerate(neural_networks)]
        """ CREATE PIPES """
        if REPEATING_PIPES:
            self.pipes = Pipes(PIPE_PATTERN)
        else:
            self.pipes = Pipes()

        """ CREATE BASE """
        self.base = Base(self.movementInfo['basex'])


    def play(self):

        while True:
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()

            if self.on_loop():
                return
            else:
                self.on_render()



    def on_loop(self):

        # =========----==========================================================
        """ CHECK FLAP """              # NEURAL NET WILL INTERFACE HERE
        # =========----==========================================================
        for bird in self.ships:
            bird.flap_decision(self.pipes)
        # =========----==========================================================



        # =========----==========================================================
        """ CHECK CRASH """
        # =========----==========================================================
        for index, ship in enumerate(self.ships):
            if bird.check_crash(self.totalPoints):
                self.crash_info.append(bird.crashInfo)
                del self.birds[index]
                if len(self.birds) == 0:
                    return True
        # =========----==========================================================


        # =========----==========================================================
        """ CHECK FOR SCORE """
        # =========----==========================================================
        break_one = break_two = False
        for bird in self.birds:
            playerMidPos = bird.x + IMAGES['player'][0].get_width() / 2
            for pipe in self.pipes.upper:
                pipeMidPos = pipe['x'] + IMAGES['pipe'][0].get_width() / 2
                if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                    self.score += 1
                    break_one = break_two = True
                    SOUNDS['point'].play() if SOUND_ON else None
                if break_one:
                    break
            if break_two:
                break

        # =========----==========================================================


        # =========----==========================================================
        """ MOVE BASE """
        # =========----==========================================================
        self.base.move(self.birds)
        # =========----==========================================================


        # =========----==========================================================
        """ MOVE PLAYER """
        # =========----==========================================================
        for bird in self.birds:
            bird.move()
        # =========----==========================================================


        # =========----==========================================================
        """ MOVE PIPES """
        # =========----==========================================================
        self.pipes.move(self.birds)
        # =========----==========================================================
        return False


    def on_render(self):
        # =========----==========================================================
        """ DRAW BACKGROUND """
        # =========----==========================================================
        SCREEN.blit(IMAGES['background'], (0,0))
        # =========----==========================================================


        # =========----==========================================================
        """ DRAW PIPES """
        # =========----==========================================================
        self.pipes.draw(SCREEN)
        # =========----==========================================================


        # =========----==========================================================
        """ DRAW BASE """
        # =========----==========================================================
        SCREEN.blit(IMAGES['base'], (self.base.basex, BASEY))
        # =========----==========================================================


        # =========----==========================================================
        """ DRAW STATS """
        # =========----==========================================================
        disp_tools.displayStat(SCREEN, self.birds[0].distance*-1, text="distance")
        disp_tools.displayStat(SCREEN, self.score, text="scores")
        disp_tools.displayStat(SCREEN, self.num_organisms, text="organism")
        for bird in self.birds:
            # disp_tools.displayStat(SCREEN, bird.energy_used, text="energy")
            # disp_tools.displayStat(SCREEN, neural_network.topology, text="topology")
            disp_tools.displayStat(SCREEN, bird.neural_network.species_number, text="species")
            disp_tools.displayStat(SCREEN, bird.neural_network.generation_number, text="generation")
            SCREEN.blit(IMAGES['player'][bird.index], (bird.x, bird.y))
        # =========----==========================================================


        # =========----==========================================================
        """ UPDATE DISPLAY """
        # =========----==========================================================
        pygame.display.update()
        # =========----==========================================================


        # =========----==========================================================
        """ TICK CLOCK """
        # =========----==========================================================
        FPSCLOCK.tick(FPS)
        # =========----==========================================================

'''

if __name__ == '__main__':
    game = SpaceInvaders()
    game.main()
