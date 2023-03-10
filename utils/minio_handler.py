from typing import Sequence

from minio import Minio


class MinioHandler:
    def __init__(self, host: str, access_key: str, secret_key: str) -> None:
        self.client = Minio(host, access_key=access_key, secret_key=secret_key, secure=False)

    def create_bucket_if_not_exists(self, bucket_name):
        bucket_exists = self.client.bucket_exists(bucket_name)
        if not bucket_exists:
            self.client.make_bucket(bucket_name)

    def save_file_in_bucket(self, bucket_name: str, object_name: str, file_path: str):
        self.create_bucket_if_not_exists(bucket_name)
        self.client.fput_object(
            bucket_name=bucket_name,
            object_name=object_name,
            file_path=file_path,
            content_type="keras-model",
        )

    def save_in_bucket(self, bucket_name: str, object_name: str, data: Sequence[bytes]):
        self.create_bucket_if_not_exists(bucket_name)
        self.client.put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            data=data,
            length=data.getbuffer().nbytes,
            content_type="image",
        )

    def load_file_to_path(self, bucket_name: str, object_name: str, file_path: str):
        self.client.fget_object(
            bucket_name=bucket_name,
            object_name=object_name,
            file_path=file_path,
        )

    def load_file_in_memory(self, bucket_name: str, object_name: str):
        return self.client.get_object(
            bucket_name=bucket_name,
            object_name=object_name,
        ).data
