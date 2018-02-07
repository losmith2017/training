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
				sh '/usr/bin/python /home/losmith/practice_python/list_comprehensions.py'
			}
		}
	}
}
