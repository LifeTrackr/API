from typing import Union

import boto3
from fastapi import UploadFile


def validate_image(contents: Union[bytes, str], file: UploadFile):
    if len(contents) <= 50 * 1024:  # TODO: check database for max file size, even per user
        if file.content_type.split("/") == ['image', 'png']:
            return True
        else:
            return "Error: file is not an image"
    else:
        return "Error: file above 50 Kb"


s3 = boto3.resource('s3')
bucket_name = 'lifetrackr-bucket1'


def upload_image(image_base64: bytes, companion_id: int) -> str:  #
    obj_name = f"id{companion_id}.png"
    obj = s3.Object(bucket_name, obj_name)
    obj.put(Body=image_base64)
    return obj_name
