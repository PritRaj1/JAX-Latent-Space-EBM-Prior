import matplotlib.pyplot as plt
from matplotlib import rc
from functools import partial
import pandas as pd
import numpy as np

from src.pipeline.initialise import *
from src.pipeline.batch_steps import train_step, val_step
from src.metrics.unbiased_metrics import profile_generation
from src.utils.helper_functions import make_grid

# Set plot styling
rc("font", **{"family": "serif", "serif": ["Computer Modern"]}, size=12)
rc("text", usetex=True)

parser = configparser.ConfigParser()
parser.read("hyperparams.ini")

save_every = int(parser["PIPELINE"]["SAVE_EVERY"])
num_epochs = int(parser["PIPELINE"]["NUM_EPOCHS"])

min_samples = int(parser["GENERATION_EVAL"]["MIN_SAMPLES"])
max_samples = int(parser["GENERATION_EVAL"]["MAX_SAMPLES"])
num_points = int(parser["GENERATION_EVAL"]["NUM_POINTS"])
num_plot = int(parser["GENERATION_EVAL"]["NUM_PLOT"])


def run_experiment(exp_num, train_loader, val_x, log_path):

    # Initialise the pipeline
    key = jax.random.PRNGKey(0)
    key, EBM_params, EBM_fwd = init_EBM(key)
    key, GEN_params, GEN_fwd = init_GEN(key)
    EBM_optimiser, EBM_opt_state = init_EBM_optimiser(EBM_params)
    GEN_optimiser, GEN_opt_state = init_GEN_optimiser(GEN_params)
    temp_schedule = init_temp_schedule()

    # Tuple up for cleanliness
    params_tup = (EBM_params, GEN_params)
    fwd_fcn_tup = (EBM_fwd, GEN_fwd)
    optimiser_tup = (EBM_optimiser, GEN_optimiser)
    opt_state_tup = (EBM_opt_state, GEN_opt_state)

    # Preload the pipeline functions with immutable arguments
    loaded_train_step = partial(
        train_step,
        optimiser_tup=optimiser_tup,
        fwd_fcn_tup=fwd_fcn_tup,
        temp_schedule=temp_schedule,
    )
    loaded_val_step = partial(
        val_step, fwd_fcn_tup=fwd_fcn_tup, temp_schedule=temp_schedule
    )

    # Jit the pipeline functions
    jit_train_step = jax.jit(loaded_train_step)
    jit_val_step = jax.jit(loaded_val_step)

    # Preload the metric function
    metrics_fcn = partial(
        profile_generation,
        x=val_x,
        fwd_fcn_tup=fwd_fcn_tup,
        min_samples=min_samples,
        max_samples=max_samples,
        num_points=num_points,
        num_plot=num_plot,
    )

    def val_batches(carry, x, params_tup):
        """Batch validation fcn for scanning."""
        key = carry
        key, loss, var = jit_val_step(key, x, params_tup)
        return (key), (loss, var)

    img_evolution = np.zeros((num_epochs // save_every, 64, 64, 3))

    df = pd.DataFrame(
        columns=[
            "Epoch",
            "Train Loss",
            "Train Grad Var",
            "Val Loss",
            "Val Grad Var",
            "FID_inf",
            "MIFID_inf",
            "KID_inf",
        ]
    )

    for epoch in range(num_epochs):

        # Train - cannot scan due to large param count, default to for loop
        train_loss = 0
        train_grad_var = 0
        for x, _ in train_loader:
            key, params_tup, opt_state_tup, train_loss, train_grad_var = jit_train_step(
                key, x, params_tup, opt_state_tup
            )

            train_loss += train_loss
            train_grad_var += train_grad_var

        # Validate
        key, (val_loss, val_grad_var) = jax.lax.scan(
            f=partial(val_batches, params_tup=params_tup), init=key, xs=val_x
        )

        val_loss = val_loss.sum()
        val_grad_var = val_grad_var.sum()

        # Profile generative capacity using unbiased metrics
        key, fid_inf, mifid_inf, kid_inf, four_fake, four_real = metrics_fcn(
            key, params_tup
        )

        # Save to dataframe
        df = df.append(
            {
                "Epoch": epoch,
                "Train Loss": train_loss,
                "Train Grad Var": train_grad_var,
                "Val Loss": val_loss,
                "Val Grad Var": val_grad_var,
                "FID_inf": fid_inf,
                "MIFID_inf": mifid_inf,
                "KID_inf": kid_inf,
            },
            ignore_index=True,
        )

        if epoch % save_every == 0 and exp_num == 0:
            fake_grid = make_grid(four_fake, n_row=2)
            real_grid = make_grid(four_real, n_row=2)

            fig, ax = plt.subplots(1, 2)
            ax[0].imshow(real_grid)
            ax[0].set_title("Real Images")
            ax[0].axis("off")
            ax[1].imshow(fake_grid)
            ax[1].set_title("Generated Images")
            ax[1].axis("off")
            plt.suptitle(
                f"Epoch: {epoch} \n\n"
                + r"$\overline{FID}_\infty$: "
                + f"{fid_inf:.2f}, "
                + r"$\overline{MIFID}_\infty$: "
                + f"{mifid_inf:.2f}, "
                + r"$\overline{KID}_\infty$: "
                + f"{kid_inf:.2f}"
            )
            plt.tight_layout()
            plt.savefig(f"{log_path}/images/{epoch}.png", dpi=750)

            img_evolution[epoch // save_every] = four_fake[0]

    if exp_num == 0:
        evol_grid = make_grid(img_evolution, n_row=1)
        plt.figure()
        plt.imshow(evol_grid)
        plt.axis("off")
        plt.title("Evolution of Generated Images")
        plt.tight_layout()
        plt.savefig(f"{log_path}/images/evolution.png", dpi=750)

    with pd.ExcelWriter(f"{log_path}/metrics.xlsx") as writer:
        df.to_excel(writer, sheet_name=f"Experiment_{exp_num}", index=False)
