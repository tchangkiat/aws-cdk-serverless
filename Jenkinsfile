pipeline {
  agent any
  stages {
    stage('Install dependencies') {
      steps {
        sh 'npm install -g aws-cdk'
        sh 'npm install'
      }
    }

    stage('Build dependencies') {
      steps {
        sh 'npm run build'
      }
    }

    stage('CDK bootstrap') {
      steps {
        sh 'cdk bootstrap'
      }
    }

    stage('CDK synth') {
      steps {
        sh 'cdk synth'
      }
    }

    stage('CDK deploy') {
      steps {
        sh 'cdk deploy --require-approval=never'
      }
    }
  }
}
