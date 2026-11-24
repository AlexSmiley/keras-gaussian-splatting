import numpy as np
from gsplat_keras.camera import qvec_to_rotmat,project_points,Camera

def test_identity_quaternion():
    np.testing.assert_allclose(qvec_to_rotmat([1,0,0,0]),np.eye(3),atol=1e-6)

def test_project_point():
    c=Camera(100,100,50,50,50,50,np.eye(3,dtype=np.float32),np.zeros(3,dtype=np.float32))
    uv,z=project_points(np.array([[0,0,2]],np.float32),c)
    np.testing.assert_allclose(uv,[[50,50]])
    np.testing.assert_allclose(z,[2])
