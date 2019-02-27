import urllib.parse


class Request(object):
    '''
    保存客户端的 request
    '''
    def __init__(self):
        self.method = 'GET'  # 请求方法
        self.path = ''  # 请求的 path
        self.query = {}  # 请求的 query
        self.body = ''  # request body
        self.headers = {}  # request header
        self.cookies = {}  # cookie

    def add_cookies(self):
        '''
        添加 cookies
        '''
        cookies = self.headers.get('Cookie', '')
        kvs = cookies.split('; ')
        for kv in kvs:
            if '=' in kv:
                k, v = kv.split('=')
                self.cookies[k] = v

    def add_headers(self, header):
        '''
        接受 request header
        '''
        lines = header
        for line in lines:
            k, v = line.split(': ', 1)
            self.headers[k] = v
        self.add_cookies()

    def form(self):
        body = urllib.parse.unquote(self.body)
        args = body.split('&')
        f = {}
        for arg in args:
            k, v = arg.split('=')
            f[k] = v
        return f
