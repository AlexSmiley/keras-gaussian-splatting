import tensorflow as tf

def render_gaussians(params, camera, height, width, background=(0.,0.,0.)):
    # Dense differentiable reference renderer: O(N*H*W) memory and compute.
    means,scales=params["means"],params["scales"]
    opacity,colors=params["opacity"],params["colors"]
    xyz=tf.linalg.matmul(means,camera["rotation"],transpose_b=True)+camera["translation"]
    z=xyz[:,2]; safe_z=tf.maximum(z,1e-4)
    u=camera["fx"]*xyz[:,0]/safe_z+camera["cx"]
    v=camera["fy"]*xyz[:,1]/safe_z+camera["cy"]
    radius=tf.maximum(camera["fx"]*tf.reduce_mean(scales,axis=-1)/safe_z,0.55)
    xs,ys=tf.meshgrid(tf.range(width,dtype=tf.float32),tf.range(height,dtype=tf.float32))
    dx=xs[None]-u[:,None,None]; dy=ys[None]-v[:,None,None]
    exponent=(dx*dx+dy*dy)/(2.*radius[:,None,None]**2+1e-8)
    alpha=tf.exp(-exponent)*opacity[:,0,None,None]
    visible=(z>1e-4)&(u>-3*radius)&(u<width+3*radius)&(v>-3*radius)&(v<height+3*radius)
    alpha*=tf.cast(visible[:,None,None],tf.float32)
    alpha=tf.clip_by_value(alpha,0.,0.99)
    order=tf.argsort(z,direction="ASCENDING")
    alpha=tf.gather(alpha,order); colors=tf.gather(colors,order)
    one_minus=tf.clip_by_value(1.-alpha,1e-6,1.)
    trans=tf.math.cumprod(one_minus,axis=0,exclusive=True)
    weights=alpha*trans
    rgb=tf.einsum("nhw,nc->hwc",weights,colors)
    remaining=tf.reduce_prod(one_minus,axis=0)
    return tf.clip_by_value(rgb+remaining[...,None]*tf.constant(background,tf.float32),0.,1.)
