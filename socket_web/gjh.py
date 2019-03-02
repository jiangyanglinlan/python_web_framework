import socket
import _thread
import os

from werkzeug.routing import Map, Rule, MapAdapter
from jinja2 import Environment, FileSystemLoader

from socket_web.request import Request


class GJH(object):
    def __init__(self):
        self.e = {
            404: b'HTTP/1.1 404 NOT FOUND\r\n\r\n<h1>404 NOT FOUND</h1>',
        }  # error
        self.routes = None  # 路由

    def error(self, request, code=404):
        '''
        错误处理
        '''
        return self.e.get(code, b'')

    def add_error(self, error):
        self.e.update(error)

    def update_route(self, new_route):
        '''
        添加路由
        :param route:
        :return:
        '''
        url_map = Map()
        for k, v in new_route.items():
            rule = Rule(k, endpoint=v)
            url_map.add(rule)
            self.routes = url_map.bind(k)

    def register_blueprint(self, blue_print):
        url_map = Map()
        for k, v in blue_print.routes.items():
            rule = Rule(k, endpoint=v)
            url_map.add(rule)
            self.routes = url_map.bind(k)

    @staticmethod
    def parse_path(path):
        '''
        处理 path
        '''
        index = path.find('?')
        if index == -1:
            return path, {}
        else:
            path, query_string = path.split('?', 1)
            args = query_string.split('&')
            query = {}
            for arg in args:
                k, v = args.split('=')
                query[k] = v
            return path, query

    def response_for_path(self, path, request):
        '''
        根据 path 返回 response
        '''
        path, query = self.parse_path(path)
        request.path = path
        request.query = query
        kwargs = {}
        try:
            response, kwargs = self.routes.match(path)
            print('kwargs =', kwargs)
        except:
            response = None
        if response is None:
            response = self.error
        return response(request, **kwargs)

    def process_request(self, connection):
        buffer_size = 1024
        # 获得 request
        r = b''
        while True:
            request = connection.recv(buffer_size)
            r += request
            if len(request) < buffer_size:
                break
        r = r.decode('utf-8')

        # 避免浏览器可能发送空请求导致 list 为空
        if len(r.split()) < 2:
            # 如果请求为空, 关闭此次连接
            connection.close()

        path = r.split()[1]
        # 创建一个新的 request
        request = Request()
        request.method = r.split()[0]
        request.add_headers(r.split('\r\n\r\n', 1)[0].split('\r\n')[1:])
        # 把 body 放入 request 中
        request.body = r.split('\r\n\r\n', 1)[1]
        response = self.response_for_path(path, request)
        # 发送 response 给客户端
        connection.sendall(response)
        # 关闭连接
        connection.close()

    def run(self, host='127.0.0.1', port=5000):
        '''
        启动服务器, 默认端口 5000
        '''
        with socket.socket() as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 让套接字允许地址重用
            s.bind((host, port))
            # 监听
            s.listen(5)
            # 处理请求
            while True:
                connection, address = s.accept()
                _thread.start_new_thread(self.process_request, (connection,))


class Blueprint(object):
    '''
    蓝图
    '''
    def __init__(self, name='blueprint'):
        self.name = name
        self.routes = {}

    def route(self, *args, **kwargs):
        path = args[0]
        def _common(func):
            self.routes.update({path: func})
            def _deco(*args, **kwargs):
                return func(*args, **kwargs)
            return _deco
        return _common


# __file__ 就是本文件的名字
# 得到用于加载模板的目录
path = '{}/templates/'.format(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
# 创建一个加载器, jinja2 会从这个目录中加载模板
loader = FileSystemLoader(path)
# 用加载器创建一个环境, 有了它才能读取模板文件
env = Environment(loader=loader)


def template(path, **kwargs):
    """
    本函数接受一个路径和一系列参数
    读取模板并渲染返回
    """
    t = env.get_template(path)
    return t.render(**kwargs)


def response_with_headers(headers, status_code=200):
    '''
    自定义 header
    '''
    if 'Content-Type' not in headers:
        headers['Content-Type'] = 'text/html'
    header = f'HTTP/1.1 {status_code} OK\r\n'
    header += ''.join([f'{k}: {v}\r\n' for k, v in headers.items()])
    return header


def render_template(body, headers=None):
    header = response_with_headers({})
    if headers is not None:
        header = response_with_headers(headers)
    else:
        header = response_with_headers({})
    r = header + '\r\n' + body
    return r.encode(encoding='utf-8')


def redirect(location, headers=None):
    if headers is None:
        headers = {
            'Content-Type': 'text/html',
        }
    headers['Location'] = location
    header = response_with_headers(headers, 302)
    r = header + '\r\n' + ''
    return r.encode(encoding='utf-8')