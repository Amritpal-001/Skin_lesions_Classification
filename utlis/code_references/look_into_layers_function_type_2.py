import tensorflow as tf
import numpy as np
import random
from tensorflow.keras.preprocessing.image import img_to_array, load_img
import matplotlib.pyplot as plt
import time
import os

physical_devices = tf.config.experimental.list_physical_devices('GPU')
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)

model = tf.keras.models.load_model(
    '/home/amritpal/PycharmProjects/100-days-of-code/100_days_of_code/Skin_disease_working_version_minimal'
    '/saved_model/model_name_RGB_224__0.55__1.61__12-3_2:59')
image_directory = 'img.jpg'

model_save_path = 'model_layers/' + str(time.time())
os.mkdir(model_save_path)


def Look_into_filter(model, image_directory):
    # Let's define a new Model that will take an image as input, and will output
    # intermediate representations for all layers in the previous model after
    # the first.
    successive_outputs = [layer.output for layer in model.layers[1:]]

    # visualization_model = Model(img_input, successive_outputs)
    visualization_model = tf.keras.models.Model(inputs=model.input, outputs=successive_outputs)

    '''# Let's pick a random input image of a normal or pneumonia from the training set.
    normal_img_files = [os.path.join(train_normal_dir, f) for f in train_normal_fnames]
    pneumonia_img_files = [os.path.join(train_pneumonia_dir, f) for f in train_pneumonia_fnames]

    img_path = random.choice(normal_img_files + pneumonia_img_files)'''

    img = load_img(image_directory, target_size=(224, 224))  # this is a PIL image
    x = img_to_array(img)  # Numpy array with shape (150, 150, 3)
    x = x.reshape((1,) + x.shape)  # Numpy array with shape (1, 150, 150, 3)
    x /= 255.0  # Rescale by 1/255

    # Let's run our image through our network, thus obtaining all intermediate representations for this image.
    successive_feature_maps = visualization_model.predict(x)
    layer_names = [layer.name for layer in model.layers]  # names of the layers, to make our plot

    # Now let's display our representations
    for layer_name, feature_map in zip(layer_names, successive_feature_maps):
        if len(feature_map.shape) == 4:
            # Just do this for the conv / maxpool layers, not the fully-connected layers
            n_features = feature_map.shape[-1]  # number of features in the feature map
            size = feature_map.shape[1]  # feature map shape (1, size, size, n_features)

            # We will tile our images in this matrix
            display_grid = np.zeros((size, size * n_features))

            # Postprocess the feature to be visually palatable
            for i in range(n_features):
                x = feature_map[0, :, :, i]
                x -= x.mean()
                x /= x.std()
                x *= 64
                x += 128
                x = np.clip(x, 0, 255).astype('uint8')
                display_grid[:, i * size: (i + 1) * size] = x
            # Tile each filter into a horizontal grid

            # Display the grid
            scale = 20. / n_features
            plt.figure(figsize=(scale * n_features, scale))
            plt.title(layer_name)
            plt.grid(False)
            plt.imshow(display_grid, aspect='auto', cmap='viridis')
            plt.savefig(model_save_path + '/' + layer_name + str(time.time()) + '.png')


Look_into_filter(model, image_directory)
