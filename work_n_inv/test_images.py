from PIL import Image
import numpy as np
from matplotlib import pyplot as plt
import cv2 as cv

file_pathRN=[
    '../captured/0_1628624649397679090.jpg',
    '../captured/0_1628624652178055047.jpg',
    '../captured/0_1628624659394366025.jpg',
    '../captured/0_1628624691826435089.jpg',
]

file_pathYN=[
    '../captured/1_1628624409777710914.jpg',
    '../captured/1_1628626984201232910.jpg',
    '../captured/1_1628624411373053073.jpg',
    
]

file_pathGN=[
    '../captured/2_1628624397801417112.jpg',
    '../captured/2_1628624522189229965.jpg',
    '../captured/2_1628624595403445005.jpg',
]


def draw_samples( files, low, up ):
    fig = plt.figure()
    for i in range(0, len(files) ):
        image = cv.imread( files[i] ) 
        ax = fig.add_subplot(len(files),2,i*2+1)
        ax.imshow( cv.cvtColor(image, cv.COLOR_BGR2RGB)  )
        lower = np.array(low)
        upper = np.array(up)
        shapeMask = cv.inRange(image, lower, upper)
        ax = fig.add_subplot(len(files),2,i*2+2)
        ax.imshow(shapeMask, cmap='gray' )
    plt.show()


if True:
    draw_samples(file_pathRN, [  0,   0, 200], [100, 100, 255] )

if True:
    draw_samples(file_pathYN, [  0, 200, 200], [100, 255, 255] )

if True:
    draw_samples(file_pathGN, [  0, 200,   0], [115, 255, 100] )
    
if False:
    # imgP = Image.open()
    tr=100
    #imgPR = imgP.resize( (200,150) )
    img = np.asarray(imgP).copy()
    maskR = img[:,:,1]>150
    maskG = img[:,:,1]<50
    maskB = img[:,:,2]<50
    img[maskR & maskG & maskB] = [0,0,0]
    plt.imshow(img)
    plt.show()

if False:
    r=img[:,:,0];
    r=r>tr

    g=img[:,:,1];
    g=g>tr

    b=img[:,:,2];
    b=b>tr


    fig = plt.figure()
    ax1 = fig.add_subplot(3,1,1)
    ax1.imshow(r, cmap='gray')
    ax1 = fig.add_subplot(3,1,2)
    ax1.imshow(g, cmap='gray')
    ax1 = fig.add_subplot(3,1,3)
    ax1.imshow(b, cmap='gray')

    plt.show()
