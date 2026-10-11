from flask import Flask

app = Flask(__name__)

# Change ce numéro pour tester le déploiement automatique
VERSION = "2"


@app.route("/")
def accueil():
    return f"""
    <html>
      <head><title>Mon projet DevOps</title></head>
      <body style="font-family: sans-serif; text-align: center; margin-top: 100px;">
        <h1>Bonjour Lamine</h1>
        <p>Version {VERSION}</p>
      </body>
    </html>
    """


if __name__ == "__main__":
    # 0.0.0.0 = accessible depuis le réseau (nécessaire plus tard pour Docker)
    app.run(host="0.0.0.0", port=5000)
