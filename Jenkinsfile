pipeline {
	agent any
	stages {
		stage('Stage 1') {
			steps {
				echo "Hello World"
			}
		}
		stage('Stage 2') {
			steps {
				sh 'list_comprehensions.py'
			}
		}
	}
}
