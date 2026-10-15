from yacs.config import CfgNode as CN

class BaseConfig:
  def __init__(self):
    ###########################
    # Config definition
    ###########################
    cfg = CN(new_allowed=True)

    ###########################
    # Env
    ###########################
    cfg.ENV = CN(new_allowed=True)
    cfg.ENV.VERSION = 1
    cfg.ENV.SEED = -1
    # Directory to save the output files (like log.txt and model weights)
    cfg.ENV.OUTPUT_DIR = "./output"
    # Path to a directory where the files were saved previously
    cfg.ENV.RESUME = ""
    cfg.ENV.GPU = [0]
    cfg.ENV.USE_CUDA = True
    # Distributed training settings
    cfg.ENV.DISTRIBUTED = False
    cfg.ENV.LOCAL_RANK = -1  # Set by torchrun automatically
    cfg.ENV.WORLD_SIZE = 1
    cfg.ENV.DIST_BACKEND = 'nccl'  # 'nccl' for GPU, 'gloo' for CPU
    cfg.ENV.DIST_URL = 'env://'  # Use environment variables set by torchrun
    # Print detailed information
    # E.g. trainer, dataset, and backbone
    cfg.ENV.VERBOSE = True
    # Name and description of the experiment 
    cfg.ENV.NAME = ""
    cfg.ENV.DESCRIPTION = ""
    cfg.ENV.USE_WANDB = False
    # Container for arbitrary runtime/env-specific options
    cfg.ENV.EXTRA = CN(new_allowed=True)
    
    cfg.ENV.USE_WANDB = True
    cfg.ENV.WANDB = CN()
    cfg.ENV.WANDB.KEY = None
    cfg.ENV.WANDB.ENTITY = "3DVZHao"
    cfg.ENV.WANDB.PROJECT = "FLowTalker"
    cfg.ENV.WANDB.NAME = "TrainingModel"
    cfg.ENV.WANDB.NOTES = "Training as baseline."
    cfg.ENV.WANDB.TAGS = "Baseline"
    cfg.ENV.WANDB.MODE = "online"

    ###########################
    # Input
    ###########################
    cfg.INPUT = CN()
    # If True, tfm_train and tfm_test will be None
    cfg.INPUT.NO_TRANSFORM = False
    # Gaussian noise
    cfg.INPUT.GN_MEAN = 0.0
    cfg.INPUT.GN_STD = 0.15
    # RandomAugment
    cfg.INPUT.RANDAUGMENT_N = 2
    cfg.INPUT.RANDAUGMENT_M = 10

    ###########################
    # Dataset
    ###########################
    cfg.DATASET = CN()
    cfg.DATASET.NAME = ""
    cfg.DATASET.ROOT = ""   # Directory where datasets are stored
    # Percentage of validation data, set to 0 if do not want to use val data
    cfg.DATASET.VAL_PERCENT = 0.1

    # for vocaset
    cfg.DATASET.VOCASET = CN()
    cfg.DATASET.VOCASET.AUDIO = ""
    cfg.DATASET.VOCASET.VERTICES = ""
    cfg.DATASET.VOCASET.TEMPLATE = ""
    cfg.DATASET.VOCASET.TRAIN = list(range(1, 41))
    cfg.DATASET.VOCASET.VAL = list(range(21, 41))
    cfg.DATASET.VOCASET.TEST = list(range(21, 41))
    cfg.DATASET.VOCASET.WAV2VEC2 = ""
    cfg.DATASET.VOCASET.READ_AUDIO = True

    # for HDTF_TFHP
    cfg.DATASET.HDTF_TFHP = CN()
    cfg.DATASET.HDTF_TFHP.LMDB = ""
    cfg.DATASET.HDTF_TFHP.COEF_STATS = "stats_train.npz"
    cfg.DATASET.HDTF_TFHP.TRAIN = "train.txt"
    cfg.DATASET.HDTF_TFHP.VAL = "val.txt"
    cfg.DATASET.HDTF_TFHP.TEST = "test.txt"
    cfg.DATASET.HDTF_TFHP.COEF_FPS = 25      # frames per second for coefficients (sequence fps)
    cfg.DATASET.HDTF_TFHP.MOTIONS = 100      # number of motions per sample
    cfg.DATASET.HDTF_TFHP.N_PREV_MOTIONS = 10   # audio sampling rate
    cfg.DATASET.HDTF_TFHP.CROP = "random"    # crop strategy
    cfg.DATASET.HDTF_TFHP.AUDIO_SR = 16000   # audio sampling rate
    cfg.DATASET.HDTF_TFHP.USE_CONTEXT_AUDIO = True  # whether to use context audio for model input
    cfg.DATASET.HDTF_TFHP.TRUNC_PROB1 = 0.3 # truncation probability for clip 1
    cfg.DATASET.HDTF_TFHP.TRUNC_PROB2 = 0.4 # truncation probability for clip 2
    cfg.DATASET.HDTF_TFHP.PAD_MODE = 'zero' # 'zero' or 'replicate'
    cfg.DATASET.HDTF_TFHP.USE_INDICATOR = True
    cfg.DATASET.HDTF_TFHP.ROT_REPR = 'aa'
    cfg.DATASET.HDTF_TFHP.NO_HEAD_POSE = False

    ###########################
    # Dataloader
    ###########################
    cfg.DATALOADER = CN()
    cfg.DATALOADER.NUM_WORKERS = 4
    # Setting for the train data-loader
    cfg.DATALOADER.TRAIN = CN()
    cfg.DATALOADER.TRAIN.BATCH_SIZE = 32

    # Setting for the test data-loader
    cfg.DATALOADER.TEST = CN()
    cfg.DATALOADER.TEST.BATCH_SIZE = 32

    ###########################
    # Model
    ###########################
    cfg.MODEL = CN()
    cfg.MODEL.NAME = ""
    cfg.MODEL.IN_DIM = 50
    cfg.MODEL.HIDDEN_DIM = 50
    cfg.MODEL.OUT_DIM = 128
    cfg.MODEL.USE_MOTION_PRIOR = True

    # Activation function
    cfg.MODEL.ACTIVATION = CN()
    cfg.MODEL.ACTIVATION.NAME = 'relu'  # relu, leakyrelu
    # leakyrelu: https://docs.pytorch.org/docs/stable/generated/torch.nn.LeakyReLU.html
    cfg.MODEL.ACTIVATION.NEG_SLOPE = 0.2  # negative slope for leakyrelu

    # Normalization layer
    cfg.MODEL.NORM = CN()
    cfg.MODEL.NORM.NAME = 'batchnorm'  # batchnorm, layernorm
    # InstanceNorm1d: https://docs.pytorch.org/docs/stable/generated/torch.nn.InstanceNorm1d.html
    cfg.MODEL.NORM.AFFINE = True
    
    # Classifier-free guidance
    cfg.MODEL.CFG_MODE = 'incremental' # 'full', 'incremental', 'none'
    cfg.MODEL.CFG_SCALE = [1.15, 3]
    cfg.MODEL.CFG_COND = 'audio,style'

    # Dynamic Thresholding Configuration
    cfg.MODEL.DYNAMIC_THRESHOLD = CN()
    cfg.MODEL.DYNAMIC_THRESHOLD.ENABLE = True
    # Quantile ratio for computing adaptive threshold per sample
    # Typical values: 0.90 ~ 0.99
    cfg.MODEL.DYNAMIC_THRESHOLD.RATIO = 0.99
    # Lower bound of threshold to prevent over-clipping
    cfg.MODEL.DYNAMIC_THRESHOLD.MIN = 1.0
    # Upper bound of threshold to suppress extreme outliers
    cfg.MODEL.DYNAMIC_THRESHOLD.MAX = 4.0

    # Convolutional Transformer settings
    cfg.MODEL.CONV = CN()
    # Number of 2x downsampling stages (0 = no downsampling, n = reduces length by 2^n)
    cfg.MODEL.CONV.DOWN_SAMPLE_FACTOR = 0
    
    # Audio model
    cfg.MODEL.AUDIO_MODEL = 'wav2vec2'
    cfg.MODEL.AUDIO_DIM = 768
    # VQ-VAE settings
    cfg.MODEL.VQVAE = CN()
    cfg.MODEL.VQVAE.HIDDEN_SIZE = 512
    cfg.MODEL.VQVAE.INTERMEDIATE_SIZE = 512
    cfg.MODEL.VQVAE.NUM_HIDDEN_LAYERS = 4
    cfg.MODEL.VQVAE.NUM_ATTENTION_HEADS = 4
    cfg.MODEL.VQVAE.QUANT_FACTOR = 0
    cfg.MODEL.VQVAE.NEG = 0.2
    cfg.MODEL.VQVAE.INAFFINE = False
    cfg.MODEL.VQVAE.N_EMBED = 128
    cfg.MODEL.VQVAE.ZQUANT_DIM = 128
    # RQ-VAE settings
    cfg.MODEL.RQVAE = CN()
    cfg.MODEL.RQVAE.INTERMEDIATE_SIZE = 512
    cfg.MODEL.RQVAE.NEG = 0.2
    cfg.MODEL.RQVAE.QUANT_FACTOR = 0
    cfg.MODEL.RQVAE.INAFFINE = False
    cfg.MODEL.RQVAE.LATEBT_SHAPE = [100, 512]
    cfg.MODEL.RQVAE.CODE_SHAPE = [100, 4]
    cfg.MODEL.RQVAE.N_EMBED = 1024
    cfg.MODEL.RQVAE.DECAY = 0.99
    cfg.MODEL.RQVAE.SHARED_CODDEBOOK = True
    cfg.MODEL.RQVAE.RESTART_UNUSED_CODES = True
    # Transformer settings
    cfg.MODEL.TRANSFORMER = CN()
    cfg.MODEL.TRANSFORMER.NUM_LAYERS = 4
    cfg.MODEL.TRANSFORMER.NUM_ATTENTION_HEADS = 4
    cfg.MODEL.TRANSFORMER.MLP_RATIO = 4
    cfg.MODEL.TRANSFORMER.ALIGN_MASK_WIDTH = 1
    cfg.MODEL.TRANSFORMER.USE_LEARNABLE_PE = False

    # Diffusion settings
    cfg.MODEL.DIFFUSION = CN()
    cfg.MODEL.DIFFUSION.N_STEPS = 500
    cfg.MODEL.DIFFUSION.DIFF_SCHEDULE = 'cosine'  # linear, cosine, quadratic, sigmoid

    # Path to model weights (for initialization)
    cfg.MODEL.INIT_WEIGHTS = ""
    
    ###########################
    # Pretrained Models Config
    ###########################
    cfg.MODEL.PRETRAINED = CN()
    # Style encoder checkpoint (used in multi-stage training)
    cfg.MODEL.PRETRAINED.STYLE_ENCODER_PATH = ""  # Path to checkpoint
    cfg.MODEL.PRETRAINED.STYLE_DIM = 128  # Style feature dimension
    cfg.MODEL.PRETRAINED.FLAME_ROOT = "pretrained/FLAME"
    # Definition of embedding layers
    cfg.MODEL.HEAD = CN()
    # If none, do not construct embedding layers, the
    # backbone's output will be passed to the classifier
    cfg.MODEL.HEAD.NAME = ""
    # Structure of hidden layers (a list), e.g. [512, 512]
    # If undefined, no embedding layer will be constructed
    cfg.MODEL.HEAD.HIDDEN_LAYERS = ()
    cfg.MODEL.HEAD.ACTIVATION = "relu"
    cfg.MODEL.HEAD.BN = True
    cfg.MODEL.HEAD.DROPOUT = 0.0
    # VQ-VAE config
    cfg.MODEL.HEAD.N_EMBED = 256
    cfg.MODEL.HEAD.ZQUANT_DIM = 64
    # Audio model
    cfg.MODEL.HEAD.AUDIO_MODEL = 'wav2vec2'
    cfg.MODEL.HEAD.AUDIO_DIM = 128
    # Style ref
    cfg.MODEL.HEAD.USER_MOTION_PRIOR = True
    cfg.MODEL.HEAD.USE_RECON = False

    # align mask width for transformer decoder
    cfg.MODEL.HEAD.ALIGN_MASK_WIDTH = 0
    # learnable positional encoding
    cfg.MODEL.HEAD.USE_LEARNABLE_PE = True
    cfg.MODEL.HEAD.LATENT_DIM = 256

    cfg.MODEL.BACKBONE = CN()
    cfg.MODEL.BACKBONE.NAME = ""
    cfg.MODEL.BACKBONE.IN_DIM = 15069
    cfg.MODEL.BACKBONE.HIDDEN_SIZE = 1024
    cfg.MODEL.BACKBONE.NUM_HIDDEN_LAYERS = 6
    cfg.MODEL.BACKBONE.NUM_ATTENTION_HEADS = 8
    cfg.MODEL.BACKBONE.INTERMEDIATE_SIZE = 1536
    cfg.MODEL.BACKBONE.WINDOW_SIZE = 1
    # for VQ-VAE config
    cfg.MODEL.BACKBONE.QUANT_FACTOR = 0
    cfg.MODEL.BACKBONE.FACE_QUAN_NUM = 16
    cfg.MODEL.BACKBONE.NEG = 0.2
    cfg.MODEL.BACKBONE.INAFFINE = False

    cfg.MODEL.TAIL = CN()
    cfg.MODEL.TAIL.NAME = ""
    cfg.MODEL.TAIL.NUM_HIDDEN_LAYERS = 4
    cfg.MODEL.TAIL.MLP_RATIO = 4
    cfg.MODEL.TAIL.TYARGET = "sample"  # for diffusion model, either "sample" or "noise"

    cfg.ALGORITHM = CN()
    cfg.ALGORITHM.FLOWMATCHING = CN()
    cfg.ALGORITHM.FLOWMATCHING.MIN_SIGMA = 0.0
    cfg.ALGORITHM.FLOWMATCHING.INFERENCE_MODE = 'euler'  # 'euler' or 'adaptive' for ODE solving         # Minimum sigma for numerical stability
    cfg.ALGORITHM.FLOWMATCHING.NUM_STEPS = 25            # Number of Euler steps for sampling
    cfg.ALGORITHM.FLOWMATCHING.REVERSE_FLOW = True       # Use reverse flow (x1->x0)
    cfg.ALGORITHM.FLOWMATCHING.LOG_NORMAL_MEAN = 0.0     # Log-normal sampling mean for time
    cfg.ALGORITHM.FLOWMATCHING.LOG_NORMAL_STD = 1.0      # Log-normal sampling std for time
    cfg.ALGORITHM.FLOWMATCHING.T_MID = 0.8

    ###########################
    # Optimization
    ###########################
    cfg.OPTIM = CN()
    
    # Optimizer
    ## adam
    cfg.OPTIM.NAME = "adam"
    cfg.OPTIM.LR = 0.001
    cfg.OPTIM.WEIGHT_DECAY = 5e-4
    cfg.OPTIM.ADAM_BETA1 = 0.9
    cfg.OPTIM.ADAM_BETA2 = 0.999
    
    # sgd
    cfg.OPTIM.MOMENTUM = 0.9
    cfg.OPTIM.SGD_DAMPNING = 0
    cfg.OPTIM.SGD_NESTEROV = True

    # rmsprop
    cfg.OPTIM.RMSPROP_ALPHA = 0.99

    # Learning rate update frequency (in iterations/steps)
    # Set to 1 to update every step (default)
    # Set to N to update every N steps (useful for iteration-based training)
    cfg.OPTIM.LR_UPDATE_FREQ = 1

    # Learning rate scheduler
    ## training settings
    cfg.OPTIM.MAX_STEP = 0
    cfg.OPTIM.LR_SCHEDULER = "single_step"
    cfg.OPTIM.STEP_SIZE = 20
    cfg.OPTIM.GAMMA = 0.5  # Multiplicative factor of learning rate decay for 'single/multi step'

    ## warmup settings
    cfg.OPTIM.WARMUP_TYPE = "linear"
    cfg.OPTIM.WARMUP_STEP = 0  # Set larger than 0 to activate warmup training
    cfg.OPTIM.MULTIPLIER = 0 # for GradualWarmupScheduler
    cfg.OPTIM.MIN_LR_RATIO = 0.02 # for gradualThenDecay

    ###########################
    # Trainer specifics
    ###########################
    cfg.TRAINER = CN()
    cfg.TRAINER.NAME = ""

    ###########################
    # Train
    ###########################
    cfg.TRAIN = CN()
    cfg.TRAIN.USE_SGD = False
    cfg.TRAIN.SYNC_BN = False  # adopt sync_bn or not
    
    ## training settings
    cfg.TRAIN.USE_ITERS = False
    cfg.TRAIN.START_EPOCH = 0
    cfg.TRAIN.MAX_EPOCHS = 50
    cfg.TRAIN.START_ITER = 0
    cfg.TRAIN.MAX_ITERS = 10000
    cfg.TRAIN.EVAL_ROUND = 1    # when using iterations
    # How often (batch/iteration) to print training information
    cfg.TRAIN.PRINT_FREQ = 10
    # How often (epoch/iteration) to save model during training
    cfg.TRAIN.SAVE_FREQ = 0
    # Whether to perform evaluation during training
    cfg.TRAIN.EVALUATE = True
    # How often (epoch/iteration) to eval model during training
    cfg.TRAIN.EVAL_FREQ = 10
    cfg.TRAIN.RENDER_FREQ = 10
    cfg.TRAIN.GRAD_CLIP = 1.0

    ###########################
    # Test
    ###########################
    cfg.TEST = CN()
    # If NO_TEST=True, no testing will be conducted
    cfg.TEST.NO_TEST = False
    # Use test or val set for FINAL evaluation
    cfg.TEST.SPLIT = "test"
    # Which model to test after training (last_step or best_val)
    # If best_val, evaluation is done every epoch (if val data
    # is unavailable, test data will be used)
    cfg.TEST.FINAL_MODEL = "last_step"
    
    cfg.LOSS = CN()
    cfg.LOSS.NAME = "L2Loss"
    cfg.LOSS.CRITERION = "l2"
    cfg.LOSS.NO_CONSTRAIN_PREV = False   # for time windows prediction
    cfg.LOSS.CONTRASTIVE = CN()
    cfg.LOSS.CONTRASTIVE.TEMPRATURE = 0.1
    cfg.LOSS.GEOMETRIC = CN()
    cfg.LOSS.GEOMETRIC.W_VERTEX = 2e6  # weight of the vertex loss
    cfg.LOSS.GEOMETRIC.W_VELOCITY = 1e7  # weight of the velocity loss
    cfg.LOSS.GEOMETRIC.W_SMOOTH = 1e5   # weight of the vertex acceleration regularization
    cfg.LOSS.GEOMETRIC.HEAD = CN()
    cfg.LOSS.GEOMETRIC.HEAD.W_ANGLE = 0.05  # weight of the head angle loss
    cfg.LOSS.GEOMETRIC.HEAD.W_VELOCITY = 5.0 # weight of the head angular velocity loss
    cfg.LOSS.GEOMETRIC.HEAD.W_SMOOTH = 0.5  # weight of the head angular acceleration regularization
    cfg.LOSS.GEOMETRIC.HEAD.W_TRANS = 0.5  # weight of the head constraint during window transition
    cfg.LOSS.VQVAE = CN()
    cfg.LOSS.VQVAE.W_QUANT = 0.5

    cfg.EVALUATE = CN()
    cfg.EVALUATE.EVALUATOR = "TalkerEvaluator"
    cfg.EVALUATE.LOAD_RENDER = False
    cfg.EVALUATE.SAVE_VERTS = False
    cfg.EVALUATE.SAVE_COEF = False
    cfg.EVALUATE.SAVE_COEF_FORMAT = "npz"
    cfg.EVALUATE.WITH_GLOBAL_POSE = False
    cfg.EVALUATE.REGION_PATH = "pretrained/metric"

    cfg.EVALUATE.RENDER = CN()
    cfg.EVALUATE.RENDER.NAME = "PyMeshRenderer"
    cfg.EVALUATE.RENDER.USE_GAUSSIAN = False   # whether use gaussian splatting (3dgs)
    cfg.EVALUATE.RENDER.SH_DEGREE = 3
    cfg.EVALUATE.RENDER.PLY_PATH = ""
    cfg.EVALUATE.RENDER.BLACK_BG = False
    cfg.EVALUATE.RENDER.REND_SIZE = (640, 640)
    cfg.EVALUATE.RENDER.UV_ROOT = 'uv_coords.npz'

    cfg.EVALUATE.METRIC = CN()
    cfg.EVALUATE.METRIC.MOD_TOP_INDICES = [3533, 2785, 1668]
    cfg.EVALUATE.METRIC.MOD_BOTTOM_INDICES = [3513, 2929, 1827]
    
    # OP
    self.cfg = cfg