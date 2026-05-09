# 🌐 NetScanner v2.0
### Network Discovery Tool — Application Web Locale pour Windows

---

## 📁 Structure du projet

```
netscanner/
├── start.bat        ← Double-clique ici pour lancer !
├── backend.py       ← Serveur Flask (Python)
├── index.html       ← Interface utilisateur (navigateur)
└── README.md        ← Ce fichier
```

---

## 🚀 Démarrage rapide

1. **Installe Python** (si pas déjà fait)
   - Télécharge sur https://www.python.org/downloads/
   - ⚠️ Coche **"Add Python to PATH"** lors de l'installation

2. **Lance l'application**
   - Double-clique sur `start.bat`
   - Le script installe les dépendances automatiquement
   - Le navigateur s'ouvre avec l'interface

3. **Utilise l'interface**
   - Clique sur **AUTO-DETECT** pour détecter ta plage IP automatiquement
   - Ajuste les paramètres si besoin
   - Clique sur **▶ SCANNER**

---

## ⚙️ Fonctionnalités

| Fonctionnalité | Description |
|---|---|
| 🔍 Scan ping | Détecte tous les hôtes actifs via ICMP |
| 🏷️ Résolution DNS | Reverse lookup pour trouver les hostnames |
| 📟 Adresse MAC | Récupération via ARP (même sous-réseau) |
| 🔌 Scan de ports | 18 ports communs (HTTP, RDP, SSH, SMB...) |
| ⚡ Temps réel | Mode SSE : les hôtes apparaissent au fur et à mesure |
| 🧵 Multi-thread | Jusqu'à 200 threads en parallèle |
| 📊 Export JSON | Sauvegarde les résultats |
| 🔎 Filtrage | Recherche par IP ou hostname |

### Ports scannés (si activé)
`21 FTP` `22 SSH` `23 Telnet` `25 SMTP` `53 DNS` `80 HTTP`
`110 POP3` `135 RPC` `139 NetBIOS` `143 IMAP` `443 HTTPS`
`445 SMB` `3306 MySQL` `3389 RDP` `5900 VNC` `8080 HTTP-Alt`
`8443 HTTPS-Alt` `9100 Imprimante`

---

## 🎛️ Paramètres

| Paramètre | Valeur par défaut | Description |
|---|---|---|
| Plage IP | `192.168.1.1-254` | Plage à scanner (CIDR ou tiret) |
| Timeout | `1.0 s` | Délai d'attente par hôte |
| Threads | `50` | Parallélisme du scan |
| Ports TCP | Désactivé | Active le scan de ports (plus lent) |
| Mode SSE | Activé | Résultats en temps réel |

### Formats de plage IP acceptés
```
192.168.1.1-254        ← Plage simple (recommandé)
192.168.1.0/24         ← Notation CIDR
10.0.0.1-50            ← Sous-plage
172.16.0.1             ← IP unique
```

---

## 🔧 Dépendances Python

```
flask
flask-cors
```
Installées automatiquement par `start.bat`.

---

## ❓ Dépannage

**Le backend ne démarre pas**
→ Vérifie que Python est dans le PATH : ouvre un terminal et tape `python --version`

**"Backend hors ligne" dans l'interface**
→ Relance `start.bat` et attends 3-4 secondes avant d'utiliser l'interface

**Aucun hôte trouvé**
→ Vérifie la plage IP avec AUTO-DETECT
→ Augmente le timeout à 2s
→ Vérifie que le pare-feu Windows n'bloque pas les pings

**Adresse MAC "N/A"**
→ Normal pour les hôtes hors du sous-réseau direct (routeur, VPN...)
→ Nécessite de lancer `start.bat` **en tant qu'administrateur** pour ARP complet

---

## 📝 Notes

- Le scan de ports ralentit significativement le scan global
- Mode SSE recommandé pour voir les résultats en temps réel
- Pour de grandes plages (/16 soit 65535 IPs), utilise 200 threads et timeout 0.5s
- L'export JSON sauvegarde tous les hôtes trouvés avec leurs ports
