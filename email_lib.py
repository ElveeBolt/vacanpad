import smtplib, ssl, poplib, imaplib
import email as em
from email.header import decode_header


class EmailWrapper:
    def __init__(self,
                 email: str,
                 login: str,
                 password: str,
                 smtp_server: str,
                 smtp_port: int,
                 pop3_server: str,
                 pop3_port: int,
                 imap_server: str,
                 imap_port: int
                 ):
        self.email = email
        self.login = login
        self.password = password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.pop_server = pop3_server
        self.pop_port = pop3_port
        self.imap_server = imap_server
        self.imap_port = imap_port

    def send(self, receiver_email: str, subject: str, message: str):
        """
        Send email to receiver email

        :return:
        """
        context = ssl.create_default_context()

        message = f'Subject: {subject}\n\n{message}'

        with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
            server.login(self.login, self.password)
            server.sendmail(self.email, receiver_email, message)

    def get_emails(self, messages_nums, protocol='IMAP'):
        if protocol == 'POP3':
            return self.get_pop3(messages_nums)
        elif protocol == 'IMAP':
            return self.get_imap(messages_nums)
        else:
            raise ValueError('Unknown protocol')

    def get_pop3(self, messages):
        M = poplib.POP3_SSL(self.pop_server)
        M.port = self.pop_port
        M.user(self.login)
        M.pass_(self.password)

        results = []
        for msg_num in messages:
            msg_data = M.retr(msg_num)[1]
            raw_email = b"\n".join(msg_data)
            msg = em.message_from_bytes(raw_email)
            msg = self.parse_message(msg)
            results.append(msg)

        M.quit()
        return results

    def get_imap(self, messages):
        M = imaplib.IMAP4_SSL(self.imap_server)
        M.login(self.login, self.password)
        M.select()

        results = []
        for msg_num in messages:
            typ, data = M.fetch(str(msg_num), '(RFC822)')
            msg = em.message_from_bytes(data[0][1])
            msg = self.parse_message(msg)
            results.append(msg)

        M.close()
        M.logout()
        return results

    def parse_message(self, message):
        subject, encoding = decode_header(message["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding)

        from_, encoding = decode_header(message.get("From"))[0]
        if isinstance(from_, bytes):
            from_ = from_.decode(encoding)

        date, encoding = decode_header(message["Date"])[0]
        if isinstance(date, bytes):
            date = date.decode(encoding)

        return {'subject': subject, 'from': from_, 'date': date}
