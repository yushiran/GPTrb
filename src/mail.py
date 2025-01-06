import smtplib
from email.mime.text import MIMEText
from email.header import Header
from dotenv import load_dotenv
load_dotenv()
import os
import time
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def send_email(subject, body, sender, receivers, smtp_server, smtp_port, smtp_password, attachment_path=None):
    # 创建邮件内容
    message = MIMEMultipart()
    message['From'] = Header("Sender<%s>" % sender)  # 发送者
    message['To'] = Header("Receiver<%s>" % receivers[0])  # 接收者
    message['Subject'] = Header(subject, 'utf-8')  # 设置邮件主题

    # 添加邮件正文
    message.attach(MIMEText(body, 'plain', 'utf-8'))

    # 添加附件
    if attachment_path:
        with open(attachment_path, 'rb') as attachment:
            mime_base = MIMEBase('application', 'octet-stream')
            mime_base.set_payload(attachment.read())
            encoders.encode_base64(mime_base)
            mime_base.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment_path)}')
            message.attach(mime_base)

    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender, smtp_password)
        server.sendmail(sender, receivers, message.as_string())
        print("邮件发送成功")
        server.close()
    except smtplib.SMTPException as e:
        print(f"Error: 无法发送邮件. 错误详情: {e}")

def mail_main():
    while True:
        current_time = time.localtime()
        if (current_time.tm_hour == 15 and current_time.tm_min == 35) or (current_time.tm_hour == 18 and current_time.tm_min == 35):
            # 示例调用
            subject = "gpt advice"
            with open(f"{CURRENT_DIR}/../json/gpt_advice.txt", 'r', encoding='utf-8') as file:
                body = file.read()
            sender = os.getenv("sender_mail")
            receivers = os.getenv("receivers_mail")
            smtp_server = os.getenv("smtp_server")
            smtp_port = os.getenv("smtp_port")
            smtp_password = os.getenv("smtp_password")
            attachment_path = f"{CURRENT_DIR}/../json/today_recommedation.png"  # 示例附件路径
            send_email(
                subject=subject,
                body=body,
                sender=sender,  # 发件人邮箱
                receivers=[receivers],  # 收件人邮箱，可以是一个列表
                smtp_server=smtp_server,  # 邮件服务SMTP服务器地址
                smtp_port=smtp_port,  # 邮件服务SMTP服务器端口（一般为587）
                smtp_password=smtp_password,  # 邮箱的密码或授权码
                attachment_path=attachment_path  # 附件路径
            )
            time.sleep(60)

def mail_main_pipeline():
    current_time = time.localtime()
    # 示例调用
    subject = "gpt advice"
    with open(f"{CURRENT_DIR}/../json/gpt_advice.txt", 'r', encoding='utf-8') as file:
        body = file.read()
    sender = os.getenv("sender_mail")
    receivers = os.getenv("receivers_mail")
    smtp_server = os.getenv("smtp_server")
    smtp_port = os.getenv("smtp_port")
    smtp_password = os.getenv("smtp_password")
    attachment_path = f"{CURRENT_DIR}/../json/today_recommedation.png"  # 示例附件路径
    send_email(
        subject=subject,
        body=body,
        sender=sender,  # 发件人邮箱
        receivers=[receivers],  # 收件人邮箱，可以是一个列表
        smtp_server=smtp_server,  # 邮件服务SMTP服务器地址
        smtp_port=smtp_port,  # 邮件服务SMTP服务器端口（一般为587）
        smtp_password=smtp_password,  # 邮箱的密码或授权码
        attachment_path=attachment_path  # 附件路径
    )

# Example usage
if __name__ == "__main__":
    mail_main()
