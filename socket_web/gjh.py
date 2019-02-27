import socket
import _thread

from socket_web.request import Request


class GJH(object):
    def __init__(self):
        self.e = {
            404: b'HTTP/1.1 404 NOT FOUND\r\n\r\n<h1>404 NOT FOUND</h1>',
        }  # error
        self.routes = {}  # 路由

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
        self.routes.update(new_route)

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
        response = self.routes.get(path, self.error)
        return response(request)

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