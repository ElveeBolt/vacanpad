import os
from celery import Celery
import database
from models import EmailCred
from email_lib import EmailWrapper

RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'localhost')

app = Celery('celery_worker', broker=f'pyamqp://guest@{RABBITMQ_HOST}//')


@app.task
def send_email(id_email_option: str, receiver_email: str, subject: str, message: str):
    database.init_db()
    email_option = database.db_session.query(EmailCred).get(id_email_option)
    email_wrapper = EmailWrapper(**email_option.to_dict())
    email_wrapper.send(receiver_email=receiver_email, subject=subject, message=message)