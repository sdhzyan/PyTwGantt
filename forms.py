#-*- coding:utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from django.contrib import auth

class LoginForm(forms.Form):
    username = forms.CharField(max_length=30)
    userpwd = forms.CharField(max_length=50,widget=forms.PasswordInput)

    # def clean_username(self):
    #     username = self.cleaned_data['username']
    #     user = User.objects.filter(username = username)
    #
    #     if not user:
    #         raise forms.ValidationError(u'用户不存在!')
    #     elif not user.is_active:
    #         raise forms.ValidationError(u'用户未激活!')
    #     return username

    def clean(self):
        super(LoginForm,self).clean()
        username = self.cleaned_data.get('username')
        userpwd = self.cleaned_data.get('userpwd')

        user = User.objects.filter(username = username)

        if not user:
            # raise forms.ValidationError(u'用户不存在!')
            self.add_error('username',u'用户不存在!')
        elif not user[0].is_active:
            # raise forms.ValidationError(u'用户未激活!')
            self.add_error('username', u'用户未激活!')
        elif user[0].is_active:
            auth_user = auth.authenticate(username=username, password=userpwd)

            if not auth_user:
                # raise forms.ValidationError(u'密码错误!')
                self.add_error('userpwd', u'密码错误!')
        return self.cleaned_data