import pandas as pd
import numpy as np
import math

import torch
from torch import nn
from torch import optim
from torch import Tensor
from torch import from_numpy
from torch import cat
from random import random
from copy import deepcopy as dc
from collections import deque

class Model1 (object):
    l1 = 50
    l2 = 512
    l3 = 1024
    l4 = 128
    l5 = 3
    model = nn.Sequential(
        nn.Linear(l1,l2),
        nn.ReLU(),
        nn.Linear(l2,l3),
        nn.ReLU(),
        nn.Linear(l3,l4),
        nn.ReLU(),
        nn.Linear(l4,l5)
    )
    cmodel = dc(model)
    opt = optim.Adam(model.parameters(),lr=1e-3)
    gamma = 0.9
    epsilon = 0.3
    loss = nn.MSELoss
    input = None
    output = False
    s2 = None
    replay = deque()

    def __init__(self,state_dict=None):
        if state_dict is not None:
            self.model.load_state_dict(torch.load(state_dict))

    def feed_forward(self,inputs):
        self.s2 = self.input
        n = np.array(inputs).reshape(1,50)
        self.input = from_numpy(n).float()
        self.output = self.model(self.input) if random() > self.epsilon else from_numpy(np.random.random((1,3)))
        print(self.output,self.output.shape)
        self.replay.append((self.input,self.output,self.s2,False))

        return list(self.output.data.numpy().reshape(3,1))

    def save(self, file_name):
        torch.save(self.model.state_dict(),file_name)

    def load(self,file_name):
        self.model.load_state_dict(torch.load(file_name))

    def train(self,score):
        self.replay.popleft()
        self.replay.append((self.input,self.output,self.s2,True))

        reward = Tensor([score/len(self.replay) for i in range(len(self.replay))])
        state1 = cat([s1 for (s1,a,s2,d) in self.replay])
        output = cat([a for (s1, a, s2, d) in self.replay])
        state2 = cat([s2 for (s1, a, s2, d) in self.replay])
        done = Tensor([d for (s1, a, s2, d) in self.replay])

        Q1 = self.model(state1)
        with torch.no_grad():
            Q2 = self.cmodel(state2)
        Y = reward + self.gamma * ((1 - done) * torch.max(Q2,dim=1)[0])
        # X = torch.gather(Q1,-2,output)
        # loss = self.loss(X,Y.detach())
        # self.losses.append(loss.item())
        self.opt.step()