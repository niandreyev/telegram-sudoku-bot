from json import dumps

import numpy as np
import requests
from kafka_handler import KafkaHandler
from keras.models import load_model
from minio_handler import MinioHandler

from cropper import ImageParser


class SudokuImagePipeline:
    def __init__(
        self,
        minio_host: str,
        minio_access_key: str,
        minio_secret_key: str,
        image_bucket_name: str,
        model_bucket_name: str,
        model_object_name: str,
        model_file_path: str,
        kafka_bootstrap: str,
        kafka_sudoku_topic: str,
        api_endpoint: str,
    ) -> None:
        self.image_bucket_name = image_bucket_name
        self.minio_client = MinioHandler(minio_host, minio_access_key, minio_secret_key)
        self.minio_client.load_file_to_path(model_bucket_name, model_object_name, model_file_path)
        self.kafka_client = KafkaHandler(kafka_bootstrap, kafka_sudoku_topic)
        self.model = load_model(model_file_path)
        self.api_endpoint = api_endpoint

    def parse_image(self, chat_id: int, file_minio_path: str, **__):
        image = self.minio_client.load_file_in_memory(self.image_bucket_name, file_minio_path)
        parser = ImageParser(image)

        try:
            parser.do_parse()
        except Exception as err:
            print(err)
            requests.get(self.api_endpoint, params={"chat_id": chat_id, "text": "Sudoku not found"})
        else:
            sudoku = []
            for row_of_cells, row_of_mask in zip(parser.cells, parser.digit_mask):
                sudoku_row = []
                for cell, flag in zip(row_of_cells, row_of_mask):
                    if flag:
                        resized = parser.resize_and_norm_image(cell).reshape(1, 20, 20, 1)
                        predicted = np.argmax(self.model.predict(resized, verbose=0)) + 1
                        sudoku_row.append(int(predicted))
                    else:
                        sudoku_row.append(0)
                sudoku.append(sudoku_row)

            kafka_message = {
                "chat_id": chat_id,
                "file_minio_name": file_minio_path.rsplit(".", maxsplit=1)[0],
                "sudoku": sudoku,
            }
            self.kafka_client.send_message_to_topic(dumps(kafka_message))
