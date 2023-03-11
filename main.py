from flask import Flask, request, render_template, redirect, url_for, session, flash
import database
from mongodb import MongoDB
from datetime import datetime
from models import Vacancy, Event, EmailCred, Template, Document, User
from email_lib import EmailWrapper
from celery_worker import send_email

app = Flask(__name__)

app.secret_key = 'super secret key'


def login_required(func):
    def wrap(*args, **kwargs):
        if session.get('user_id') is not None:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('user_login'))

    return wrap


# Home Page
@app.route('/', methods=['GET'], endpoint='index')
@login_required
def index():
    database.init_db()
    statistic = {
        'vacancies': database.db_session.query(Vacancy).count(),
        'events': database.db_session.query(Event).count()
    }

    current_user = session.get('user_name')
    return render_template('index.html', statistic=statistic, current_user=current_user)


# Vacancies
@app.route('/vacancies', methods=['GET'], endpoint='vacancies')
@login_required
def vacancies():
    database.init_db()
    context = {
        'title': 'Вакансии',
        'subtitle': 'Список добавленых вакансий',
    }
    vacancies = database.db_session.query(Vacancy).filter_by(user_id=session.get('user_id')).all()

    return render_template('vacancies/index.html', context=context, vacancies=vacancies)


@app.route('/vacancies/add', methods=['GET', 'POST'], endpoint='vacancy_add')
@login_required
def vacancy_add():
    database.init_db()
    context = {
        'title': 'Добавление вакансии',
        'subtitle': 'Страница добавления новой вакансии',
    }

    if request.method == 'POST':
        vacancy = Vacancy(
            title=request.form.get('title'),
            description=request.form.get('description'),
            position=request.form.get('position'),
            company=request.form.get('company'),
            url=request.form.get('url'),
            user_id=1,
            contacts_id=1,
            comment=request.form.get('comment'),
            status=request.form.get('status')
        )

        database.db_session.add(vacancy)
        database.db_session.commit()

        contact = {
            'user_id': session.get('user_id'),
            'vacancy_id': vacancy.id,
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'website': request.form.get('website')
        }

        mongo = MongoDB()
        mongo.insert_contact(contact)

        return redirect(url_for('vacancy_add'))

    return render_template('vacancies/add.html', context=context)


@app.route('/vacancies/<vacancy_id>', methods=['GET', 'POST'], endpoint='vacancy')
@login_required
def vacancy(vacancy_id):
    database.init_db()
    mongo = MongoDB()
    context = {
        'title': 'Детали вакансии',
        'subtitle': 'Детальная информация касательно вакансии',
    }

    vacancy = database.db_session.query(Vacancy).get(vacancy_id)
    events = database.db_session.query(Event).filter_by(vacancy_id=vacancy_id).limit(5).all()
    emails = database.db_session.query(EmailCred).filter_by(user_id=1).all()
    contacts = mongo.get_contacts_by_vacancy_id(vacancy_id)

    if request.method == 'POST':
        subject = request.form.get('subject')
        receiver_email = request.form.get('receiver_email')
        message = request.form.get('message')
        send_email.apply_async(args=[request.form.get('email'), receiver_email, subject, message])

    return render_template('vacancies/vacancy.html', context=context, vacancy=vacancy, events=events, emails=emails,
                           contacts=contacts)


@app.route('/vacancies/<vacancy_id>/edit', methods=['GET', 'POST'], endpoint='vacancy_edit')
@login_required
def vacancy_edit(vacancy_id):
    database.init_db()
    context = {
        'title': 'Редактирование вакансии',
        'subtitle': 'Детальная информация касательно вакансии',
    }

    if request.method == 'POST':
        database.db_session.query(Vacancy).filter_by(id=vacancy_id).update({
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'position': request.form.get('position'),
            'company': request.form.get('company'),
            'url': request.form.get('url'),
            'user_id': 1,
            'contacts_id': 1,
            'comment': request.form.get('comment'),
            'status': request.form.get('status')
        })
        database.db_session.commit()

    vacancy = database.db_session.query(Vacancy).get(vacancy_id)

    return render_template('vacancies/edit.html', context=context, vacancy=vacancy)


@app.route('/vacancies/<vacancy_id>/delete', methods=['GET', 'POST'], endpoint='vacancy_delete')
@login_required
def vacancy_delete(vacancy_id):
    if request.method == 'POST':
        database.init_db()
        database.db_session.query(Vacancy).filter_by(id=vacancy_id).delete()
        database.db_session.commit()

    return redirect(url_for('vacancies'))


@app.route('/vacancies/<vacancy_id>/events', methods=['GET'], endpoint='vacancy_events')
@login_required
def vacancy_events(vacancy_id):
    database.init_db()
    context = {
        'title': 'События',
        'subtitle': 'Список событий',
    }

    vacancy = database.db_session.query(Vacancy).get(vacancy_id)
    events = database.db_session.query(Event).filter_by(vacancy_id=vacancy_id).all()

    return render_template('events/index.html', context=context, events=events, vacancy=vacancy)


@app.route('/events/<event_id>', methods=['GET'], endpoint='vacancy_event')
@login_required
def vacancy_event(event_id):
    database.init_db()
    context = {
        'title': 'Детали события',
        'subtitle': 'Детальная информация касательно события',
    }

    event = database.db_session.query(Event).get(event_id)

    return render_template('events/event.html', context=context, event=event)


@app.route('/vacancies/<vacancy_id>/events/add', methods=['GET', 'POST'], endpoint='vacancy_event_add')
@login_required
def vacancy_event_add(vacancy_id):
    database.init_db()
    context = {
        'title': 'Добавление события',
        'subtitle': 'Страница добавления нового события',
    }
    if request.method == 'POST':
        event = Event(
            title=request.form.get('title'),
            description=request.form.get('description'),
            vacancy_id=vacancy_id,
            due_to_date=request.form.get('due_to_date'),
            status=request.form.get('status')
        )

        database.db_session.add(event)
        database.db_session.commit()

        return redirect(url_for('vacancy_event_add', vacancy_id=vacancy_id))

    return render_template('events/add.html', context=context, vacancy_id=vacancy_id)


@app.route('/events/<event_id>/edit', methods=['GET', 'POST'], endpoint='vacancy_event_edit')
@login_required
def vacancy_event_edit(event_id):
    database.init_db()
    context = {
        'title': 'Редактирование события',
        'subtitle': 'Страница редактирования события',
    }

    if request.method == 'POST':
        database.db_session.query(Event).filter_by(id=event_id).update({
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'due_to_date': datetime.strptime(request.form.get('due_to_date').replace('T', ' '), '%Y-%m-%d %H:%M'),
            'status': request.form.get('status')
        })

        database.db_session.commit()

        return redirect(url_for('vacancy_event_edit', event_id=event_id))

    event = database.db_session.query(Event).get(event_id)

    return render_template('events/edit.html', context=context, event=event)


@app.route('/events/<event_id>/delete', methods=['GET', 'POST'], endpoint='vanvacy_event_delete')
@login_required
def vacancy_event_delete(event_id):
    if request.method == 'POST':
        database.init_db()
        database.db_session.query(Event).filter_by(id=event_id).delete()
        database.db_session.commit()

    return redirect(url_for('vacancies'))


@app.route('/vacancies/<vacancy_id>/contacts', methods=['GET'], endpoint='vacancy_contacts')
@login_required
def vacancy_contacts(vacancy_id):
    mongo = MongoDB()
    context = {
        'title': 'Контакты вакансии',
        'subtitle': 'Список контактов связанных с вакансией',
    }
    contacts = mongo.get_contacts_by_vacancy_id(vacancy_id)

    return render_template('contacts/index.html', context=context, contacts=contacts)


@app.route('/vacancies/<vacancy_id>/history', methods=['GET'], endpoint='vacancy_history')
@login_required
def vacancy_history():
    return 'Vacancy history'


# User
@app.route('/user', methods=['GET'], endpoint='user')
def user():
    return 'User'


@app.route('/user/login', methods=['GET', 'POST'], endpoint='user_login')
def user_login():
    context = {
        'title': 'Авторизация',
        'subtitle': 'Для того чтобы начать работу с VacanPad выполните авторизацию',
    }

    if request.method == 'POST':
        database.init_db()
        username = request.form.get('username')
        password = request.form.get('password')

        if username == '' or password == '':
            return redirect(url_for('index'))

        user = database.db_session.query(User).filter(User.login == username).first()
        if user is None:
            flash('Пользователь не найден')
            return redirect(url_for('user_login'))
        if user.password != password:
            flash('Вы ввели неверный пароль. Пожалуйста, повторите попытку ещё раз.')
            return redirect(url_for('user_login'))

        session['user_id'] = user.id
        session['user_name'] = user.name

        return redirect(url_for('index'))

    return render_template('users/login.html', context=context)


@app.route('/user/signup', methods=['GET', 'POST'], endpoint='user_signup')
def user_signup():
    context = {
        'title': 'Регистрация',
        'subtitle': 'Для того, чтобы зарегистрировать аккаунт, заполните форму ниже',
    }

    if request.method == 'POST':
        database.init_db()
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        password_repeat = request.form.get('password_repeat')

        if password != password_repeat:
            return render_template('users/signup.html', context=context)

        user = User(
            name=name,
            login=username,
            password=password
        )

        database.db_session.add(user)
        database.db_session.commit()

        return redirect(url_for('user_login'))

    return render_template('users/signup.html', context=context)


@app.route('/user/logout', methods=['GET'], endpoint='user_logout')
def user_logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/user/documents', methods=['GET'], endpoint='user_documents')
@login_required
def user_documents():
    database.init_db()
    context = {
        'title': 'Документы',
        'subtitle': 'Список документов',
    }

    documents = database.db_session.query(Document).all()

    return render_template('documents/index.html', context=context, documents=documents)


@app.route('/user/documents/<document_id>', methods=['GET'], endpoint='user_document')
@login_required
def user_document(document_id):
    database.init_db()
    context = {
        'title': 'Детали документа',
        'subtitle': 'Детальная информация касательно документа',
    }

    document = database.db_session.query(Document).get(document_id)

    return render_template('documents/document.html', context=context, document=document)


@app.route('/user/documents/add', methods=['GET', 'POST'], endpoint='user_documents_add')
@login_required
def user_documents_add():
    database.init_db()
    context = {
        'title': 'Добавление документа',
        'subtitle': 'Страница добавления нового документа',
    }
    if request.method == 'POST':
        document = Document(
            user_id=1,
            title=request.form.get('title'),
            description=request.form.get('description'),
            content=request.form.get('content')
        )

        database.db_session.add(document)
        database.db_session.commit()

        return redirect(url_for('user_documents_add'))

    return render_template('documents/add.html', context=context)


@app.route('/user/documents/<document_id>/edit', methods=['GET', 'POST'], endpoint='user_document_edit')
@login_required
def user_document_edit(document_id):
    database.init_db()
    context = {
        'title': 'Редактирование документа',
        'subtitle': 'Страница редактирования документа',
    }

    if request.method == 'POST':
        database.db_session.query(Document).filter_by(id=document_id).update({
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'content': request.form.get('content'),
        })

        database.db_session.commit()

        return redirect(url_for('user_document_edit', document_id=document_id))

    document = database.db_session.query(Document).get(document_id)

    return render_template('documents/edit.html', context=context, document=document)


@app.route('/user/documents/<document_id>/delete', methods=['GET', 'POST'], endpoint='user_document_delete')
@login_required
def user_document_delete(document_id):
    if request.method == 'POST':
        database.init_db()
        database.db_session.query(Document).filter_by(id=document_id).delete()
        database.db_session.commit()

    return redirect(url_for('user_documents'))


@app.route('/user/templates', methods=['GET'], endpoint='user_templates')
@login_required
def user_templates():
    database.init_db()
    context = {
        'title': 'Шаблоны писем',
        'subtitle': 'Список шаблонов писем',
    }

    templates = database.db_session.query(Template).all()

    return render_template('templates/index.html', context=context, templates=templates)


@app.route('/user/templates/<template_id>', methods=['GET'], endpoint='user_template')
@login_required
def user_template(template_id):
    database.init_db()
    context = {
        'title': 'Детали шаблона письма',
        'subtitle': 'Детальная информация касательно шаблонов писем',
    }

    template = database.db_session.query(Template).get(template_id)

    return render_template('templates/document.html', context=context, template=template)


@app.route('/user/templates/add', methods=['GET', 'POST'], endpoint='user_templates_add')
@login_required
def user_templates_add():
    database.init_db()
    context = {
        'title': 'Добавление шаблона письма',
        'subtitle': 'Страница добавления нового шаблона письма',
    }
    if request.method == 'POST':
        template = Template(
            user_id=1,
            title=request.form.get('title'),
            content=request.form.get('content')
        )

        database.db_session.add(template)
        database.db_session.commit()

        return redirect(url_for('user_templates_add'))

    return render_template('templates/add.html', context=context)


@app.route('/user/templates/<template_id>/edit', methods=['GET', 'POST'], endpoint='user_template_edit')
@login_required
def user_template_edit(template_id):
    database.init_db()
    context = {
        'title': 'Редактирование шаблона письма',
        'subtitle': 'Страница редактирования шаблона письма',
    }

    if request.method == 'POST':
        database.db_session.query(Template).filter_by(id=template_id).update({
            'title': request.form.get('title'),
            'content': request.form.get('content'),
        })

        database.db_session.commit()

        return redirect(url_for('user_template_edit', template_id=template_id))

    template = database.db_session.query(Template).get(template_id)

    return render_template('templates/edit.html', context=context, template=template)


@app.route('/user/templates/<template_id>/delete', methods=['GET', 'POST'], endpoint='user_template_delete')
@login_required
def user_template_delete(template_id):
    if request.method == 'POST':
        database.init_db()
        database.db_session.query(Template).filter_by(id=template_id).delete()
        database.db_session.commit()

    return redirect(url_for('user_templates'))


@app.route('/user/emails', methods=['GET'], endpoint='user_emails')
@login_required
def user_emails():
    database.init_db()
    context = {
        'title': 'Настройки E-mails',
        'subtitle': 'Список настроек e-mail адресов',
    }

    emails = database.db_session.query(EmailCred).all()

    return render_template('emails/index.html', context=context, emails=emails)


@app.route('/user/emails/<email_id>', methods=['GET', 'POST'], endpoint='user_email')
@login_required
def user_email(email_id):
    database.init_db()
    context = {
        'title': 'Детали E-mail',
        'subtitle': 'Детальная информация касательно e-mail',
    }

    email = database.db_session.query(EmailCred).get(email_id)

    email_wrapper = EmailWrapper(
        email=email.email,
        login=email.login,
        password=email.password,
        smtp_server=email.smtp_server,
        smtp_port=email.smtp_port,
        pop3_server=email.pop3_server,
        pop3_port=email.pop3_port,
        imap_server=email.imap_server,
        imap_port=email.imap_port
    )
    emails = email_wrapper.get_emails([1, 2, 3, 4, 5], protocol='IMAP')

    if request.method == 'POST':
        subject = request.form.get('subject')
        receiver_email = request.form.get('receiver_email')
        message = request.form.get('message')
        send_email.apply_async(args=[request.form.get('email'), receiver_email, subject, message])

    return render_template('emails/email.html', context=context, email=email, emails=emails)


@app.route('/user/emails/add', methods=['GET', 'POST'], endpoint='user_emails_add')
@login_required
def user_emails_add():
    database.init_db()
    context = {
        'title': 'Добавление e-mail',
        'subtitle': 'Страница добавления нового e-mail',
    }
    if request.method == 'POST':
        email = EmailCred(
            user_id=1,
            email=request.form.get('email'),
            login=request.form.get('login'),
            password=request.form.get('password'),
            smtp_server=request.form.get('smtp_server'),
            smtp_port=request.form.get('smtp_port'),
            pop3_server=request.form.get('pop3_server'),
            pop3_port=request.form.get('pop3_port'),
            imap_server=request.form.get('imap_server'),
            imap_port=request.form.get('imap_port'),
        )

        database.db_session.add(email)
        database.db_session.commit()

        return redirect(url_for('user_emails'))

    return render_template('emails/add.html', context=context)


@app.route('/user/emails/<email_id>/edit', methods=['GET', 'POST'], endpoint='user_email_edit')
@login_required
def user_email_edit(email_id):
    database.init_db()
    context = {
        'title': 'Редактирование E-mail',
        'subtitle': 'Страница редактирования e-mail',
    }

    if request.method == 'POST':
        database.db_session.query(EmailCred).filter_by(id=email_id).update({
            'email': request.form.get('email'),
            'login': request.form.get('login'),
            'password': request.form.get('password'),
            'smtp_server': request.form.get('smtp_server'),
            'smtp_port': request.form.get('smtp_port'),
            'pop3_server': request.form.get('pop3_server'),
            'pop3_port': request.form.get('pop3_port'),
            'imap_server': request.form.get('imap_server'),
            'imap_port': request.form.get('imap_port'),
        })

        database.db_session.commit()

        return redirect(url_for('user_emails'))

    email = database.db_session.query(EmailCred).get(email_id)

    return render_template('emails/edit.html', context=context, email=email)


@app.route('/user/emails/<email_id>/delete', methods=['GET', 'POST'], endpoint='user_email_delete')
@login_required
def user_email_delete(email_id):
    if request.method == 'POST':
        database.init_db()
        database.db_session.query(EmailCred).filter_by(id=email_id).delete()
        database.db_session.commit()

    return redirect(url_for('user_emails'))


@app.route('/user/contacts/', methods=['GET'], endpoint='user_contacts')
@login_required
def user_contacts():
    mongo = MongoDB()
    context = {
        'title': 'Мои контакты',
        'subtitle': 'Список моих контактов',
    }
    contacts = mongo.get_contacts(user_id=session.get('user_id'))

    return render_template('contacts/index.html', context=context, contacts=contacts)


@app.route('/user/contacts/<contact_id>', methods=['GET', 'POST'], endpoint='user_contact_edit')
@login_required
def user_contact_edit(contact_id):
    mongo = MongoDB()
    context = {
        'title': 'Редактирование контакта',
        'subtitle': 'Страница редактирования контакта',
    }
    contact = mongo.get_contact_by_id(contact_id)

    if request.method == 'POST':
        contact = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'website': request.form.get('website')
        }
        mongo.update_contact(contact_id, contact)

        return redirect(url_for('user_contacts'))

    return render_template('contacts/edit.html', context=context, contact=contact)


@app.route('/user/contacts/add/<vacancy_id>', methods=['GET', 'POST'], endpoint='user_contacts_add')
@login_required
def user_contacts_add(vacancy_id):
    context = {
        'title': 'Добавление контакта',
        'subtitle': 'Страница добавления контакта',
    }

    if request.method == 'POST':
        mongo = MongoDB()

        contact = {
            'user_id': session.get('user_id'),
            'vacancy_id': int(vacancy_id),
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'website': request.form.get('website')
        }

        mongo.insert_contact(contact)

        return redirect(url_for('vacancy', vacancy_id=vacancy_id))

    return render_template('contacts/add.html', context=context)


@app.route('/user/contacts/<contact_id>/delete', methods=['GET', 'POST'], endpoint='user_contact_delete')
@login_required
def user_contact_delete(contact_id):
    if request.method == 'POST':
        mongo = MongoDB()
        mongo.delete_contact(contact_id)

    return redirect(url_for('user_contacts'))


@app.route('/user/calendar', methods=['GET'], endpoint='calendar')
@login_required
def user_calendar():
    return 'User calendar'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
