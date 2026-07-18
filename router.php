<?php
/**
 * VitePress cleanUrls 路由 — 将无扩展名的路径映射到 .html 文件
 * 例如 /search → search.html, /md/xxx → md/xxx.html
 */
$uri = $_SERVER['REQUEST_URI'];
$path = urldecode(parse_url($uri, PHP_URL_PATH));
$ext  = pathinfo($path, PATHINFO_EXTENSION);

// 情况1：路径不含扩展名 → 尝试映射到 .html
if ($path !== '/' && $ext === '') {
    // 先试 /path.html
    $htmlFile = __DIR__ . $path . '.html';
    if (is_file($htmlFile)) {
        header('Content-Type: text/html; charset=utf-8');
        readfile($htmlFile);
        return;
    }
    // 再试 /path/index.html（目录型路径如 /md/xx/）
    $htmlFile = __DIR__ . rtrim($path, '/') . '/index.html';
    if (is_file($htmlFile)) {
        header('Content-Type: text/html; charset=utf-8');
        readfile($htmlFile);
        return;
    }
    // 映射失败 → 404
    http_response_code(404);
    header('Content-Type: text/html; charset=utf-8');
    $nf = __DIR__ . '/404.html';
    if (is_file($nf)) { readfile($nf); return; }
    echo '404 Not Found';
    return;
}

// 情况2：路径有扩展名 → 交给 PHP 返回真实文件
return false;
