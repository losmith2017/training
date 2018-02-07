env.BUILD_ID = 5.0
pipeline {
	agent any
	stages {
		stage('Stage 1') {
			steps {
				echo "Hello World"
				echo env.BUILD_ID
			}
		}
		stage('Stage 2') {
			steps {
				sh '/usr/bin/python /home/losmith/practice_python/list_comprehensions.py > list_output.txt'
				archiveArtifacts artifacts: '**/*.txt', fingerprint true
		}
	}
}
