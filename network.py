from config import *
from layer import *
import tensorlayer as tl
import tensorflow as tf

class GlimpsNetwork(object):
    def __init__(self, location_ph):
        self.location_ph = location_ph

    def getGlimps(self, location_ph):
        self.input_layer = tl.layers.InputLayer(self.location_ph, name='glimps_input_layer')
        self.glimps_imgs = tl.layers.ReshapeLayer(self.input_layer, [-1, 28, 28, 1], name='reshape_layer_1')
        self.glimps_imgs = GlimpsExtractLayer(self.glimps_imgs, location_ph)
        self.glimps_imgs = tl.layers.ReshapeLayer(self.glimps_imgs, [-1, win_size * win_size * 1], name='reshape_layer_2')
        return self.glimps_imgs

    def __call__(self, loc_tensor):
        self.retina_imgs = self.getGlimps(loc_tensor)
        self.retina_net = tl.layers.DenseLayer(self.retina_imgs, n_units = 128, act = tf.nn.relu, name='glimps_ind_fc_1')
        self.location_input_layer = tl.layers.InputLayer(loc_tensor, name='location_state_input')
        self.location_net = tl.layers.DenseLayer(self.location_input_layer, n_units = 128, act = tf.nn.relu, name='glimps_ind_fc_2')
        self.glimps_net = tl.layers.ConcatLayer([self.retina_net, self.location_net], concat_dim = -1)
        self.glimps_net = tl.layers.DenseLayer(self.glimps_net, n_units = 256, act = tf.nn.relu, name='glimps_merge_fc_1')
        return self.glimps_net.outputs

class LocationNetwork(object):
    def __init__(self):
        pass

    def __call__(self, state_tensor):
        self.location_net = tl.layers.InputLayer(state_tensor)

        print (tf.get_variable_scope().reuse)
        
        self.location_net = tl.layers.DenseLayer(self.location_net, n_units = loc_dim, name='location_net_fc1')
        mean = tf.stop_gradient(tf.clip_by_value(self.location_net.outputs, -1.0, 1.0))
        location = mean + tf.random_normal((tf.shape(state_tensor)[0], loc_dim), stddev=loc_std)
        location = tf.stop_gradient(location)
        
        return location, mean

"""
location_ph = tf.placeholder(tf.float32, [None, 28, 28, 1])
net = LocationNetwork()
net(tf.random_uniform((1, 2), minval=-1, maxval=1))
"""