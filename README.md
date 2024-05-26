# JAX-Latent-Space-EBM-Prior
A JAX implementation of the Learning Latent Space Energy-Based Prior Model, presented by [Pang et al. (2020)](https://proceedings.neurips.cc/paper_files/paper/2020/file/fa3060edb66e6ff4507886f9912e1ab9-Paper.pdf). Thermodynamic Integration, presented by [Calderhead and Girolami (2009)](https://www.sciencedirect.com/science/article/pii/S0167947309002722),
 has also been implemented as a means of exerting control over learning gradient variance.

WORK IN PROGRESS

## Abstract

The performances of deep generative models depend on the distributional characteristics of their learning gradients. Despite this, the exact influence of learning gradient variance remains poorly understood, and investigations into the topic are bounded by our limited ability to control gradient variance. For example, managing gradient variance through batching alone is challenging, especially under constrained computational resources.

To address this, we propose leveraging Thermodynamic Integration as a means of robustly controlling the learning gradient variance. This is achieved by parameterising the temperature schedule used to evaluate the thermodynamic integral. This parameterisation allows us to exert precise control over the variances in estimates of latent space variables derived through Markov chain Monte Carlo (MCMC) sampling, as well as the error in Monte Carlo estimates of the mean. The method is subsequently proven and applied to investigate the relationship between learning gradient variance and the fidelity of images generated by the latent space energy-based prior model introduced by [Pang et al., 2020](https://proceedings.neurips.cc/paper_files/paper/2020/file/fa3060edb66e6ff4507886f9912e1ab9-Paper.pdf). 

This study reveals that although there is a notable relationship between learning gradient variance and image fidelity, learning gradient variance alone is inadequate as a predictor of the generative capacity of the latent space energy-based prior model. Instead, the study demonstrates that the temperature schedule itself exerts an even greater influence on image fidelity, serving as a direct reflection of the balance between exploration and exploitation that the deep generative model maintains over the loss landscape. 

## More detailed intro

Deep generative models belong to a category of machine learning algorithms characterised as neural networks for generating new data samples, such as images or text. These models undergo training primarily by minimising a loss function, denoted as $\mathcal{L}(\theta, \mathbf{x})$, achieved through iterative adjustments of the neural network parameters, represented as $\theta$. The form of these adjustments are evaluated through gradient-based optimisation techniques, such as [stochastic gradient descent (SGD)](https://api.semanticscholar.org/CorpusID:16945044) and [Adam optimisation](https://arxiv.org/abs/1412.6980).

Importantly, these methods require the learning gradient, $\nabla_\theta \mathcal{L}(\theta, \mathbf{x})$, i.e. the gradient of the loss with respect to the parameters, evaluated at a training sample $\mathbf{x}$. However, due to the probabilistic nature of the data and the inherent noise introduced by gradient-based optimisation methods, the learning gradient forms a non-deterministic probability distribution.

In agreement with the previous work of [Faghri et al.](https://arxiv.org/abs/2007.04532), we therefore argue that adopting a distributional perspective on gradient-based optimisation and exploring the characteristics of $\nabla_\theta \mathcal{L}(\theta, \mathbf{x})$ are crucial steps toward enhancing optimisation speed and the model's ability to generalise beyond the training dataset. 

However, exerting explicit control over the shape of this distribution presents a persistent obstacle that has prevented researchers from fully grasping its exact influence in the optimisation of deep neural networks. Hence, we introduce thermodynamic integration as a method to effectively shape this distribution by directly parameterising its variance, aiming for its adoption in similar investigations concerning gradient-based learning.

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




