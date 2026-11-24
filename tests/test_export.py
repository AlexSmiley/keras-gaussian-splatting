import tensorflow as tf
from gsplat_keras.export import export_ply,export_splat

def test_exports(tmp_path):
    p={"means":tf.constant([[0.,0.,1.]]),"scales":tf.constant([[.1,.1,.1]]),
       "rotations":tf.constant([[1.,0.,0.,0.]]),"opacity":tf.constant([[.5]]),
       "colors":tf.constant([[1.,0.,0.]])}
    ply=export_ply(tmp_path/"a.ply",p); splat=export_splat(tmp_path/"a.splat",p)
    assert ply.read_text().startswith("ply")
    assert splat.stat().st_size==32
