pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build') {
            steps {
                sh 'docker build -t flask-app .'
            }
        }
        
        stage('Test') {
            steps {
                sh 'docker run --rm flask-app python -m pytest'
            }
        }
        
        stage('Push to Registry') {
            when {
                branch 'main'
            }
            steps {
 		withDockerRegistry(credentialsId: 'dockerhub-credentials-fnz-id', url: 'https://index.docker.io/v1/') {
                        sh 'docker push raniabenabdallah11/flask-app:latest'

            }
        }
        
        stage('Deploy') {
            when {
                branch 'CI_CD'
            }
            steps {
                docker run -d --name flask-app -p 5000:5000 flask-app-jenkins
            }
        }
    }
    
    post {
        success {
            script {
                if (env.CHANGE_ID) {
                    pullRequest.comment('Pipeline réussie ! Prêt pour la revue.')
                }
            }
        }
        failure {
            script {
                if (env.CHANGE_ID) {
                    pullRequest.comment('Échec du pipeline. Veuillez vérifier les logs.')
                }
            }
        }
    }
}
