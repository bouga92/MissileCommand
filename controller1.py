from tqdm.auto import tqdm
import numpy as np
import random
import os
import json
import subprocess
import time
import shutil
import pandas as pd
from model1 import Model1


class Controller():
    def __init__(self):
        self.number_of_models = 1 #Number of cpus
        self.iteration_number = 1
        self.epochs = 1000
        self.directory = "training1/"
        self.models = []
        self.times = []
        if os.path.exists(self.directory):
            self.load_previous_models()
        else:
            os.makedirs(self.directory)

    def load_previous_models(self):
        self.iteration_number = np.max([int(i) for i in os.listdir(self.directory)])

        if os.path.exists(self.directory + str(self.iteration_number)):
            shutil.rmtree(self.directory + str(self.iteration_number) + "/")

        self.training_step_dir = self.directory + str(self.iteration_number-1) + "/"
        for model_index in range(self.number_of_models):
            model = Model1()
            model.load(self.training_step_dir + str(model_index) + ".npy")
            self.models.append(model)

    def initialize_training(self):
        self.training_step_dir = self.directory + str(self.iteration_number) + "/"
        os.mkdir(self.training_step_dir)
        if self.iteration_number == 1:
            for model_index in range(self.number_of_models):
                model = Model1()
                model.save(self.training_step_dir + str(model_index) + ".npy")
                self.models.append(model)
        else:
            for model_index, model in enumerate(self.models):
                model.save(self.training_step_dir + str(model_index) + ".npy")


    def train_step(self):
        self.scores = []
        """This is one step for training, each of the models runs the game, then total time is used as score

        Score is then scaled by dividing my total score value.
        """

        scores = {model_index:0 for model_index in range(len(self.models))}
        processes = []

        with open(self.training_step_dir + "scores.json", "w+") as f:
            json.dump(scores, f)


        pbar = tqdm(total=self.number_of_models)

        for model_index in range(len(self.models)):
            # p = subprocess.Popen(f"python main.py --save_dir {self.training_step_dir} --model_index {model_index}")
            p = subprocess.Popen(f"python main_game_display1.py --save_dir {self.training_step_dir} --model_index {model_index}",shell=True)
            processes.append(p)
            time.sleep(0.1)

        time.sleep(5)
        running = True
        completed = 0
        while running:
            running = False
            new_completed = 0
            for poll in processes:
                if poll.poll() is None:
                    running = True
                else:
                    new_completed+=1

            pbar.update(new_completed-completed)
            completed=new_completed


        with open(self.training_step_dir + "scores.json") as f:
            model_scores = json.load(f)

        for model_index in range(len(self.models)):
            self.scores.append(model_scores[str(model_index)])

        self.times.append(np.max(self.scores))

        self.scores = np.array(self.scores)
        self.scores = self.scores / np.sum(self.scores)

        #pd.Series(self.models).apply(lambda f: f.train(self.scores))

    def prepare_next_step(self):
        for model_index in range(len(self.models)):
            self.models[model_index].load(self.training_step_dir + str(model_index) + ".npy")

        self.iteration_number += 1

controller = Controller()




for _ in range(controller.epochs):
    controller.initialize_training()
    controller.train_step()
    controller.prepare_next_step()

    with open("all_times1.json", "w+") as f:
        json.dump([int(i) for i in controller.times], f)
    f.close()