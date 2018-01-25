pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'python ./list_overlap.sh'
            }
        }
    }
}
