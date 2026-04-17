"""
加密工具
用于加密敏感信息(如IM应用Secret)
"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import os


class CryptoUtil:
    """加密工具类"""
    
    def __init__(self):
        """初始化加密工具"""
        # 从环境变量获取加密密钥,如果没有则使用默认密钥(生产环境必须设置)
        secret_key = os.getenv('CRYPTO_SECRET_KEY', 'default-secret-key-change-in-production')
        
        # 使用PBKDF2派生密钥
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'mengxiaotan-salt',  # 固定salt,生产环境应该使用随机salt
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret_key.encode()))
        self.cipher = Fernet(key)
    
    def encrypt(self, text: str) -> str:
        """
        加密文本
        
        Args:
            text: 要加密的文本
            
        Returns:
            加密后的文本(Base64编码)
        """
        if not text:
            return ''
        
        try:
            encrypted = self.cipher.encrypt(text.encode())
            return encrypted.decode()
        except Exception as e:
            raise ValueError(f"加密失败: {str(e)}")
    
    def decrypt(self, encrypted_text: str) -> str:
        """
        解密文本
        
        Args:
            encrypted_text: 加密的文本
            
        Returns:
            解密后的原文
        """
        if not encrypted_text:
            return ''
        
        try:
            decrypted = self.cipher.decrypt(encrypted_text.encode())
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"解密失败: {str(e)}")
    
    def mask_secret(self, secret: str, show_chars: int = 4) -> str:
        """
        脱敏显示Secret
        
        Args:
            secret: 原始Secret
            show_chars: 显示的字符数
            
        Returns:
            脱敏后的Secret
        """
        if not secret:
            return ''
        
        if len(secret) <= show_chars:
            return '*' * len(secret)
        
        return secret[:show_chars] + '*' * (len(secret) - show_chars)


# 全局加密工具实例
crypto_util = CryptoUtil()


def encrypt_im_app_config(config: dict) -> dict:
    """
    加密IM应用配置中的敏感信息
    
    Args:
        config: IM应用配置
        
    Returns:
        加密后的配置
    """
    if not config:
        return {}
    
    encrypted_config = {}
    
    # 企业微信
    if 'enterprise_wechat' in config:
        wechat = config['enterprise_wechat'].copy()
        if wechat.get('secret'):
            wechat['secret'] = crypto_util.encrypt(wechat['secret'])
        encrypted_config['enterprise_wechat'] = wechat
    
    # 钉钉
    if 'dingtalk' in config:
        dingtalk = config['dingtalk'].copy()
        if dingtalk.get('app_secret'):
            dingtalk['app_secret'] = crypto_util.encrypt(dingtalk['app_secret'])
        encrypted_config['dingtalk'] = dingtalk
    
    # 飞书
    if 'feishu' in config:
        feishu = config['feishu'].copy()
        if feishu.get('app_secret'):
            feishu['app_secret'] = crypto_util.encrypt(feishu['app_secret'])
        encrypted_config['feishu'] = feishu
    
    return encrypted_config


def decrypt_im_app_config(config: dict) -> dict:
    """
    解密IM应用配置中的敏感信息
    
    Args:
        config: 加密的IM应用配置
        
    Returns:
        解密后的配置
    """
    if not config:
        return {}
    
    decrypted_config = {}
    
    # 企业微信
    if 'enterprise_wechat' in config:
        wechat = config['enterprise_wechat'].copy()
        if wechat.get('secret'):
            try:
                wechat['secret'] = crypto_util.decrypt(wechat['secret'])
            except:
                wechat['secret'] = ''  # 解密失败返回空
        decrypted_config['enterprise_wechat'] = wechat
    
    # 钉钉
    if 'dingtalk' in config:
        dingtalk = config['dingtalk'].copy()
        if dingtalk.get('app_secret'):
            try:
                dingtalk['app_secret'] = crypto_util.decrypt(dingtalk['app_secret'])
            except:
                dingtalk['app_secret'] = ''
        decrypted_config['dingtalk'] = dingtalk
    
    # 飞书
    if 'feishu' in config:
        feishu = config['feishu'].copy()
        if feishu.get('app_secret'):
            try:
                feishu['app_secret'] = crypto_util.decrypt(feishu['app_secret'])
            except:
                feishu['app_secret'] = ''
        decrypted_config['feishu'] = feishu
    
    return decrypted_config


def mask_im_app_config(config: dict) -> dict:
    """
    脱敏显示IM应用配置
    
    Args:
        config: IM应用配置
        
    Returns:
        脱敏后的配置
    """
    if not config:
        return {}
    
    masked_config = {}
    
    # 企业微信
    if 'enterprise_wechat' in config:
        wechat = config['enterprise_wechat'].copy()
        if wechat.get('secret'):
            wechat['secret'] = crypto_util.mask_secret(wechat['secret'])
        masked_config['enterprise_wechat'] = wechat
    
    # 钉钉
    if 'dingtalk' in config:
        dingtalk = config['dingtalk'].copy()
        if dingtalk.get('app_secret'):
            dingtalk['app_secret'] = crypto_util.mask_secret(dingtalk['app_secret'])
        masked_config['dingtalk'] = dingtalk
    
    # 飞书
    if 'feishu' in config:
        feishu = config['feishu'].copy()
        if feishu.get('app_secret'):
            feishu['app_secret'] = crypto_util.mask_secret(feishu['app_secret'])
        masked_config['feishu'] = feishu
    
    return masked_config
