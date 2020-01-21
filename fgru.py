import torch.nn as nn
import torch.nn.functional as F
import torch
import numpy as np
from torch.nn import init
from collections import OrderedDict

# torch.manual_seed(42)


class fConvGRUCell(nn.Module):
    """
    Generate a convolutional GRU cell
    """

    def __init__(self, input_size, hidden_size, kernel_size, timesteps=8,
                 normtype='batchnorm', channel_sym=True):
        """
        Parameters
        - input_size (tuple): shape of one input sample
        - hidden_size (int): number of hidden/output channels in layer
        - kernel_size (int): size of W kernels
        - timesteps (int): number of expected timesteps
        - normtype (bool): if set, use ReLU+normtype for each timestep; 
                           if None, use tanh+timestep weights
        - channel_sym (bool): if True, apply channel symmetric constraint for W conv (Hebbian)
        """
        super().__init__()
        self.padding = kernel_size // 2
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.timesteps = timesteps
        self.normtype = normtype

        self.u1_gate = nn.Conv2d(hidden_size, hidden_size, 1)
        self.u2_gate = nn.Conv2d(hidden_size, hidden_size, 1)

        self.w_gate_inh = nn.Parameter(torch.empty(
            hidden_size, hidden_size, kernel_size, kernel_size))
        self.w_gate_exc = nn.Parameter(torch.empty(
            hidden_size, hidden_size, kernel_size, kernel_size))

        self.alpha = nn.Parameter(torch.empty((hidden_size, 1, 1)))
        self.gamma = nn.Parameter(torch.empty((hidden_size, 1, 1)))
        self.kappa = nn.Parameter(torch.empty((hidden_size, 1, 1)))
        self.w = nn.Parameter(torch.empty((hidden_size, 1, 1)))
        self.mu = nn.Parameter(torch.empty((hidden_size, 1, 1)))

        self.params = nn.ParameterDict()
        self.params['w_inh'] = self.w_gate_inh
        self.params['w_exc'] = self.w_gate_exc
        self.params['alpha'] = self.alpha
        self.params['gamma'] = self.gamma
        self.params['kappa'] = self.kappa
        self.params['omega'] = self.w

        if normtype == 'instancenorm':
            self.norm = nn.ModuleList(
                [nn.InstanceNorm2d(hidden_size, eps=1e-03) for i in range(4*timesteps)])
        elif normtype == 'batchnorm':
            self.norm = nn.ModuleList(
                [nn.BatchNorm2d(hidden_size, eps=1e-03) for i in range(4*timesteps)])
        else:
            self.n = nn.Parameter(torch.randn(self.timesteps, 1, 1))
            self.params['eta'] = self.n

        init.orthogonal_(self.w_gate_inh)
        init.orthogonal_(self.w_gate_exc)
        if channel_sym:
            self.w_gate_inh.register_hook(lambda grad: (
                grad + torch.transpose(grad, 1, 0))*0.5)
            self.w_gate_exc.register_hook(lambda grad: (
                grad + torch.transpose(grad, 1, 0))*0.5)

        init.orthogonal_(self.u1_gate.weight)
        init.orthogonal_(self.u2_gate.weight)
        init.uniform_(self.u1_gate.bias.data, 1, 8.0 - 1)
        self.u1_gate.bias.data.log()
        self.u2_gate.bias.data = -self.u1_gate.bias.data

        if normtype == 'batchnorm':
            for norm in self.norm:
                init.constant_(norm.weight, 0.1)

        init.constant_(self.alpha, 0.1)
        init.constant_(self.gamma, 1.0)
        init.constant_(self.kappa, 0.5)
        init.constant_(self.w, 0.5)
        init.constant_(self.mu, 1)

    def forward(self, input_, prev_state2, timestep):

        # NOTE: do NOT init h2; this is handled externally

        #import pdb; pdb.set_trace()
        i = timestep
        if self.normtype is not None:
            g1_t = torch.sigmoid(self.norm[i*4+0](self.u1_gate(prev_state2)))
            c1_t = self.norm[i*4+1](F.conv2d(prev_state2 *
                                             g1_t, self.w_gate_inh, padding=self.padding))
            next_state1 = F.relu(
                input_ - F.relu(c1_t*(self.alpha*prev_state2 + self.mu)))
            g2_t = torch.sigmoid(self.norm[i*4+2](self.u2_gate(next_state1)))
            c2_t = self.norm[i*4+3](F.conv2d(next_state1,
                                             self.w_gate_exc, padding=self.padding))
            h2_t = F.relu(self.kappa*next_state1 + self.gamma *
                          c2_t + self.w*next_state1*c2_t)
            prev_state2 = (1 - g2_t)*prev_state2 + g2_t*h2_t

        else:
            g1_t = torch.sigmoid(self.u1_gate(prev_state2))
            c1_t = F.conv2d(prev_state2 * g1_t,
                            self.w_gate_inh, padding=self.padding)
            next_state1 = F.tanh(
                input_ - c1_t*(self.alpha*prev_state2 + self.mu))
            g2_t = torch.sigmoid(self.norm[i*4+2](self.u2_gate(next_state1)))
            c2_t = F.conv2d(next_state1, self.w_gate_exc, padding=self.padding)
            h2_t = torch.tanh(self.kappa*(next_state1 + self.gamma *
                                          c2_t) + (self.w*(next_state1*(self.gamma*c2_t))))
            prev_state2 = self.n[timestep]*((1 - g2_t)*prev_state2 + g2_t*h2_t)

        return prev_state2
