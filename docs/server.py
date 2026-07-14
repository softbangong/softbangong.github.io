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
import urllib.parse
import concurrent.futures
import time
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QSpinBox,
    QFileDialog, QSplitter, QStackedWidget, QMessageBox, QFrame, QGroupBox,
    QScrollArea, QComboBox, QSizePolicy, QCheckBox
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
                # 迁移旧的扁平 github 字段到多仓库结构
                if 'github_repos' not in cfg:
                    repos = {}
                    old_repo = cfg.pop('github_repo', '')
                    if old_repo:
                        repos[old_repo] = {
                            'token': cfg.pop('github_token', ''),
                            'branch': cfg.pop('github_branch', 'main'),
                            'subfolder': cfg.pop('github_subfolder', ''),
                            'exclude': cfg.pop('github_exclude',
                                '.git, .server_config.json, __pycache__, .qoder, 1.exe'),
                        }
                    # 清理残留旧字段
                    for k in ('github_token', 'github_branch', 'github_subfolder', 'github_exclude'):
                        cfg.pop(k, None)
                    cfg['github_repos'] = repos
                    cfg['github_active'] = old_repo if repos else ''
                return cfg
        except:
            pass
    return {'port': 8080, 'folder': SCRIPT_DIR, 'php_path': r'C:\php\php.exe',
            'generator_path': os.path.join(SCRIPT_DIR, 'sidebar-generator.html'),
            'github_repos': {}, 'github_active': ''}

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
# 部署后台线程
# ═══════════════════════════════════════════════════════════════════════════════

class DeployWorker(QThread):
    """部署工作线程 —— 使用 Git Data API 将所有文件变更合入一次原子提交

    流程：获取基础树 → 并行创建 Blob → 创建 Tree → 创建 Commit → 更新分支引用
    优势：只需 1 次提交，彻底消除并行 SHA 冲突问题
    """
    log_signal = pyqtSignal(str, str)
    progress_signal = pyqtSignal(int, int)
    done_signal = pyqtSignal(int, int)

    def __init__(self, files, token, repo, branch, msg, sync_delete=False, subfolder='', threads=8):
        super().__init__()
        self.files = files
        self.token = token
        self.repo = repo
        self.branch = branch
        self.msg = msg
        self.sync_delete = sync_delete
        self.subfolder = subfolder
        self.threads = threads
        self._stopped = False

    def _api(self, method, path, data=None):
        return ServerApp._api_request_sync(self.token, method, path, data)

    # ── Phase 0: 获取远端基础信息 ─────────────────────────────────────────

    def _get_base_tree_info(self):
        """获取分支最新 commit SHA、tree SHA 和 ref 路径

        返回 (parent_sha, tree_sha, ref_path)
        - parent_sha: 分支最新 commit 的 SHA，None 表示分支不存在
        - tree_sha:   commit 对应 tree 的 SHA，None 表示无基础树
        - ref_path:   分支 ref API 路径（用于后续更新）
        """
        ref_path = f'/repos/{self.repo}/git/refs/heads/{self.branch}'
        status, ref_data = self._api('GET', ref_path)
        if status != 200:
            return (None, None, ref_path)
        parent_sha = ref_data.get('object', {}).get('sha')
        if not parent_sha:
            return (None, None, ref_path)
        status2, commit_data = self._api(
            'GET', f'/repos/{self.repo}/git/commits/{parent_sha}')
        if status2 != 200:
            return (parent_sha, None, ref_path)
        tree_sha = commit_data.get('tree', {}).get('sha')
        return (parent_sha, tree_sha, ref_path)

    # ── Phase 1: 创建 Blob（可并行）──────────────────────────────────────

    def _create_blob(self, full, rel):
        """读取本地文件并创建 Git Blob，返回 (rel, ok, sha|err, mode)"""
        if self._stopped:
            return (rel, False, '已停止', '100644')
        try:
            with open(full, 'rb') as f:
                content = base64.b64encode(f.read()).decode('ascii')
            mode = '100644'
            ext = os.path.splitext(full)[1].lower()
            if ext in ('.exe', '.bat', '.cmd', '.com'):
                mode = '100755'
            blob_data = {'content': content, 'encoding': 'base64'}
            status, resp = self._api(
                'POST', f'/repos/{self.repo}/git/blobs', blob_data)
            if status == 201:
                return (rel, True, resp['sha'], mode)
            return (rel, False, resp.get('message', f'HTTP {status}'), mode)
        except Exception as e:
            return (rel, False, str(e), '100644')

    # ── 删除辅助 ─────────────────────────────────────────────────────────

    def _delete_one(self, rel):
        """删除单个远端文件，返回 (rel, ok, info)"""
        if self._stopped:
            return (rel, False, '已停止')
        encoded_rel = urllib.parse.quote(rel, safe='')
        base_url = f'/repos/{self.repo}/contents'
        status, body = self._api(
            'GET', f'{base_url}/{encoded_rel}?ref={self.branch}')
        if status != 200:
            return (rel, False, f'获取信息失败({status})')
        sha = body.get('sha')
        if not sha:
            return (rel, False, '无SHA')
        req_data = {'message': self.msg + ' (删除)',
                     'branch': self.branch, 'sha': sha}
        status2, body2 = self._api(
            'DELETE', f'{base_url}/{encoded_rel}', req_data)
        if 200 <= status2 < 300:
            return (rel, True, '已删除')
        return (rel, False, body2.get('message', str(status2)))

    def _get_remote_tree(self):
        """获取远端仓库完整文件列表"""
        path = f'/repos/{self.repo}/git/trees/{self.branch}?recursive=1'
        status, body = self._api('GET', path)
        if status != 200:
            self.log_signal.emit(
                f'  获取远端文件列表失败({status})', "#CE9178")
            return []
        files = []
        for item in body.get('tree', []):
            if item.get('type') == 'blob':
                files.append(item.get('path', ''))
        return files

    # ── 主流程 ────────────────────────────────────────────────────────────

    def run(self):
        total = len(self.files)
        local_paths = {rel for _, rel in self.files}

        # ── Phase 0: 获取远端基础 commit 和 tree ──
        self.log_signal.emit('>>> 获取远端仓库状态...', "#569CD6")
        parent_sha, base_tree_sha, ref_path = self._get_base_tree_info()
        if parent_sha:
            self.log_signal.emit(
                f'    分支 {self.branch}  ← {parent_sha[:8]}...', "#D4D4D4")
        else:
            self.log_signal.emit(
                '    ⚠ 分支不存在，将创建初始提交', "#CE9178")

        # ── Phase 1: 并行创建 Blob ──
        self.log_signal.emit(
            f'>>> 并行创建 Blob ({total} 个文件, {self.threads}线程)...',
            "#569CD6")

        tree_entries = []
        blob_errors = 0

        with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.threads) as executor:
            future_map = {
                executor.submit(self._create_blob, full, rel): (full, rel)
                for full, rel in self.files
            }

            for future in concurrent.futures.as_completed(future_map):
                if self._stopped:
                    for f in future_map:
                        f.cancel()
                    break
                rel, ok, sha_or_err, mode = future.result()
                done = len(tree_entries) + blob_errors + 1
                if ok:
                    tree_entries.append({
                        'path': rel, 'mode': mode,
                        'type': 'blob', 'sha': sha_or_err
                    })
                    self.log_signal.emit(
                        f'  ✓ [{done}/{total}] Blob: {rel}', "#4EC9B0")
                else:
                    blob_errors += 1
                    self.log_signal.emit(
                        f'  ✗ [{done}/{total}] Blob失败: {rel} → {sha_or_err}',
                        "#CE9178")
                if done % 10 == 0 or done == total:
                    self.progress_signal.emit(done, total)

        if self._stopped:
            self.done_signal.emit(0, 0)
            return

        if not tree_entries:
            self.log_signal.emit(
                f'  ✗ 没有成功创建任何 Blob ({blob_errors} 失败)', "#CE9178")
            self.done_signal.emit(0, blob_errors)
            return

        self.log_signal.emit(
            f'    Blob 完成: {len(tree_entries)} 成功, {blob_errors} 失败',
            "#D4D4D4")

        # ── Phase 2: 创建 Tree（原子合并所有变更）──
        self.log_signal.emit(
            f'>>> 创建 Tree ({len(tree_entries)} 条目)...', "#569CD6")

        tree_data = {'tree': tree_entries}
        if base_tree_sha:
            tree_data['base_tree'] = base_tree_sha

        status, tree_resp = self._api(
            'POST', f'/repos/{self.repo}/git/trees', tree_data)
        if status != 201:
            err = tree_resp.get('message', f'HTTP {status}') if isinstance(
                tree_resp, dict) else f'HTTP {status}'
            self.log_signal.emit(
                f'  ✗ 创建 Tree 失败: {err}', "#CE9178")
            self.done_signal.emit(0, total)
            return
        new_tree_sha = tree_resp['sha']
        self.log_signal.emit(
            f'    Tree SHA: {new_tree_sha[:8]}...', "#4EC9B0")

        # ── Phase 3: 创建 Commit ──
        self.log_signal.emit('>>> 创建 Commit...', "#569CD6")
        commit_data = {'message': self.msg, 'tree': new_tree_sha}
        if parent_sha:
            commit_data['parents'] = [parent_sha]

        status, commit_resp = self._api(
            'POST', f'/repos/{self.repo}/git/commits', commit_data)
        if status != 201:
            err = commit_resp.get('message', f'HTTP {status}') if isinstance(
                commit_resp, dict) else f'HTTP {status}'
            self.log_signal.emit(
                f'  ✗ 创建 Commit 失败: {err}', "#CE9178")
            self.done_signal.emit(0, total)
            return
        new_commit_sha = commit_resp['sha']
        self.log_signal.emit(
            f'    Commit: {new_commit_sha[:8]}...', "#4EC9B0")

        # ── Phase 4: 更新／创建分支引用 ──
        self.log_signal.emit('>>> 更新分支引用...', "#569CD6")
        if parent_sha is None:
            # 分支不存在 → 创建
            ref_create_data = {
                'ref': f'refs/heads/{self.branch}',
                'sha': new_commit_sha
            }
            status, ref_resp = self._api(
                'POST', f'/repos/{self.repo}/git/refs', ref_create_data)
        else:
            # 分支存在 → 更新
            update_data = {'sha': new_commit_sha, 'force': False}
            status, ref_resp = self._api('PATCH', ref_path, update_data)

        if 200 <= status < 300:
            uploaded = len(tree_entries)
            self.log_signal.emit(
                f'✅ 上传完成 ({uploaded} 文件 → 1 次提交)', "#4EC9B0")
        else:
            err = ref_resp.get('message', f'HTTP {status}') if isinstance(
                ref_resp, dict) else f'HTTP {status}'
            self.log_signal.emit(
                f'  ✗ 更新分支失败: {err}', "#CE9178")
            self.log_signal.emit(
                f'  ⚠ 文件已上传但未提交。Commit: {new_commit_sha[:8]}... '
                f'可手动 git update-ref refs/heads/{self.branch} '
                f'{new_commit_sha}', "#CE9178")
            self.done_signal.emit(0, total)
            return

        # ── Phase 5: 同步删除远端多余文件 ──
        if self.sync_delete and not self._stopped:
            self.log_signal.emit('', "#D4D4D4")
            self.log_signal.emit(
                '>>> 检查远端多余文件...', "#569CD6")

            remote_files = self._get_remote_tree()
            prefix = (self.subfolder.strip('/') +
                      '/') if self.subfolder else ''
            to_delete = []
            for rp in remote_files:
                if prefix and not rp.startswith(prefix):
                    continue
                rel = rp[len(prefix):] if prefix else rp
                if rel and rel not in local_paths:
                    to_delete.append(rel)

            if to_delete:
                self.log_signal.emit(
                    f'  发现 {len(to_delete)} 个远端多余文件，开始删除...',
                    "#CE9178")
                del_total = len(to_delete)
                del_ok = 0
                del_err = 0

                with concurrent.futures.ThreadPoolExecutor(
                        max_workers=3) as executor:
                    del_futures = {
                        executor.submit(self._delete_one, rel): rel
                        for rel in to_delete
                    }
                    for future in concurrent.futures.as_completed(del_futures):
                        if self._stopped:
                            for f in del_futures:
                                f.cancel()
                            break
                        rel, ok, info = future.result()
                        if ok:
                            del_ok += 1
                            self.log_signal.emit(
                                f'  🗑 [{del_ok}/{del_total}] 已删除: {rel}',
                                "#CE9178")
                        else:
                            del_err += 1
                            self.log_signal.emit(
                                f'  ✗ 删除失败: {rel} → {info}', "#CE9178")
                self.log_signal.emit(
                    f'  删除完成: {del_ok} 成功 / {del_err} 失败', "#569CD6")
            else:
                self.log_signal.emit(
                    '  没有需要删除的远端文件', "#4EC9B0")

        self.done_signal.emit(len(tree_entries), blob_errors)


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

        def wrap_scroll(widget):
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(widget)
            scroll.setFrameShape(QFrame.NoFrame)
            return scroll

        # 页面 0：控制面板
        self.page_control = QWidget()
        self._build_control_page()
        self.stack.addWidget(wrap_scroll(self.page_control))

        # 页面 1：日志
        self.page_log = QWidget()
        self._build_log_page()
        self.stack.addWidget(wrap_scroll(self.page_log))

        # 页面 2：侧边栏生成器
        self.page_generator = QWidget()
        self._build_generator_page()
        self.stack.addWidget(wrap_scroll(self.page_generator))

        # 页面 3：GitHub Pages 部署
        self.page_deploy = QWidget()
        self._build_deploy_page()
        self.stack.addWidget(wrap_scroll(self.page_deploy))

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

        desc = QLabel("通过 GitHub API 直接上传文件，无需安装 git。可添加多个仓库并分别保存配置。")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #7F8C8D; font-size: 10pt;")
        layout.addWidget(desc)

        # ── 仓库选择器 ──
        selector_group = QGroupBox("选择仓库")
        sel_layout = QHBoxLayout(selector_group)
        sel_layout.addWidget(QLabel("仓库:"))
        self.repo_combo = QComboBox()
        self.repo_combo.setMinimumHeight(28)
        self.repo_combo.currentIndexChanged.connect(self._on_repo_changed)
        sel_layout.addWidget(self.repo_combo, 1)
        add_repo_btn = QPushButton("➕ 添加")
        add_repo_btn.setCursor(Qt.PointingHandCursor)
        add_repo_btn.clicked.connect(self._add_repo)
        sel_layout.addWidget(add_repo_btn)
        self.remove_repo_btn = QPushButton("➖ 移除")
        self.remove_repo_btn.setCursor(Qt.PointingHandCursor)
        self.remove_repo_btn.clicked.connect(self._remove_repo)
        sel_layout.addWidget(self.remove_repo_btn)
        layout.addWidget(selector_group)

        # ── 仓库设置 ──
        repo_group = QGroupBox("仓库设置")
        repo_rl = QVBoxLayout(repo_group)
        repo_rl.setSpacing(6)

        row_r = QHBoxLayout()
        row_r.addWidget(QLabel("仓库:"))
        self.repo_input = QLineEdit()
        self.repo_input.setPlaceholderText("owner/repo")
        self.repo_input.textChanged.connect(lambda: self._on_field_changed())
        row_r.addWidget(self.repo_input)
        repo_rl.addLayout(row_r)

        row_b = QHBoxLayout()
        row_b.addWidget(QLabel("分支:"))
        self.branch_input = QLineEdit()
        self.branch_input.setPlaceholderText("main / gh-pages")
        self.branch_input.textChanged.connect(lambda: self._on_field_changed())
        row_b.addWidget(self.branch_input)
        repo_rl.addLayout(row_b)

        # Token（放在分支下方）
        row_t = QHBoxLayout()
        row_t.addWidget(QLabel("Token:"))
        self.token_input = QLineEdit()
        self.token_input.setEchoMode(QLineEdit.Password)
        self.token_input.setPlaceholderText("ghp_xxxxxxxxxxxxxxxxxxxx")
        self.token_input.textChanged.connect(lambda: self._on_field_changed())
        row_t.addWidget(self.token_input)
        self.token_show = QPushButton("👁 显示")
        self.token_show.setMinimumWidth(60)
        self.token_show.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.token_show.setCursor(Qt.PointingHandCursor)
        self.token_show.setCheckable(True)
        self.token_show.clicked.connect(self._toggle_token)
        row_t.addWidget(self.token_show)
        repo_rl.addLayout(row_t)

        # 推送文件夹（必填）
        sub_row = QHBoxLayout()
        sub_row.addWidget(QLabel("推送文件夹:"))
        self.subfolder_input = QLineEdit()
        self.subfolder_input.setPlaceholderText("必填，不能为空")
        self.subfolder_input.textChanged.connect(lambda: self._on_field_changed())
        sub_row.addWidget(self.subfolder_input)
        browse_sub = QPushButton("选择...")
        browse_sub.setObjectName("browse_btn")
        browse_sub.setCursor(Qt.PointingHandCursor)
        browse_sub.clicked.connect(self._browse_subfolder)
        sub_row.addWidget(browse_sub)
        repo_rl.addLayout(sub_row)

        # 排除文件
        ex_row = QHBoxLayout()
        ex_row.addWidget(QLabel("排除文件:"))
        self.exclude_input = QLineEdit()
        self.exclude_input.setPlaceholderText(".git, .server_config.json, __pycache__")
        self.exclude_input.textChanged.connect(lambda: self._on_field_changed())
        ex_row.addWidget(self.exclude_input)
        repo_rl.addLayout(ex_row)

        layout.addWidget(repo_group)

        # ── 提交信息 ──
        commit_group = QGroupBox("提交信息")
        commit_layout = QHBoxLayout(commit_group)
        commit_layout.addWidget(QLabel("Commit:"))
        self.commit_msg = QLineEdit("更新文档")
        commit_layout.addWidget(self.commit_msg)
        self.sync_check = QCheckBox("同步删除（删除远端多余文件）")
        self.sync_check.setToolTip("本地不存在的文件将从远端仓库删除")
        commit_layout.addWidget(self.sync_check)
        commit_layout.addWidget(QLabel("  线程:"))
        self.threads_spin = QSpinBox()
        self.threads_spin.setRange(1, 20)
        self.threads_spin.setValue(8)
        self.threads_spin.setFixedWidth(50)
        commit_layout.addWidget(self.threads_spin)
        commit_layout.addStretch()
        layout.addWidget(commit_group)

        # ── 操作按钮 ──
        btn_layout = QHBoxLayout()

        self.save_cfg_btn = QPushButton("💾 保存设置")
        self.save_cfg_btn.setCursor(Qt.PointingHandCursor)
        self.save_cfg_btn.clicked.connect(self._save_deploy_config)
        btn_layout.addWidget(self.save_cfg_btn)

        self.deploy_btn = QPushButton("🚀 部署到 GitHub Pages")
        self.deploy_btn.setObjectName("start_btn")
        self.deploy_btn.setCursor(Qt.PointingHandCursor)
        self.deploy_btn.clicked.connect(self._deploy_api)
        btn_layout.addWidget(self.deploy_btn)

        self.deploy_stop_btn = QPushButton("⏹ 停止推送")
        self.deploy_stop_btn.setObjectName("stop_btn")
        self.deploy_stop_btn.setCursor(Qt.PointingHandCursor)
        self.deploy_stop_btn.clicked.connect(self._stop_deploy)
        self.deploy_stop_btn.hide()
        btn_layout.addWidget(self.deploy_stop_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # ── 日志 ──
        log_label = QLabel("操作日志")
        log_label.setStyleSheet("font-weight: bold; color: #2C3E50;")
        layout.addWidget(log_label)

        self.deploy_log = LogWidget()
        layout.addWidget(self.deploy_log)

        # ── 状态条 ──
        self.deploy_status = QLabel("")
        self.deploy_status.setWordWrap(True)
        self.deploy_status.setStyleSheet("color: #7F8C8D; font-size: 9pt;")
        layout.addWidget(self.deploy_status)

        # 初始化仓库下拉列表
        self._populate_repo_combo()
        self._updating_fields = False

    # ── 仓库管理方法 ──

    def _populate_repo_combo(self):
        """根据 cfg 填充下拉列表"""
        self.repo_combo.blockSignals(True)
        self.repo_combo.clear()
        repos = self.cfg.get('github_repos', {})
        for i, name in enumerate(repos.keys()):
            display = name if len(name) <= 35 else name[:32] + '...'
            self.repo_combo.addItem(display, name)
        active = self.cfg.get('github_active', '')
        if active and active in repos:
            self.repo_combo.setCurrentIndex(list(repos.keys()).index(active))
        self.remove_repo_btn.setEnabled(self.repo_combo.count() > 0)
        self.repo_combo.blockSignals(False)
        self._load_repo_fields()

    def _on_repo_changed(self, index):
        """切换仓库时保存当前并加载新仓库"""
        if index < 0:
            return
        self._save_current_repo()
        name = self.repo_combo.itemData(index)
        if name:
            self.cfg['github_active'] = name
        self._load_repo_fields()

    def _load_repo_fields(self):
        """从当前选中仓库加载字段"""
        self._updating_fields = True
        name = self.repo_combo.currentData()
        repos = self.cfg.get('github_repos', {})
        if name and name in repos:
            r = repos[name]
            self.repo_input.setText(name)
            self.branch_input.setText(r.get('branch', 'main'))
            self.token_input.setText(r.get('token', ''))
            self.subfolder_input.setText(r.get('subfolder', ''))
            self.exclude_input.setText(r.get('exclude',
                '.git, .server_config.json, __pycache__, .qoder, 1.exe'))
        else:
            self.repo_input.clear()
            self.branch_input.setText('main')
            self.token_input.clear()
            self.subfolder_input.clear()
            self.exclude_input.setText('.git, .server_config.json, __pycache__, .qoder, 1.exe')
        self._updating_fields = False

    def _on_field_changed(self):
        """字段变更时自动保存到当前仓库"""
        if getattr(self, '_updating_fields', False):
            return
        self._save_current_repo()

    def _save_current_repo(self):
        """将表单内容保存到当前选中仓库"""
        name = self.repo_combo.currentData()
        if not name:
            return
        repos = self.cfg.get('github_repos', {})
        new_name = self.repo_input.text().strip()
        # 如果更改了仓库名，需要做键重命名
        if new_name and new_name != name:
            if name in repos:
                repos[new_name] = repos.pop(name)
            name = new_name
            self.cfg['github_active'] = name
        if name not in repos:
            repos[name] = {}
        repos[name].update({
            'token': self.token_input.text().strip(),
            'branch': self.branch_input.text().strip() or 'main',
            'subfolder': self.subfolder_input.text().strip(),
            'exclude': self.exclude_input.text().strip(),
        })
        self.cfg['github_repos'] = repos
        # 更新下拉列表（可能名称变了）
        self._populate_repo_combo()

    def _add_repo(self):
        """添加新仓库"""
        name = self.repo_input.text().strip()
        repos = self.cfg.get('github_repos', {})
        if not name:
            name = 'owner/repo'
        base = name
        i = 1
        while name in repos:
            name = f'{base} ({i})'
            i += 1
        repos[name] = {
            'token': self.token_input.text().strip(),
            'branch': self.branch_input.text().strip() or 'main',
            'subfolder': self.subfolder_input.text().strip(),
            'exclude': self.exclude_input.text().strip(),
        }
        self.cfg['github_repos'] = repos
        self.cfg['github_active'] = name
        save_config(self.cfg)
        self.deploy_log.log(f'已添加仓库: {name}', "#4EC9B0")
        self._populate_repo_combo()

    def _remove_repo(self):
        """移除当前仓库"""
        name = self.repo_combo.currentData()
        if not name:
            return
        reply = QMessageBox.question(self, "确认移除",
            f'确定要移除仓库 "{name}" 吗？\n此操作不可恢复。',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        repos = self.cfg.get('github_repos', {})
        repos.pop(name, None)
        self.cfg['github_repos'] = repos
        self.cfg['github_active'] = next(iter(repos.keys())) if repos else ''
        save_config(self.cfg)
        self.deploy_log.log(f'已移除仓库: {name}', "#CE9178")
        self._populate_repo_combo()

    # ── Token 显隐 ──

    def _toggle_token(self):
        if self.token_show.isChecked():
            self.token_input.setEchoMode(QLineEdit.Normal)
            self.token_show.setText("👁 隐藏")
            self.token_show.setStyleSheet("background:#E67E22; color:white; border:none; border-radius:3px;")
        else:
            self.token_input.setEchoMode(QLineEdit.Password)
            self.token_show.setText("👁 显示")
            self.token_show.setStyleSheet("")

    def _save_deploy_config(self):
        """手动保存设置"""
        self._save_current_repo()
        save_config(self.cfg)
        self.deploy_log.log("设置已保存", "#4EC9B0")

    @staticmethod
    def _api_request_sync(token, method, path, data=None, retries=2):
        """调用 GitHub API，返回 (status, body_json)（可在线程中安全调用）
        网络错误自动重试"""
        url = f'https://api.github.com{path}'
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'server-py',
        }
        body = json.dumps(data).encode('utf-8') if data else None
        last_err = None
        for attempt in range(retries + 1):
            try:
                req = urllib.request.Request(url, data=body, headers=headers, method=method)
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return resp.status, json.loads(resp.read().decode('utf-8'))
            except urllib.error.HTTPError as e:
                err_body = e.read().decode('utf-8', errors='replace')
                body_json = json.loads(err_body) if err_body else {'message': str(e)}
                if e.code == 409 or e.code == 422:  # 冲突/校验失败，不重试
                    return e.code, body_json
                last_err = body_json
            except (urllib.error.URLError, OSError) as e:
                last_err = {'message': str(e)}
            if attempt < retries:
                QThread.msleep(1000)  # 等1秒重试
        return 0, last_err or {'message': '网络错误'}

    # ── 后台上传线程 ─────────────────────────────────────────────────────

    def _deploy_api(self):
        token = self.token_input.text().strip()
        repo = self.repo_input.text().strip()
        branch = self.branch_input.text().strip() or 'main'
        msg = self.commit_msg.text().strip() or '更新文档'
        subfolder = self.subfolder_input.text().strip()

        if not token or not repo:
            QMessageBox.critical(self, "错误", "请填写 Token 和仓库地址")
            return
        if not subfolder:
            QMessageBox.critical(self, "错误", "推送子文件夹不能为空，请输入或选择")
            return

        self._save_deploy_config()

        folder = self.cfg.get('folder', SCRIPT_DIR)
        scan_root = os.path.join(folder, subfolder)
        scan_root = os.path.normpath(scan_root)
        if not os.path.isdir(scan_root):
            QMessageBox.critical(self, "错误", f"子文件夹不存在:\n{scan_root}")
            return

        self.deploy_log.log(f'扫描目录: {scan_root}', "#D4D4D4")

        # 收集文件
        files = []
        # 解析排除列表
        exclude_str = self.exclude_input.text().strip()
        excludes_raw = [e.strip() for e in exclude_str.split(',') if e.strip()]
        excludes = set(excludes_raw) if excludes_raw else {'.git'}
        for root, dirs, fnames in os.walk(scan_root):
            dirs[:] = [d for d in dirs if d not in excludes]
            for fn in fnames:
                full = os.path.join(root, fn)
                rel = os.path.relpath(full, scan_root).replace('\\', '/')
                skip = False
                for ex in excludes:
                    if rel == ex or rel.startswith(ex + '/'):
                        skip = True
                        break
                if skip:
                    continue
                files.append((full, rel))

        self.deploy_btn.setEnabled(False)
        self.deploy_stop_btn.show()
        sync_on = self.sync_check.isChecked()
        self.deploy_log.log(f'>>> 开始部署 ({len(files)} 个文件)...', "#569CD6")
        self.deploy_log.log(f'仓库: {repo}  分支: {branch}  线程: {self.threads_spin.value()}  同步删除: {"是" if sync_on else "否"}', "#D4D4D4")
        self.deploy_status.setText(f'准备上传 {len(files)} 个文件...')

        self._upload_worker = DeployWorker(files, token, repo, branch, msg,
            sync_delete=sync_on, subfolder=subfolder, threads=self.threads_spin.value())
        self._upload_worker.log_signal.connect(
            lambda m, c: self.deploy_log.log(m, c))
        self._upload_worker.progress_signal.connect(
            lambda u, t: self.deploy_status.setText(f'进度: {u}/{t}'))
        self._upload_worker.done_signal.connect(self._on_deploy_done)
        self._upload_worker.start()

    def _on_deploy_done(self, uploaded, errors):
        self.deploy_btn.setEnabled(True)
        self.deploy_stop_btn.hide()
        self._upload_worker = None
        total = uploaded + errors
        self.deploy_status.setText(
            f'完成: {uploaded} 成功 / {errors} 失败 (共 {total})')
        if errors == 0:
            self.deploy_log.log(f'✅ 部署完成! ({uploaded} 个文件)', "#4EC9B0")
        else:
            self.deploy_log.log(
                f'⚠ 部署完成 ({uploaded} 成功, {errors} 失败)', "#CE9178")

    def _stop_deploy(self):
        if self._upload_worker and self._upload_worker.isRunning():
            self._upload_worker._stopped = True
            self._upload_worker.quit()
            self._upload_worker.wait(3000)
            if self._upload_worker.isRunning():
                self._upload_worker.terminate()
            self.deploy_log.log('⏹ 已停止推送', "#CE9178")
            self.deploy_btn.setEnabled(True)
            self.deploy_stop_btn.hide()
            self.deploy_status.setText('已停止')

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

    def _browse_subfolder(self):
        path = QFileDialog.getExistingDirectory(
            self, "选择推送子文件夹", self.cfg.get('folder', SCRIPT_DIR))
        if path:
            folder = self.cfg.get('folder', SCRIPT_DIR)
            try:
                rel = os.path.relpath(path, folder)
                self.subfolder_input.setText('' if rel == '.' else rel)
            except ValueError:
                self.subfolder_input.setText(path)
            self._save_current_repo()

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
