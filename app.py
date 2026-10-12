import os
import socket
import time
from concurrent.futures import ThreadPoolExecutor

import yaml
from flask import Flask, jsonify, render_template

app = Flask(__name__)

# Change ce numéro pour tester le déploiement automatique
VERSION = "4"

DOSSIER = os.path.dirname(os.path.abspath(__file__))
FICHIER_SERVICES = os.path.join(DOSSIER, "services.yml")


def charger_services():
    """Lit la liste des machines dans services.yml."""
    with open(FICHIER_SERVICES, encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def tester(service):
    """Teste si le port répond, et mesure le temps de réponse."""
    debut = time.perf_counter()
    try:
        with socket.create_connection((service["hote"], service["port"]), timeout=1.5):
            ms = round((time.perf_counter() - debut) * 1000)
        return {**service, "en_ligne": True, "ms": ms}
    except OSError:
        return {**service, "en_ligne": False, "ms": None}


def etat_homelab():
    """Teste toutes les machines en parallèle."""
    services = charger_services()
    with ThreadPoolExecutor(max_workers=20) as pool:
        resultats = list(pool.map(tester, services))

    # Regroupement par catégorie, dans l'ordre du fichier
    groupes = {}
    for s in resultats:
        groupes.setdefault(s.get("groupe", "Autres"), []).append(s)
    return resultats, groupes


@app.route("/")
def accueil():
    resultats, groupes = etat_homelab()
    en_ligne = sum(1 for s in resultats if s["en_ligne"])
    return render_template(
        "index.html",
        groupes=groupes,
        en_ligne=en_ligne,
        total=len(resultats),
        version=VERSION,
        heure=time.strftime("%H:%M:%S"),
    )


@app.route("/api/etat")
def api_etat():
    resultats, _ = etat_homelab()
    return jsonify(resultats)


@app.route("/health")
def health():
    return {"status": "ok", "version": VERSION}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
