from socket_web.gjh import Blueprint
from socket_web.gjh import (
    render_template,
    template,
)
from socket_web.gjh import session
from models.user import User


index_bp = Blueprint('index')


def current_user(request):
    session_id = request.cookies.get('user', '')
    user_id = session.get(session_id, -1)
    return user_id


@index_bp.route('/')
def index(request):
    uid = current_user(request)
    user = User.get(uid)
    body = template('base.html', user=user)
    return render_template(body)
