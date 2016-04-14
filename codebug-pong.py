import pygame
import os, sys
import pygame.locals
import random
import time
import codebug_tether
import codebug_tether.sprites
from codebug_tether import (IO_DIGITAL_INPUT, IO_ANALOGUE_INPUT, IO_PWM_OUTPUT, IO_DIGITAL_OUTPUT)


logo = pygame.image.load('codebug-logo.png')

codebug0 = codebug_tether.CodeBug('/dev/ttyACM0')
codebug1 = codebug_tether.CodeBug('/dev/ttyACM1')
codebug2 = codebug_tether.CodeBug('/dev/ttyACM2')
codebug3 = codebug_tether.CodeBug('/dev/ttyACM3')


cb0_pin = 6
cb1_pin = 6
cb2_pin = 6
cb3_pin = 0

codebug0.set_leg_io(cb0_pin, IO_ANALOGUE_INPUT)
codebug1.set_leg_io(cb1_pin, IO_ANALOGUE_INPUT)
codebug2.set_leg_io(cb2_pin, IO_ANALOGUE_INPUT)
codebug3.set_leg_io(cb3_pin, IO_ANALOGUE_INPUT)


# codebug2 = codebug_tether.CodeBug('/dev/ttyACM0')
# codebug2.set_leg_io(6, IO_ANALOGUE_INPUT)

PIN_AVERAGE = 3


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


screen = pygame.display.set_mode(size,pygame.FULLSCREEN)

#score1 = 0
#score2 = 0

# Initialise pygame, needed for fonts
pygame.init()
# turn off cursor
pygame.mouse.set_visible(0)
paddle_wall_gap = 10

font = pygame.font.Font(None,48)

game_over_font = pygame.font.Font(None, 200)
game_over_display = font.render("GAME OVER",True , red)
game_over_rect = game_over_display.get_rect()
game_over_rect.centerx = screen_width/2
game_over_rect.centery = screen_height/4 * 1

in_play = True
play_again = True


def check_for_input():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.KEYDOWN:
            # if event.key == pygame.K_LEFT:
            #     paddles[0].x += 10
            if event.key == pygame.K_ESCAPE:
                sys.exit()

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

def most_common(given_list):
    d = {}
    for elm in given_list:
        d[elm] = d.get(elm, 0) + 1
    counts = [(j,i) for i,j in d.items()]
    return max(counts)[1]

# def read_leg(codebug, codebug_pin):
#     return codebug.read_analogue(codebug_pin)

class Paddle:

    def __init__(self, given_width, given_height, given_x, given_y, given_colour, given_orientation, given_codebug, given_codebug_pin):

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
        self.codebug_pin = given_codebug_pin
        # needed to smooth out interference on the analogue leg
        self.leg_average_list = [self.read_leg()] * 5

    def read_leg(self):
        return self.codebug.read_analogue(self.codebug_pin)



    def move_paddle(self):
        # add the new analogue read to the averaging list and remove the oldest value
        del self.leg_average_list[0]
        self.leg_average_list.append(self.read_leg())

        # use this for a smooth paddle movement, but jitter when not moving
        # ave_leg_read = sum(self.leg_average_list)/len(self.leg_average_list)

        # use this for low jitter, but not smooth paddle movement
        ave_leg_read = most_common(self.leg_average_list)

        # print (self.leg_average_list)

        if self.orientation == VERTICAL:
            self.y = ave_leg_read*((screen_height-self.height)/255)
            self.rect.y = self.y
        else:
            self.x = ave_leg_read*((screen_width-self.width)/255)
            self.rect.x = self.x

    def draw_paddle(self):
        pygame.draw.rect(screen, self.colour,self.rect , self.line_thickness)

    def display_score(self):
        score = codebug_tether.sprites.StringSprite(str(self.score))
        self.codebug.draw_sprite(0, 0, score)


class Ball:

    def __init__(self, given_width, given_height, given_x, given_y, given_speed, given_colour):

        self.width = given_width
        self.height = given_height
        self.x = screen_width/2
        self.y = screen_height/2
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
            paddles[2].display_score()
            self.reset_ball()

        if self.y <= 0:
            #print("off top edge")
            # self.y = 0 -self.y
            # self.delta_y = 0 - self.delta_y
            paddles[3].score += 1
            paddles[3].display_score()
            self.reset_ball()


        if self.x < 0:
            #print("p1 lost")
            paddles[0].score += 1
            paddles[0].display_score()
            self.reset_ball()

        if self.x > screen_width:
            #print("p2 lost")
            paddles[1].score += 1
            paddles[1].display_score()
            self.reset_ball()

        for paddle in paddles:
            if self.rect.colliderect(paddle.rect):
                if paddle.orientation == VERTICAL:
                    self.delta_x = 0 - self.delta_x
                else:
                    self.delta_y = 0 - self.delta_y

        self.rect = self.rect.move(self.delta_x, self.delta_y)






while play_again:
    #initialise paddles
    paddle1 = Paddle(100, 20, paddle_wall_gap, screen_height/2, blue, VERTICAL, codebug0, cb0_pin)
    paddle2 = Paddle(100, 20, screen_width -(20 + paddle_wall_gap), screen_height/2, red, VERTICAL, codebug1, cb1_pin)
    paddle3 = Paddle(100, 20, screen_width/2, screen_height -(20 + paddle_wall_gap), green, HORIZONTAL, codebug2, cb2_pin)
    paddle4 = Paddle(100, 20, screen_width/2, paddle_wall_gap, yellow, HORIZONTAL, codebug3, cb3_pin)
    paddles = [paddle1, paddle2, paddle3, paddle4]

    #initialise balls
    ball1 = Ball( 20, 20,  screen_width/2 , screen_height/2, 4, white)
    balls = [ball1]

    in_play = True
    while in_play:

        check_for_input()

        # draw the background
        screen.fill(black)

        # draw logo
        screen.blit(logo,((screen_width-logo.get_width())/2,(screen_height-logo.get_height())/2))

        # draw paddles
        move_paddles()
        draw_paddles()


        # draw balls
        move_balls()
        draw_balls()

        # draw scores
        display_scores()

        screen.blit(screen,(0,0))
        pygame.display.flip()

        for paddle in paddles:
            if paddle.score == 9:
                in_play = False
        #time.sleep(.1)


    screen.blit(game_over_display, game_over_rect)
    pygame.display.flip()
    time.sleep(5)

