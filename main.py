from flask import Flask, request, render_template, redirect, url_for
import database
from datetime import datetime
from models import Vacancy, Event, EmailCred, Template, Document
from email_lib import EmailWrapper

app = Flask(__name__)


# Home Page
@app.route('/')
def index():
    database.init_db()
    statistic = {
        'vacancies': database.db_session.query(Vacancy).count(),
        'events': database.db_session.query(Event).count()
    }
    return render_template('index.html', statistic=statistic)


# Vacancies
@app.route('/vacancies', methods=['GET'])
def vacancies():
    database.init_db()
    context = {
        'title': 'Вакансии',
        'subtitle': 'Список добавленых вакансий',
    }
    vacancies = database.db_session.query(Vacancy).all()

    return render_template('vacancies/index.html', context=context, vacancies=vacancies)


@app.route('/vacancies/add', methods=['GET', 'POST'])
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

        return redirect(url_for('vacancy_add'))

    return render_template('vacancies/add.html', context=context)


@app.route('/vacancies/<vacancy_id>', methods=['GET', 'POST'])
def vacancy(vacancy_id):
    database.init_db()
    context = {
        'title': 'Детали вакансии',
        'subtitle': 'Детальная информация касательно вакансии',
    }

    vacancy = database.db_session.query(Vacancy).get(vacancy_id)
    events = database.db_session.query(Event).filter_by(vacancy_id=vacancy_id).limit(5).all()
    emails = database.db_session.query(EmailCred).filter_by(user_id=1).all()

    if request.method == 'POST':
        email = database.db_session.query(EmailCred).get(request.form.get('email'))
        subject = request.form.get('subject')
        receiver_email = request.form.get('receiver_email')
        message = request.form.get('message')
        sender = EmailWrapper(
            email=email.email,
            login=email.login,
            password=email.password,
            smtp_server=email.smtp_server,
            smtp_port=email.smtp_port,
            pop3_server=email.pop3_server,
            pop3_port=email.pop3_port,
            imap_server=email.imap_server,
            imap_port=email.imap_port,
            subject=subject,
            message=message,
            receiver_email=receiver_email
        )
        sender.send()

    return render_template('vacancies/vacancy.html', context=context, vacancy=vacancy, events=events, emails=emails)


@app.route('/vacancies/<vacancy_id>/edit', methods=['GET', 'POST'])
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


@app.route('/vacancies/<vacancy_id>/delete', methods=['GET', 'POST'])
def vacancy_delete(vacancy_id):
    if request.method == 'POST':
        database.init_db()
        database.db_session.query(Vacancy).filter_by(id=vacancy_id).delete()
        database.db_session.commit()

    return redirect(url_for('vacancies'))


@app.route('/vacancies/<vacancy_id>/events', methods=['GET'])
def vacancy_events(vacancy_id):
    database.init_db()
    context = {
        'title': 'События',
        'subtitle': 'Список событий',
    }

    vacancy = database.db_session.query(Vacancy).get(vacancy_id)
    events = database.db_session.query(Event).filter_by(vacancy_id=vacancy_id).all()

    return render_template('events/index.html', context=context, events=events, vacancy=vacancy)


@app.route('/events/<event_id>', methods=['GET'])
def vacancy_event(event_id):
    database.init_db()
    context = {
        'title': 'Детали события',
        'subtitle': 'Детальная информация касательно события',
    }

    event = database.db_session.query(Event).get(event_id)

    return render_template('events/event.html', context=context, event=event)


@app.route('/vacancies/<vacancy_id>/events/add', methods=['GET', 'POST'])
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


@app.route('/events/<event_id>/edit', methods=['GET', 'POST'])
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


@app.route('/events/<event_id>/delete', methods=['GET', 'POST'])
def vacancy_event_delete(event_id):
    if request.method == 'POST':
        database.init_db()
        database.db_session.query(Event).filter_by(id=event_id).delete()
        database.db_session.commit()

    return redirect(url_for('vacancies'))


@app.route('/vacancies/<vacancy_id>/history', methods=['GET'])
def vacancy_history():
    return 'Vacancy history'


# User
@app.route('/user', methods=['GET'])
def user():
    return 'User'


@app.route('/user/documents', methods=['GET'])
def user_documents():
    database.init_db()
    context = {
        'title': 'Документы',
        'subtitle': 'Список документов',
    }

    documents = database.db_session.query(Document).all()

    return render_template('documents/index.html', context=context, documents=documents)


@app.route('/user/documents/<document_id>', methods=['GET'])
def user_document(document_id):
    database.init_db()
    context = {
        'title': 'Детали документа',
        'subtitle': 'Детальная информация касательно документа',
    }

    document = database.db_session.query(Document).get(document_id)

    return render_template('documents/document.html', context=context, document=document)


@app.route('/user/documents/add', methods=['GET', 'POST'])
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


@app.route('/user/documents/<document_id>/edit', methods=['GET', 'POST'])
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


@app.route('/user/documents/<document_id>/delete', methods=['GET', 'POST'])
def user_document_delete(document_id):
    if request.method == 'POST':
        database.init_db()
        database.db_session.query(Document).filter_by(id=document_id).delete()
        database.db_session.commit()

    return redirect(url_for('user_documents'))


@app.route('/user/templates', methods=['GET'])
def user_templates():
    database.init_db()
    context = {
        'title': 'Шаблоны писем',
        'subtitle': 'Список шаблонов писем',
    }

    templates = database.db_session.query(Template).all()

    return render_template('templates/index.html', context=context, templates=templates)


@app.route('/user/templates/<template_id>', methods=['GET'])
def user_template(template_id):
    database.init_db()
    context = {
        'title': 'Детали шаблона письма',
        'subtitle': 'Детальная информация касательно шаблонов писем',
    }

    template = database.db_session.query(Template).get(template_id)

    return render_template('templates/document.html', context=context, template=template)


@app.route('/user/templates/add', methods=['GET', 'POST'])
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


@app.route('/user/templates/<template_id>/edit', methods=['GET', 'POST'])
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


@app.route('/user/templates/<template_id>/delete', methods=['GET', 'POST'])
def user_template_delete(template_id):
    if request.method == 'POST':
        database.init_db()
        database.db_session.query(Template).filter_by(id=template_id).delete()
        database.db_session.commit()

    return redirect(url_for('user_templates'))


@app.route('/user/emails', methods=['GET'])
def user_emails():
    database.init_db()
    context = {
        'title': 'Настройки E-mails',
        'subtitle': 'Список настроек e-mail адресов',
    }

    emails = database.db_session.query(EmailCred).all()

    return render_template('emails/index.html', context=context, emails=emails)


@app.route('/user/emails/<email_id>', methods=['GET', 'POST'])
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
        email_wrapper.send(receiver_email=receiver_email, subject=subject, message=message)

    return render_template('emails/email.html', context=context, email=email, emails=emails)


@app.route('/user/emails/add', methods=['GET', 'POST'])
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


@app.route('/user/emails/<email_id>/edit', methods=['GET', 'POST'])
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


@app.route('/user/emails/<email_id>/delete', methods=['GET', 'POST'])
def user_email_delete(email_id):
    if request.method == 'POST':
        database.init_db()
        database.db_session.query(EmailCred).filter_by(id=email_id).delete()
        database.db_session.commit()

    return redirect(url_for('user_emails'))


@app.route('/user/calendar', methods=['GET'])
def user_calendar():
    return 'User calendar'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
