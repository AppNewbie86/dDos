# dDos


Dokumentation eines Ansatzes für einen möglichen DDos_Guard
![DDosBild](https://github.com/AppNewbie86/dDos/assets/101304191/5cd6d85e-91be-4383-b8d0-321abc01061f)



Diese Dokumentation dient dazu, den vorliegenden Python-Code zu erklären und anderen Entwicklern dabei zu helfen, 
das Projekt zu verstehen und zu erweitern. Der Code ist eine Flask-Webanwendung, die Rate-Limiting, IP-Sperrung und Whitelisting-Funktionalitäten 
bietet.

Importieren der benötigten Bibliotheken und Module

Zunächst werden die erforderlichen Bibliotheken und Module importiert. 
Hierbei handelt es sich um Flask, Werkzeug (zur Behandlung von Proxys), Flask-Limiter und datetime.


from flask import Flask, request
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_limiter import Limiter
from datetime import timedelta

Flask-Anwendung initialisieren

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

Hier wird eine Flask-Webanwendung initialisiert. Die Verwendung von ProxyFix sorgt dafür, dass die Anwendung korrekt mit Proxys umgehen kann.

Rate-Limiting-Einstellungen

limiter = Limiter(app, key_func=lambda: request.remote_addr)
limiter.limit("10 per minute")(app)

Diese Abschnitte des Codes richten das Rate-Limiting für die Anwendung ein. Es wird festgelegt, dass nur 10 Anfragen pro Minute pro IP-Adresse 
erlaubt sind.

IP-Adressen-Sperrung und Whitelisting

blocked_ips = set()
whitelisted_ips = {'127.0.0.1', '192.168.1.100', '203.0.113.45'}

In diesen Zeilen werden leere Sets für gesperrte IP-Adressen (blocked_ips) und eine Beispiel-Whitelist (whitelisted_ips) definiert.

Dauer der automatischen Entsperrung

block_duration = timedelta(minutes=10)
block_duration legt die Zeitspanne fest, nach der eine automatisch gesperrte IP-Adresse wieder freigeschaltet wird (hier 10 Minuten).

Routen der Flask-Anwendung

Die folgenden Abschnitte des Codes definieren Routen und Funktionen für die Flask-Anwendung.

/ - Die Hauptseite

@app.route('/')
def index():
    # Überprüft, ob die IP-Adresse in der Whitelist steht
    if request.remote_addr in whitelisted_ips:
        return "Willkommen auf unserer Website!"
    
    # Überprüft, ob die IP-Adresse in der Sperrliste steht
    if request.remote_addr in blocked_ips:
        return "Ihre IP-Adresse ist gesperrt.", 403
    return "Willkommen auf unserer Website!"
    
Hier wird die Hauptseite der Anwendung definiert. Wenn die IP-Adresse des Benutzers in der Whitelist steht, wird eine Willkommensnachricht 
angezeigt. Wenn die IP-Adresse in der Sperrliste steht, wird eine Fehlermeldung mit dem Statuscode 403 zurückgegeben.

/block_ip/<ip> - IP-Adresse blockieren

@app.route('/block_ip/<ip>')
def block_ip(ip):
    # Fügt eine IP-Adresse zur Sperrliste hinzu
    blocked_ips.add(ip)
    # Plant das automatische Entfernen der IP-Adresse aus der Blacklist
    remove_from_blocked_ips(ip, block_duration)
    return f"IP-Adresse {ip} wurde gesperrt."
    
Diese Route ermöglicht das Hinzufügen einer IP-Adresse zur Sperrliste. Die IP-Adresse wird hinzugefügt, und es wird eine Meldung 
über die Sperrung zurückgegeben. Zudem wird die automatische Entsperrung geplant.

/unblock_ip/<ip> - IP-Adresse entsperren

@app.route('/unblock_ip/<ip>')
def unblock_ip(ip):
    # Entfernt eine IP-Adresse aus der Sperrliste
    blocked_ips.discard(ip)
    return f"IP-Adresse {ip} wurde entsperrt."
    
Diese Route ermöglicht das Entfernen einer IP-Adresse aus der Sperrliste. Die IP-Adresse wird aus der Liste entfernt, und es wird eine 
Meldung über die Entsperrung zurückgegeben.

Automatisches Entfernen von gesperrten IP-Adressen

def remove_from_blocked_ips(ip, duration):
    # Entfernt eine IP-Adresse nach einer bestimmten Zeit aus der Sperrliste
    def remove_ip():
        blocked_ips.discard(ip)
    app.logger.info(f"Entferne {ip} aus der Sperrliste in {duration.total_seconds()} Sekunden")
    app.logger.info(f"Starte Timer zum Entfernen von {ip}")
    
Diese Funktion plant das Entfernen einer IP-Adresse aus der Sperrliste nach Ablauf der in block_duration definierten Zeitspanne. 
Sie verwendet einen Timer, um die Entfernung zu planen und gibt Informationen darüber im Anwendungsprotokoll aus.

Ausführung der Anwendung

if __name__ == '__main__':
    app.run()
    
Die Anwendung wird nur gestartet, wenn die Datei direkt ausgeführt wird und nicht als Modul in einem anderen Skript importiert wird.

Insgesamt handelt es sich bei diesem Code um eine Flask-Anwendung, die Rate-Limiting, IP-Sperrung und Whitelisting bietet. 
Sie ermöglicht die einfache Verwaltung von Zugriffsberechtigungen für bestimmte IP-Adressen und die automatische Entsperrung nach einer 
festgelegten Zeitdauer. Der Code ist gut strukturiert und dokumentiert, um anderen Entwicklern die Erweiterung und Anpassung des 
Projekts zu erleichtern.
