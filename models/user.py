from orm import Model
import config


class User(Model):
    '''
    用户 model
    '''
    def __init__(self, form):
        self.id = form.get('id', None)
        self.username = form.get('username', '')  # 用户名
        self.password = form.get('password', '')  # 密码
        self.bio = form.get('bio', '')  # 用户简介
        self.email = form.get('email', '')  # email
        self.user_image = 'default.img'  # 用户头像

    def salted_password(self, password, salt=config.password_salt):
        import hashlib
        def sha256(ascii_str):
            return hashlib.sha256(ascii_str.encode('ascii')).hexdigest()
        hash1 = sha256(password)
        hash2 = sha256(hash1 + salt)
        return hash2

    def hashed_password(self, password):
        import hashlib
        pwd = password.encode('ascii')
        s = hashlib.sha256(pwd)
        return s.hexdigest()

    @classmethod
    def register(cls, form):
        '''
        注册
        '''
        name = form.get('username', '')
        pwd = form.get('password', '')
        email = form.get('email', '')
        if len(name) > 3 and len(pwd) > 3 and User.find_by(username=name) is None:
            u = User.new(form)
            u.password = u.salted_password(pwd)
            u.save()
            return u
        else:
            return None

    @classmethod
    def validate_login(cls, form):
        '''
        登录验证
        '''
        u = User(form)
        user = User.find_by(username=u.username)
        if user is not None and user.password == u.salted_password(u.password):
            return user
        else:
            return None

    @staticmethod
    def validateEmail(email):
        import re
        if len(email) > 7:
            if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
                return True
        return False
