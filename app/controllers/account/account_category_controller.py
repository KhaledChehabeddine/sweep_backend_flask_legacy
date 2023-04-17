"""Summary: Account Category Controller CRUD Operations

A controller that assigns a child blueprint to sweep_api_v1 with routes for functions to create, read, update, and
delete account categories from the database
"""

import pymongo
from bson import ObjectId
from flask import Blueprint, Response, jsonify, request
from pymongo.errors import OperationFailure
from app.database.database import get_database
from app.models.account.account_category import AccountCategory
from app.routes.blueprints import sweep_api_v1

account_category_api_v1 = Blueprint('account_category_api_v1', __name__, url_prefix='/account_category')
account_category_collection = get_database()['account_categories']

account_category_collection.create_index([('name', pymongo.ASCENDING)], unique=True)


@account_category_api_v1.route('/create', methods=['POST'])
def create_account_category() -> Response:
    """
    :return: Response object with a message describing if the account category was created and the status code
    """
    account_category_document = request.json
    account_category = AccountCategory(account_category_document=account_category_document)
    try:
        account_category_collection.insert_one(account_category.database_dict())
    except OperationFailure:
        return jsonify(
            message='Account category not added to the database.',
            status=500
        )
    return jsonify(
        message='Account category added to the database.',
        status=200
    )


@account_category_api_v1.route('/read/id/<string:_id>', methods=['GET'])
def read_account_category_by_id(_id: str) -> Response:
    """
    :param _id: Account category's id
    :return: Response object with a message describing if the account category was found (if yes: add account category)
    and the status code
    """
    account_category_document = account_category_collection.find_one({'_id': ObjectId(_id)})
    if account_category_document:
        account_category = AccountCategory(account_category_document=account_category_document)
        return jsonify(
            data=account_category.__dict__,
            message='Account category found in the database using the id.',
            status=200
        )
    return jsonify(
        message='Account category not found in the database using the id.',
        status=500
    )


@account_category_api_v1.route('/read', methods=['GET'])
def read_account_categories() -> Response:
    """
    :return: Response object with a message describing if all the account categories were found (if yes: add account
    categories) and the status code
    """
    account_categories = []
    account_category_documents = account_category_collection.find()
    if account_category_documents:
        for account_category_document in account_category_documents:
            account_category = AccountCategory(account_category_document=account_category_document)
            account_categories.append(account_category.__dict__)
        return jsonify(
            data=account_categories,
            message='Account categories found in the database.',
            status=200
        )
    return jsonify(
        message='No account category found in the database.',
        status=500
    )


@account_category_api_v1.route('/update/id/<string:_id>', methods=['PUT'])
def update_account_category_by_id(_id: str) -> Response:
    """
    :param _id: Account category's id
    :return: Response object with a message describing if the account category was found (if yes: update account
    category) and the status code
    """
    account_category_document = request.json
    account_category = AccountCategory(account_category_document=account_category_document)
    result = account_category_collection.update_one(
        {'_id': ObjectId(_id)},
        {'$set': account_category.__dict__}
    )
    if result.modified_count == 1:
        return jsonify(
            message='Account category updated in the database using the id.',
            status=200
        )
    return jsonify(
        message='Account category not updated in the database using the id.',
        status=500
    )


@account_category_api_v1.route('/delete/id/<string:_id>', methods=['DELETE'])
def delete_account_category_by_id(_id: str) -> Response:
    """
    :param _id: Account category's id
    :return: Response object with a message describing if the account category was found (if yes: delete account
    category) and the status code
    """
    result = account_category_collection.delete_one({'_id': ObjectId(_id)})
    if result.deleted_count == 1:
        return jsonify(
            message='Account category deleted from the database using the id.',
            status=200
        )
    return jsonify(
        message='Account category not deleted in the database using the id.',
        status=500
    )


sweep_api_v1.register_blueprint(account_category_api_v1)
