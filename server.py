#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PHP 本地服务器启动器 (PyQt5)

用法一：双击运行 → 打开 GUI 管理界面
用法二：将 HTML/PHP 文件拖拽到窗口 → 自动用 localhost 在浏览器打开
用法三：将文件直接拖到 server.py 脚本上 → 同上
"""

import os
import sys
import json
import socket
import base64
import urllib.request
import urllib.error
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QSpinBox,
    QFileDialog, QSplitter, QStackedWidget, QMessageBox, QFrame, QGroupBox
)
from PyQt5.QtCore import Qt, QProcess, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QTextCursor

SCRIPT_DIR = str(Path(__file__).parent.resolve())
CONFIG_FILE = os.path.join(SCRIPT_DIR, '.server_config.json')

# ═══════════════════════════════════════════════════════════════════════════════
# 全局样式
# ═══════════════════════════════════════════════════════════════════════════════

STYLE_SHEET = """
QMainWindow { background-color: #F0F2F5; }
#sidebar {
    background-color: #E8ECF1;
    border-right: 1px solid #D0D5DD;
    min-width: 180px;
    max-width: 300px;
}
#drop_hint {
    background-color: #eef6ff;
    color: #2096ff;
    border: 2px dashed #2096ff;
    border-radius: 8px;
    font-size: 11pt;
    padding: 12px;
}
QGroupBox {
    font-weight: bold;
    border: 1px solid #D5D8DC;
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 16px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}
QLineEdit, QSpinBox {
    border: 1px solid #D5D8DC;
    border-radius: 4px;
    padding: 6px;
    background-color: white;
}
QLineEdit:focus { border: 1px solid #3498DB; }
QPushButton {
    border: 1px solid #BDC3C7;
    border-radius: 4px;
    padding: 8px 16px;
    background-color: #ECF0F1;
}
QPushButton:hover { background-color: #D5D8DC; }
QPushButton#start_btn {
    background-color: #27AE60;
    color: white;
    border: none;
    font-weight: bold;
    padding: 10px 24px;
}
QPushButton#start_btn:hover { background-color: #219A52; }
QPushButton#start_btn:disabled { background-color: #A8D5BA; }
QPushButton#stop_btn {
    background-color: #E74C3C;
    color: white;
    border: none;
    font-weight: bold;
    padding: 10px 24px;
}
QPushButton#stop_btn:hover { background-color: #C0392B; }
QPushButton#stop_btn:disabled { background-color: #F5B7B1; }
QPushButton#browse_btn {
    background-color: #3498DB;
    color: white;
    border: none;
}
QPushButton#browse_btn:hover { background-color: #2980B9; }
QTextEdit#log_view {
    font-family: "Consolas", "Courier New", monospace;
    font-size: 10pt;
    background-color: #1E1E1E;
    color: #D4D4D4;
    border: 1px solid #333;
    border-radius: 4px;
    padding: 8px;
}
#status_label { font-size: 11pt; }
QLabel#sidebar_title {
    font-size: 12pt;
    font-weight: bold;
    color: #2C3E50;
    padding: 12px 8px 4px 8px;
}
#sidebar_btn {
    text-align: left;
    border: none;
    border-radius: 4px;
    padding: 10px 16px;
    background: transparent;
    font-size: 10pt;
}
#sidebar_btn:hover { background-color: #D5D8DC; }
#sidebar_btn[active="true"] {
    background-color: #3498DB;
    color: white;
}
"""


# ═══════════════════════════════════════════════════════════════════════════════
# 工具函数
# ═══════════════════════════════════════════════════════════════════════════════

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
                # 兼容旧配置（无 php_path 字段）
                if 'php_path' not in cfg:
                    cfg['php_path'] = r'C:\php\php.exe'
                if 'generator_path' not in cfg:
                    cfg['generator_path'] = os.path.join(SCRIPT_DIR, 'sidebar-generator.html')
                if 'github_token' not in cfg:
                    cfg['github_token'] = ''
                if 'github_repo' not in cfg:
                    cfg['github_repo'] = ''
                if 'github_branch' not in cfg:
                    cfg['github_branch'] = 'gh-pages'
                return cfg
        except:
            pass
    return {'port': 8080, 'folder': SCRIPT_DIR, 'php_path': r'C:\php\php.exe',
            'generator_path': os.path.join(SCRIPT_DIR, 'sidebar-generator.html'),
            'github_token': '', 'github_repo': '', 'github_branch': 'gh-pages'}

def save_config(cfg):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=2)

def is_port_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) != 0

def file_to_url(file_path, folder, port):
    """将文件绝对路径转为 localhost URL
    .md 文件走 docsify Hash 路由: /#/xxx/file (去掉 .md)
    .html/.php 直连: /xxx/file.ext
    """
    folder = folder.rstrip('\\').rstrip('/')
    fp = os.path.abspath(file_path)
    if not fp.lower().startswith(folder.lower()):
        return None
    rel = fp[len(folder)+1:].replace('\\', '/')
    ext = os.path.splitext(rel)[1].lower()
    if ext == '.md':
        # docsify Hash 路由，去掉 .md 后缀
        rel_no_ext = rel[:-3]
        return 'http://localhost:%d/#/%s' % (port, rel_no_ext)
    return 'http://localhost:%d/%s' % (port, rel)


# ═══════════════════════════════════════════════════════════════════════════════
# 日志控件
# ═══════════════════════════════════════════════════════════════════════════════

class LogWidget(QTextEdit):
    MAX_LINES = 800
    FLUSH_MS = 100

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("log_view")
        self.setReadOnly(True)
        self._buffer = []
        self._flush_timer = QTimer(self)
        self._flush_timer.timeout.connect(self._flush)
        self._flush_timer.setSingleShot(True)

    def log(self, msg, color="#D4D4D4"):
        self._buffer.append((msg, color))
        if not self._flush_timer.isActive():
            self._flush_timer.start(self.FLUSH_MS)

    def _flush(self):
        if not self._buffer:
            return
        html_parts = []
        for msg, color in self._buffer:
            escaped = msg.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            html_parts.append(f'<span style="color:{color}">{escaped}</span>')
        self._buffer.clear()

        self.moveCursor(QTextCursor.End)
        self.insertHtml('<br>'.join(html_parts) + '<br>')

        # 裁剪旧行
        doc = self.document()
        while doc.blockCount() > self.MAX_LINES:
            cursor = QTextCursor(doc.firstBlock())
            cursor.select(QTextCursor.BlockUnderCursor)
            cursor.removeSelectedText()
            cursor.deleteChar()

        self.moveCursor(QTextCursor.End)


# ═══════════════════════════════════════════════════════════════════════════════
# 主窗口
# ═══════════════════════════════════════════════════════════════════════════════

class ServerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cfg = load_config()
        self.process = None
        self.running = False

        self.setWindowTitle("PHP 本地服务器")
        self.resize(880, 720)
        self.setMinimumSize(600, 420)
        self.setStyleSheet(STYLE_SHEET)
        self.setAcceptDrops(True)

        self._init_ui()
        self._update_status_ui()

    # ── UI 初始化 ──────────────────────────────────────────────────────────

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # ── 侧边栏 ──
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setMinimumWidth(160)
        sidebar.setMaximumWidth(220)
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(0, 0, 0, 0)
        sb_layout.setSpacing(2)

        title = QLabel("PHP Server")
        title.setObjectName("sidebar_title")
        sb_layout.addWidget(title)

        def make_btn(text, page_name):
            btn = QPushButton(text)
            btn.setObjectName("sidebar_btn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda: self._show_page(page_name))
            sb_layout.addWidget(btn)
            return btn

        self.btn_control = make_btn("⚡ 服务器控制", "control")
        self.btn_log = make_btn("📋 日志", "log")
        self.btn_tool = make_btn("🔧 侧边栏生成器", "generator")
        self.btn_deploy = make_btn("🚀 GitHub Pages", "deploy")
        sb_layout.addStretch()

        # ── 内容区 ──
        self.stack = QStackedWidget()

        # 页面 0：控制面板
        self.page_control = QWidget()
        self._build_control_page()
        self.stack.addWidget(self.page_control)

        # 页面 1：日志
        self.page_log = QWidget()
        self._build_log_page()
        self.stack.addWidget(self.page_log)

        # 页面 2：侧边栏生成器
        self.page_generator = QWidget()
        self._build_generator_page()
        self.stack.addWidget(self.page_generator)

        # 页面 3：GitHub Pages 部署
        self.page_deploy = QWidget()
        self._build_deploy_page()
        self.stack.addWidget(self.page_deploy)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(sidebar)
        splitter.addWidget(self.stack)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([200, 480])
        main_layout.addWidget(splitter)

        # 默认选中控制页
        self._show_page("control")

    def _build_control_page(self):
        layout = QVBoxLayout(self.page_control)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 状态条
        self.status_label = QLabel("● 未启动")
        self.status_label.setObjectName("status_label")
        self.status_label.setStyleSheet("color: #95A5A6; font-size: 12pt; font-weight: bold;")
        layout.addWidget(self.status_label)

        # 文件夹选择
        group = QGroupBox("网站根目录")
        g_layout = QVBoxLayout(group)
        row = QHBoxLayout()
        self.folder_input = QLineEdit(self.cfg['folder'])
        row.addWidget(self.folder_input)
        browse = QPushButton("浏览...")
        browse.setObjectName("browse_btn")
        browse.setCursor(Qt.PointingHandCursor)
        browse.clicked.connect(self._browse_folder)
        row.addWidget(browse)
        g_layout.addLayout(row)
        layout.addWidget(group)

        # PHP 路径 + 端口
        group2 = QGroupBox("PHP 服务器")
        g2_layout = QVBoxLayout(group2)

        # PHP 路径
        php_row = QHBoxLayout()
        php_row.addWidget(QLabel("PHP 路径:"))
        self.php_input = QLineEdit(self.cfg.get('php_path', r'C:\php\php.exe'))
        php_row.addWidget(self.php_input)
        browse_php = QPushButton("浏览...")
        browse_php.setObjectName("browse_btn")
        browse_php.setCursor(Qt.PointingHandCursor)
        browse_php.clicked.connect(self._browse_php)
        php_row.addWidget(browse_php)
        g2_layout.addLayout(php_row)

        # 端口
        port_row = QHBoxLayout()
        port_row.addWidget(QLabel("端口号:"))
        self.port_input = QSpinBox()
        self.port_input.setRange(1024, 65535)
        self.port_input.setValue(self.cfg['port'])
        port_row.addWidget(self.port_input)
        port_row.addStretch()
        g2_layout.addLayout(port_row)

        layout.addWidget(group2)

        # 按钮
        btn_row = QHBoxLayout()
        self.start_btn = QPushButton("▶ 启动服务器")
        self.start_btn.setObjectName("start_btn")
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.clicked.connect(self._start)
        btn_row.addWidget(self.start_btn)

        self.stop_btn = QPushButton("■ 停止")
        self.stop_btn.setObjectName("stop_btn")
        self.stop_btn.setCursor(Qt.PointingHandCursor)
        self.stop_btn.clicked.connect(self._stop)
        btn_row.addWidget(self.stop_btn)

        self.open_btn = QPushButton("🌐 浏览器打开")
        self.open_btn.setCursor(Qt.PointingHandCursor)
        self.open_btn.clicked.connect(self._open_browser)
        btn_row.addWidget(self.open_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        # 拖拽提示
        drop_hint = QLabel(
            "📂 将 .html / .php 文件拖拽到此窗口\n"
            "     → 自动用 http://localhost 打开\n\n"
            "💡 也可将文件直接拖到 server.py 图标上"
        )
        drop_hint.setObjectName("drop_hint")
        drop_hint.setAlignment(Qt.AlignCenter)
        drop_hint.setWordWrap(True)
        layout.addWidget(drop_hint)

        layout.addStretch()

    def _build_log_page(self):
        layout = QVBoxLayout(self.page_log)
        layout.setContentsMargins(0, 0, 0, 0)
        self.log_view = LogWidget()
        layout.addWidget(self.log_view)

    def _build_generator_page(self):
        layout = QVBoxLayout(self.page_generator)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("侧边栏索引生成器")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #2C3E50;")
        layout.addWidget(title)

        desc = QLabel(
            "拖入 md 文件夹自动扫描子目录，生成 _sidebar.md 索引文件。\n"
            "支持穿透子文件夹、中文路径，生成后可复制或下载。"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #7F8C8D; font-size: 10pt;")
        layout.addWidget(desc)

        # 提示
        hint = QLabel(
            "💡 请先在「服务器控制」中启动服务器，\n"
            "   然后点击下方按钮在浏览器中打开生成器。"
        )
        hint.setWordWrap(True)
        hint.setStyleSheet(
            "background: #FFF3CD; border: 1px solid #FFEEBA; border-radius: 6px;"
            "padding: 12px; color: #856404; font-size: 10pt;")
        layout.addWidget(hint)

        # 生成器 HTML 路径
        gen_group = QGroupBox("生成器 HTML 路径")
        gen_layout = QHBoxLayout(gen_group)
        default_generator = os.path.join(SCRIPT_DIR, 'sidebar-generator.html')
        self.generator_input = QLineEdit(self.cfg.get('generator_path', default_generator))
        gen_layout.addWidget(self.generator_input)
        browse_gen = QPushButton("浏览...")
        browse_gen.setObjectName("browse_btn")
        browse_gen.setCursor(Qt.PointingHandCursor)
        browse_gen.clicked.connect(self._browse_generator)
        gen_layout.addWidget(browse_gen)
        layout.addWidget(gen_group)

        # 按钮行
        btn_layout = QHBoxLayout()

        self.open_generator_btn = QPushButton("🌐 在浏览器中打开生成器")
        self.open_generator_btn.setObjectName("start_btn")
        self.open_generator_btn.setCursor(Qt.PointingHandCursor)
        self.open_generator_btn.clicked.connect(self._open_generator)
        btn_layout.addWidget(self.open_generator_btn)

        open_local_btn = QPushButton("📄 本地打开 HTML 文件")
        open_local_btn.setCursor(Qt.PointingHandCursor)
        open_local_btn.clicked.connect(self._open_generator_local)
        btn_layout.addWidget(open_local_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        layout.addStretch()

    # ── 侧边栏生成器 ─────────────────────────────────────────────────────

    def _open_generator(self):
        port = self.cfg.get('port', 8080)
        if self.running:
            url = f'http://localhost:{port}/sidebar-generator.html'
            self._log(f'打开生成器: {url}', "#4EC9B0")
            os.startfile(url)
        else:
            QMessageBox.information(self, "提示",
                "服务器未启动，请先在「服务器控制」中启动服务器。")

    def _open_generator_local(self):
        gen_path = self.generator_input.text().strip()
        if os.path.exists(gen_path):
            os.startfile(gen_path)
        else:
            QMessageBox.critical(self, "错误", f"文件未找到:\n{gen_path}")

    def _browse_generator(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择侧边栏生成器 HTML", self.generator_input.text(),
            "HTML 文件 (*.html *.htm);;所有文件 (*.*)")
        if path:
            self.generator_input.setText(path)
            self.cfg['generator_path'] = path
            save_config(self.cfg)

    # ── GitHub Pages 部署 ─────────────────────────────────────────────────

    def _build_deploy_page(self):
        layout = QVBoxLayout(self.page_deploy)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)

        title = QLabel("部署到 GitHub Pages")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #2C3E50;")
        layout.addWidget(title)

        desc = QLabel("通过 GitHub API 直接上传文件，无需安装 git。")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #7F8C8D; font-size: 10pt;")
        layout.addWidget(desc)

        # Token
        token_group = QGroupBox("Personal Access Token")
        token_layout = QHBoxLayout(token_group)
        self.token_input = QLineEdit(self.cfg.get('github_token', ''))
        self.token_input.setEchoMode(QLineEdit.Password)
        self.token_input.setPlaceholderText("ghp_xxxxxxxxxxxxxxxxxxxx")
        token_layout.addWidget(self.token_input)
        layout.addWidget(token_group)

        # 仓库 + 分支
        repo_group = QGroupBox("仓库")
        repo_layout = QVBoxLayout(repo_group)
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("仓库:"))
        self.repo_input = QLineEdit(self.cfg.get('github_repo', ''))
        self.repo_input.setPlaceholderText("owner/repo")
        row1.addWidget(self.repo_input)
        repo_layout.addLayout(row1)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("分支:"))
        self.branch_input = QLineEdit(self.cfg.get('github_branch', 'gh-pages'))
        row2.addWidget(self.branch_input)
        row2.addStretch()
        repo_layout.addLayout(row2)
        layout.addWidget(repo_group)

        # 提交信息
        commit_group = QGroupBox("提交信息")
        commit_layout = QHBoxLayout(commit_group)
        commit_layout.addWidget(QLabel("Commit:"))
        self.commit_msg = QLineEdit("更新文档")
        commit_layout.addWidget(self.commit_msg)
        layout.addWidget(commit_group)

        # 操作按钮
        btn_layout = QHBoxLayout()

        save_cfg_btn = QPushButton("💾 保存设置")
        save_cfg_btn.setCursor(Qt.PointingHandCursor)
        save_cfg_btn.clicked.connect(self._save_deploy_config)
        btn_layout.addWidget(save_cfg_btn)

        self.deploy_btn = QPushButton("🚀 部署到 GitHub Pages")
        self.deploy_btn.setObjectName("start_btn")
        self.deploy_btn.setCursor(Qt.PointingHandCursor)
        self.deploy_btn.clicked.connect(self._deploy_api)
        btn_layout.addWidget(self.deploy_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # 日志
        log_label = QLabel("操作日志")
        log_label.setStyleSheet("font-weight: bold; color: #2C3E50;")
        layout.addWidget(log_label)

        self.deploy_log = LogWidget()
        layout.addWidget(self.deploy_log)

        # 状态条
        self.deploy_status = QLabel("")
        self.deploy_status.setWordWrap(True)
        self.deploy_status.setStyleSheet("color: #7F8C8D; font-size: 9pt;")
        layout.addWidget(self.deploy_status)

    def _save_deploy_config(self):
        self.cfg['github_token'] = self.token_input.text().strip()
        self.cfg['github_repo'] = self.repo_input.text().strip()
        self.cfg['github_branch'] = self.branch_input.text().strip() or 'gh-pages'
        save_config(self.cfg)
        self.deploy_log.log("设置已保存", "#4EC9B0")

    def _api_request(self, method, path, data=None):
        """调用 GitHub API，返回 (status, body_json)"""
        token = self.cfg.get('github_token', '')
        url = f'https://api.github.com{path}'
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'server-py',
        }
        body = json.dumps(data).encode('utf-8') if data else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.status, json.loads(resp.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            err_body = e.read().decode('utf-8', errors='replace')
            return e.code, json.loads(err_body) if err_body else {'message': str(e)}

    # ── 后台上传线程 ─────────────────────────────────────────────────────

    def _deploy_api(self):
        token = self.token_input.text().strip()
        repo = self.repo_input.text().strip()
        branch = self.branch_input.text().strip() or 'gh-pages'
        msg = self.commit_msg.text().strip() or '更新文档'

        if not token or not repo:
            QMessageBox.critical(self, "错误", "请填写 Token 和仓库地址")
            return

        # 保存到配置
        self._save_deploy_config()

        folder = self.cfg.get('folder', SCRIPT_DIR)
        base_url = f'/repos/{repo}/contents'

        # 收集文件
        files = []
        excludes = {'.git', '.server_config.json', '__pycache__', '.qoder'}
        for root, dirs, fnames in os.walk(folder):
            dirs[:] = [d for d in dirs if d not in excludes]
            for fn in fnames:
                full = os.path.join(root, fn)
                rel = os.path.relpath(full, folder).replace('\\', '/')
                if any(rel.startswith(e + '/') or rel == e for e in excludes):
                    continue
                files.append((full, rel))

        self.deploy_btn.setEnabled(False)
        self.deploy_log.log(f'>>> 开始部署 ({len(files)} 个文件)...', "#569CD6")
        self.deploy_log.log(f'仓库: {repo}  分支: {branch}', "#D4D4D4")

        self._uploaded = 0
        self._errors = 0
        self._total = len(files)

        def do_upload(file_list, idx):
            if idx >= len(file_list):
                self._on_deploy_done()
                return

            full, rel = file_list[idx]
            with open(full, 'rb') as f:
                content = base64.b64encode(f.read()).decode('ascii')

            # 先查远端文件 SHA（存在则覆盖）
            def after_check():
                status, body = self._api_request('GET',
                    f'{base_url}/{rel}?ref={branch}')
                sha = body.get('sha') if status == 200 else None

                req_data = {
                    'message': msg,
                    'content': content,
                    'branch': branch,
                }
                if sha:
                    req_data['sha'] = sha

                status2, body2 = self._api_request('PUT', f'{base_url}/{rel}', req_data)
                if 200 <= status2 < 300:
                    self._uploaded += 1
                    if self._uploaded % 10 == 0 or self._uploaded == self._total:
                        self.deploy_status.setText(
                            f'进度: {self._uploaded}/{self._total}')
                else:
                    self._errors += 1
                    err_msg = body2.get('message', str(status2))
                    self.deploy_log.log(f'✗ {rel}: {err_msg}', "#CE9178")

                # 下一秒继续下一个
                QTimer.singleShot(200, lambda: do_upload(file_list, idx + 1))

            after_check()

        # 启动上传
        QTimer.singleShot(0, lambda: do_upload(files, 0))

    def _on_deploy_done(self):
        self.deploy_btn.setEnabled(True)
        self.deploy_status.setText(
            f'完成: {self._uploaded} 成功 / {self._errors} 失败 (共 {self._total})')
        if self._errors == 0:
            self.deploy_log.log(f'✅ 部署完成! ({self._uploaded} 个文件)', "#4EC9B0")
        else:
            self.deploy_log.log(
                f'⚠ 部署完成 ({self._uploaded} 成功, {self._errors} 失败)', "#CE9178")

    # ── 页面切换 ──────────────────────────────────────────────────────────

    def _show_page(self, name):
        index = {"control": 0, "log": 1, "generator": 2, "deploy": 3}.get(name, 0)
        self.stack.setCurrentIndex(index)
        for btn, n in [(self.btn_control, "control"), (self.btn_log, "log"),
                       (self.btn_tool, "generator"), (self.btn_deploy, "deploy")]:
            btn.setProperty("active", n == name)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    # ── 状态 ──────────────────────────────────────────────────────────────

    def _update_status_ui(self):
        if self.running:
            self.status_label.setText("● 运行中")
            self.status_label.setStyleSheet("color: #27AE60; font-size: 12pt; font-weight: bold;")
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.open_btn.setEnabled(True)
        else:
            self.status_label.setText("● 未启动")
            self.status_label.setStyleSheet("color: #95A5A6; font-size: 12pt; font-weight: bold;")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.open_btn.setEnabled(False)

    # ── 日志 ──────────────────────────────────────────────────────────────

    def _log(self, msg, color="#D4D4D4"):
        if hasattr(self, 'log_view'):
            self.log_view.log(msg, color)

    # ── 文件夹选择 ────────────────────────────────────────────────────────

    def _browse_folder(self):
        path = QFileDialog.getExistingDirectory(self, "选择网站根目录", self.folder_input.text())
        if path:
            self.folder_input.setText(path)

    def _browse_php(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择 PHP 可执行文件", self.php_input.text(),
            "可执行文件 (*.exe);;所有文件 (*.*)")
        if path:
            self.php_input.setText(path)

    # ── 服务器控制 ────────────────────────────────────────────────────────

    def _start(self):
        folder = self.folder_input.text().strip()
        port = self.port_input.value()
        php_path = self.php_input.text().strip()

        if not os.path.isdir(folder):
            QMessageBox.critical(self, "错误", f"文件夹不存在:\n{folder}")
            return
        if not os.path.isfile(php_path):
            QMessageBox.critical(self, "错误", f"PHP 未找到:\n{php_path}")
            return
        if not is_port_free(port):
            QMessageBox.critical(self, "错误", f"端口 {port} 已被占用")
            return

        self.cfg = {'port': port, 'folder': folder, 'php_path': php_path}
        save_config(self.cfg)

        self._log(f'根目录: {folder}', "#6A9955")
        self._log(f'PHP: {php_path}', "#569CD6")
        self._log(f'命令: php -S localhost:{port}', "#569CD6")
        self._log('正在启动...', "#D4D4D4")

        self.process = QProcess(self)
        self.process.setWorkingDirectory(folder)
        self.process.readyReadStandardOutput.connect(self._on_stdout)
        self.process.finished.connect(self._on_process_finished)
        self.process.start(php_path, ['-S', f'localhost:{port}', '-t', folder])

        if self.process.waitForStarted(3000):
            self.running = True
            self._update_status_ui()
            self._log(f'✓ 服务器已启动: http://localhost:{port}', "#4EC9B0")
        else:
            self._log('✗ 启动失败', "#F44747")
            QMessageBox.critical(self, "错误", "PHP 进程启动失败")

    def _stop(self):
        if self.process and self.process.state() != QProcess.NotRunning:
            self.process.terminate()
            if not self.process.waitForFinished(3000):
                self.process.kill()
                self.process.waitForFinished(1000)
        self.running = False
        self._update_status_ui()
        self._log('■ 服务器已停止', "#CE9178")

    def _on_stdout(self):
        data = self.process.readAllStandardOutput().data().decode('utf-8', errors='replace')
        for line in data.splitlines():
            if line.strip():
                self._log(line.strip())

    def _on_process_finished(self, exit_code, exit_status):
        if self.running:
            self.running = False
            self._update_status_ui()
            self._log(f'进程已退出 (code={exit_code})', "#F44747")

    def _open_browser(self):
        url = f'http://localhost:{self.cfg["port"]}'
        os.startfile(url)

    # ── 拖拽支持 ──────────────────────────────────────────────────────────

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        folder = self.cfg.get('folder', SCRIPT_DIR)
        port = self.cfg.get('port', 8080)
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            ext = os.path.splitext(path)[1].lower()
            if ext in ('.html', '.htm', '.php', '.md'):
                target_url = file_to_url(path, folder, port)
                if target_url:
                    self._log(f'打开: {target_url}', "#4EC9B0")
                    os.startfile(target_url)
                else:
                    self._log(f'⚠ 忽略（不在根目录下）: {os.path.basename(path)}', "#CE9178")

    # ── 关闭 ──────────────────────────────────────────────────────────────

    def closeEvent(self, event):
        if self.running:
            reply = QMessageBox.question(
                self, "确认", "服务器正在运行，确定退出？",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                event.ignore()
                return
            self._stop()
        event.accept()


# ═══════════════════════════════════════════════════════════════════════════════
# 入口
# ═══════════════════════════════════════════════════════════════════════════════

def open_files_via_localhost(files):
    """命令行模式：将传入的文件路径用 localhost 打开"""
    cfg = load_config()
    opened = False
    for f in files:
        ext = os.path.splitext(f)[1].lower()
        if ext in ('.html', '.htm', '.php', '.md'):
            url = file_to_url(f, cfg['folder'], cfg['port'])
            if url:
                os.startfile(url)
                opened = True
            else:
                # 从文件所在目录向上查找配置
                d = os.path.dirname(f)
                while True:
                    p = os.path.join(d, '.server_config.json')
                    if os.path.exists(p):
                        try:
                            with open(p, 'r', encoding='utf-8') as fp:
                                cfg2 = json.load(fp)
                            url = file_to_url(f, cfg2['folder'], cfg2['port'])
                            if url:
                                os.startfile(url)
                                opened = True
                        except:
                            pass
                        break
                    parent = os.path.dirname(d)
                    if parent == d:
                        break
                    d = parent
    return opened

if __name__ == '__main__':
    # 命令行模式：文件拖到 .py 上
    if len(sys.argv) > 1:
        open_files_via_localhost(sys.argv[1:])
    else:
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        window = ServerApp()
        window.show()
        sys.exit(app.exec_())
