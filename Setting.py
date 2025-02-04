class Setting:
    def __init__(self):
        # 允许上传的文件格式
        self.ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'doc', 'docx'}
        # 允许上传的最大size
        self.MAX_FILE_SIZE = 100  # 单位：MB
        # 服务开放端口
        self.PORT = 5000
