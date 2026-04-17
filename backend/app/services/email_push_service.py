"""
邮件推送服务 (EmailPushService)
支持 SMTP 邮件发送，包含 HTML 和纯文本格式
实现重试机制（3次，间隔5分钟）
"""
import smtplib
import logging
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from flask import current_app

logger = logging.getLogger(__name__)


class EmailPushService:
    """
    邮件推送服务
    
    职责:
    - 发送 HTML 和纯文本格式的邮件
    - 实现重试机制（3次，间隔5分钟）
    - 使用 SMTP 协议发送邮件
    """
    
    def __init__(self, smtp_server: Optional[str] = None, smtp_port: Optional[int] = None,
                 username: Optional[str] = None, password: Optional[str] = None):
        """
        初始化邮件推送服务
        
        Args:
            smtp_server: SMTP 服务器地址（可选，默认从配置读取）
            smtp_port: SMTP 端口（可选，默认从配置读取）
            username: SMTP 用户名（可选，默认从配置读取）
            password: SMTP 密码（可选，默认从配置读取）
        """
        self.smtp_server = smtp_server or current_app.config.get('SMTP_SERVER', '')
        self.smtp_port = smtp_port or current_app.config.get('SMTP_PORT', 587)
        self.username = username or current_app.config.get('SMTP_USER', '')
        self.password = password or current_app.config.get('SMTP_PASSWORD', '')
        
        # 重试配置
        self.max_retries = 3
        self.retry_interval = 300  # 5分钟 = 300秒
    
    def send(self, to_email: str, subject: str, content: str, html: bool = True) -> bool:
        """
        发送邮件（带重试机制）
        
        Args:
            to_email: 收件人邮箱地址
            subject: 邮件主题
            content: 邮件内容
            html: 是否为 HTML 格式（True: HTML, False: 纯文本）
            
        Returns:
            是否发送成功
        """
        # 验证配置
        if not self._validate_config():
            logger.error("邮件配置不完整，无法发送邮件")
            return False
        
        # 验证收件人邮箱
        if not to_email or not isinstance(to_email, str) or '@' not in to_email:
            logger.error(f"无效的收件人邮箱地址: {to_email}")
            return False
        
        # 实现重试机制
        for attempt in range(1, self.max_retries + 1):
            try:
                success = self._send_email(to_email, subject, content, html)
                if success:
                    logger.info(f"邮件发送成功: {to_email}, 主题: {subject}")
                    return True
                else:
                    logger.warning(f"邮件发送失败 (尝试 {attempt}/{self.max_retries}): {to_email}")
            except Exception as e:
                logger.error(f"邮件发送异常 (尝试 {attempt}/{self.max_retries}): {e}")
            
            # 如果不是最后一次尝试，等待后重试
            if attempt < self.max_retries:
                logger.info(f"等待 {self.retry_interval} 秒后重试...")
                time.sleep(self.retry_interval)
        
        logger.error(f"邮件发送失败，已达到最大重试次数 ({self.max_retries}): {to_email}")
        return False
    
    def _send_email(self, to_email: str, subject: str, content: str, html: bool) -> bool:
        """
        实际发送邮件的内部方法
        
        Args:
            to_email: 收件人邮箱地址
            subject: 邮件主题
            content: 邮件内容
            html: 是否为 HTML 格式
            
        Returns:
            是否发送成功
        """
        try:
            # 创建邮件对象
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.username
            msg['To'] = to_email
            
            # 根据格式创建邮件内容
            if html:
                part = MIMEText(content, 'html', 'utf-8')
            else:
                part = MIMEText(content, 'plain', 'utf-8')
            
            msg.attach(part)
            
            # 连接 SMTP 服务器并发送邮件
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP 认证失败: {e}")
            return False
        except smtplib.SMTPConnectError as e:
            logger.error(f"SMTP 连接失败: {e}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP 错误: {e}")
            return False
        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            return False
    
    def _validate_config(self) -> bool:
        """
        验证 SMTP 配置是否完整
        
        Returns:
            配置是否有效
        """
        if not self.smtp_server:
            logger.error("SMTP_SERVER 未配置")
            return False
        
        if not self.smtp_port:
            logger.error("SMTP_PORT 未配置")
            return False
        
        if not self.username:
            logger.error("SMTP_USER 未配置")
            return False
        
        if not self.password:
            logger.error("SMTP_PASSWORD 未配置")
            return False
        
        return True
    
    def send_batch(self, to_emails: list, subject: str, content: str, html: bool = True) -> dict:
        """
        批量发送邮件
        
        Args:
            to_emails: 收件人邮箱地址列表
            subject: 邮件主题
            content: 邮件内容
            html: 是否为 HTML 格式
            
        Returns:
            {
                'success_count': int,  # 成功数量
                'failed_count': int,   # 失败数量
                'failed_emails': list  # 失败的邮箱列表
            }
        """
        success_count = 0
        failed_count = 0
        failed_emails = []
        
        for email in to_emails:
            if self.send(email, subject, content, html):
                success_count += 1
            else:
                failed_count += 1
                failed_emails.append(email)
        
        logger.info(f"批量邮件发送完成: 成功 {success_count}, 失败 {failed_count}")
        
        return {
            'success_count': success_count,
            'failed_count': failed_count,
            'failed_emails': failed_emails
        }


# 创建全局实例（延迟初始化，在应用上下文中使用）
def get_email_push_service() -> EmailPushService:
    """
    获取邮件推送服务实例
    
    Returns:
        EmailPushService 实例
    """
    return EmailPushService()
