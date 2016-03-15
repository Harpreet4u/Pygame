import sys
import pygame
import random

SCREEN_X = 640
SCREEN_Y = 640

DEBUG = True


class Game(object):
    def main(self, screen):
        clock = pygame.time.Clock()
        
        sprites = pygame.sprite.Group()
        self.player = Player(sprites)
        
        # 1 --- health
        # 2 --- success
        # 3 -- bot mode
        flag = 0
        while True:
            clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN and \
                        event.key == pygame.K_ESCAPE:
                    return
                if event.type == pygame.KEYDOWN and \
                        event.key == pygame.K_TAB:
                    flag = 3
            if flag == 0:
                sprites.update()
            elif flag == 3:
                self.player.bot_update()
            
            screen.fill((200, 200, 200))
            
            bot = ""
            if flag == 3:
                bot = "Bot Mode-"
            

            if self.player.health <= 0:
                flag = 1
                self.pprint(bot + " Game Over, no health!")
            else:
                self.pprint(bot + " Health: " + str(self.player.health) + "%")
                pass

            if self.player.exit.position == self.player.position:
                flag = 2
                self.pprint(bot + " You Won!")

            sprites.draw(screen)
            pygame.display.flip()


    def pprint(self, msg, position=(200, 10)):
        screen.fill((200, 200, 200))
        myfont = pygame.font.SysFont("monospace", 25)
        # render text
        label = myfont.render(msg, 1, (255,0,0))
        screen.blit(label, position)


class Player(pygame.sprite.Sprite):

    position = (0, 0)
    # -10 for each enemy hit
    health = 100

    def __init__(self, *groups):
        super(Player, self).__init__(*groups)
        self.wall = Wall()
        self.enemy = Enemy()
        self.enemy.spawn_enemies(self.wall.wall_positions)
        self.exit = Exit(self.wall.wall_positions, self.enemy.enemy_positions)
        self.step = 80
        self.image = pygame.image.load('player.png')
        self.image = pygame.transform.scale(self.image, (self.step, self.step))

        self.rect = pygame.rect.Rect((0, self.step), self.image.get_size())

    def update(self):
        key = pygame.key.get_pressed()

        if key[pygame.K_LEFT] and (self.rect.x - self.step) >= 0:
            self.rect.x -= self.step
        if key[pygame.K_RIGHT] and (self.rect.x + self.step) <= (SCREEN_X -\
                self.step):
            self.rect.x += self.step
        if key[pygame.K_UP] and (self.rect.y - self.step) >= 80:
            self.rect.y -= self.step
        if key[pygame.K_DOWN] and (self.rect.y + self.step) <= (SCREEN_Y -\
                self.step):
            self.rect.y += self.step

        old_pos = self.position
        self.position = (self.rect.x / 80, (self.rect.y / 80) - 1)
        
        if self.wall.is_wall(self.position):
            self.position = old_pos
            self.rect.x = self.position[0]*80
            self.rect.y = (self.position[1]+1)*80
        
        if self.enemy.is_enemy(self.position):
            self.health -= 2

        if False and DEBUG:
            print "X: " + str(self.rect.x)
            print "Y: " + str(self.rect.y)
            print "Position - X: " + str(self.position[0]) + " Y: " +\
            str(self.position[1])

    def bot_update(self):
        if not self.found:
            for i in range(7):
                ls = []
                for j in range(8):
                    ls.append(0)
                self.sol_path.append(ls)
            self.find_path(self.position)
            for i in range(7):
                print self.sol_path[i]
        else:
            if len(self.path) > 0:
                print self.path
                if self.sol_path[self.path[0][1]][self.path[0][0]]:
                    x, y = self.path[0][0]*80, (self.path[0][1]+1)*80
                    self.rect.x = x
                    self.rect.y = y
                    self.position = self.path[0]
                self.path = self.path[1:]


    sol_path = []
    found = False
    cnt = 1
    path = []

    def find_path(self, pos):
        #print pos
        if pos[0] >= 0 and pos[0] <= 7 and pos[1] >= 0 and pos[1] <= 6:
        
            if self.sol_path[pos[1]][pos[0]] == 1:
                return False
            if pos == self.exit.position:
                self.found = True
                self.sol_path[pos[1]][pos[0]] = self.cnt
                self.path.append(pos)
                self.cnt += 1
                return True
            if pos in self.wall.wall_positions or pos in self.enemy.enemy_positions:
                return False
            self.sol_path[pos[1]][pos[0]] = self.cnt
            self.path.append(pos)
            if not self.found and self.find_path((pos[0], pos[1]-1)) == True:
                return True
            if not self.found and self.find_path((pos[0] + 1, pos[1])) == True:
                return True
            if not self.found and self.find_path((pos[0], pos[1]+1)) == True:
                return True
            if not self.found and self.find_path((pos[0]-1, pos[1])) == True:
                return True
            if not self.found:
                self.sol_path[pos[1]][pos[0]] = 0
        return False


class Wall():
    
    min_walls = 2
    max_walls = 6

    # tuple of positions
    wall_positions = []
    
    def __init__(self):
        walls_to_place = random.randrange(self.min_walls, self.max_walls)
        
        for i in range(walls_to_place):
            (x, y) = self.generate_position()
            self.wall_positions.append((x, y))

        if DEBUG:
            print self.wall_positions


    def is_wall(self, position):
        if tuple(position) in self.wall_positions:
            return True
        return False

    def generate_position(self):
        (x, y) = (random.randrange(7), random.randrange(8))
        while (x, y) in self.wall_positions or (0, 0) == (x, y):
            (x, y) = (random.randrange(7), random.randrange(8))

        return (x, y)

class Enemy():

    min_enemy = 3
    max_enemy = 5

    enemy_positions = []

    def __init__(self):
        self.enemies_to_place = random.randrange(self.min_enemy, self.max_enemy)


    def spawn_enemies(self, walls):
        for i in range(self.enemies_to_place):
            (x, y) = self.generate_positions(walls)
            self.enemy_positions.append((x, y))

        if DEBUG:
            print self.enemy_positions

    def is_enemy(self, position):
        if tuple(position) in self.enemy_positions:
            return True
        return False

    def generate_positions(self, walls):
        (x, y) = (random.randrange(7), random.randrange(8))
        while (x, y) in self.enemy_positions or (x, y) in walls or \
                (x, y) == (0, 0):
            (x, y) = (random.randrange(7), random.randrange(8))

        return (x, y)

class Exit():

    position = (6, 6)

    def __init__(self, walls, enemies):
        self.position = self.generate_position(walls, enemies)
        if DEBUG:
            print self.position

    def generate_position(self, walls, enemies):
        (x, y) = (random.randrange(7), random.randrange(8))
        while (x, y) in enemies or (x, y) in walls or (x, y) == (0, 0):
            (x, y) = (random.randrange(7), random.randrange(8))

        return (x, y)


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_X, SCREEN_Y))
    Game().main(screen)
