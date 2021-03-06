import time
import cv2
import numpy as np

class ImgGreyscale():

    def run(self, img_arr):
        img_arr = cv2.cvtColor(img_arr, cv2.COLOR_RGB2GRAY)
        return img_arr



class ImgCanny():

    def __init__(self, low_threshold=60, high_threshold=110):
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold
        
        
    def run(self, img_arr):
        return cv2.Canny(img_arr, 
                         self.low_threshold, 
                         self.high_threshold)

    

class ImgGaussianBlur():

    def __init__(self, kernal_size=5):
        self.kernal_size = kernal_size
        
    def run(self, img_arr):
        return cv2.GaussianBlur(img_arr, 
                                (self.kernel_size, self.kernel_size), 0)



class ImgCrop:
    """
    Crop an image to an area of interest. 
    """
    def __init__(self, top=0, bottom=0, left=0, right=0):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right
        
    def run(self, img_arr):
        width, height, _ = img_arr.shape
        img_arr = img_arr[self.top:height-self.bottom, 
                          self.left: width-self.right]
        return img_arr
        


class ImgStack:
    """
    Stack N previous images into a single N channel image, after converting each to grayscale.
    The most recent image is the last channel, and pushes previous images towards the front.
    """
    def __init__(self, num_channels=3):
        self.img_arr = None
        self.num_channels = num_channels

    def rgb2gray(self, rgb):
        '''
        take a numpy rgb image return a new single channel image converted to greyscale
        '''
        return np.dot(rgb[...,:3], [0.299, 0.587, 0.114])
        
    def run(self, img_arr):
        width, height, _ = img_arr.shape        
        gray = self.rgb2gray(img_arr)
        
        if self.img_arr is None:
            self.img_arr = np.zeros([width, height, self.num_channels], dtype=np.dtype('B'))

        for ch in range(self.num_channels - 1):
            self.img_arr[...,ch] = self.img_arr[...,ch+1]

        self.img_arr[...,self.num_channels - 1:] = np.reshape(gray, (width, height, 1))

        return self.img_arr

        
        
class Pipeline():
    def __init__(self, steps):
        self.steps = steps
    
    def run(self, val):
        for step in self.steps:
            f = step['f']
            args = step['args']
            kwargs = step['kwargs']
            
            val = f(val, *args, **kwargs)
        return val
    
class CvCam(object):
    def __init__(self, image_w=160, image_h=120, iCam=0):

        self.frame = None
        self.cap = cv2.VideoCapture(iCam)
        self.running = True
        self.cap.set(3, image_w)
        self.cap.set(4, image_h)

    def poll(self):
        if self.cap.isOpened():
            ret, self.frame = self.cap.read()

    def update(self):
        '''
        poll the camera for a frame
        '''
        while(self.running):
            self.poll()

    def run_threaded(self):
        return self.frame

    def run(self):
        self.poll()
        return self.frame

    def shutdown(self):
        self.running = False
        time.sleep(0.2)
        self.cap.release()


class CvImageView(object):

    def run(self, image):
        if image is None:
            return
        cv2.imshow('frame', image)
        cv2.waitKey(1)

    def shutdown(self):
        cv2.destroyAllWindows()
