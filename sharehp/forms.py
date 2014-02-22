# -*- coding: utf-8 -*-
from django import forms
from models import User
from utils import common

# 注册表单
class RegisterForm(forms.Form):
    email = forms.EmailField(max_length=128,
                             error_messages={'required': u'请输入邮箱', 'invalid': u'邮箱格式不正确', 'max_length': u'邮箱太长了哎'})
    nickname = forms.CharField(min_length=4, max_length=16,
                               error_messages={'required': u'请输入昵称', 'min_length': u'昵称长度太短了（至少四个字符）',
                                               'max_length': u'昵称太长了哎'})
    password = forms.CharField(min_length=6, max_length=16,
                               error_messages={'required': u'请输入密码', 'min_length': u'密码长度太短了（至少六位）',
                                               'max_length': u'密码太长了哎'})

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        is_exist = User.objects.filter(email=email).exists()
        if is_exist:
            raise forms.ValidationError(u'邮箱已经被注册！')
        return email

    def clean_nickname(self):
        nickname = self.cleaned_data['nickname'].strip()
        is_exist = User.objects.filter(nickname=nickname).exists()
        if is_exist:
            raise forms.ValidationError(u'昵称已经被占用, 换一个吧！')
        return nickname


# 登录表单
class LoginForm(forms.Form):
    email = forms.EmailField(max_length=128,
                             error_messages={'required': u'请输入邮箱', 'invalid': u'邮箱格式不正确', 'max_length': u'邮箱太长了哎'})
    password = forms.CharField(max_length=16, error_messages={'required': u'请输入密码', 'max_length': u'密码太长了哎'})

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        is_exist = User.objects.filter(email=email).exists()
        if not is_exist:
            raise forms.ValidationError(u'邮箱还没有注册哦！')
        return email

    def clean(self):
        cleaned_data = self.cleaned_data
        email = cleaned_data.get("email", '')
        password = cleaned_data.get("password", '')
        if password and email:
            is_exist = User.objects.filter(email=email.strip(),
                                           password=common.encode_password(password).strip()).exists()
            if not is_exist:
                raise forms.ValidationError(u"密码错误！")
        return cleaned_data


# 修改密码
class ChangePasswordForm(forms.Form):
    password = forms.CharField(max_length=16, error_messages={'required': u'请输入旧密码', 'max_length': u'密码太长了哎'})
    new_password = forms.CharField(max_length=16, error_messages={'required': u'请输入新密码', 'max_length': u'密码太长了哎'})
    confirm_password = forms.CharField(max_length=16, error_messages={'required': u'请再次输入新密码', 'max_length': u'密码太长了哎'})

    def clean(self):
        cleaned_data = self.cleaned_data
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")
        if confirm_password and new_password:
            if not (confirm_password == new_password):
                raise forms.ValidationError(u"两次输入密码不一致！")
        return cleaned_data
