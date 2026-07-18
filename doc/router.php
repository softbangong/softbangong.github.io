<?php
/**
 * VitePress cleanUrls 路由 — 将无扩展名的路径映射到 .html 文件
 * 支持任意子路径部署：/doc/md/xxx → dist/md/xxx (自动剥离首级子路径)
 */
$uri = $_SERVER['REQUEST_URI'];
$fullPath = urldecode(parse_url($uri, PHP_URL_PATH));
$ext = pathinfo($fullPath, PATHINFO_EXTENSION);

// 路由函数：给定路径尝试映射到 .html 文件，成功返回 true
$tryRoute = function($path) {
    if ($path === '/' || $path === '') return false;
    $ext = pathinfo($path, PATHINFO_EXTENSION);
    if ($ext !== '') return false;
    // 先试 /path.html
    $htmlFile = __DIR__ . $path . '.html';
    if (is_file($htmlFile)) {
        header('Content-Type: text/html; charset=utf-8');
        readfile($htmlFile);
        return true;
    }
    // 再试 /path/index.html（目录型路径如 /md/xx/）
    $htmlFile = __DIR__ . rtrim($path, '/') . '/index.html';
    if (is_file($htmlFile)) {
        header('Content-Type: text/html; charset=utf-8');
        readfile($htmlFile);
        return true;
    }
    return false;
};

// 1) 按完整路径尝试（根路径部署）
if ($tryRoute($fullPath)) return;

// 2) 剥离首级子路径后尝试（如 /doc/md/xxx → /md/xxx，支持子路径部署）
$stripped = preg_replace('#^/[^/]+#', '', $fullPath);
if ($stripped && $stripped !== '/' && $tryRoute($stripped)) return;

// 映射失败 → 404
http_response_code(404);
header('Content-Type: text/html; charset=utf-8');
$nf = __DIR__ . '/404.html';
if (is_file($nf)) { readfile($nf); return; }
echo '404 Not Found';
return;

// 情况2：路径有扩展名 → 交给 PHP 返回真实文件
return false;
