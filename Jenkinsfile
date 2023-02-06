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
        sh 'node -v'
        sh 'npm -v'
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
        sh 'npx cdk bootstrap'
      }
    }

    stage('CDK synth') {
      steps {
        sh 'npx cdk synth'
      }
    }

    stage('CDK deploy') {
      steps {
        sh 'npx cdk deploy --require-approval=never'
      }
    }
  }
}
