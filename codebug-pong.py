import pygame
import os, sys
import pygame.locals
import random
import time
import codebug_tether
import codebug_tether.sprites
from codebug_tether import (IO_DIGITAL_INPUT, IO_ANALOGUE_INPUT, IO_PWM_OUTPUT, IO_DIGITAL_OUTPUT)


logo = pygame.image.load('codebug-logo.png')

codebug1 = codebug_tether.CodeBug('/dev/ttyACM1')
codebug1.set_leg_io(0, IO_ANALOGUE_INPUT)


codebug2 = codebug_tether.CodeBug('/dev/ttyACM0')
codebug2.set_leg_io(0, IO_ANALOGUE_INPUT)


red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
yellow = (255,255,0)
white = (255,255,255)
black =(0,0,0)

size = screen_width, screen_height = 800, 600
#speed = [2, 2]


# paddle orientation
HORIZONTAL = 0
VERTICAL = 1


screen = pygame.display.set_mode(size)

#score1 = 0
#score2 = 0

# Initialise pygame, needed for fonts
pygame.init()
# turn off cursor
pygame.mouse.set_visible(0)
paddle_wall_gap = 10

font = pygame.font.Font(None,48)

in_play = True
play_again = True


def check_for_input():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                paddles[0].x += 10

def display_scores():
    score_1_display = font.render(str(paddles[0].score),True, paddles[0].colour)
    score_1_rect = score_1_display.get_rect()
    score_1_rect.centerx =  50
    score_1_rect.centery = 25

    screen.blit(score_1_display,score_1_rect)

    score_2_display = font.render(str(paddles[1].score),True , paddles[1].colour)
    score_2_rect = score_2_display.get_rect()
    score_2_rect.centerx = screen_width - 50
    score_2_rect.centery = screen_height - 25
    screen.blit(score_2_display,score_2_rect)

    score_3_display = font.render(str(paddles[2].score),True , paddles[2].colour)
    score_3_rect = score_3_display.get_rect()
    score_3_rect.centerx = 50
    score_3_rect.centery = screen_height - 25
    screen.blit(score_3_display,score_3_rect)

    score_4_display = font.render(str(paddles[3].score),True , paddles[3].colour)
    score_4_rect = score_4_display.get_rect()
    score_4_rect.centerx = screen_width - 50
    score_4_rect.centery = 25
    screen.blit(score_4_display,score_4_rect)


def draw_balls():
    for ball in balls:
        ball.draw_ball()

def move_balls():
    for ball in balls:
        ball.move_ball()

def move_paddles():
    for paddle in paddles:
        paddle.move_paddle()


def draw_paddles():
    for paddle in paddles:
        paddle.draw_paddle()



class Paddle:

    def __init__(self, given_width, given_height, given_x, given_y, given_colour, given_orientation, given_codebug):

        self.orientation = given_orientation
        if self.orientation == VERTICAL:
            self.width = given_height
            self.height = given_width
        else:
            self.width = given_width
            self.height = given_height

        self.x = given_x
        self.y = given_y
        self.colour = given_colour
        self.line_thickness = 0
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.codebug = given_codebug
        self.score = 0
        self.display_score()



    def move_paddle(self):
        if self.orientation == VERTICAL:
            self.y = self.codebug.read_analogue(0)*((screen_height-self.height)/255)
            self.rect.y = self.y
        else:
            self.x = self.codebug.read_analogue(0)*((screen_width-self.width)/255)
            self.rect.x = self.x

    def draw_paddle(self):
        pygame.draw.rect(screen, self.colour,self.rect , self.line_thickness)

    def display_score(self):
        #score = codebug_tether.sprites.StringSprite(str(self.score))
        #self.codebug.draw_sprite(0, 0, score)
        pass


class Ball:

    def __init__(self, given_width, given_height, given_x, given_y, given_speed, given_colour):

        self.width = given_width
        self.height = given_height
        self.x = given_width
        self.y = given_height
        self.delta_x = 3
        self.delta_y = 3
        self.line_thickness = 0
        self.colour = given_colour
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.serve_direction = random.randint(0,3)


    def reset_ball(self):
        self.x = screen_width/2
        self.y = screen_height/2
        self.delta_y = 3

        if self.serve_direction == 0:
            self.delta_x = 3
            self.delta_y = 3

        elif self.serve_direction == 1:
            self.delta_x = -3
            self.delta_y = 3


        elif self.serve_direction == 2:
            self.delta_x = 3
            self.delta_y = -3


        elif self.serve_direction == 3:
            self.delta_x = -3
            self.delta_y = -3


        self.rect.x = self.x
        self.rect.y = self.y

        self.serve_direction = random.randint(0,3)

    def draw_ball(self):
        pygame.draw.rect(screen, self.colour,self.rect , self.line_thickness)

    def move_ball(self):
        #global score1, score2

        self.x += self.delta_x
        self.y += self.delta_y



        #check top and bottom
        if self.y > (screen_height-self.height):
            #print("off bottom edge")
            #self.y = screen_height-(screen_height-self.y)
            #self.delta_y = 0 - self.delta_y
            paddles[2].score += 1
            self.reset_ball()

        if self.y <= 0:
            #print("off top edge")
            # self.y = 0 -self.y
            # self.delta_y = 0 - self.delta_y
            paddles[3].score += 1
            self.reset_ball()


        if self.x < 0:
            #print("p1 lost")
            paddles[0].score += 1
            self.reset_ball()

        if self.x > screen_width:
            #print("p2 lost")
            paddles[1].score += 1
            self.reset_ball()

        for paddle in paddles:
            if self.rect.colliderect(paddle.rect):
                if paddle.orientation == VERTICAL:
                    self.delta_x = 0 - self.delta_x
                else:
                    self.delta_y = 0 - self.delta_y

        self.rect = self.rect.move(self.delta_x, self.delta_y)


#initialise paddles
paddle1 = Paddle(100, 20, paddle_wall_gap, screen_height/2, blue, VERTICAL, codebug1)
paddle2 = Paddle(100, 20, screen_width -(20 + paddle_wall_gap), screen_height/2, red, VERTICAL, codebug1)
paddle3 = Paddle(100, 20, screen_width/2, screen_height -(20 + paddle_wall_gap), green, HORIZONTAL, codebug2)
paddle4 = Paddle(100, 20, screen_width/2, paddle_wall_gap, yellow, HORIZONTAL, codebug2)
paddles = [paddle1, paddle2, paddle3, paddle4]

#initialise balls
ball1 = Ball( 20, 20,  screen_width/2 , screen_height/2, 4, white)
balls = [ball1]



while play_again:
    while in_play:

        check_for_input()

        # draw the background
        screen.fill(black)

        # draw logo
        screen.blit(logo,((screen_width-logo.get_width())/2,(screen_height-logo.get_height())/2))

        # draw paddles
        move_paddles()
        draw_paddles()

        # draw scores
        display_scores()

        # draw balls
        move_balls()
        draw_balls()

        screen.blit(screen,(0,0))
        pygame.display.flip()
        #time.sleep(.1)