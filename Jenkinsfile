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
				sh 'mkdir textfiles' || true'
				sh '/usr/bin/python /home/losmith/practice_python/list_comprehensions.py > textfiles/list_output.txt'
				archiveArtifacts artifacts: '**/textfiles/*.txt', fingerprint:true
			}
		}
		stage('Test') {
			steps {
				sh '/usr/bin/python /home/losmith/practice_python/even_odd.py 355'
			}
		}
	}
}
