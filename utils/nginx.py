def generate_nginx_openai_lb(backend_servers, lb_listen="127.0.0.1:3000", lb_server_name="localhost", algorithm="least_conn"):
    """
    生成 OpenAI 风格本地负载均衡的 Nginx 配置文件
    :param backend_servers: 后端服务器列表，格式如 ["192.168.1.101:8080", "localhost:8081", ...]
    :param lb_listen: Nginx 监听地址+端口（默认本地 3000 端口）
    :param lb_server_name: Nginx 服务器名（默认 localhost）
    :param algorithm: 负载均衡算法（least_conn/round_robin，默认 least_conn）
    :return: 完整的 Nginx 配置字符串
    """
    # 验证负载均衡算法合法性
    if algorithm not in ["least_conn", "round_robin"]:
        raise ValueError("算法仅支持 least_conn（最少连接）或 round_robin（轮询）")
    
    # 生成 upstream 后端服务器池配置
    upstream_config = """
# 全局配置（适配 CPU 核心数，提高并发性能）
worker_processes auto;  # 自动检测 CPU 核心数，启动对应数量的工作进程
worker_rlimit_nofile 65535;  # 提高每个进程的最大文件描述符限制（适配高并发）

# 必需：events 块（Nginx 网络连接配置）
events {
    worker_connections 1024;  # 每个工作进程最多处理 1024 个连接（可根据服务器配置调整）
    use epoll;  # 使用 epoll 事件模型（Linux 系统最优选择，提高并发性能）
    multi_accept on;  # 允许工作进程同时接收多个新连接
}    
"""
    upstream_config += "http{\nupstream openai_backends {\n"
    # 添加负载均衡算法
    if algorithm != "round_robin":  # round_robin 是默认值，可省略不写
        upstream_config += f"    {algorithm};\n"
    # 添加所有后端服务器
    for server in backend_servers:
        # 验证服务器地址格式（简单校验是否包含 : 和端口）
        if ":" not in server or not server.split(":")[-1].isdigit():
            raise ValueError(f"无效的服务器地址：{server}，格式应为 IP:端口 或 localhost:端口")
        upstream_config += f"    server {server} max_fails=2 fail_timeout=10s;\n"
    # 添加健康检查和连接配置（适配 OpenAI 场景）
    upstream_config += """
    
    # 关闭长连接（适配 OpenAI 短连接场景）

}

"""
    
    # 生成 server 前端配置
    server_config = "server {\n"
    server_config += f"    listen {lb_listen};\n"
    server_config += f"    server_name {lb_server_name};\n\n"
    
    # location 转发配置（核心）
    server_config += """    location / {
        proxy_pass http://openai_backends;  # 转发到后端服务器池
        
        # 透传 OpenAI 关键请求头（必需配置）
        proxy_set_header Host $proxy_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Authorization $http_authorization;  # 透传 API 密钥
        proxy_set_header Content-Type $http_content_type;    # 透传请求格式
        proxy_set_header Accept $http_accept;
        
        # 超时配置（适配大模型长耗时响应）
        proxy_connect_timeout 10s;   # 连接超时（快速失败）
        proxy_send_timeout 120s;     # 发送请求超时
        proxy_read_timeout 1800s;    # 读取响应超时（5分钟，适配长文本生成）
        
        # 异常重试（自动跳过故障后端）
        proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504;
        proxy_next_upstream_tries 3;
        proxy_next_upstream_timeout 10s;
        
        # 禁用缓存+缓冲配置
        proxy_cache off;
        proxy_buffering on;
        proxy_buffer_size 16k;
        proxy_buffers 4 64k;
    }\n\n"""
    
    # 日志配置
    server_config += """    # 日志配置（便于排查问题）
    access_log /var/log/nginx/openai_access.log;
    error_log /var/log/nginx/openai_error.log warn;
}\n}"""
    
    # 组合完整配置
    full_config = upstream_config + server_config
    return full_config


# ------------------- 示例使用 -------------------
if __name__ == "__main__":
    # 1. 输入：后端服务器地址列表（16台本地服务器，支持 IP:端口 或 localhost:端口）
    backend_servers = ['10.124.41.85:32771', '10.124.41.153:36471', '10.124.41.85:33891', '10.124.41.153:40499', '10.124.41.85:37181', '10.124.41.153:39969', '10.124.41.153:37533', '10.124.41.85:34079', '10.124.41.153:47749', '10.124.41.85:36181', '10.124.41.85:46325', '10.124.41.153:38711', '10.124.41.85:34419', '10.124.41.153:46029', '10.124.41.85:48215', '10.124.41.153:35587']
    # 2. 生成 Nginx 配置
    try:
        nginx_config = generate_nginx_openai_lb(
            backend_servers=backend_servers,
            lb_listen="127.0.0.1:8000",  # Nginx 本地监听端口
            algorithm="least_conn"        # 负载算法：least_conn 或 round_robin
        )
        
        # 3. 输出到文件（保存为 nginx 配置文件）
        output_file = "openai_lb.conf"  # Nginx 配置路径
        # 本地测试可改为：output_file = "openai_lb.conf"（保存到当前目录）
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(nginx_config)
        
        print(f"✅ Nginx 配置文件已生成：{output_file}")
        print("启动 Nginx：")
        print("sudo nginx -c /opt/tiger/open_verl/openai_lb.conf")
        
    except Exception as e:
        print(f"❌ 生成失败：{str(e)}")