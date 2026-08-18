import torch.nn as nn

class Norm(nn.Module):
  """ Norm Layer """

  def __init__(self, fn, size):
    super().__init__()
    self.norm = nn.LayerNorm(size, eps=1e-5)
    self.fn = fn

  def forward(self, x_data):
    if type(x_data) is dict:
        x_norm = self.fn({'x_a':x_data['x_a'], 'x_b':self.norm(x_data['x_b'])})
        return x_norm
    else:
        x, mask_info = x_data
        x_norm, _ = self.fn((self.norm(x), mask_info))
        return (x_norm, mask_info)