# -*- coding: utf-8 -*-
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header


class SendEmail:
    """ 发送测试报告到邮箱 """

    def __init__(self, email_server, username, password, to_list, msg_content):
        self.email_server = email_server
        self.username = username
        self.password = password
        self.to_list = to_list
        self.status = msg_content["status"]
        self.content = msg_content["msg"]

    def send_email(self):
        """ 使用第三方SMTP服务发送邮件 """
        message = MIMEMultipart()  # 邮件对象

        # 邮件title
        email_title = f'自动化测试：{"通过" if self.status == "success" else "不通过"}'
        message["Subject"] = Header(email_title, "utf-8").encode()

        # 邮件正文
        email_body = MIMEText(_text=self.content, _subtype="html", _charset="utf-8")  # 邮件正文内容为报告附件body
        message.attach(email_body)

        message["From"] = self.username
        message["To"] = Header("".join(self.to_list), "utf-8")

        try:
            # 发送邮件
            print(f'{"=" * 30} 开始发送邮件，发件箱为 {self.username} {"=" * 30}')
            service = smtplib.SMTP_SSL(host=self.email_server, port=smtplib.SMTP_SSL_PORT)
            service.login(user=self.username, password=self.password)  # 登录
            service.sendmail(from_addr=self.username, to_addrs=self.to_list, msg=message.as_string())
            print(f'{"=" * 30} 邮件发送成功 {"=" * 30}')
            service.close()
            return True
        except Exception as error:
            print(f'发送邮件出错，错误信息为：\n {error}')
            return False

if __name__ == '__main__':
    pass