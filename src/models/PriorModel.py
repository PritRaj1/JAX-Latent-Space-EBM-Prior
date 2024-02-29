import flax.linen as nn
import configparser

parser = configparser.ConfigParser()
parser.read("hyperparams.ini")

hidden_units = int(parser['EBM']['EBM_FEATURE_DIM'])
output_dim = int(parser['EBM']['Z_CHANNELS'])
leak_coef = float(parser['EBM']['EBM_LEAK'])

class EBM(nn.Module):

    @nn.compact
    def __call__(self, z):
        f = nn.activation.leaky_relu

        z = nn.Dense(hidden_units)(z)
        z = f(z, leak_coef)
        z = nn.Dense(hidden_units)(z)
        z = f(z, leak_coef)
        z = nn.Dense(output_dim)(z)

        return z
