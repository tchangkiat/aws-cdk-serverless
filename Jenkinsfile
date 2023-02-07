pipeline {
  agent any
    
  stages {
    stage('Clone source code') {
      steps {
        git 'https://github.com/tchangkiat/aws-cdk-serverless'
      }
    }
     
    stage('CDK Synthesize') {
      steps {
        sh 'npm install'
          sh 'cdk synth'
      }
    }
  }
}
