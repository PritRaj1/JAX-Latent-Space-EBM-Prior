# JAX-Latent-Space-EBM-Prior
A JAX implementation of the Learning Latent Space Energy-Based Prior Model, presented by [Pang et al. (2020)](https://proceedings.neurips.cc/paper_files/paper/2020/file/fa3060edb66e6ff4507886f9912e1ab9-Paper.pdf). Thermodynamic Integration, presented by [Calderhead and Girolami (2009)](https://www.sciencedirect.com/science/article/pii/S0167947309002722),
 has also been implemented as a means of exerting control over learning gradient variance.

The comprehensive **42-page** thesis has been uploaded [here](https://github.com/PritRaj1/JAX-ThermoEBM/blob/main/MEng%20Report.pdf). Everything is detailed in this document for your reference.

<p align="center">
  <img src="results/demo/all_temperature_schedule.gif" alt="Temperature Schedules" width="48%" style="padding-right: 20px;">
  <img src="results/demo/all_integral.gif" alt="Thermodynamic Integral" width="48%">
</p>

## To run

To get started, follow these steps:

1. Make sure you have Python version 3.9 or higher installed.
 
2. Install the required dependencies by running:

```bash
pip install -r requirements.txt
```

3. Edit the hyperparameters in the `hyperparams.ini` file according to your experiment setup.

4. Run the main experiment script `main.py` to gather CSV logs. You can do this by executing:

```bash
python main.py
```

## Technical Introduction

The performances of deep generative models depend on the distributional characteristics of their learning gradients. Despite this, the exact influence of learning gradient variance remains poorly understood, and investigations into the topic are bounded by our limited ability to control gradient variance. For example, managing gradient variance through batching alone is challenging, especially under constrained computational resources.

To address this, we propose leveraging Thermodynamic Integration as a means of robustly controlling the learning gradient variance. This is achieved by parameterising the temperature schedule used to evaluate the thermodynamic integral. This parameterisation allows us to exert precise control over the variances in estimates of latent space variables derived through Markov chain Monte Carlo (MCMC) sampling, as well as the error in Monte Carlo estimates of the mean. The method is subsequently proven and applied to investigate the relationship between learning gradient variance and the fidelity of images generated by the latent space energy-based prior model introduced by [Pang et al., 2020](https://proceedings.neurips.cc/paper_files/paper/2020/file/fa3060edb66e6ff4507886f9912e1ab9-Paper.pdf). 

This study reveals that although there is a notable relationship between learning gradient variance and image fidelity, learning gradient variance alone is inadequate as a predictor of the generative capacity of the latent space energy-based prior model. Instead, the study demonstrates that the temperature schedule itself exerts an even greater influence on image fidelity, serving as a direct reflection of the balance between exploration and exploitation that the deep generative model maintains over the loss landscape. 

## Does learning gradient variance matter?

Yes! Learning gradient variance is very important. It is reflective of the exploratory vs exploitative capacity of your neural network during training. It often has a deterministic form, (in theory):

```math  
\nabla _\theta \mathcal{L}(\theta, \mathbf{x}) = - \nabla _\theta \log(p_\theta(\mathbf{x}))
```

However, it has to be evaluated using stochastic approximation approaches, therefore in reality...

```math
\left[ \nabla_\theta \mathcal{L}(\theta, \mathbf{x}) \right] \quad \text{is a distribution!}
```

We argue that adopting a distributional standpoint regarding a neural network's learning process, and being able to shape the form of its learning gradient distribution are important steps towards improving optimisation efficiency, generalisation, and generative capacity. You want proof? Here are some artificially generated images, with their corresponding learning gradients captioned underneath:

<p align="center">
<img src="https://github.com/PritRaj1/JAX-ThermoEBM/assets/77790119/b526520f-4d92-4eb2-a458-3b0224678a6b" width="50%">
</p>
 
As you can see, increasing learning gradient variance improves image fidelity **until a minimum is achieved**, (so long as mode collapse has not occurred). Increasing further beyond this worsens image quality. Previous attempts at shaping the distribution of the learning gradient have sought or provided expressions to reduce or minimise variance, (see [Calderhead and Girolami (2009)](https://www.sciencedirect.com/science/article/pii/S0167947309002722) and [Faghri et al. (2007)](https://arxiv.org/abs/2007.04532)). This would make sense if the learning gradient had an analytic form, since minimising variance is akin to minimising error. However, instead...

```math
\left[ \nabla_\theta \mathcal{L}(\theta, \mathbf{x}) \right] \quad \text{is a distribution!}
```

In fact, this was one of the demonstrated findings of the report, which persisted across datasets:

<p align="center">
<img src="https://github.com/PritRaj1/JAX-ThermoEBM/assets/77790119/bfaa49a8-5d5c-4862-bac0-b9759e263bdc" width="50%">
<img src="https://github.com/PritRaj1/JAX-ThermoEBM/assets/77790119/e16042e4-94af-461f-9b26-c41665f742ea" width="50%">
</p>

These plots are fairly nuanced and are covered in more depth in the report. However, the important thing is that **there is a striking relationship between image fidelity and learning gradient variance!** Minmising or maximising variance is **not necessarily the best thing to do**, and the relationships can be separated out into different regimes of operation.

As such, more focus needs to be placed on investigating the distributional characteristics of the learning gradient, which requires a means of arbitrarily shaping what it looks like, (rather than simply minimising or maximising its variance). We show that this can be accomplished using **Thermodynamic Integration**.  

## Thermodynamic Integration

Batch size is another means of controlling the learning gradient variance, however it's not easy to control. Below is an experiment I ran comprising 5 repetitions. Here, batch size was varied and the range of learning gradient variances achieved across the repetitions was plotted. For reference, this is contrasted below against a model incorporating Thermodynamic Integration with a fixed batch size, and different values for a particular hyperparameter, p. 

<p align="center">
  <img src="results/CelebA/boxplots/grad_var_bsize.png" alt="Control of variance with batch size" width="50%" style="padding-right: 20px;">
  <img src="results/CelebA/boxplots/grad_var_p.png" alt="Control of variance with p" width="50%">
</p>

Evidently, Thermodynamic Integration can achieve comparable variances to the model incorporating different batch sizes, except it achieves much greater consistency across repetitions. This means that learning gradient variance can be robustly tuned by varying p, which facilitates investigations and studies into the learning gradient variance!





