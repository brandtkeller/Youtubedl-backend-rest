pipeline {
   agent none
 
   environment {
         HOME_REPO = 'http://192.168.0.122:32600/brandtkeller/video-cache-backend.git'
         GITHUB_REPO = 'github.com/brandtkeller/video-cache-backend.git'
         REGISTRY = '192.168.0.128:5000/'
         IMAGE = '192.168.0.128:5000/video-cache-backend'
         FROM_IMAGE = 'ubuntu:latest'
         PROJECT = 'video-cache-backend'
    }

   stages {
      // On push to development branches run tests
      stage('Development build & push') {
          agent { node { label 'docker' } }
          options { skipDefaultCheckout true }
          when { not { branch 'master' } }
          steps {
            sh 'rm -rf *'
            sh 'git clone $HOME_REPO'
            sh 'echo Building....'
          }
      }
      // On push to master, build prod image and scan

      stage('Master build & push') {
          agent { node { label 'docker' } }
          options { skipDefaultCheckout true }
          when { branch 'master' }
          steps {
               sh 'rm -rf ${PROJECT} || echo "No Project folder present"'
               sh 'git clone ${HOME_REPO}'
               // Force the build command to pull a new latest tag image
               sh 'docker image rm ${FROM_IMAGE} || echo "No image to remove"'
               sh 'cd ${PROJECT} && docker build -t ${IMAGE}:0.0.${BUILD_NUMBER} .'
               sh 'docker push ${IMAGE}:0.0.${BUILD_NUMBER}'
               sh 'docker image rm ${IMAGE}:0.0.${BUILD_NUMBER}'
               sh 'rm -rf ${PROJECT}'
          }
      }

      stage('Rolling Deployment to Cluster') {
            agent { node { label 'docker' } }
            options { skipDefaultCheckout true }
            when { branch 'master' }
            steps {
                sh 'kubectl config set-context --current --namespace=app-development'
                sh 'kubectl set image deployments/video-cache-backend video-cache-backend=${IMAGE}:0.0.${BUILD_NUMBER}'
            }
        }

      stage('Mirror to public Github') {
         agent any
         options { skipDefaultCheckout true }
         when { branch 'master' }
         steps {
            catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
               withCredentials([usernamePassword(credentialsId: 'git_creds', passwordVariable: 'GIT_PASSWORD', usernameVariable: 'GIT_USERNAME')]) {
                            sh 'rm -rf *'
                            sh 'git clone --mirror $HOME_REPO'
               }
               withCredentials([usernamePassword(credentialsId: 'github_creds', passwordVariable: 'GIT_PASSWORD', usernameVariable: 'GIT_USERNAME')]) {
                           dir("${PROJECT}.git"){
                                 sh 'git remote add --mirror=fetch github https://$GIT_USERNAME:$GIT_PASSWORD@$GITHUB_REPO'
                                 sh 'git push github --all'
                           }
               }
            }
         }
      }
   }
}