import pygame
import sys
import random

from missile import Missile
from explosion import Explosion
from launcher import Launcher
from model1 import Model1
import pandas as pd
import math
import numpy as np
import time
import json
import os

# width = 480
# height = 480

# WIDTH = int(INFO.current_h * 0.5)
# HEIGHT = int(INFO.current_h * 0.5)
#
# GROUND_HEIGHT = int(HEIGHT / 15)
# SHELTER_HEIGHT = int(HEIGHT / 10)

#Changing width and height to set values

#set variable if still alive

def draw():
    s.fill((0, 0, 0))
    w = HEIGHT - SHELTER_HEIGHT
    pygame.draw.rect(s, pygame.Color(255, 255, 0), (0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT))
    for ss in range(len(launcher_list)):
        pygame.draw.polygon(s, pygame.Color(255, 255, 0),
                            [(ss * WIDTH / 2 - SHELTER_HEIGHT/2 + GROUND_HEIGHT - (GROUND_HEIGHT * ss), w), (ss * WIDTH / 2 + SHELTER_HEIGHT/2 + GROUND_HEIGHT - (GROUND_HEIGHT * ss), w),
                             (ss * WIDTH / 2 + SHELTER_HEIGHT + GROUND_HEIGHT - (GROUND_HEIGHT * ss), HEIGHT), (ss * WIDTH / 2 - SHELTER_HEIGHT + GROUND_HEIGHT - (GROUND_HEIGHT * ss), HEIGHT)])
        counter = launcher_list[ss].ammo
        number = 1
        while counter > 0:
            for j in range(number):
                pygame.draw.ellipse(s, (0, 0, 255), (launcher_positions[ss] - ((number - 2 * j) * WIDTH/100) + WIDTH/200, HEIGHT - SHELTER_HEIGHT + ((number-1) * WIDTH/100), WIDTH/100, WIDTH/100))
                counter = counter-1
                if counter == 0:
                    break
            number = number+1
    launcher_pos = 1
    for i in range(len(shelter)):
        if shelter[i]:
            pygame.draw.rect(s, pygame.Color(0, 0, 255), ((i+launcher_pos) * WIDTH/9 + SHELTER_HEIGHT/4, HEIGHT - GROUND_HEIGHT*1.2, SHELTER_HEIGHT/2, SHELTER_HEIGHT/3))
        if (i + 1) % 3 == 0:
            launcher_pos = launcher_pos+1

    for p in player_missiles:
        pygame.draw.line(s, pygame.Color(0, 255, 0), (p.start_x, p.start_y), (p.current_x, p.current_y), 1)
        pygame.draw.ellipse(s, random.choice(colors_list),
                            (p.current_x-1.5, p.current_y-1.5, 4, 4), 0)
        col = random.choice(colors_list)
        pygame.draw.line(s, col, (p.end_x-5, p.end_y-5),
                         (p.end_x+5, p.end_y+5), 1)
        pygame.draw.line(s, col, (p.end_x+5, p.end_y-5),
                         (p.end_x-5, p.end_y+5), 1)
        p.move()

    for p in enemy_missiles:
        pygame.draw.line(s, pygame.Color(255, 0, 0), (p.start_x, p.start_y), (p.current_x, p.current_y), 1)
        pygame.draw.ellipse(s, random.choice(colors_list),
                            (p.current_x-1.5, p.current_y-1.5, 4, 4), 0)

        p.move()

    for w in explosion_list:
        if w.expires:
            w.frame -= 2
            if w.frame == 0:
                explosion_list.remove(w)
                del w
                continue
        elif w.frame == explosion_speed:
            w.expires = True
        else:
            w.frame += 1
        pygame.draw.ellipse(s, random.choice(colors_list),
                            (w.poz_x-w.frame/int(explosion_speed/25), w.poz_y-w.frame/int(explosion_speed/25), w.frame/int(explosion_speed/50), w.frame/int(explosion_speed/50)), 0)

    pygame.display.update()


def designate_launcher(x, y):
    minimum_x = 10
    y1 = HEIGHT - 50
    dy = y-y1
    minimum = 100000
    if launcher_list[0].ammo > 0:
        x1 = launcher_positions[0]
        dx = x1-x
        temp = math.sqrt(dx*dx + dy*dy)
        if temp < minimum:
            minimum = temp
            minimum_x = x1
    if launcher_list[1].ammo > 0:
        x1 = launcher_positions[1]
        dx = x1-x
        temp = math.sqrt(dx*dx + dy*dy)
        if temp < minimum:
            minimum = temp
            minimum_x = x1
    if launcher_list[2].ammo > 0:
        x1 = launcher_positions[2]
        dx = x1-x
        temp = math.sqrt(dx*dx + dy*dy)
        if temp < minimum:
            minimum = temp
            minimum_x = x1
    return minimum_x


def launch_rocket(x, y):
    if y > HEIGHT-SHELTER_HEIGHT*1.4:
        return

    launcher_position = designate_launcher(x, y)
    if launcher_position == launcher_positions[0]:
        launcher_list[0].ammo -= 1
    elif launcher_position == launcher_positions[1]:
        launcher_list[1].ammo -= 1
    elif launcher_position == launcher_positions[2]:
        launcher_list[2].ammo -= 1
    else:
        return
    player_missiles.append(Missile(launcher_position, HEIGHT - SHELTER_HEIGHT, x, y, player_missile_speed, 0))


def middle_point(x, y, wx, wy, r):
    p = ((math.pow((x - wx), 2) // math.pow(r+1, 2)) +
         (math.pow((y - wy), 2) // math.pow(r+1, 2)))

    return p


def collision():
    for p in player_missiles:
        if p.current_y-p.end_y < 0.1:
            temp = Explosion(p.current_x, p.current_y)
            explosion_list.append(temp)
            player_missiles.remove(p)
            del p
            continue

        for w in explosion_list:
            if middle_point(p.current_x, p.current_y, w.poz_x, w.poz_y, w.frame / int(explosion_speed/25)) < 1:
                temp = Explosion(p.current_x, p.current_y)
                explosion_list.append(temp)
                player_missiles.remove(p)
                del p
                break
    for p in enemy_missiles:
        if p.current_y-p.end_y > -0.1:
            temp = Explosion(p.current_x, p.current_y)
            explosion_list.append(temp)
            if p.end_x == shelter_positions[0]:
                launcher_list[0].ammo = 0
            elif p.end_x == shelter_positions[1]:
                shelter[0] = False
            elif p.end_x == shelter_positions[2]:
                shelter[1] = False
            elif p.end_x == shelter_positions[3]:
                shelter[2] = False
            elif p.end_x == shelter_positions[4]:
                launcher_list[1].ammo = 0
            elif p.end_x == shelter_positions[5]:
                shelter[3] = False
            elif p.end_x == shelter_positions[6]:
                shelter[4] = False
            elif p.end_x == shelter_positions[7]:
                shelter[5] = False
            elif p.end_x == shelter_positions[8]:
                launcher_list[2].ammo = 0
            lose()
            if len(enemy_missiles) != 0:
                enemy_missiles.remove(p)
                del p
            continue

        for w in explosion_list:
            if middle_point(p.current_x, p.current_y, w.poz_x, w.poz_y, w.frame / int(explosion_speed/25)) < 1:
                temp = Explosion(p.current_x, p.current_y)
                explosion_list.append(temp)
                enemy_missiles.remove(p)
                del p
                break


def new_level():
    if not enemy_missiles:
        launcher_list[0].ammo = 10
        launcher_list[1].ammo = 10
        launcher_list[2].ammo = 10
        explosion_list.clear()
        global points
        points += 1
        for i in range(10):
            temp = Missile(random.randrange(WIDTH), 0,
                           random.choice(shelter_positions), HEIGHT - GROUND_HEIGHT, enemy_missile_speed, random.randrange(4000))
            enemy_missiles.append(temp)

def lose():
    for i in shelter:
        if i:
            return
    del explosion_list[:]
    del player_missiles[:]
    del enemy_missiles[:]
    global points
    draw()
    large_text = pygame.font.SysFont("consolas", int(HEIGHT * 0.035))
    text_surface = large_text.render("Survived waves : " + str(points) +
                                     " Press space to start again", True, (255, 0, 0))
    text_rect = text_surface.get_rect()
    text_rect.center = ((WIDTH / 2), (HEIGHT / 2))
    s.blit(text_surface, text_rect)

    pygame.display.update()

### New Functions ###
def get_input_information():
    #Get health as booleans for first 6 positions
    health = [int(i) for i in shelter]

    #Get health of launchers for next 3 position
    launcher_health = [launcher.ammo/10 for launcher in launcher_list]

    #Get enemy rockets for the remaining
    enemy_rockets = []

    for rocket_index in range(10):
        #If rocket exists, put information
        try:
            rocket = enemy_missiles[rocket_index]

            enemy_rockets.append(1)
            #Scale positions
            enemy_rockets.append(rocket.current_x / 720)
            enemy_rockets.append(rocket.current_y / 720)
            enemy_rockets.append(rocket.end_x / 720)

        #If rocket does not exist, put 0
        except:
            enemy_rockets.append(0)
            enemy_rockets.append(0)
            enemy_rockets.append(0)
            enemy_rockets.append(0)

    #Combine all into input data that will go into model
    input_data = []

    for data in [health, launcher_health, enemy_rockets]:
        for datapoint in data:
            input_data.append(datapoint)

    #Add bias
    input_data.append(1)

    return input_data


def play(model):
    """Starts the game with a given model, this model is then used to play the game.
    """
    STILL_ALIVE = True
    total_frames = 0
    while STILL_ALIVE:
        total_frames+=1
        collision()
        draw()
        new_level()
        input_data = get_input_information()

        output = model.feed_forward(input_data)
        #Check if missile should be launched:
        if output[0] >=0.5:
            x = output[1] * 720
            y = output[2] * 720

            launch_rocket(x, y)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                sys.exit(0)

        if (np.array(shelter) == False).all():
            STILL_ALIVE = False
    model.train(total_frames)


    #Resetting health
    for index in range(len(shelter)):
        shelter[index] = True

    return total_frames

import argparse

def parse_args():
    parser = argparse.ArgumentParser(
    )

    parser.add_argument("--save_dir", type=str, default="/")

    parser.add_argument(
        "--model_index", type=str, required=True
    )

    return parser.parse_args()



if __name__ == "__main__":
    args = parse_args()

    model_index = args.model_index
    save_dir = args.save_dir

    model = Model1(save_dir + model_index + ".npy")

    import os
    import pygame

    x = np.random.randint(50,2500)
    y = np.random.randint(50,800)
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x, y)
    pygame.init()

    pygame.mouse.set_cursor(*pygame.cursors.diamond)

    WIDTH = 720
    HEIGHT = 720

    GROUND_HEIGHT = 48
    SHELTER_HEIGHT = 72


    s = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Missile Command')
    clock = pygame.time.Clock()

    level = 0

    half = WIDTH / 18
    shelter_positions = [WIDTH / 9 - half, 2 * WIDTH / 9 - half, 3 * WIDTH / 9 - half, 4 * WIDTH / 9 - half,
                         5 * WIDTH / 9 - half,
                         6 * WIDTH / 9 - half, 7 * WIDTH / 9 - half, 8 * WIDTH / 9 - half, 9 * WIDTH / 9 - half]

    enemy_missiles = []
    points = 0
    player_missiles = []
    explosion_list = []
    shelter = [True, True, True, True, True, True]
    launcher_list = [Launcher(0), Launcher(1), Launcher(2)]
    # launcher_positions = [30, WIDTH / 2, WIDTH - 30]
    launcher_positions = [WIDTH / 9 - half, 5 * WIDTH / 9 - half, 9 * WIDTH / 9 - half]

    colors_list = [pygame.Color(0, 255, 0), pygame.Color(255, 0, 0), pygame.Color(255, 255, 0),
                   pygame.Color(0, 255, 255), pygame.Color(255, 0, 255), pygame.Color(255, 255, 255),
                   pygame.Color(0, 0, 255)]

    enemy_missile_speed = 1
    player_missile_speed = enemy_missile_speed * 5
    explosion_speed = int((1500 * 0.04) / enemy_missile_speed)
    total_frames =play(model)

    with open(save_dir + "scores.json") as f:
        scores = json.load(f)
    f.close()

    scores[model_index] = total_frames

    with open(save_dir + "scores.json", "w+") as f:
        json.dump(scores, f)
    f.close()