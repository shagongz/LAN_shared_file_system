import os
import socket
import tkinter as tk
from tkinter import filedialog
from flask import Flask, render_template, send_from_directory, abort, request, flash, redirect
from werkzeug.utils import secure_filename
from Setting import Setting

# 初始化Flask应用
app = Flask(__name__)
app.secret_key = os.urandom(24)

# 初始化设置
setting = Setting()


# ███ 新增文件夹选择功能 ████████████████████████████████████████████████████
def select_folder():
    """弹出文件夹选择对话框"""
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    folder = filedialog.askdirectory(title="请选择要共享的文件夹")
    root.destroy()

    if not folder:
        print("错误：必须选择共享文件夹")
        exit(1)

    # 创建Upload子目录
    upload_folder = os.path.join(folder, "Upload")
    os.makedirs(upload_folder, exist_ok=True)

    return folder, upload_folder


# 启动时选择文件夹
if setting.PATH == "":
    BASE_DIR, UPLOAD_FOLDER = select_folder()
else:
    BASE_DIR = setting.PATH
    upload_folder = os.path.join(BASE_DIR, "Upload")
    os.makedirs(upload_folder, exist_ok=True)
    UPLOAD_FOLDER = upload_folder
print("共享文件夹：", BASE_DIR)
print("上传文件夹：", UPLOAD_FOLDER)

# ███ 配置参数 ███████████████████████████████████████████████████████████
ALLOWED_EXTENSIONS = setting.ALLOWED_EXTENSIONS
MAX_FILE_SIZE = setting.MAX_FILE_SIZE
HOST_IP = "0.0.0.0"
PORT = setting.PORT

# Flask配置
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE * 1024 * 1024


# ███ 功能函数 █████████████████████████████████████████████████████████████
def get_local_ip():
    """获取本机局域网IP"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        try:
            return socket.gethostbyname(socket.gethostname())
        except:
            return 'localhost'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_directory_structure(rootdir):
    """生成目录结构"""
    structure = {'name': os.path.basename(rootdir), 'children': []}
    try:
        for item in os.listdir(rootdir):
            path = os.path.join(rootdir, item)
            if os.path.isdir(path):
                structure['children'].append(get_directory_structure(path))
            else:
                structure['children'].append({'name': item, 'type': 'file'})
    except PermissionError:
        pass
    return structure


# ███ 路由处理 ███████████████████████████████████████████████████████████████
@app.route('/')
@app.route('/<path:subpath>')
def index(subpath=''):
    current_dir = os.path.join(BASE_DIR, subpath)

    # 安全验证
    if not os.path.abspath(current_dir).startswith(os.path.abspath(BASE_DIR)):
        abort(403)

    try:
        items = os.listdir(current_dir)
    except (FileNotFoundError, NotADirectoryError):
        abort(404)
    except PermissionError:
        abort(403)

    # 面包屑导航
    breadcrumbs = []
    path_parts = subpath.split('/') if subpath else []
    for i in range(len(path_parts)):
        breadcrumbs.append({
            'name': path_parts[i],
            'path': '/'.join(path_parts[:i + 1])
        })

    return render_template('index.html',
                           current_dir=current_dir.replace(BASE_DIR, '').lstrip('\\'),
                           items=items,
                           breadcrumbs=breadcrumbs,
                           base_dir=BASE_DIR,
                           os=os,
                           upload_folder=UPLOAD_FOLDER,
                           allowed_extensions=', '.join(ALLOWED_EXTENSIONS),
                           max_file_size=MAX_FILE_SIZE)


@app.route('/download/<path:filename>')
def download(filename):
    file_path = os.path.join(BASE_DIR, filename)
    if not os.path.abspath(file_path).startswith(os.path.abspath(BASE_DIR)):
        abort(403)
    directory = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    return send_from_directory(directory, file_name, as_attachment=True)


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('未选择文件')
        return redirect(request.referrer)

    file = request.files['file']
    if file.filename == '':
        flash('未选择文件')
        return redirect(request.referrer)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # 处理重名文件
        counter = 1
        name_part, ext_part = os.path.splitext(filename)
        while os.path.exists(save_path):
            save_path = os.path.join(
                app.config['UPLOAD_FOLDER'],
                f"{name_part}_{counter}{ext_part}"
            )
            counter += 1

        try:
            file.save(save_path)
            flash(f'文件上传成功：{os.path.basename(save_path)}')
        except Exception as e:
            flash(f'文件保存失败：{str(e)}')
    else:
        flash('不支持的文件类型')

    return redirect(request.referrer)


# ███ 模板文件 █████████████████████████████████████████████████████████████
if __name__ == '__main__':

    # 启动服务
    local_ip = get_local_ip()
    print("\n" + "=" * 40)
    print(f"共享文件夹：{BASE_DIR}")
    print(f"上传目录：{UPLOAD_FOLDER}")
    print(f"服务已启动！访问地址：")
    print(f"本机访问: http://localhost:{PORT}")
    print(f"局域网访问: http://{local_ip}:{PORT}")
    print("=" * 40 + "\n")

    app.run(host=HOST_IP, port=PORT, debug=False)
