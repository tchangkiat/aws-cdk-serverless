pipeline {
  agent {
    docker {
      image 'node:lts-bullseye-slim' 
      args '-p 3000:3000' 
    }
  }
  stages {
    stage('Install dependencies') {
      steps {
        sh 'sudo chown -R 995:993 "/.npm"'
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
