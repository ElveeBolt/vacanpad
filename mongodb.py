import os
import pymongo
from bson import ObjectId

DB_HOST = os.environ.get('MONGO_HOST', 'localhost')


class MongoDB:
    def __init__(self):
        self._client = pymongo.MongoClient(f'mongodb://root:example@{DB_HOST}:27017/')
        self._database = self._client['vacanpad']

    def get_contacts(self) -> list:
        """
        Get all contacts

        :return: list of contacts
        """
        collection = self._database['contacts']

        return list(collection.find())

    def get_contacts_by_vacancy_id(self, vacancy_id) -> list:
        """
        Get contact list by vacancy id

        :param vacancy_id:
        :return: list of contacts
        """
        collection = self._database['contacts']

        return list(collection.find({'vacancy_id': int(vacancy_id)}))

    def get_contact_by_id(self, contact_id: str) -> dict:
        """
        Get contact by contact id

        :param contact_id:
        :return: dict of contacts
        """
        collection = self._database['contacts']

        return collection.find_one({"_id": ObjectId(contact_id)})

    def insert_contact(self, contact: dict) -> str:
        """
        Insert new contact for vacancy

        :param contact: dict of contact
        :return: str of id
        """
        collection = self._database['contacts']

        return collection.insert_one(contact).inserted_id

    def update_contact(self, contact_id: str, contact: dict):
        """
        Update contact data by contact id

        :param contact_id: str of contact id
        :param contact: data of contact
        :return:
        """
        collection = self._database['contacts']

        collection.update_one(
            {
                '_id': ObjectId(contact_id)
            },
            {
                '$set': contact
            }
        )

    def delete_contact(self, contact_id: str):
        """
        Delete contact by contact id

        :param contact_id: str of contact id
        :return:
        """
        collection = self._database['contacts']

        return collection.delete_one({'_id': ObjectId(contact_id)})

