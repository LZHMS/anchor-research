import math
import torch
import torch.nn.functional as F

def enc_dec_mask(T, S, frame_width=1, expansion=2, device='cuda'):
    mask = torch.ones(T, S)
    for i in range(T):
        mask[i, max(0, (i - expansion) * frame_width):(i + expansion + 1) * frame_width] = 0
    return (mask == 1).to(device=device)


# linear interpolation layer
def linear_interpolation(features, input_fps, output_fps, output_len=None):
    # features: (N, C, L)
    seq_len = features.shape[2] / float(input_fps)
    if output_len is None:
        output_len = int(seq_len * output_fps)
    output_features = F.interpolate(features, size=output_len, align_corners=False, mode='linear')
    return output_features

def pad_audio(audio, audio_unit=320, pad_threshold=80):
    batch_size, audio_len = audio.shape
    n_units = audio_len // audio_unit
    side_len = math.ceil((audio_unit * n_units + pad_threshold - audio_len) / 2)
    if side_len >= 0:
        reflect_len = side_len // 2
        replicate_len = side_len % 2
        if reflect_len > 0:
            audio = F.pad(audio, (reflect_len, reflect_len), mode='reflect')
            audio = F.pad(audio, (reflect_len, reflect_len), mode='reflect')
        if replicate_len > 0:
            audio = F.pad(audio, (1, 1), mode='replicate')

    return audio

def get_sinusoid_encoding_table(n_position, d_hid, padding_idx=None):
	"""
	Sinusoidal position encoding table.
	Args:
		n_position (int): the length of the input sequence
		d_hid (int): the dimension of the hidden state
	"""
	def cal_angle(position, hid_idx):
		return position / (10000 ** (2 * (hid_idx // 2) / d_hid))

	def get_posi_angle_vec(position):
		return [cal_angle(position, hid_j) for hid_j in range(d_hid)]

	sinusoid_table = torch.Tensor([get_posi_angle_vec(pos_i) for pos_i in range(n_position)])
	sinusoid_table[:, 0::2] = torch.sin(sinusoid_table[:, 0::2])  # dim 2i
	sinusoid_table[:, 1::2] = torch.cos(sinusoid_table[:, 1::2])  # dim 2i+1
	if padding_idx is not None: sinusoid_table[padding_idx] = 0.
	return sinusoid_table