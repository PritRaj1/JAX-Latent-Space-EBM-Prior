import jax
import jax.numpy as jnp
import configparser
import optax

from src.MCMC_Samplers.sample_distributions import sample_p0
from src.models.PriorModel import EBM
from src.models.GeneratorModel import GEN

parser = configparser.ConfigParser()
parser.read("hyperparams.ini")

E_lr = float(parser["OPTIMIZER"]["E_LR"])
G_lr = float(parser["OPTIMIZER"]["G_LR"])
E_beta_1 = float(parser["OPTIMIZER"]["E_BETA_1"])
G_beta_1 = float(parser["OPTIMIZER"]["G_BETA_1"])
E_beta_2 = float(parser["OPTIMIZER"]["E_BETA_2"])
G_beta_2 = float(parser["OPTIMIZER"]["G_BETA_2"])
E_gamma = float(parser["OPTIMIZER"]["E_GAMMA"])
G_gamma = float(parser["OPTIMIZER"]["G_GAMMA"])
temp_power = float(parser["TEMP"]["TEMP_POWER"])
num_temps = int(parser["TEMP"]["NUM_TEMPS"])


def init_EBM(key):
    """Initialise the EBM model and its parameters."""

    key, z_init = sample_p0(key)
    EBM_model = EBM()
    EBM_params = jax.jit(EBM_model.init)(key, z_init)
    EBM_fwd = jax.jit(EBM_model.apply)

    return key, EBM_params, EBM_fwd


def init_GEN(key):
    """Initialise the GEN model and its parameters."""

    key, z_init = sample_p0(key)
    GEN_model = GEN()
    GEN_params = jax.jit(GEN_model.init)(key, z_init)
    GEN_fwd = jax.jit(GEN_model.apply)

    return key, GEN_params, GEN_fwd


def init_EBM_optimiser(EBM_params):
    """Initialise the EBM optimiser and its state."""

    schedule = optax.exponential_decay(E_lr, 10, E_gamma)
    E_optimiser = optax.adam(schedule, b1=E_beta_1, b2=E_beta_2)
    E_opt_state = E_optimiser.init(EBM_params)

    return E_optimiser, E_opt_state


def init_GEN_optimiser(GEN_params):
    """Initialise the GEN optimiser and its state."""

    schedule = optax.exponential_decay(G_lr, 10, G_gamma)
    GEN_optimiser = optax.adam(schedule, b1=G_beta_1, b2=G_beta_2)
    GEN_opt_state = GEN_optimiser.init(GEN_params)

    return GEN_optimiser, GEN_opt_state


def init_temp_schedule():
    """Set the temperature schedule."""

    if temp_power >= 1:
        print("Using Temperature Schedule with Power: {}".format(temp_power))
        temp = jnp.linspace(0, 1, num_temps) ** temp_power
        print("Temperature Schedule: {}".format(temp))

    else:
        print("Using no Thermodynamic Integration, defaulting to Vanilla Model")
        temp = jnp.array([1])
        print("Temperature Schedule: {}".format(temp))

    return temp
