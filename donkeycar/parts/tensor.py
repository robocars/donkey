import tensorflow as tf
import numpy as np


class Tensor():
    def load(self, model_path):
        self.estimator = tf.estimator.Estimator(
            model_fn=model_fn,
            model_dir=model_path)
        
    def run(self, img_arr):
        img = np.reshape(img_arr, (-1,120,160,3))
        imgs = { 'image' : np.array(img, dtype=np.float32) }
        input_fn = tf.estimator.inputs.numpy_input_fn(imgs, y = None,
                        num_epochs = 1, shuffle = False, batch_size = 1)
        estimation = tf.estimator.predict(input_fn)
        est = next(estimation)
        angle_binned = est["angle_probabilities"]
        angle_unbinned = dk.utils.linear_unbin(angle_binned)
        return angle_unbinned, est['throttle'][0]


class Model(object):

    def __init__(self):
        self.conv1 = tf.layers.Conv2D(24, 5, 2, activation=tf.nn.relu)
        self.conv2 = tf.layers.Conv2D(24, 5, 2, activation=tf.nn.relu)
        self.conv3 = tf.layers.Conv2D(36, 5, 2, activation=tf.nn.relu)
        self.conv4 = tf.layers.Conv2D(48, 3, 2, activation=tf.nn.relu)
        self.conv5 = tf.layers.Conv2D(64, 3, 1, activation=tf.nn.relu)
        self.conv6 = tf.layers.Conv2D(64, 3, 1, activation=tf.nn.relu)
        self.dense1 = tf.layers.Dense(100, activation=tf.nn.relu)
        self.dropout1 = tf.layers.Dropout(.1)
        self.dense2 = tf.layers.Dense(50, activation=tf.nn.relu)
        self.dropout2 = tf.layers.Dropout(.1)
        self.angle_logits = tf.layers.Dense(15, activation=tf.nn.relu)
        self.predicted_throttle = tf.layers.Dense(1)

    def __call__(self, inputs, training):

        y = tf.reshape(inputs,  [-1, 120, 160, 3])
        y = self.conv1(y)
        y = self.conv2(y)
        y = self.conv3(y)
        y = self.conv4(y)
        y = self.conv5(y)
        y = self.conv6(y)
        y = tf.layers.flatten(y)
        y = self.dense1(y)
        y = self.dropout1(y, training=training)
        y = self.dense2(y)
        y = self.dropout2(y, training=training)
        return self.angle_logits(y), self.predicted_throttle(y)

def model_fn(features, labels, mode):
    """The model_fn argument for creating an Estimator."""
    model = Model()
    image = features['image']
    training = mode == tf.estimator.ModeKeys.TRAIN
    angle_logits, predicted_throttle = model(image, training=training)
    predicted_angle = tf.argmax(input=angle_logits, axis=1,)
    if mode == tf.estimator.ModeKeys.PREDICT:
        predictions = {
            "throttle": predicted_throttle,
            "angle": predicted_angle,
            "angle_probabilities": tf.nn.softmax(angle_logits, name="softmax_tensor")
        }
        return tf.estimator.EstimatorSpec(
            mode=tf.estimator.ModeKeys.PREDICT,
            predictions=predictions,
            export_outputs={
                'autopilot': tf.estimator.export.PredictOutput(predictions)
            })
    angle = labels['angle']
    throttle = labels['throttle']
    angle_loss = tf.losses.softmax_cross_entropy(onehot_labels=angle, logits=angle_logits)
    throttle_loss = tf.losses.absolute_difference(labels=throttle,predictions=predicted_throttle)
    tf.summary.scalar('angle_loss', angle_loss)
    tf.summary.scalar('throttle_loss', throttle_loss)
    loss = angle_loss + throttle_loss
    angle_accuracy = tf.metrics.accuracy(labels=angle, predictions=angle_logits)
    throttle_accuracy = tf.metrics.accuracy(labels=throttle, predictions=predicted_throttle)
    if training:
        optimizer = tf.train.AdamOptimizer(learning_rate=1e-2)
        angle_train_op = optimizer.minimize(
            loss=angle_loss,
            global_step=tf.train.get_global_step())
        throttle_train_op = optimizer.minimize(
            loss=throttle_loss,
            global_step=tf.train.get_global_step())
        train_op = tf.group(angle_train_op, throttle_train_op)
        tf.identity(angle_accuracy[1], name='angle_accuracy')
        tf.summary.scalar('angle_accuracy', angle_accuracy[1])
        tf.identity(throttle_accuracy[1], name='throttle_accuracy')
        tf.summary.scalar('throttle_accuracy', throttle_accuracy[1])
        return tf.estimator.EstimatorSpec(
            mode=tf.estimator.ModeKeys.TRAIN,
            loss=loss,
            train_op=train_op)


    if mode == tf.estimator.ModeKeys.EVAL:
        return tf.estimator.EstimatorSpec(
            mode=tf.estimator.ModeKeys.EVAL,
            loss=loss,
            eval_metric_ops={
                'angle_accuracy':angle_accuracy,
                'throttle_accuracy':throttle_accuracy
            })
