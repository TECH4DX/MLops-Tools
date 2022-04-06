# coding: utf-8
import tensorflow as tf
import numpy as np
from tensorflow.examples.tutorials.mnist import input_data

mnist = input_data.read_data_sets('MNIST_data', one_hot=True)

def weight_variable(shape):
  initial = tf.truncated_normal(shape, stddev=0.1)
  return tf.Variable(initial)

def bias_variable(shape):
  initial = tf.constant(0.1, shape=shape)
  return tf.Variable(initial)

def conv2d(x, W):
  return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

def max_pool_2x2(x):
  return tf.nn.max_pool(x, ksize=[1, 2, 2, 1],
            strides=[1, 2, 2, 1], padding='SAME')

class mnistmodel(object):
    def __init__(self):
        self._build_model()
    def _build_model(self):
        self.images = tf.placeholder(tf.float32, [None,784])  #设置图片占位符
        with tf.variable_scope('feature_extractor'):#特征提取部分（包含两个卷积层）
            self.processimages = tf.reshape(self.images,[-1,28,28,1]) #将输入图片reshape成[28,28,1]形状
            #网络第一层
            W_conv0 = weight_variable([5,5,1,32])  #该层有32个5*5卷积核
            b_conv0 = bias_variable([32])  #32个bias
            h_conv0 = tf.nn.relu(conv2d(self.processimages, W_conv0) + b_conv0) #卷积操作，使用relu激活函数
            h_pool0 = max_pool_2x2(h_conv0)  #max pooling操作
            #网络第二层，与第一层类似
            W_conv1 = weight_variable([5,5,32,48])
            b_conv1 = bias_variable([48])
            h_conv1 = tf.nn.relu(conv2d(h_pool0,W_conv1)+b_conv1)
            h_pool1 = max_pool_2x2(h_conv1)
            #将第二层输出reshape为二维矩阵以便输入全连接层
            self.feature = tf.reshape(h_pool1, [-1, 7 * 7 * 48])
        with tf.variable_scope('label_predictor'):#标签预测部分（两层全连接层）
            #从7*7*48映射到100
            W_fc0 = weight_variable([7*7*48,100])
            b_fc0 = bias_variable([100])
            h_fc0 = tf.nn.relu(tf.matmul(self.feature,W_fc0) + b_fc0)
			#从100映射到10，以便之后分类操作
            W_fc1 = weight_variable([100, 10])
            b_fc1 = bias_variable([10])
            logits = tf.matmul(h_fc0,W_fc1) + b_fc1
			
            self.pred = tf.nn.softmax(logits)#使用Softmax将连续数值转化成相对概率


graph = tf.get_default_graph()
with graph.as_default():
    model = mnistmodel()

def inference(input):
  with tf.Session(graph= graph) as sess:
      tf.global_variables_initializer().run()
      saver = tf.train.Saver()
      model_file = tf.train.latest_checkpoint('./mnist/data/ckpt/')
      saver.restore(sess,model_file)
      return sess.run(model.pred, feed_dict={model.images: input}).flatten().tolist()