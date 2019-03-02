from socket_web.gjh import GJH

from routes.routes_user import auth_bp
from routes.routes_static import static_bp
from routes.routes_index import index_bp


app = GJH()

app.register_blueprint(auth_bp)
app.register_blueprint(static_bp)
app.register_blueprint(index_bp)

app.run(host='127.0.0.1', port=5000)  # 启动服务器