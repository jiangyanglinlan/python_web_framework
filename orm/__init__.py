import json


def save(data, path):
    # 保存数据
    s = json.dumps(data, indent=2, ensure_ascii=False)
    with open(path, 'w+', encoding='utf-8') as f:
        f.write(s)


def load(path):
    with open(path, 'r', encoding='utf-8') as f:
        s = f.read()
        return json.loads(s)


class Model(object):
    @classmethod
    def db_path(cls):
        classname = cls.__name__
        path = f'data/{classname}.txt'
        return path

    @classmethod
    def _new_from_dict(cls, d):
        '''
        初始化数据
        '''
        m = cls({})
        for k, v in d.items():
            setattr(m, k, v)
        return m

    @classmethod
    def new(cls, form, **kwargs):
        '''
        生成示例对象
        '''
        m = cls(form)
        for k, v in kwargs.items():
            # 设置对象额外的属性
            setattr(m, k, v)
        m.save()
        return m

    @classmethod
    def all(cls):
        path = cls.db_path()
        models = load(path)
        ms = [cls._new_from_dict(m) for m in models]
        return ms

    @classmethod
    def find_all(cls, **kwargs):
        '''
        查询符合条件的数据, 返回所有结果
        '''
        ms = []
        k, v = '', ''
        for key, value in kwargs.items():
            k, v = key, value
        all = cls.all()
        for m in all:
            if v == m.__dict__[k]:
                ms.append(m)
        return ms

    @classmethod
    def find_by(cls, **kwargs):
        '''
        查询符合条件的数据, 返回一条结果
        '''
        k, v = '', ''
        for key, value in kwargs.items():
            k, v = key, value
        all = cls.all()
        for m in all:
            if v == m.__dict__[k]:
                return m
        return None

    @classmethod
    def get(cls, id):
        '''
        根据 id 查询
        '''
        return cls.find_by(id=id)

    @classmethod
    def delete(cls, id):
        models = cls.all()
        index = -1
        for i, e in enumerate(models):
            if e.id == id:
                index = i
                break
        if index == -1:
            pass
        else:
            obj = models.pop(index)
            l = [m.__dict__ for m in models]
            path = cls.db_path()
            save(l, path)
            return obj

    def __repr__(self):
        classname = self.__class__.__name__
        properties = [f'{k}: ({v})' for k, v in self.__dict__.items()]
        s = '\n'.join(properties)
        return f'< {classname}\n{s} \n>\n'

    def json(self):
        d = self.__dict__.copy()
        return d

    def save(self):
        models = self.all()
        if self.id is None:
            if len(models) == 0:
                self.id = 1
            else:
                m = models[-1]
                self.id = m.id + 1
            models.append(self)
        else:
            index = -1
            for i, m in enumerate(models):
                if m.id == self.id:
                    index = i
                    break
            models[index] = self
        l = [m.__dict__ for m in models]
        path = self.db_path()
        save(l, path)