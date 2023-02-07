pipeline {
  agent any
    
  stages {
    stage('CDK Synthesize') {
      steps {
        sh 'npm install'
          sh 'cdk synth'
      }
    }
  }
}
