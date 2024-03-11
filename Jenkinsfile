pipeline {
  agent any
  stages {
    stage("verify tooling") {
      steps {
        sh '''
          sudo docker version
          sudo docker info
          sudo docker compose version 
          sudo curl --version
        '''
      }
    }
    stage('Prune Docker data') {
      steps {
        sh 'sudo docker compose down'
        sh 'sudo docker system prune -a --volumes -f'
        sh 'sudo apt-get update -y'
        sh 'sudo apt-get install libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libcairo2 libcairo-gobject2 libffi-dev shared-mime-info -y'

      }
    }
    stage('Start container') {
      steps {

        sh 'sudo docker compose build'
        sh 'sudo docker compose up -d'
        sh 'sudo docker compose ps'
      }
    }
  }
  post {
    failure {
      sh 'sudo docker compose down --remove-orphans -v'
      sh 'sudo docker compose ps'
    }
  }
}