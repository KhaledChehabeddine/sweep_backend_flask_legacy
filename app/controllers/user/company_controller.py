"""Summary: Company Controller

A controller that assigns a child blueprint to sweep_api_v1 with routes for functions to create, read, update, and
delete companies from the database
"""
import json
from datetime import datetime
from typing import Any
from bson import ObjectId
from elasticsearch import NotFoundError
from flask import Blueprint, Response, jsonify, request
from pymongo import ASCENDING, errors
from app.aws.aws_s3_client import upload_images_to_aws_s3, delete_images_from_aws_s3
from app.controllers.user.worker_controller import read_workers_by_company_id, convert_object_ids
from app.database.database import get_database
from app.elasticsearch.elasticsearch_client import get_elasticsearch_client
from app.elasticsearch.elasticsearch_search import search_companies
from app.functions.create_mongodb_indices import create_service_provider_indexes
from app.functions.create_object_metadata import create_service_provider_metadata
from app.functions.update_object_metadata import update_service_provider_metadata
from app.models.user.company import Company

raw_company_api_v1 = Blueprint('company_api_v1', __name__, url_prefix='/company')
company_collection = get_database()['companies']

company_collection.create_index([('name', ASCENDING)], unique=True)
create_service_provider_indexes(service_provider_collection=company_collection)
elasticsearch_client = get_elasticsearch_client()
if not elasticsearch_client.client.indices.exists(index='companies'):
    elasticsearch_client.create_index(index_name='companies', body={})


class CustomJSONEncoder(json.JSONEncoder):
    """
    :return: A JSON encoder that converts datetime objects to isoformat and ObjectId objects to strings
    """
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)


def _configure_company(company_document: dict) -> Company:
    """
    :param company_document: A company document
    :return: A company object with configured ids
    """
    company = Company(company_document=company_document)

    for category_document in company.service_provider['categories']:
        category_document['_id'] = str(category_document['_id'])

    for review_document in company.service_provider['reviews']:
        review_document['_id'] = str(review_document['_id'])

    return company


def _configure_company_document(company_document: dict, company_images: list[tuple[str, Any, Any]]) -> dict:
    """
    :param company_document: A company document
    :param company_images: A list of tuples of each image info in the format [type, data, path]
    :return: A company document with a configured metadata
    """
    company_document['metadata'] = upload_images_to_aws_s3(
        object_metadata_document=company_document['metadata'],
        object_images=company_images
    ).json['data']
    company_document['metadata']['total_employees'] = (
        0 if company_document['_id'] == "-1"
        else len(read_workers_by_company_id(company_id=company_document['_id']).json['data'])
    )
    company_document['metadata']['total_service_categories'] = len(company_document['service_category_ids'])

    return company_document


@raw_company_api_v1.route('/create', methods=['POST'])
def create_company() -> Response:
    """
    :return: Response object with a message describing if the company was created (if yes: add company id) and the
    status code.
    """
    company_document = request.json

    company_images = [
        ('banner_', company_document['banner_image'], company_document['banner_image_path']),
        ('logo_', company_document['logo_image'], company_document['logo_image_path'])
    ]
    company_document = _configure_company_document(company_document=company_document, company_images=company_images)

    company_document['service_provider'] = \
        create_service_provider_metadata(service_provider_document=company_document['service_provider'])

    company = Company(company_document=company_document)

    try:
        if '_id' in company_document:
            del company_document['_id']

        company_id = str(company_collection.insert_one(company.database_dict()).inserted_id)

        if '_id' in company_document:
            del company_document['_id']

        json_data = json.dumps(company_document, cls=CustomJSONEncoder)

        elasticsearch_client.client.index(index='companies', id=company_id, body=json_data)
    except errors.OperationFailure:
        return jsonify(
            message='Company not added to the database and Elasticsearch.',
            status=500
        )
    return jsonify(
        data=company_id,
        message='Company added to the database and indexed in Elasticsearch.',
        status=200
    )


@raw_company_api_v1.route('/login/username/<string:username>/password/<string:password>', methods=['POST'])
def login_company(username: str, password: str) -> Response:
    """
    :return: Response object with a message describing if the customer was logged in and the status code
    """
    company = company_collection.find_one({'user.username': username})
    if company:
        company = Company(company_document=company)
        if company.service_provider.user.password == password:
            return jsonify(
                data=company.__dict__,
                message='Company logged in.',
                status=200
            )
    return jsonify(
        message='Company not logged in.',
        status=404
    )


@raw_company_api_v1.route('/indexCompanies', methods=['POST'])
def index_workers():
    """
    :return: Response object with a message describing if the companies were indexed and the status code.
    """
    try:
        companies = company_collection.find()

        for company_document in companies:
            company_id = str(company_document['_id'])
            if not elasticsearch_client.client.exists(index='companies', id=company_id):
                json_data = json.dumps(company_document, cls=CustomJSONEncoder)
                elasticsearch_client.client.index(index='companies', id=company_id, body=json_data)

        return jsonify(message='Companies indexed in Elasticsearch', status=200)
    except Exception as e:
        return jsonify(message='Failed to index companies', error=str(e), status=500)


@raw_company_api_v1.route('/read/id/<string:_id>', methods=['GET'])
def read_company_by_id(_id: str) -> Response:
    """
    :param _id: Company's id
    :return: Response object with a message describing if the company was found and the status code
    """
    company_document = company_collection.find_one({'_id': ObjectId(_id)})
    if company_document:
        company = _configure_company(company_document=company_document)
        return jsonify(
            data=company.__dict__,
            message='Company found in the database using the id.',
            status=200
        )
    return jsonify(
        message='Company not found in the database using the id.',
        status=500
    )


@raw_company_api_v1.route('/read/service_category_id/<string:service_category_id>', methods=['GET'])
def read_companies_by_service_category_id(service_category_id: str) -> Response:
    """
    :param service_category_id: Service category's id
    :return: Response object with a message describing if the company was found and the status code
    """
    company_documents = company_collection.find({
        'service_category_ids': {
            '$in': [service_category_id]
        }
    })
    if company_documents:
        companies = []
        for company_document in company_documents:
            company = _configure_company(company_document=company_document)
            companies.append(company.__dict__)
        if companies:
            return jsonify(
                data=companies,
                message='Companies found in the database using the service category id.',
                status=200
            )
    return jsonify(
        message='No company found in the database using the service category id.',
        status=500
    )


@raw_company_api_v1.route('/read/all', methods=['GET'])
def read_companies() -> Response:
    """
    :return: Response object with a message describing if all the companies were found (if yes: add companies) and the
    status code
    """
    companies = []
    company_documents = company_collection.find()
    if company_documents:
        for company_document in company_documents:
            company = _configure_company(company_document=company_document)
            companies.append(company.__dict__)
        if companies:
            return jsonify(
                data=companies,
                message='All companies found in the database.',
                status=200
            )
    return jsonify(
        message='No company found in the database.',
        status=500
    )


@raw_company_api_v1.route('/search/<string:query>', methods=['GET'])
def search_companies_endpoint(query: str) -> Response:
    """
    :param query: The search query.
    :return: A response object containing the search results as a list of serialized companies.
    """
    if query:
        companies = search_companies(query)

        serialized_companies = []
        for company in companies:
            serialized_company = company.__dict__
            if 'id' in serialized_company:
                serialized_company['_id'] = str(serialized_company.pop('id'))  # Convert id to _id
            serialized_companies.append(serialized_company)

        serialized_companies = convert_object_ids(serialized_companies)

        return jsonify(data=serialized_companies, message='Search results', status=200)
    else:
        return jsonify(message='No query parameter provided', status=400)


@raw_company_api_v1.route('/update/id/<string:_id>', methods=['PUT'])
def update_company_by_id(_id: str) -> Response:
    """
    :param _id: Company's id
    :return: Response object with a message describing if the company was updated and the status code
    """
    company_document = request.json

    company_images = [
        ('banner_', company_document['banner_image'], company_document['banner_image_path']),
        ('logo_', company_document['logo_image'], company_document['logo_image_path'])
    ]
    company_document = _configure_company_document(company_document=company_document, company_images=company_images)

    company_document['service_provider'] = update_service_provider_metadata(service_provider_document=
                                                                            company_document['service_provider'])

    company = Company(company_document=company_document)
    result = company_collection.update_one(
        {'_id': ObjectId(_id)},
        {'$set': company.database_dict()}
    )
    if result.modified_count == 1:
        # Update the company document in Elasticsearch
        try:
            if '_id' in company_document:
                del company_document['_id']

            json_data = json.dumps(company_document, cls=CustomJSONEncoder)

            elasticsearch_client.client.update(
                index='companies',
                id=_id,
                body={'doc': json.loads(json_data)}  # Convert JSON string to dictionary
            )
            return jsonify(
                message='Company updated in the database and Elasticsearch using the id.',
                status=200
            )
        except NotFoundError:
            return jsonify(
                message='Company not found in Elasticsearch.',
                status=500
            )
    return jsonify(
        message='Company not updated in the database using the id.',
        status=500
    )


@raw_company_api_v1.route('/delete/id/<string:_id>', methods=['DELETE'])
def delete_company_by_id(_id: str) -> Response:
    """
    :param _id: Company's id
    :return: Response object with a message describing if the company was deleted and the status code
    """
    company_document = company_collection.find_one({'_id': ObjectId(_id)})

    if company_document is None:
        return jsonify(
            message='Company not found in the database.',
            status=404
        )

    image_paths = [company_document['banner_image_path'], company_document['logo_image_path']]
    delete_images_from_aws_s3(image_paths=image_paths)

    result = company_collection.delete_one({'_id': ObjectId(_id)})
    if result.deleted_count == 1:
        try:
            elasticsearch_client.client.delete(index='companies', id=_id)
            return jsonify(
                message='Company deleted from the database and Elasticsearch using the id.',
                status=200
            )
        except NotFoundError:
            return jsonify(
                message='Company not found in Elasticsearch.',
                status=500
            )
    return jsonify(
        message='Company not deleted from the database and Elasticsearch using the id.',
        status=500
    )


@raw_company_api_v1.route('/delete/all/', methods=['DELETE'])
def delete_all_companies():
    """
    :return: response object with a message describing if the workers were deleted and the status code
    """
    try:
        company_collection.delete_many({})

        elasticsearch_client.delete_index(index_name='companies')

        return jsonify(message='All workers deleted from MongoDB and Elasticsearch', status=200)
    except Exception as e:
        return jsonify(message='Failed to delete workers', error=str(e), status=500)


company_api_v1 = raw_company_api_v1
