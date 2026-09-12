pipeline {

    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing Python dependencies...'

                bat '''
                    python -m pip install --upgrade pip
                    python -m pip install -r requirements.txt
                '''
            }
        }

        stage('Code Quality') {
            steps {
                echo 'Running Flake8...'

                bat '''
                    flake8 app tests
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running unit tests...'

                bat '''
                    pytest -v
                '''
            }
        }

        stage('Build') {
            steps {
                echo 'Building application...'

                bat '''
                    python build.py
                '''
            }
        }
    }

    post {

        success {
            echo '================================'
            echo 'PIPELINE SUCCESSFUL'
            echo '================================'
        }

        failure {
            echo '================================'
            echo 'PIPELINE FAILED'
            echo '================================'
        }

        always {
            echo 'Pipeline execution completed.'
        }
    }
}