from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from database import Base
from datetime import datetime


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    login = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)

    def __init__(self, name, login, password):
        self.name = name
        self.login = login
        self.password = password

    def __repr__(self):
        return f'<User {self.name}>'


class Vacancy(Base):
    __tablename__ = 'vacancies'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    position = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    url = Column(String(255), nullable=False)
    contacts_id = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))
    comment = Column(Text)
    status = Column(Integer, nullable=False)
    date_publish = Column(DateTime, nullable=False, default=datetime.now())

    def __init__(self, title, description, position, company, url, contacts_id, user_id, comment, status):
        self.title = title
        self.description = description
        self.position = position
        self.company = company
        self.url = url
        self.contacts_id = contacts_id
        self.user_id = user_id
        self.comment = comment
        self.status = status

    def __repr__(self):
        return f'<Vacancy {self.title}>'


class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    vacancy_id = Column(Integer, ForeignKey('vacancies.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    due_to_date = Column(DateTime, nullable=False)
    status = Column(Integer, nullable=False)
    date_publish = Column(DateTime, nullable=False, default=datetime.now())

    def __init__(self, vacancy_id, user_id, title, description, due_to_date, status):
        self.vacancy_id = vacancy_id
        self.user_id = user_id
        self.title = title
        self.description = description
        self.due_to_date = datetime.strptime(due_to_date.replace('T', ' '), '%Y-%m-%d %H:%M')
        self.status = status

    def __repr__(self):
        return f'<Event {self.title}>'


class Template(Base):
    __tablename__ = 'templates'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String(255), nullable=False)
    content = Column(String(255), nullable=False)

    def __init__(self, user_id, title, content):
        self.user_id = user_id
        self.title = title
        self.content = content

    def __repr__(self):
        return f'<Template {self.title}>'


class EmailCred(Base):
    __tablename__ = 'email_creds'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    email = Column(String(255), nullable=False)
    login = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    smtp_server = Column(String(255), nullable=True)
    smtp_port = Column(Integer, nullable=True)
    pop3_server = Column(String(255), nullable=True)
    pop3_port = Column(Integer, nullable=True)
    imap_server = Column(String(255), nullable=True)
    imap_port = Column(Integer, nullable=True)

    def __init__(self, user_id, email, login, password, smtp_server, smtp_port, pop3_server, pop3_port, imap_server, imap_port):
        self.user_id = user_id
        self.email = email
        self.login = login
        self.password = password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.pop3_server = pop3_server
        self.pop3_port = pop3_port
        self.imap_server = imap_server
        self.imap_port = imap_port

    def to_dict(self):
        return {
            'email': self.email,
            'login': self.login,
            'password': self.password,
            'smtp_server': self.smtp_server,
            'smtp_port': self.smtp_port,
            'pop3_server': self.pop3_server,
            'pop3_port': self.pop3_port,
            'imap_server': self.imap_server,
            'imap_port': self.imap_port,
        }

    def __repr__(self):
        return f'<EmailCred {self.email}>'


class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    content = Column(String(255), nullable=False)

    def __init__(self, user_id, title, description, content):
        self.user_id = user_id
        self.title = title
        self.description = description
        self.content = content

    def __repr__(self):
        return f'<Document {self.title}>'
