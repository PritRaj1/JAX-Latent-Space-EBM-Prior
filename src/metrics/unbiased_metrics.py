import jax
import jax.numpy as jnp
import numpy as np
from functools import partial
from sklearn.linear_model import LinearRegression

from src.metrics.get_metrics import get_metrics
from src.metrics.inception_network import extract_features
from src.pipeline.generate import generate

def metrics_fcn(key, sample_size, num_features, x_activations, x_pred_activations):

    # Build random subset
    keys = jax.random.split(key, 3)
    key, subkey1, subkey2 = keys
    x_act_i = jax.random.choice(
        subkey1, x_activations, (sample_size,), replace=True
    )
    x_pred_act_i = jax.random.choice(
        subkey2, x_pred_activations,  (sample_size,), replace=True
    )

    # Compute metrics
    fid, mifid, kid = get_metrics(x_act_i, x_pred_act_i)

    return key, (fid, mifid, kid)


def profile_generation(
    key, params_tup, x, fwd_fcn_tup, min_samples, max_samples, num_points, num_plot
):
    """
    Function to profile the generative capacity of the model.
    Traditional image-quality metrics are generally biased,
    so following the previous work of Chong et. al, we aim to
    remove bias by interpolating to an infinite sample size.

    https://doi.org/10.48550/arXiv.1911.07023

    Args:
    - key: PRNG key
    - x: all test data
    - gen_fcn: generative function, partially preloaded with immutables
    - min_samples: minimum number of samples
    - max_samples: maximum number of samples
    - num_points: number of points to profile
    - num_plot: number of images to plot for visual inspection

    Returns:
    - fid_inf: the unbiased FID
    - mifid_inf: the unbiased MIFID
    - kid_inf: the unbiased KID
    - four_real: 4 random real images
    - four_fake: 4 random fake images
    """

    # Preload the generation and profile functions with immutable arguments
    gen_fcn = partial(
        generate, params_tup=params_tup, num_images=max_samples, fwd_fcn_tup=fwd_fcn_tup
    )

    if max_samples > len(x):
        raise ValueError("Max samples cannot exceed the number of test images.")
    elif min_samples > max_samples:
        raise ValueError("Min samples cannot exceed max samples.")

    batch_sizes = jnp.linspace(min_samples, max_samples, num_points, dtype=int)

    # Generate the maximum number of samples
    key, x_pred = gen_fcn(key)

    # Get all activations
    x_activations = extract_features(x)
    x_pred_activations = extract_features(x_pred)

    loop_metrics = partial(
        metrics_fcn,
        num_features=x_activations.shape[-1],
        x_activations=x_activations,
        x_pred_activations=x_pred_activations,
    )

    fid, mifid, kid = np.zeros(num_points), np.zeros(num_points), np.zeros(num_points)

    for idx, sample_size in enumerate(batch_sizes):
        key, (fid_i, mifid_i, kid_i) = loop_metrics(key, sample_size)
        fid[idx], mifid[idx], kid[idx] = fid_i, mifid_i, kid_i

    # Fit a linear regression to the inverse of the batch sizes
    reg_fid = LinearRegression().fit(1 / batch_sizes.reshape(-1, 1), fid)
    reg_mifid = LinearRegression().fit(1 / batch_sizes.reshape(-1, 1), mifid)
    reg_kid = LinearRegression().fit(1 / batch_sizes.reshape(-1, 1), kid)

    # Interpolate to infinite sample size
    fid_inf = reg_fid.predict(np.array([[0]]))[0, 0]
    mifid_inf = reg_mifid.predict(np.array([[0]]))[0, 0]
    kid_inf = reg_kid.predict(np.array([[0]]))[0, 0]

    # Return 4 random images for plotting (visual inspection)
    random_indices = np.random.choice(len(x_pred), num_plot, replace=False)
    four_real = np.array([x[i] for i in random_indices])
    four_fake = np.array([x_pred[i] for i in random_indices])

    return key, fid_inf, mifid_inf, kid_inf, four_real, four_fake