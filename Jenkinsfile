pipeline {
    agent any

    stages {

        stage('Recette : déployer') {
            environment {
                DOCKER_HOST = 'ssh://root@192.168.1.93'
            }
            steps {
                sh '''
                    docker build -t mon-app:${BUILD_NUMBER} app/
                    docker rm -f mon-app || true
                    docker run -d --name mon-app --restart unless-stopped -p 5000:5000 mon-app:${BUILD_NUMBER}
                '''
            }
        }

        stage('Recette : tester') {
            steps {
                sh '''
                    sleep 5
                    python3 -c "import urllib.request; print(urllib.request.urlopen('http://192.168.1.93:5000', timeout=10).read().decode())" | grep "Bonjour Lamine"
                '''
            }
        }

        stage('Validation') {
            steps {
                input message: 'Recette OK sur http://192.168.1.93:5000. Déployer en production ?', ok: 'Déployer'
            }
        }

        stage('Production : déployer') {
            environment {
                DOCKER_HOST = 'ssh://root@192.168.1.73'
            }
            steps {
                sh '''
                    docker build -t mon-app:${BUILD_NUMBER} app/
                    docker rm -f mon-app || true
                    docker run -d --name mon-app --restart unless-stopped -p 5000:5000 mon-app:${BUILD_NUMBER}
                '''
            }
        }
    }
}