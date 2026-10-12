# mon-projet-devops

Projet d'apprentissage DevOps : une chaîne CI/CD complète, montée de bout en bout sur un homelab Proxmox.

Un simple `git push` déclenche le test et le déploiement automatique d'une application web, d'abord en **recette**, puis en **production** après validation manuelle.

## Architecture

```
                    git push
   Poste dev  ─────────────────►  GitHub
                                    │
                                    │  scrutation toutes les 2 min
                                    ▼
                              ┌───────────┐
                              │  Jenkins  │  debjenk01
                              └─────┬─────┘
                                    │  Docker piloté via SSH
                   ┌────────────────┴────────────────┐
                   ▼                                  ▼
            ┌─────────────┐   validation      ┌─────────────┐
            │   RECETTE   │ ───────────────►  │ PRODUCTION  │
            │  debtest01  │     manuelle      │  debdock01  │
            └─────────────┘                   └─────────────┘
             créé par Terraform                créé à la main
```

| Machine     | Rôle                          | Type          | Créée par  | Configurée par |
|-------------|-------------------------------|---------------|------------|----------------|
| `debprod10` | Poste d'administration        | CT LXC        | –          | –              |
| `debjenk01` | Serveur Jenkins (CI/CD)       | CT LXC        | Manuel     | Ansible        |
| `debdock01` | Production (Docker)           | CT LXC        | Manuel     | Ansible        |
| `debtest01` | Recette (Docker)              | CT LXC        | Terraform  | Ansible        |

Tous les CT tournent sous **Debian 13**, sur un cluster **Proxmox** de 3 nœuds.

## Rôle de chaque outil

| Outil         | Rôle dans le projet                                                   |
|---------------|-----------------------------------------------------------------------|
| **Git/GitHub** | Versionner tout le projet : application, infrastructure, pipeline     |
| **Terraform** | Créer le CT de recette sur Proxmox (provider `bpg/proxmox`)           |
| **Ansible**   | Installer Docker sur les CT, et Jenkins sur `debjenk01`              |
| **Docker**    | Empaqueter l'application dans une image                              |
| **Jenkins**   | Construire, tester et déployer automatiquement à chaque commit       |

En résumé : **Terraform crée**, **Ansible configure**, **Jenkins déploie**.

## Structure du dépôt

```
mon-projet-devops/
├── app/
│   ├── app.py              # Application web Flask
│   ├── requirements.txt    # Dépendances Python
│   └── Dockerfile          # Construction de l'image
├── ansible/
│   ├── inventory.ini       # Les CT du projet (jenkins, docker, recette)
│   ├── install-docker.yml  # Installation de Docker
│   └── install-jenkins.yml # Installation de Jenkins + Java 21
├── terraform/
│   ├── main.tf             # Définition du CT de recette
│   ├── variables.tf        # Paramètres
│   └── .terraform.lock.hcl # Versions des providers
├── Jenkinsfile             # Pipeline CI/CD
└── README.md
```

## Le pipeline

| Étape                 | Action                                                              |
|-----------------------|---------------------------------------------------------------------|
| Recette : déployer    | Construit l'image et lance le conteneur sur `debtest01`             |
| Recette : tester      | Vérifie que la page répond et contient le texte attendu             |
| Validation            | Pause : un humain doit cliquer sur **Déployer**                     |
| Production : déployer | Construit l'image et lance le conteneur sur `debdock01`             |

Si le test de recette échoue, le pipeline s'arrête et la production n'est jamais touchée.

## Reconstruire l'environnement

### 1. Créer le CT de recette (Terraform)

```bash
cd terraform
# Créer un fichier terraform.tfvars (non versionné) :
#   proxmox_api_token = "root@pam!terraform=SECRET"
#   gateway           = "192.168.1.1"
terraform init
terraform plan
terraform apply
```

### 2. Configurer les CT (Ansible)

```bash
cd ansible
ansible all -i inventory.ini -m ping
ansible-playbook -i inventory.ini install-docker.yml
ansible-playbook -i inventory.ini install-jenkins.yml
```

### 3. Préparer Jenkins

- Installer les plugins **Pipeline** et **Git**
- Donner à l'utilisateur `jenkins` une clé SSH autorisée sur `debtest01` et `debdock01`
- Créer un job **Pipeline** → *Pipeline script from SCM* → ce dépôt, branche `main`
- Activer *Poll SCM* : `H/2 * * * *`

### 4. Tester la chaîne

Modifier `VERSION` dans `app/app.py`, puis :

```bash
git add . && git commit -m "Nouvelle version" && git push
```

- Recette : http://192.168.1.93:5000
- Production : http://192.168.1.73:5000 (après validation dans Jenkins)

## Problèmes rencontrés et solutions

| Problème | Cause | Solution |
|----------|-------|----------|
| Deux CT avec la même adresse MAC | CT cloné | Régénérer la MAC, le `machine-id` et les clés SSH du clone |
| `apt_repository` échoue dans Ansible | `gpg`/`apt-key` absents sur Debian 13 minimal | Écrire le fichier `.list` avec le module `copy` |
| Jenkins : « Network is unreachable » | Passerelle IPv4 absente sur le CT | Ajouter la passerelle dans la configuration réseau du CT |
| Terraform : template introuvable | Le stockage `local` est propre à chaque nœud Proxmox | Télécharger le template sur le nœud cible |
| Ansible : « Host key verification failed » | Première connexion SSH à un nouveau CT | Valider la clé d'hôte une première fois |

## Sécurité

- Le secret du jeton Proxmox est dans `terraform.tfvars`, **exclu du dépôt** par `.gitignore`
- L'état Terraform (`*.tfstate`) reste sur le poste d'administration et n'est pas versionné
- Les CT créés par Terraform n'ont pas de mot de passe root : accès par clé SSH uniquement
- Les adresses IP présentes ici sont celles d'un réseau local privé

## Pistes d'amélioration

- Ajouter un **registre d'images** pour construire l'image une seule fois
- **Importer** les CT existants dans Terraform
- Ajouter des **tests unitaires** Python dans le pipeline
- Utiliser un **agent Jenkins** séparé plutôt que le nœud principal
