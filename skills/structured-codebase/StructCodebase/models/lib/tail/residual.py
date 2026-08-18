import torch.nn as nn

def modulate(x, scale, shift):
    """
    Modulates input tensor x with scale and shift parameters.
    
    Args:
        x: Input tensor to be modulated
        scale: Scaling factor tensor
        shift: Shifting factor tensor
    
    Returns:
        Modulated tensor: x * (1 + scale) + shift
    """
    return x * (1 + scale.unsqueeze(1)) + shift.unsqueeze(1)


class Residual(nn.Module):
  """ Residual Layer """

  def __init__(self, fn):
    super().__init__()
    self.fn = fn

  def forward(self, x_data):
    if type(x_data) is dict:
        x_resid = self.fn(x_data)['x_b']
        return {'x_a':x_data['x_a'], 'x_b':x_resid+x_data['x_b']}
    else:
        x, mask_info = x_data
        x_resid, _ = self.fn(x_data)
        return (x_resid + x, mask_info)