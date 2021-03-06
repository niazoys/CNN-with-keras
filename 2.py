from __future__ import print_function

# The two folloing lines allow to reduce tensorflow verbosity
import os

os.environ[
    'TF_CPP_MIN_LOG_LEVEL'] = '1'  # '0' for DEBUG=all [default], '1' to filter INFO msgs, '2' to filter WARNING
# msgs, '3' to filter all msgs

import tensorflow as tf
import tensorflow.keras
from tensorflow.keras.datasets import cifar10
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Conv2D, MaxPooling2D, Flatten
from tensorflow.keras.optimizers import RMSprop, SGD, Adam
from sklearn.model_selection import train_test_split


import matplotlib.pyplot as plt
import numpy as np

print('tensorflow:', tf.__version__)
print('keras:', tensorflow.keras.__version__)


# load and prepocess data
def load_and_process_data():
    """
    This model loads the MNIST dataset from the keras api

    """
    num_classes = 10

    # load dataset
    (x_train, y_train), (x_test, y_test) = cifar10.load_data()

    num_classes = 10
    print('y_train.shape=', y_train.shape)
    print('y_test.shape=', y_test.shape)

    # Convert class vectors to binary class matrices ("one hot encoding")
    ## Doc : https://keras.io/utils/#to_categorical
    y_train = tensorflow.keras.utils.to_categorical(y_train)
    y_test = tensorflow.keras.utils.to_categorical(y_test)

    # Convert to float
    x_train = x_train.astype('float32')
    x_test = x_test.astype('float32')
    print('x_train.shape=', x_train.shape)
    print('x_test.shape=', x_test.shape)

    # Normalize inputs from [0; 255] to [0; 1]
    x_train = x_train / 255
    x_test = x_test / 255
    x_train, x_val, y_train, y_val = train_test_split(x_train, y_train, test_size=0.2, train_size=0.8)

    return x_train, y_train, x_test, y_test, x_val, y_val


# draw the training statistics
def plot_training_metrics(choice, history):
    # directory to save the plots
    path = os.path.join('results/cifar10', str(choice))
    if not os.path.exists(path):
        os.makedirs(path)
    # plotting the metrics
    fig = plt.figure(1)
    plt.plot(history.history['accuracy'])
    plt.plot(history.history['val_accuracy'])
    plt.title('model accuracy')
    plt.ylabel('accuracy')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='lower right')
    plt.savefig('{}/cifar-accuracy-model-{}.png'.format(path, choice), format='png')

    plt.figure(2)
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'val'], loc='upper right')
    plt.tight_layout()
    plt.savefig('{}/cifar-loss-model-{}.png'.format(path, choice), format='png')


# First baseline model
def Model1():
    """
     First baseline model ( simpler one)
    """
    model = Sequential()
    model.add(Conv2D(filters=32, kernel_size=(3, 3), activation='relu', kernel_initializer='he_uniform',
                     input_shape=(32, 32, 3)))
    model.add(MaxPooling2D(2, 2))
    model.add(Flatten())
    model.add(Dense(100, activation='relu', kernel_initializer='he_uniform'))
    model.add(Dense(10, activation='softmax'))
    optm = SGD(lr=0.001, momentum=0.9)
    model.compile(optimizer=optm, loss='categorical_crossentropy', metrics=['accuracy'])

    return model


# Second model
def Model2():
    """
    Second model with more convolutional layers and
    without any regularaization
    """
    model = Sequential()
    model.add(Conv2D(32, (3, 3), activation='relu', kernel_initializer='he_uniform', input_shape=(32, 32, 3)))
    model.add(Conv2D(32, (3, 3), activation='relu', kernel_initializer='he_uniform'))
    model.add(MaxPooling2D((2, 2)))

    model.add(Conv2D(64, (3, 3), activation='relu', kernel_initializer='he_uniform'))
    model.add(Conv2D(64, (3, 3), activation='relu', kernel_initializer='he_uniform'))
    model.add(MaxPooling2D((2, 2)))

    model.add(Flatten())
    model.add(Dense(128, activation='relu', kernel_initializer='he_uniform'))
    model.add(Dense(10, activation='softmax'))

    # compile model
    opt = SGD(lr=0.001, momentum=0.9)
    model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])
    return model


# Third model
def Model3():
    """
     This is quite interesting
    """

    model = Sequential()
    model.add(Conv2D(32, (3, 3), activation='relu', kernel_initializer='he_uniform', input_shape=(32, 32, 3)))
    model.add(Conv2D(32, (3, 3), activation='relu', kernel_initializer='he_uniform'))
    model.add(MaxPooling2D((2, 2)))

    model.add(Conv2D(64, (3, 3), activation='relu', kernel_initializer='he_uniform'))
    model.add(Conv2D(64, (3, 3), activation='relu', kernel_initializer='he_uniform'))
    model.add(MaxPooling2D((2, 2)))
    model.add(Dropout(0.2))

    model.add(Flatten())
    model.add(Dense(128, activation='relu', kernel_initializer='he_uniform'))
    model.add(Dropout(0.2))
    model.add(Dense(10, activation='softmax'))

    # compile model
    opt = SGD(lr=0.001, momentum=0.9)
    model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])
    return model


# save model
def save_model(model, model_name):
    # saving the model
    save_dir = "results/cifar10/"+str(model_name)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    file_name = str(model_name) + '.h5'
    model_path = os.path.join(save_dir, file_name)
    model.save(model_path)
    print('Saved trained model at %s ' % model_path)


# Selects specific model
def select_model(choice):
    """
    Creates model instance according to
    choice
    """
    model = None
    if choice == 1:
        model = Model1()
    elif choice == 2:
        model = Model2()
    elif choice == 3:
        model = Model3()

    return model


# Function to Run the model
def run_program():
    # load the dataset
    x_train, y_train, x_test, y_test, x_val, y_val = load_and_process_data()

    # define model
    choice = 3 # 1, 2, or 3
    model = select_model(choice)
    model.summary()

    # train model
    # Hyperparameters
    batch_size = 128
    epochs = 20
    hist = model.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, validation_data=(x_val, y_val))

    # display training details
    plot_training_metrics(choice, hist)

    # evaluate model
    loss, acc = model.evaluate(x_test, y_test, verbose=2)
    print("Test Loss: ", loss)
    print("Test Accuracy", acc)

    # save model
    save_model(model, choice)


if __name__ == "__main__":
    # ran everthing from here
    run_program()

    # show plots
    plt.show()
