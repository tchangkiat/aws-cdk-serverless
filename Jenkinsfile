pipeline {
  agent any
  stages {
    stage('Synthesize') {
      agent any
      steps {
        sh '''npm ci
npm install -g aws-cdk
cdk synth'''
      }
    }

    stage('Deploy') {
      agent any
      steps {
        sh 'cdk deploy'
      }
    }

  }
}