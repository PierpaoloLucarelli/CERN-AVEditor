import os
import smtplib

import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(user, job_id):
    from_email = os.environ['MAIL_FROM']
    to_user = user['email']

    today_date = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    url = generate_link(job_id)

    html = """
       <html>
         <head></head>
         <body>
           <p>Hello, </p>
           <p>Your video has been processed and is ready for download at the following url:</p>
           <a href='""" + url + """'>""" + url + """</a>
           <p>Best regards.</p>
           <p>The automated script.</p>
          </body>
       </html>
       """

    msg = MIMEMultipart()
    msg.attach(MIMEText(html, 'html'))

    msg['Subject'] = '[AVEDITOR] video ready for download ' + today_date
    msg['From'] = from_email
    msg['To'] = to_user

    s = smtplib.SMTP(os.environ['MAIL_HOSTNAME'])
    s.sendmail(from_email, to_user, msg.as_string())
    s.quit()


def generate_link(job_id):
    return os.environ['HOSTNAME'] + "downloads/" +job_id


