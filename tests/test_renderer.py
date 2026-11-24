import tensorflow as tf
from gsplat_keras.renderer import render_gaussians

def test_renderer_shape_and_gradients():
    p={"means":tf.Variable([[0.,0.,2.]]),"scales":tf.Variable([[.2,.2,.2]]),
       "rotations":tf.constant([[1.,0.,0.,0.]]),"opacity":tf.Variable([[.8]]),
       "colors":tf.Variable([[1.,0.,0.]])}
    c={"rotation":tf.eye(3),"translation":tf.zeros(3),"fx":tf.constant(20.),
       "fy":tf.constant(20.),"cx":tf.constant(8.),"cy":tf.constant(8.)}
    with tf.GradientTape() as tape:
        image=render_gaussians(p,c,16,16); loss=tf.reduce_sum(image)
    grads=tape.gradient(loss,[p["means"],p["scales"],p["opacity"],p["colors"]])
    assert image.shape==(16,16,3)
    assert all(g is not None for g in grads)
