# coding: utf-8
import tensorflow as tf
import numpy as np
from tensorflow.examples.tutorials.mnist import input_data
import os

IS_TRAIN = os.getenv('IS_TRAIN')

mnist = input_data.read_data_sets('MNIST_data', one_hot=True) #以one-hot编码读取mnist数据集

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
        self.labels = tf.placeholder(tf.float32,[None,10])  #设置标签占位符
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
            #使用交叉熵做标签预测损失
            self.pred_loss = tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=self.labels)


graph = tf.get_default_graph()
with graph.as_default():
    model = mnistmodel()
    learning_rate = tf.placeholder(tf.float32,[])
    pred_loss = tf.reduce_mean(model.pred_loss)
	
    
    #随机梯度下降对loss进行优化
    train_op = tf.train.GradientDescentOptimizer(learning_rate=learning_rate).minimize(pred_loss)
    # 计算标签预测准确率
    correct_label_pred = tf.equal(tf.argmax(model.labels, 1), tf.argmax(model.pred, 1))
    label_acc = tf.reduce_mean(tf.cast(correct_label_pred, tf.float32))

with tf.Session(graph= graph) as sess:
    tf.global_variables_initializer().run()
    saver = tf.train.Saver(max_to_keep=1)#创建saver对象来保存训练的模型
    max_acc = 0
    # training loop

    if IS_TRAIN == 'True':

        num_steps = int(os.getenv("NUM_STEPS"))

        for i in range(num_steps):
            lr = 0.001
            #调用mnist自带的next_batch函数生成大小为100的batch
            batch = mnist.train.next_batch(100)

            _,p_loss,l_acc = sess.run([train_op, pred_loss, label_acc],
                                         feed_dict={model.images: batch[0],model.labels: batch[1],learning_rate:lr})
            print('step:{}  pred_loss:{}  l_acc: {}'.format(i,p_loss,l_acc))
            if i%100==0 :
                test_acc = sess.run(label_acc,feed_dict={model.images:mnist.test.images, model.labels:mnist.test.labels})
                print('step: {} test_acc: {}'.format(i,test_acc))
            #计算当前模型在测试集上准确率，最终保存准确率最高的一次模型
            if test_acc>max_acc:
                max_acc = test_acc
                saver.save(sess,'./ckpt/mnist.ckpt',global_step=i+1)
    #读取模型日志文件进行测试
    elif IS_TRAIN == 'False':
        model_file = tf.train.latest_checkpoint('./ckpt/')
        saver.restore(sess,model_file)
        test_acc = sess.run(label_acc, feed_dict={model.images: mnist.test.images, model.labels: mnist.test.labels})
        print('test_acc: {}'.format(test_acc))
    else:
        print("You neend to set environment variable IS_TRAIN correctly!")
