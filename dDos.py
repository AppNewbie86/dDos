from flask import Flask, request
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_limiter import Limiter
from datetime import timedelta

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)  # Um mit Proxys korrekt umzugehen

# Rate-Limiting-Einstellungen
limiter = Limiter(app, key_func=lambda: request.remote_addr)
limiter.limit("10 per minute")(app)  # Begrenze auf 10 Anfragen pro Minute pro IP

# Liste der gesperrten und bekannten IP-Adressen
blocked_ips = set()
whitelisted_ips = {'127.0.0.1', '192.168.1.100', '203.0.113.45'}  # Beispiel-Whitelist

# Dauer der automatischen Entsperrung
block_duration = timedelta(minutes=10)

@app.route('/')
def index():
    # Überprüfe, ob die IP-Adresse in der Whitelist steht
    if request.remote_addr in whitelisted_ips:
        return "Willkommen auf unserer Website!"
    
    # Überprüfe, ob die IP-Adresse in der Sperrliste steht
    if request.remote_addr in blocked_ips:
        return "Ihre IP-Adresse ist gesperrt.", 403
    return "Willkommen auf unserer Website!"

@app.route('/block_ip/<ip>')
def block_ip(ip):
    # Füge eine IP-Adresse zur Sperrliste hinzu
    blocked_ips.add(ip)
    # Planen Sie das automatische Entfernen der IP-Adresse aus der Blacklist
    remove_from_blocked_ips(ip, block_duration)
    return f"IP-Adresse {ip} wurde gesperrt."

@app.route('/unblock_ip/<ip>')
def unblock_ip(ip):
    # Entferne eine IP-Adresse aus der Sperrliste
    blocked_ips.discard(ip)
    return f"IP-Adresse {ip} wurde entsperrt."

def remove_from_blocked_ips(ip, duration):
    # Entferne eine IP-Adresse nach einer bestimmten Zeit aus der Sperrliste
    def remove_ip():
        blocked_ips.discard(ip)
    app.logger.info(f"Entferne {ip} aus der Sperrliste in {duration.total_seconds()} Sekunden")
    app.logger.info(f"Starte Timer zum Entfernen von {ip}")
    
if __name__ == '__main__':
    app.run()
