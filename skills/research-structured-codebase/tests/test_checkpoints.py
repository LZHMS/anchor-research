"""Real core checkpoint round trips and safe rejection of object metadata."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ASSETS = Path(__file__).resolve().parents[1] / 'StructCodebase'
RUNTIME = all(importlib.util.find_spec(name) is not None for name in ('torch', 'yacs', 'loguru', 'tensorboard', 'PIL'))


@unittest.skipUnless(RUNTIME, 'Install declared framework runtime requirements')
class CheckpointTests(unittest.TestCase):
    def test_epoch_checkpoint_roundtrip_with_nested_config_and_no_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, '-B', '-c', '''
import json, sys
from collections import OrderedDict
from pathlib import Path
import torch
from base.base_config import BaseConfig
from base.base_trainer import TrainerBase
root = Path(sys.argv[1])
trainer = TrainerBase.__new__(TrainerBase)
trainer.rank = 0
trainer.use_iters = False
trainer.cfg = BaseConfig().cfg
trainer._models, trainer._optims, trainer._scheds = OrderedDict(), OrderedDict(), OrderedDict()
model = torch.nn.Linear(1, 1)
with torch.no_grad():
    model.weight.fill_(6)
optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
trainer.register_model('model', model, optimizer, None)
trainer.save_model(epoch=0, directory=str(root), val_result=None)
checkpoint = torch.load(root/'model'/'model.pth.tar-epoch-1', weights_only=True)
assert type(checkpoint['model_config']) is dict
assert type(checkpoint['model_config']['BACKBONE']) is dict
assert checkpoint['model_config']['BACKBONE']['HIDDEN_SIZE'] == trainer.cfg.MODEL.BACKBONE.HIDDEN_SIZE
assert checkpoint['val_result'] is None
with torch.no_grad():
    model.weight.fill_(99)
trainer.load_model(str(root), epoch=1)
assert model.weight.item() == 6
print(json.dumps({'restored_weight': model.weight.item(), 'epoch': checkpoint['epoch']}))
''', directory], cwd=ASSETS, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), {'restored_weight': 6.0, 'epoch': 1})

    def test_legacy_object_checkpoint_has_no_unsafe_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, '-B', '-c', '''
import sys, pickle
from pathlib import Path
import torch
from yacs.config import CfgNode
from base.base_trainer import TrainerBase
path = Path(sys.argv[1])/'legacy.pth'
torch.save({'model_config': CfgNode({'width': 4})}, path)
try:
    TrainerBase.__new__(TrainerBase).load_checkpoint(str(path))
except pickle.UnpicklingError:
    print('rejected')
else:
    raise AssertionError('Object-bearing checkpoint was loaded unsafely')
''', directory], cwd=ASSETS, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), 'rejected')


if __name__ == '__main__':
    unittest.main()
