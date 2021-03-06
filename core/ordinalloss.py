# -*- coding: utf-8 -*-
# @Time    : 2019/1/8 9:06
# @Author  : LQX
# @Email   : qixuan.lqx@qq.com
# @File    : ordinalloss.py
# @Software: PyCharm

import torch as t
from torch import nn, autograd
from torch.nn import Parameter as P
from torch.nn.modules.loss import _Loss, _WeightedLoss
from torch.nn import functional as F
import math

import ipdb


class OrdinalLoss(_WeightedLoss):
    def __init__(self, weight=None, size_average=None, reduce=None, reduction='mean'):
        super(OrdinalLoss, self).__init__(weight, size_average, reduce, reduction)
        self.w = P(t.Tensor(2))

    def forward(self, input: t.Tensor, target: t.Tensor):
        predict = t.argmax(input, dim=-1)
        correct_idx = t.nonzero(predict == target).squeeze_()
        wrong_idx = t.nonzero(predict != target).squeeze_()
        # compare in wrong_idx
        w_score = 0
        for i in range(wrong_idx.shape[0]):
            for j in range(i + 1, wrong_idx.shape[0]):
                target_ordinal = target[wrong_idx[j]] - target[wrong_idx[i]]
                predict_ordinal = predict[wrong_idx[j]] - predict[wrong_idx[i]]
                w_score += target_ordinal * predict_ordinal
        # compare between correct_idx and wrong_idx
        b_score = 0
        for i in range(correct_idx.shape[0]):
            for j in range(wrong_idx.shape[0]):
                target_ordinal = target[correct_idx[j]] - target[wrong_idx[i]]
                predict_ordinal = predict[correct_idx[j]] - predict[wrong_idx[i]]
                b_score += target_ordinal * predict_ordinal
        score = w_score + b_score
        return math.exp(0 - self.w * score) + F.mseloss(target, input)


if __name__ == "__main__":
    loss_fn = OrdinalLoss()
    x = t.ones((5, 3), requires_grad=True)
    x = x.view((-1, 1))
    w = t.randn(2, 15)
    b = t.rand(2, 1)
    y = t.mm(w, x) + b
    print(y.requires_grad)
    y.requires_grad_()
    print(y.requires_grad)
    print(y)
    print(w, b)
    print(y.grad)
    y.backward()
    print(y.grad)
    print(w, b)
