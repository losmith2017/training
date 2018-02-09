pipeline {
	agent any
	stages {
		stage('Stage 1') {
			steps {
				echo "Hello World"
				echo "env.BUILD_ID"
			}
		}
		stage('Stage 2') {
			steps {
				sh 'mkdir textfiles || true'
				sh '/usr/bin/python /home/losmith/practice_python/list_comprehensions.py > textfiles/list_output.txt'
				sh '/usr/bin/python /home/losmith/practice_python/list_ends.py'
				archiveArtifacts artifacts: '**/textfiles/*.txt', fingerprint:true
			}
		}
	}
}
