from torchvision import datasets, transforms
import jax
import numpy
import jax.numpy as jnp


def parse_input_file(input_file="hyperparams.input"):
    """Function for parse hyperparameters from input file."""
    config = {}
    with open(input_file, "r") as f:
        for line in f:
            # Skip comments and empty lines
            if line.startswith("#") or not line.strip():
                continue
            key, value = line.strip().split("=")
            config[key.strip()] = value.strip()
    return config


def get_data(name):

    img_dim = 64 if name == "CelebA" else 32

    import jax.numpy as jnp

    transform = transforms.Compose(
        [
            transforms.Resize(
                (img_dim, img_dim)
            ),  # Resize the images to defined resolution
            transforms.ToTensor(),
            transforms.Normalize(
                (0.5, 0.5, 0.5), (0.5, 0.5, 0.5)
            ),  # Normalize the image tensors
        ]
    )

    if name == "CIFAR10":
        dataset = datasets.CIFAR10(
            root="dataset/", train=True, transform=transform, download=True
        )
        val_dataset = datasets.CIFAR10(
            root="dataset/", train=False, transform=transform, download=True
        )
    elif name == "SVHN":
        dataset = datasets.SVHN(
            root="dataset/", split="train", transform=transform, download=True
        )
        val_dataset = datasets.SVHN(
            root="dataset/", split="test", transform=transform, download=True
        )
    elif name == "CelebA":
        dataset = datasets.CelebA(
            root="dataset/", split="train", transform=transform, download=True
        )
        val_dataset = datasets.CelebA(
            root="dataset/", split="test", transform=transform, download=True
        )
    else:
        raise ValueError("Invalid dataset name.")

    return dataset, val_dataset, str(img_dim)
