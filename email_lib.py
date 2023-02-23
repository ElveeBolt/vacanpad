import smtplib, ssl, poplib, imaplib


class EmailSender:
    def __init__(self,
                 email: str,
                 login: str,
                 password: str,
                 smtp_server: str,
                 smtp_port: int,
                 pop3_server: str,
                 pop3_port: int,
                 imap_server: str,
                 imap_port: int,
                 subject: str,
                 message: str,
                 receiver_email: str):
        self.email = email
        self.login = login
        self.password = password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.pop_server = pop3_server
        self.pop_port = pop3_port
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.subject = subject
        self.message = message
        self.receiver_email = receiver_email

    def send(self):
        """
        Send email to receiver email

        :return:
        """
        context = ssl.create_default_context()

        message = f'Subject: {self.subject}\n\n{self.message}'

        with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
            server.login(self.login, self.password)
            server.sendmail(self.email, self.receiver_email, message)

    def get_pop3(self):
        pass

    def get_imap(self):
        pass
