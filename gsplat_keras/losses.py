import tensorflow as tf

def photometric_loss(target, rendered, ssim_weight=0.2):
    l1=tf.reduce_mean(tf.abs(tf.cast(target,tf.float32)-tf.cast(rendered,tf.float32)))
    ssim=1.-tf.reduce_mean(tf.image.ssim(target[None],rendered[None],max_val=1.))
    return l1+ssim_weight*ssim
