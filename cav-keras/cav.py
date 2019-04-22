import numpy as np
import keras
from keras.datasets import cifar10, cifar100
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D
import os

# Set parameters
batch_size = 32
num_classes = 2
epochs = 5
num_predictions = 20
model_name = 'keras_cifar10_trained_model.h5'

# The data, split between train and test sets:
(x_train, y_train), (x_test, y_test) = cifar10.load_data()

# Keep airplanes (0) and ships (8) from CIFAR-10
airplanes = y_train == [0]
ships = y_train == [8]
indices = airplanes + ships
indx_to_use = [i for i, x in enumerate(indices) if x]

x_train = x_train[indx_to_use]
y_train = y_train[indx_to_use]

airplanes = y_test == [0]
ships = y_test == [8]
indices = airplanes + ships
indx_to_use = [i for i, x in enumerate(indices) if x]

x_test = x_test[indx_to_use]
y_test = y_test[indx_to_use]

# keep cloud (50) and sea (54) from CIFAR-100
(x_train_concept, y_train_concept), (x_test_concept, y_test_concept) = cifar100.load_data()

other = y_train_concept == [47]
concept = y_train_concept == [54]
indices = other + concept
indx_to_use = [i for i, x in enumerate(indices) if x]

x_train_concept = x_train_concept[indx_to_use]
y_train_concept = y_train_concept[indx_to_use]

other = y_test_concept == [47]  # 50 is cloud, 54 is sea
concept = y_test_concept == [54]
indices = other + concept
indx_to_use = [i for i, x in enumerate(indices) if x]

x_test_concept = x_test_concept[indx_to_use]
y_test_concept = y_test_concept[indx_to_use]

# Make sure classes are 0,1
y_train = np.where(y_train == 8, 1, y_train)
y_test = np.where(y_test == 8, 1, y_test)

# Make sure classes are 0,1
y_train_concept = np.where(y_train_concept == 47, 0, y_train_concept)
y_test_concept = np.where(y_test_concept == 47, 0, y_test_concept)
y_train_concept = np.where(y_train_concept == 54, 1, y_train_concept)
y_test_concept = np.where(y_test_concept == 54, 1, y_test_concept)

# Convert class vectors to binary class matrices.
y_train = keras.utils.to_categorical(y_train, num_classes)
y_test = keras.utils.to_categorical(y_test, num_classes)

y_train_concept = keras.utils.to_categorical(y_train_concept, num_classes)
y_test_concept = keras.utils.to_categorical(y_test_concept, num_classes)

model = Sequential()
model.add(Conv2D(32, (3, 3), padding='same',
                 input_shape=x_train.shape[1:]))
model.add(Activation('relu'))
model.add(Conv2D(32, (3, 3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Conv2D(64, (3, 3), padding='same'))
model.add(Activation('relu'))
model.add(Conv2D(64, (3, 3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Flatten())
model.add(Dense(512))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(num_classes))
model.add(Activation('sigmoid'))

# initiate optimizer
opt = keras.optimizers.Adam(lr=0.001)

# train the model
model.compile(loss='categorical_crossentropy', optimizer=opt, metrics=['accuracy'])

x_train = x_train.astype('float32')
x_test = x_test.astype('float32')
x_train /= 255
x_test /= 255

model.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, validation_data=(x_test, y_test), shuffle=True)

model2 = Sequential()
model2.add(Conv2D(32, (3, 3), padding='same',
                 input_shape=x_train.shape[1:], weights = model.layers[0].get_weights()))
model2.add(Activation('relu'))
model2.add(Conv2D(32, (3, 3), weights = model.layers[2].get_weights()))
model2.add(Activation('relu'))
model2.add(MaxPooling2D(pool_size=(2, 2)))
model2.add(Dropout(0.25))

model2.add(Conv2D(64, (3, 3), padding='same', weights = model.layers[6].get_weights()))
model2.add(Activation('relu'))
model2.add(Conv2D(64, (3, 3), weights = model.layers[8].get_weights()))
model2.add(Activation('relu'))
model2.add(MaxPooling2D(pool_size=(2, 2)))
model2.add(Flatten())
test = model2.predict(x_train_concept)

classifier = Sequential()
classifier.add(Dense(2, input_shape=test.shape[1:], activation='sigmoid', use_bias=False))
classifier.compile(loss='binary_crossentropy', optimizer=opt, metrics=['accuracy'])
classifier.fit(test, y_train_concept, batch_size=32, epochs=20, shuffle=True)

model_h = Sequential()
model_h.add(Dense(512, input_shape=test.shape[1:], weights = model.layers[13].get_weights()))
model_h.add(Activation('relu'))
model_h.add(Dropout(0.5))
model_h.add(Dense(num_classes, weights = model.layers[16].get_weights()))
model_h.add(Activation('sigmoid'))

item = x_train[0].reshape((1, 32, 32, 3))
l_pred = model2.predict(item)
l_pred[0]

outputTensor = model_h.output 
listOfVariableTensors = model_h.trainable_weights
from keras import backend as k
gradients = k.gradients(outputTensor, listOfVariableTensors)
import tensorflow as tf
sess = tf.InteractiveSession()
sess.run(tf.initialize_all_variables())
evaluated_gradients = sess.run(gradients,feed_dict={model_h.input:l_pred})

