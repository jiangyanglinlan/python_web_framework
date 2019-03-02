import random

from socket_web.gjh import Blueprint
from socket_web.gjh import (
    render_template,
    template,
    redirect,
)
from socket_web.gjh import session
from models.user import User
import config


auth_bp = Blueprint('auth')


def random_str():
    seed = config.seed
    s = ''
    for i in range(16):
        random_index = random.randint(0, len(seed) - 2)
        s += seed[random_index]
    return s


@auth_bp.route('/login')
def route_login(request):
    """
    登录页面的路由函数
    """
    if request.method == 'POST':
        form = request.form()
        u = User.validate_login(form)
        if u is not None:
            # 设置 session
            session_id = random_str()
            session[session_id] = u.id
            headers = {}
            headers['Set-Cookie'] = 'user={}'.format(session_id)
            # 登录后定向到 /
            return redirect('/', headers)
    # 显示登录页面
    body = template('auth/login.html')
    return render_template(body)


@auth_bp.route('/register')
def route_register(request):
    """
    注册页面的路由函数
    """
    if request.method == 'POST':
        form = request.form()
        u = User.register(form)
        if u is not None:
            # 注册成功后 定向到登录页面
            return redirect('/login')
        else:
            # 注册失败 定向到注册页面
            return redirect('/register')
    # 显示注册页面
    body = template('auth/register.html')
    return render_template(body)


@auth_bp.route('/logout')
def route_logout(request):
    session_id = request.cookies.get('user', '')
    if session_id is not None and session_id in session:
        session.pop(session_id)
    return redirect('/login')
