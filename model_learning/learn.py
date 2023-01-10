import io
import os
from time import sleep
from typing import Tuple

import numpy as np
import tensorflow as tf
from keras.layers import Conv2D, Dense, Dropout, Flatten, MaxPooling2D
from keras.models import Sequential
from PIL import Image
from sklearn.model_selection import train_test_split

from minio_handler import MinioHandler
from settings import settings


def load_dataset() -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    data = []
    target = []

    for dir_name in os.listdir("dataset"):
        target_val = int(dir_name)
        for img in os.listdir(f"dataset/{dir_name}"):
            with open(f"dataset/{dir_name}/{img}", "rb") as file:
                content = file.read()
                digit = np.asarray(Image.open(io.BytesIO(content))) / 255
            data.append(digit)
            target.append(target_val)

    images = np.array(data).reshape(len(data), 20, 20, 1)
    target = np.array(target) - 1
    return train_test_split(images, target, test_size=0.1)


if __name__ == "__main__":
    sleep(30)
    X_train, X_test, y_train, y_test = load_dataset()

    model = Sequential()
    model.add(Conv2D(20, kernel_size=(3, 3), input_shape=(20, 20, 1)))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Flatten())
    model.add(Dense(200, activation=tf.nn.relu))
    model.add(Dropout(0.3))
    model.add(Dense(9, activation=tf.nn.softmax))
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])

    model.fit(x=X_train, y=y_train, epochs=10)
    model.evaluate(X_test, y_test)
    model.save(settings.MODEL_NAME)  # "ocr.h5"

    minio_client = MinioHandler(settings.MINIO_API_HOST, settings.MINIO_ACCESS_KEY, settings.MINIO_SECRET_KEY)
    minio_client.save_file_in_bucket(settings.MINIO_BUCKET_MODELS, settings.MODEL_NAME, settings.MODEL_NAME)
