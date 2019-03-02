from socket_web.gjh import Blueprint


static_bp = Blueprint('static')


@static_bp.route('/static/<s_type>/<name>')
def route_static(request, s_type, name):
    """
    静态资源的处理函数, 读取图片并生成响应返回
    """
    d = {
        'css': b'HTTP/1.1 200 OK\r\nContent-Type: text/css\r\n\r\n',
        'js': b'HTTP/1.1 200 OK\r\nContent-Type: application/x-javascript\r\n\r\n',
        'txt': b'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n',
        'jpg': b'HTTP/1.1 200 OK\r\nContent-Type: image/jpg\r\n\r\n',
        'gif': b'HTTP/1.1 200 OK\r\nContent-Type: image/gif\r\n\r\n',
        'mp4': b'HTTP/1.1 200 OK\r\nContent-Type: video/x-mpg\r\n\r\n',
    }
    if name.endswith('.map'):
        name = name[:-4]
    end_name = name.split('.')[-1]

    if end_name in d:
        header = d[end_name]
    else:
        header = d['txt']

    path = 'static/' + s_type + '/' + name
    with open(path, 'rb') as f:
        s = header + f.read()
        return s
