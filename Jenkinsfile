pipeline {
    agent any

    environment {
        // Jenkins pilote le Docker de debdock01 via SSH
        DOCKER_HOST = 'ssh://root@192.168.1.73'
    }

    stages {
        stage('Construire l\'image') {
            steps {
                sh 'docker build -t mon-app:${BUILD_NUMBER} app/'
            }
        }

        stage('Déployer') {
            steps {
                sh '''
                    docker rm -f mon-app || true
                    docker run -d --name mon-app --restart unless-stopped -p 5000:5000 mon-app:${BUILD_NUMBER}
                '''
            }
        }
    }
}