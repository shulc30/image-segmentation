# -*- coding: utf-8 -*-
"""Untitled0.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ARqNjBnSvZcFAE8KjOWa7EX-ZA-yzrmD

Вариант 2 Сегментация.
"""

from tensorflow.keras.models import Model 
from tensorflow.keras.layers import Input, Conv2DTranspose, concatenate, Activation, MaxPooling2D, Conv2D, BatchNormalization 
from tensorflow.keras import backend as K 
from tensorflow.keras.optimizers import Adam 
from tensorflow.keras import utils 
from google.colab import files 
import matplotlib.pyplot as plt 
from tensorflow.keras.preprocessing import image 
import numpy as np 
from sklearn.model_selection import train_test_split
import time
import random
import os 
from PIL import Image

from google.colab import drive 
drive.mount('/content/drive')

# Commented out IPython magic to ensure Python compatibility.
# %%time
# import zipfile

zip_file = '/content/drive/MyDrive/вода.zip'
z = zipfile.ZipFile(zip_file, 'r')
z.extractall('/content')

img_width = 176
img_height = 320

num_classes = 2

images_water_v1 = []

cur_time = time.time()
for filname in sorted(os.listdir('/content/water_v2/water_v2/JPEGImages/ADE20K')):
  images_water_v1.append(image.load_img(os.path.join('/content/water_v2/water_v2/JPEGImages/ADE20K', filname), target_size=(img_width, img_height)))
print('Обучающая выборка загружена. Время загрузки: ', time.time() - cur_time, 'c', sep='')

n = 5
fig, axs = plt.subplots(1, n, figsize=(25, 5))
for i in range(n):
  img = random.choice(images_water_v1)
  axs[i].imshow(img)
plt.show()

images_water_segment = []

cur_time = time.time()
for filname in sorted(os.listdir('/content/water_v2/water_v2/Annotations/ADE20K')):
  images_water_segment.append(image.load_img(os.path.join('/content/water_v2/water_v2/Annotations/ADE20K', filname), target_size=(img_width, img_height)))
print('Обучающая выборкаю Время загрузки: ', time.time() - cur_time, 'c', sep='')

n = 5
fig, axs = plt.subplots(1, n, figsize=(25, 5))
for i in range(n):
  img = random.choice(images_water_segment)
  axs[1].imshow(img)
plt.show()

def color2index(color):
    index=0
    if (color[0] + color[1] + color[2]) > 20  : index = 1 # самолет    
    return index

def index2color(index2):
    index = np.argmax(index2)
    color=[]
    if index == 0:
        color = [0, 255, 0]  
    elif index == 1:
        color = [0, 0, 255]  
    return color

def rgbToohe(y, num_classes): 
    y_shape = y.shape 
    y = y.reshape(y.shape[0] * y.shape[1], 3) 
    yt = [] 
    for i in range(len(y)): 
        yt.append(utils.to_categorical(color2index(y[i]), num_classes=num_classes)) 
    yt = np.array(yt) 
    yt = yt.reshape(y_shape[0], y_shape[1], num_classes) 
    return yt

def yt_prep(data, num_classes):
    yTrain = [] 
    for seg in data: 
        y = image.img_to_array(seg) 
        y = rgbToohe(y, num_classes) 
        yTrain.append(y) 
        if len(yTrain) % 100 == 0: 
            print(len(yTrain)) 
    return np.array(yTrain)

xTrain = [] 
for img in images_water_v1: 
    x = image.img_to_array(img) 
    xTrain.append(x) 
xTrain = np.array(xTrain) 
print(xTrain.shape)

cur_time = time.time()
yTrain = yt_prep(images_water_segment, num_classes) 
print('Время обработки: ', round(time.time() - cur_time, 2),'c')

x_train, x_val, y_train, y_val = train_test_split(xTrain, yTrain, test_size = 0.1)

y_train.shape

def dice_coef(y_true, y_pred):
    return (2. * K.sum(y_true * y_pred) + 1.) / (K.sum(y_true) + K.sum(y_pred) + 1.)

def unet(num_classes = 3, input_shape= (88, 120, 3)):
    img_input = Input(input_shape)                                         

    # Block 1
    x = Conv2D(64, (3, 3), padding='same', name='block1_conv1')(img_input) 
    x = BatchNormalization()(x)                                            
    x = Activation('relu')(x)                                              

    x = Conv2D(64, (3, 3), padding='same', name='block1_conv2')(x)         
    x = BatchNormalization()(x)                                            
    block_1_out = Activation('relu')(x)                                    

    x = MaxPooling2D()(block_1_out)                                        

    # Block 2
    x = Conv2D(128, (3, 3), padding='same', name='block2_conv1')(x)        
    x = BatchNormalization()(x)                                            
    x = Activation('relu')(x)                                              

    x = Conv2D(128, (3, 3), padding='same', name='block2_conv2')(x)        
    x = BatchNormalization()(x)                                            
    block_2_out = Activation('relu')(x)                                    

    x = MaxPooling2D()(block_2_out)                                        

    # Block 3
    x = Conv2D(256, (3, 3), padding='same', name='block3_conv1')(x)       
    x = BatchNormalization()(x)                                            
    x = Activation('relu')(x)                                              

    x = Conv2D(256, (3, 3), padding='same', name='block3_conv2')(x)       
    x = BatchNormalization()(x)                                            
    x = Activation('relu')(x)                                              

    x = Conv2D(256, (3, 3), padding='same', name='block3_conv3')(x)        
    x = BatchNormalization()(x)                                           
    block_3_out = Activation('relu')(x)                                 

    x = MaxPooling2D()(block_3_out)                                        

    # Block 4
    x = Conv2D(512, (3, 3), padding='same', name='block4_conv1')(x)        
    x = BatchNormalization()(x)                                            
    x = Activation('relu')(x)                                            

    x = Conv2D(512, (3, 3), padding='same', name='block4_conv2')(x)        
    x = BatchNormalization()(x)                                            
    x = Activation('relu')(x)                                              

    x = Conv2D(512, (3, 3), padding='same', name='block4_conv3')(x)     
    x = BatchNormalization()(x)                                           
    block_4_out = Activation('relu')(x)                                   
    x = block_4_out 

    # UP 2
    x = Conv2DTranspose(256, (2, 2), strides=(2, 2), padding='same')(x)    
    x = BatchNormalization()(x)                                            
    x = Activation('relu')(x)                                              

    x = concatenate([x, block_3_out])                                      
    x = Conv2D(256, (3, 3), padding='same')(x)                             
    x = BatchNormalization()(x)                                           
    x = Activation('relu')(x)                                              

    x = Conv2D(256, (3, 3), padding='same')(x)
    x = BatchNormalization()(x)                                            
    x = Activation('relu')(x)                                             

    # UP 3
    x = Conv2DTranspose(128, (2, 2), strides=(2, 2), padding='same')(x)    
    x = BatchNormalization()(x)                                            
    x = Activation('relu')(x)                                              

    x = concatenate([x, block_2_out])                                      
    x = Conv2D(128, (3, 3), padding='same')(x)                             
    x = BatchNormalization()(x)                                            
    x = Activation('relu')(x)                                              

    x = Conv2D(128, (3, 3), padding='same')(x) 
    x = BatchNormalization()(x) 
    x = Activation('relu')(x) 

    # UP 4
    x = Conv2DTranspose(64, (2, 2), strides=(2, 2), padding='same')(x) 
    x = BatchNormalization()(x) 
    x = Activation('relu')(x) 

    x = concatenate([x, block_1_out])  
    x = Conv2D(64, (3, 3), padding='same')(x) 
    x = BatchNormalization()(x) 
    x = Activation('relu')(x) 

    x = Conv2D(64, (3, 3), padding='same')(x) 
    x = BatchNormalization()(x) 
    x = Activation('relu')(x) 

    x = Conv2D(num_classes, (3, 3), activation='softmax', padding='same')(x)  

    model = Model(img_input, x)

    
    model.compile(optimizer=Adam(),
                  loss='categorical_crossentropy',
                  metrics=[dice_coef])
    
    return model

modelL = unet(num_classes, (img_width, img_height, 3)) 
modelL.summary()

modelAir = unet(2, (img_width, img_height,3))
history = modelAir.fit(x_train, y_train, epochs=50, batch_size=10, validation_data = (x_val, y_val)) # Обучаем модель на выборке по трем классам

def plot_history(history):
  plt.figure(figsize=(20,5))
  plt.subplot(1,3,1)
  plt.plot(history.history['loss'], label='Ошибка на обучающем наборе')
  plt.plot(history.history['val_loss'], label='Ошибка на проверочном наборе')
  plt.xlabel('Эпоха обучения')
  plt.ylabel('Ошибка')
  plt.title('График ошибки')
  plt.grid(axis='y', linestyle = '--')
  plt.legend()


  plt.subplot(1,3,2)
  plt.plot(history.history['dice_coef'], label='dice_coef на обучающем наборе')
  plt.plot(history.history['val_dice_coef'], label='dice_coef на проверочном наборе')
  plt.xlabel('Эпоха обучения')
  plt.ylabel('dice_coef')
  plt.title('График dice_coef')
  plt.grid(axis='y', linestyle = '--')
  plt.legend()
  plt.show()

plot_history(history)

modelAir.save_weights('/content/drive/MyDrive/тестовое задание/сегмент.h5')

modelAir = unet(2, (img_width, img_height,3))
modelAir.load_weights('/content/drive/MyDrive/тестовое задание/сегмент.h5')

count = 5
n_classes = 2
indexes = np.random.randint(0, len(x_val), count)
fig, axs = plt.subplots(2, count, figsize=(25, 5)) 
for i,idx in enumerate(indexes): 
    predict = np.array(modelAir.predict(x_val[idx].reshape(1, img_width, img_height, 3))) 
    pr = predict[0] 
    pr1 = [] 
    pr = pr.reshape(-1, n_classes) 
    for k in range(len(pr)): 
        pr1.append(index2color(pr[k])) 
    pr1 = np.array(pr1) 
    pr1 = pr1.reshape(img_width, img_height,3) 
    img = Image.fromarray(pr1.astype('uint8')) 
    axs[0,i].imshow(img.convert('RGBA')) 
    axs[1,i].imshow(Image.fromarray(x_val[idx].astype('uint8')))         
plt.show()

seg = Image.fromarray(pr1.astype('uint8')).convert('RGBA')
plt.imshow(seg)

plt.imshow(Image.fromarray(x_val[idx].astype('uint8')))

mask = np.array(seg)
mask[mask[:,:,0] <= 10] = [0, 0, 0, 0]
mask[mask[:,:,0] > 10] = [0, 150, 0, 150]

img2 = Image.fromarray(x_val[idx].astype('uint8'))
img = Image.fromarray(mask).convert('RGBA')
img2.paste(img, (0, 0),img)
plt.imshow(img2)