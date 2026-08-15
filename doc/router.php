<?php
/**
 * VitePress cleanUrls 路由 — 将无扩展名的路径映射到 .html 文件
 * 支持任意子路径部署：/doc/md/xxx → /md/xxx (自动剥离首级子路径)
 * 
 * 适用场景：
 *   php -S localhost:8080 -t /path/to/dist router.php
 */
$uri = $_SERVER['REQUEST_URI'];
// 路径解码用 rawurldecode：urldecode 会把文件名中的 '+' 误解码为空格
$fullPath = rawurldecode(parse_url($uri, PHP_URL_PATH));
$ext = pathinfo($fullPath, PATHINFO_EXTENSION);

// 文档根目录（PHP -t 参数指定的目录，不是 router.php 所在目录）
$root = rtrim($_SERVER['DOCUMENT_ROOT'], '/\\');

// 有扩展名的请求（.css .js .html .png .json 等）
// PHP 内置服务器默认从文档根目录映射，但 base 子路径会导致路径不匹配。
// 例如 /doc/search-data.json 实际文件在 dist/search-data.json（而非 dist/doc/search-data.json）。
// 这里手动处理：先尝试完整路径，再尝试剥离首级子路径。
if ($ext !== '') {
    // 1) 尝试完整路径
    $filePath = $root . $fullPath;
    if (is_file($filePath)) return false;

    // 2) 剥离首级子路径后尝试（如 /doc/search-data.json → /search-data.json）
    $strippedPath = preg_replace('#^/[^/]+#', '', $fullPath);
    if ($strippedPath && is_file($root . $strippedPath)) {
        $mimeTypes = [
            'json' => 'application/json',
            'js'   => 'application/javascript',
            'css'  => 'text/css',
            'html' => 'text/html',
            'png'  => 'image/png',
            'jpg'  => 'image/jpeg',
            'jpeg' => 'image/jpeg',
            'gif'  => 'image/gif',
            'svg'  => 'image/svg+xml',
            'ico'  => 'image/x-icon',
            'woff' => 'application/font-woff',
            'woff2'=> 'application/font-woff2',
            'ttf'  => 'application/font-ttf',
            'xml'  => 'application/xml',
        ];
        $mime = $mimeTypes[$ext] ?? (mime_content_type($root . $strippedPath) ?: 'application/octet-stream');
        header('Content-Type: ' . $mime);
        readfile($root . $strippedPath);
        return;
    }

    // 都找不到，交给 PHP 内置服务器处理（最终 404）
    return false;
}

// 路由函数：给定路径尝试映射到 .html 文件，成功返回 true
$tryRoute = function($path) use ($root) {
    // 首页特殊处理：/ → index.html（PHP 内置服务器不会自动映射）
    if ($path === '/' || $path === '') {
        $htmlFile = $root . '/index.html';
        if (is_file($htmlFile)) {
            header('Content-Type: text/html; charset=utf-8');
            readfile($htmlFile);
            return true;
        }
        return false;
    }
    // 先试 /path.html
    $htmlFile = $root . $path . '.html';
    if (is_file($htmlFile)) {
        header('Content-Type: text/html; charset=utf-8');
        readfile($htmlFile);
        return true;
    }
    // 再试 /path/index.html（目录型路径如 /md/xx/）
    $htmlFile = $root . rtrim($path, '/') . '/index.html';
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
//    剥离后为 '/'（如 /doc/ → /）时也要尝试根首页
$stripped = preg_replace('#^/[^/]+#', '', $fullPath);
if ($stripped && $stripped !== '/' && $tryRoute($stripped)) return;
if ($stripped === '/' && $tryRoute('/')) return;

// 映射失败 → 404
http_response_code(404);
header('Content-Type: text/html; charset=utf-8');
$nf = $root . '/404.html';
if (is_file($nf)) { readfile($nf); return; }
echo '404 Not Found';
return;
