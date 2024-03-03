import configparser
import jax.numpy as jnp

from src.MCMC_Samplers.grad_log_probs import prior_grad_log, posterior_grad_log

parser = configparser.ConfigParser()
parser.read("hyperparams.ini")

p0_sig = float(parser["SIGMAS"]["p0_SIGMA"])
pl_sig = float(parser["SIGMAS"]["LKHOOD_SIGMA"])

prior_steps = int(parser["MCMC"]["E_SAMPLE_STEPS"])
prior_s = float(parser["MCMC"]["E_STEP_SIZE"])
posterior_steps = int(parser["MCMC"]["G_SAMPLE_STEPS"])
posterior_s = float(parser["MCMC"]["G_STEP_SIZE"])

def langevin_prior(z, noise, EBM_params, EBM_fwd):

    # Compute the gradient of the log prior
    grad_f = prior_grad_log(z, EBM_params, EBM_fwd) + (z / p0_sig**2)
    
    # Update z_prior
    new_z = z - (prior_s * grad_f) + (noise * jnp.sqrt(2 * prior_s))

    return new_z, None

def langevin_posterior(z, noise, x, t, EBM_params, GEN_params, EBM_fwd, GEN_fwd):

    # Compute the gradient of the log posterior
    grad_f = posterior_grad_log(z, x, t, EBM_params, GEN_params, EBM_fwd, GEN_fwd) + (z / p0_sig**2)

    # Update z_posterior
    new_z = z - (posterior_s * grad_f) + (noise * jnp.sqrt(2 * posterior_s))
    
    return new_z, None