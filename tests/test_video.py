import cv2
import numpy as np
from gsplat_keras.video import extract_frames

def test_extract_frames(tmp_path):
    video=str(tmp_path/"sample.avi")
    writer=cv2.VideoWriter(video,cv2.VideoWriter_fourcc(*"MJPG"),5,(32,32))
    for i in range(6): writer.write(np.full((32,32,3),i*20,np.uint8))
    writer.release()
    assert extract_frames(video,tmp_path/"frames",every=2)==3
