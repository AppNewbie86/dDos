# DDoS-Guard Dokumentation

![DDoSBild](https://github.com/AppNewbie86/dDos/assets/101304191/5cd6d85e-91be-4383-b8d0-321abc01061f)

---

**Dokumentation verfasst von Breadcrumb **

---

## Inhaltsverzeichnis

  - [Einführung](#einführung)
  - [Code-Übersicht](#code-übersicht)
  - [Importieren der benötigten Bibliotheken und Module](#importieren-der-benötigten-bibliotheken-und-module)
  - [Flask-Anwendung initialisieren](#flask-anwendung-initialisieren)
  - [Rate-Limiting-Einstellungen](#rate-limiting-einstellungen)
  - [IP-Adressen-Sperrung und Whitelisting](#ip-adressen-sperrung-und-whitelisting)
  - [Dauer der automatischen Entsperrung](#dauer-der-automatischen-entsperrung)
  - [Routen der Flask-Anwendung](#routen-der-flask-anwendung)
  - [Hauptseite (/)](#hauptseite-)
  - [IP-Adresse blockieren (/block_ip/&lt;ip&gt;)](#ip-adresse-blockieren-block_ipip)
  - [IP-Adresse entsperren (/unblock_ip/&lt;ip&gt;)](#ip-adresse-entsperren-unblock_ipip)
  - [Automatisches Entfernen von gesperrten IP-Adressen](#automatisches-entfernen-von-gesperrten-ip-adressen)
  - [Ausführung der Anwendung](#ausführung-der-anwendung)
  - [Fazit](#fazit)

---

## Einführung

Diese Dokumentation erklärt einen Python-Code für eine Flask-Webanwendung, die als DDoS-Guard 
(Schutz vor Distributed Denial of Service-Angriffen) dient. 
Die Anwendung bietet Funktionen wie Rate-Limiting, IP-Sperrung und Whitelisting. Ziel ist es, anderen Entwicklern das Verständnis des 
Codes zu erleichtern und Möglichkeiten zur Erweiterung und Anpassung aufzuzeigen.

---

## Code-Übersicht

### Importieren der benötigten Bibliotheken und Module

Zu Beginn des Codes werden die erforderlichen Bibliotheken und Module importiert. Diese sind notwendig, 
um die Funktionalität der Anwendung zu unterstützen.

```python

from flask import Flask, request
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_limiter import Limiter
from datetime import timedelta

## Flask-Anwendung initialisieren

Die Flask-Anwendung wird initialisiert, und die ProxyFix-Middleware wird hinzugefügt,
um den korrekten Umgang mit Proxys sicherzustellen.

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

## Rate-Limiting-Einstellungen

// Rate-Limiting ist eine wichtige Funktion, um die Anzahl der Anfragen pro IP-Adresse zu begrenzen.
// Diese Einstellungen legen fest, dass pro IP-Adresse nur 10 Anfragen pro Minute erlaubt sind.

limiter = Limiter(app, key_func=lambda: request.remote_addr)
limiter.limit("10 per minute")(app)

## IP-Adressen-Sperrung und Whitelisting

Um unerwünschte oder schädliche IP-Adressen zu blockieren und vertrauenswürdige
IP-Adressen zuzulassen, werden zwei Listen erstellt.

blocked_ips = set()
whitelisted_ips = {'127.0.0.1', '192.168.1.100', '203.0.113.45'}  # Beispiel-Whitelist

## Dauer der automatischen Entsperrung

Hier wird festgelegt, wie lange eine IP-Adresse automatisch
gesperrt bleibt, bevor sie wieder freigeschaltet wird.

block_duration = timedelta(minutes=10)

Routen der Flask-Anwendung

Die Anwendung enthält verschiedene Routen, die die Funktionalität
des DDoS-Guards steuern.

## Hauptseite (/)

Die Hauptseite der Anwendung überprüft, ob die IP-Adresse des Benutzers in der Whitelist steht.
Falls ja, wird eine Willkommensnachricht angezeigt. Wenn die IP-Adresse in der Sperrliste steht,
wird eine Fehlermeldung mit dem

Statuscode 403 zurückgegeben.

@app.route('/')
def index():
    # Überprüft, ob die IP-Adresse in der Whitelist steht
    if request.remote_addr in whitelisted_ips:
        return "Willkommen auf unserer Website!"
    
    # Überprüft, ob die IP-Adresse in der Sperrliste steht
    if request.remote_addr in blocked_ips:
        return "Ihre IP-Adresse ist gesperrt.", 403
    return "Willkommen auf unserer Website!"

## IP-Adresse blockieren (/block_ip/<ip>)

IP-Adresse blockieren (/block_ip/<ip>)
Diese Route ermöglicht das Hinzufügen einer IP-Adresse zur Sperrliste.
Die IP-Adresse wird hinzugefügt, und es wird eine Meldung über die Sperrung zurückgegeben.
Zudem wird die automatische Entsperrung geplant.

@app.route('/block_ip/<ip>')
def block_ip(ip):
    # Fügt eine IP-Adresse zur Sperrliste hinzu
    blocked_ips.add(ip)
    # Plant das automatische Entfernen der IP-Adresse aus der Blacklist
    remove_from_blocked_ips(ip, block_duration)
    return f"IP-Adresse {ip} wurde gesperrt."

## IP-Adresse entsperren (/unblock_ip/<ip>)

Diese Route ermöglicht das Entfernen einer IP-Adresse aus der Sperrliste.
Die IP-Adresse wird aus der Liste entfernt, und es wird eine Meldung über die
Entsperrung zurückgegeben.

@app.route('/unblock_ip/<ip>')
def unblock_ip(ip):
    # Entfernt eine IP-Adresse aus der Sperrliste
    blocked_ips.discard(ip)
    return f"IP-Adresse {ip} wurde entsperrt."

## Automatisches Entfernen von gesperrten IP-Adressen

Eine Funktion namens remove_from_blocked_ips plant das Entfernen einer IP-Adresse aus der Sperrliste
nach Ablauf der in block_duration definierten Zeitspanne. Diese Funktion verwendet einen Timer, um die
Entfernung zu planen, und gibt Informationen darüber im Anwendungsprotokoll aus.

def remove_from_blocked_ips(ip, duration):
    # Entfernt eine IP-Adresse nach einer bestimmten Zeit aus der Sperrliste
    def remove_ip():
        blocked_ips.discard(ip)
    app.logger.info(f"Entferne {ip} aus der Sperrliste in {duration.total_seconds()} Sekunden")
    app.logger.info(f"Starte Timer zum Entfernen von {ip}")

## Ausführung der Anwendung

Die Anwendung wird nur gestartet, wenn die Datei direkt ausgeführt wird und nicht als Modul in einem
anderen Skript importiert wird.

if __name__ == '__main__':
    app.run()

## Fazit

Insgesamt handelt es sich bei diesem Code um eine Flask-Anwendung,
die Rate-Limiting, IP-Sperrung und Whitelisting bietet. Sie ermöglicht die einfache Verwaltung von Zugriffsberechtigungen
für bestimmte IP-Adressen und die automatische Entsperrung nach einer festgelegten Zeitdauer.
Der Code ist gut strukturiert und dokumentiert, um anderen Entwicklern die Erweiterung und Anpassung
des Projekts zu erleichtern. Dieser DDoS-Guard kann dazu beitragen, Webanwendungen vor Angriffen zu schützen
und die Zuverlässigkeit zu gewährleisten.



