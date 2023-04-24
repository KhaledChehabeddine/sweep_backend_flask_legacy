"""Summary: AWS S3 Operations

A client that contains operations related to AWS S3
"""

import os
import base64
from io import BytesIO
import boto3
from botocore.client import BaseClient
from botocore.exceptions import ClientError
from flask import jsonify, Response

AWS_S3_CLIENT = None


def get_aws_s3_client() -> BaseClient:
    """
    :return: AWS S3 client
    """
    global AWS_S3_CLIENT
    if AWS_S3_CLIENT is None:
        AWS_S3_CLIENT = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
    return AWS_S3_CLIENT


def delete_from_aws_s3(file_path: str) -> Response:
    """
    :param file_path: The path of the file
    :return: Response object with a message describing if the file was deleted and the status code
    """
    try:
        get_aws_s3_client().delete_object(Bucket=os.getenv('AWS_S3_BUCKET'), Key=file_path)
    except ClientError:
        return jsonify(
            message='File not deleted from the AWS S3 bucket.',
            status=500
        )
    return jsonify(
        message='File deleted from the AWS S3 bucket.',
        status=200
    )


def upload_to_aws_s3(file_data: str, file_path: str) -> Response:
    """
    :param file_data: The byte data of the file
    :param file_path: The path of the file
    :return: Response object with a message describing if the file was uploaded and the status code
    """
    try:
        file_bytes = base64.b64decode(file_data)
        get_aws_s3_client().upload_fileobj(
            BytesIO(file_bytes),
            os.getenv('AWS_S3_BUCKET'),
            file_path,
            ExtraArgs={
                'ContentType': 'image/' + 'svg+xml' if file_path.endswith('.svg') else 'image/jpeg',
            }
        )
    except ClientError:
        return jsonify(
            message='File not uploaded into the AWS S3 bucket.',
            status=500
        )
    return jsonify(
        message='File uploaded into the AWS S3 bucket.',
        status=200
    )
