def buildImageCache(String tag, String altTag = null) {
  IMAGE_TAG = "${tag}"
  DOCKERFILE = '.docker/django/ci.Dockerfile'
  docker.withRegistry("${REGISTRY_URL}", "${REGISTRY_CREDS_ID}") {
    def myImage = docker.build(
      "${IMAGE_FULLNAME}:${IMAGE_TAG}",
      "--label \"org.opencontainers.image.created=${LABEL_CREATED}\" \
      --label \"org.opencontainers.image.authors=${LABEL_AUTHORS}\" \
      --label \"org.opencontainers.image.url=${LABEL_URL}\" \
      --label \"org.opencontainers.image.source=${GIT_URL}\" \
      --label \"org.opencontainers.image.version=${IMAGE_TAG}\" \
      --label \"org.opencontainers.image.revision=${REVISION}\" \
      --label \"org.opencontainers.image.title=${LABEL_TITLE}\" \
      --label \"org.opencontainers.image.description=${LABEL_DESCRIPTION}\" \
      --progress=plain \
      --cache-from ${IMAGE_FULLNAME}:${IMAGE_TAG} \
      -f ${DOCKERFILE} ."
    )
    myImage.push()
    if(altTag) {
      myImage.push(altTag)
    }
    sh "docker rmi -f \$(docker inspect -f '{{ .Id }}' ${myImage.id})"
  }
}

def buildImageNoCache(String tag, String altTag = null) {
  IMAGE_TAG = "${tag}"
  DOCKERFILE = ".docker/django/ci.Dockerfile"
  docker.withRegistry("${REGISTRY_URL}", "${REGISTRY_CREDS_ID}") {
    def myImage = docker.build(
      "${IMAGE_FULLNAME}:${IMAGE_TAG}",
      "--label \"org.opencontainers.image.created=${LABEL_CREATED}\" \
      --label \"org.opencontainers.image.authors=${LABEL_AUTHORS}\" \
      --label \"org.opencontainers.image.url=${LABEL_URL}\" \
      --label \"org.opencontainers.image.source=${GIT_URL}\" \
      --label \"org.opencontainers.image.version=${IMAGE_TAG}\" \
      --label \"org.opencontainers.image.revision=${REVISION}\" \
      --label \"org.opencontainers.image.title=${LABEL_TITLE}\" \
      --label \"org.opencontainers.image.description=${LABEL_DESCRIPTION}\" \
      --progress=plain \
      --pull \
      --no-cache \
      -f ${DOCKERFILE} ."
    )
    myImage.push()
    if(altTag) {
      myImage.push(altTag)
    }
    sh "docker rmi -f \$(docker inspect -f '{{ .Id }}' ${myImage.id})"
  }
}

pipeline {
  agent any

  options {
    buildDiscarder(logRotator(numToKeepStr: '10', daysToKeepStr: '60'))
    parallelsAlwaysFailFast()
    disableConcurrentBuilds()
  }

  triggers {
    cron('H 8 * * 6')
  }

  environment {
    REGISTRY = 'git.devmem.ru'
    REGISTRY_URL = "https://${REGISTRY}"
    REGISTRY_CREDS_ID = 'gitea-user'
    IMAGE_OWNER = 'cr'
    IMAGE_BASENAME = 'gia-api'
    IMAGE_FULLNAME = "${REGISTRY}/${IMAGE_OWNER}/${IMAGE_BASENAME}"
    LABEL_AUTHORS = 'Ilya Pavlov <piv@devmem.ru>'
    LABEL_TITLE = 'GIA API'
    LABEL_DESCRIPTION = 'GIA API'
    LABEL_URL = 'https://gia-api.devmem.ru'
    LABEL_CREATED = sh(script: "date '+%Y-%m-%dT%H:%M:%S%:z'", returnStdout: true).toString().trim()
    REVISION = GIT_COMMIT.take(7)

    ANSIBLE_IMAGE = "${REGISTRY}/${IMAGE_OWNER}/ansible:base"
    ANSIBLE_CONFIG = '.ansible/ansible.cfg'
    ANSIBLE_PLAYBOOK = '.ansible/playbook.yml'
    ANSIBLE_INVENTORY = '.ansible/hosts'
    ANSIBLE_CREDS_ID = 'jenkins-ssh-key'
    ANSIBLE_VAULT_CREDS_ID = 'ansible-vault-password'
  }

  parameters {
    booleanParam(name: 'DEPLOY', defaultValue: false, description: 'Deploy this revision?')
    booleanParam(name: 'REBUILD', defaultValue: false, description: 'Reduild this revision image?')
    string(name: 'ANSIBLE_EXTRAS', defaultValue: '', description: 'ansible-playbook extra params')
  }

  stages {
    stage('Set env vars') {
      steps {
        script {
          env.DOCKER_BUILDKIT = 1
        }
      }
    }

    stage('Build') {
      parallel {
        stage('Build api image (no cache)') {
          when {
            anyOf {
              expression { params.REBUILD }
              triggeredBy 'TimerTrigger'
            }
          }
          steps {
            script {
              buildImageNoCache("${REVISION}", 'latest')
            }
          }
        }

        stage('Build api image') {
          when {
            not {
              anyOf {
                expression { params.DEPLOY }
                expression { params.REBUILD }
                triggeredBy 'TimerTrigger'
                triggeredBy cause: 'UserIdCause'
              }
            }
          }
          steps {
            script {
              buildImageCache("${REVISION}", 'latest')
            }
          }
        }

        stage('Build postgres image') {
          when {
            not {
              anyOf {
                expression { params.DEPLOY }
                expression { params.REBUILD }
                triggeredBy 'TimerTrigger'
                triggeredBy cause: 'UserIdCause'
              }
            }
          }
          steps {
            script {
              def IMAGE_BASENAME = 'postgres'
              def IMAGE_FULLNAME = "${REGISTRY}/${IMAGE_OWNER}/${IMAGE_BASENAME}:latest"
              def DOCKERFILE = ".docker/${IMAGE_BASENAME}/Dockerfile"
              docker.withRegistry("${REGISTRY_URL}", "${REGISTRY_CREDS_ID}") {
                def myImage = docker.build(
                  "${IMAGE_FULLNAME}",
                  "--progress=plain \
                  --cache-from ${IMAGE_FULLNAME} \
                  -f ${DOCKERFILE} .docker/${IMAGE_BASENAME}"
                )
                myImage.push()
                sh "docker rmi -f \$(docker inspect -f '{{ .Id }}' ${myImage.id})"
              }
            }
          }
        }

        stage('Build redis image') {
          when {
            not {
              anyOf {
                expression { params.DEPLOY }
                expression { params.REBUILD }
                triggeredBy 'TimerTrigger'
                triggeredBy cause: 'UserIdCause'
              }
            }
          }
          steps {
            script {
              def IMAGE_BASENAME = 'redis'
              def IMAGE_FULLNAME = "${REGISTRY}/${IMAGE_OWNER}/${IMAGE_BASENAME}:latest"
              def DOCKERFILE = ".docker/${IMAGE_BASENAME}/Dockerfile"
              docker.withRegistry("${REGISTRY_URL}", "${REGISTRY_CREDS_ID}") {
                def myImage = docker.build(
                  "${IMAGE_FULLNAME}",
                  "--progress=plain \
                  --cache-from ${IMAGE_FULLNAME} \
                  -f ${DOCKERFILE} .docker/${IMAGE_BASENAME}"
                )
                myImage.push()
                sh "docker rmi -f \$(docker inspect -f '{{ .Id }}' ${myImage.id})"
              }
            }
          }
        }
      }
    }

    stage('Test') {
      when {
        not {
          anyOf {
            expression { params.DEPLOY }
            triggeredBy cause: 'UserIdCause'
          }
        }
      }
      environment {
        APP_IMAGE = "${IMAGE_FULLNAME}:${REVISION}"
        DB_IMAGE = "${REGISTRY}/${IMAGE_OWNER}/postgres:latest"
      }
      steps {
        script {
          docker.withRegistry("${REGISTRY_URL}", "${REGISTRY_CREDS_ID}") {
            docker.image("${DB_IMAGE}").withRun('-e POSTGRES_USER=dbuser -e POSTGRES_PASSWORD=dbpass') { db ->
              docker.image("${APP_IMAGE}").inside(
                "-e DJANGO_DATABASE_URL=postgres://dbuser:dbpass@db:5432/dbuser \
                -e DJANGO_SETTINGS_MODULE=config.settings.local \
                -e PYTHONPATH=\${WORKSPACE}/gia-api \
                --entrypoint='' \
                --link ${db.id}:db"
                ) {
                  sh 'pip install --no-cache-dir -r gia-api/requirements/testing.txt'
                  sh 'pytest --cov-report xml:reports/coverage.xml --junitxml=reports/pytest.xml'
              }
            }
          }
        }
      }
      post {
        always {
          sh "docker rmi ${DB_IMAGE} ${APP_IMAGE}"
        }
        success {
          junit 'reports/pytest.xml'
          cobertura coberturaReportFile: 'reports/coverage.xml', enableNewApi: true
        }
      }
    }

    stage('Deploy') {
      agent {
        docker {
          image env.ANSIBLE_IMAGE
          registryUrl env.REGISTRY_URL
          registryCredentialsId env.REGISTRY_CREDS_ID
          alwaysPull true
          reuseNode true
        }
      }
      when {
        beforeAgent true
        expression { params.DEPLOY }
      }
      environment {
        SMTP_CREDS_ID = 'common-smtp-noreply'
        SMTP_HOST = 'smtp.devmem.ru'
        SMTP_PORT = '587'
      }
      steps {
        sh 'ansible --version'
        withCredentials([
          usernamePassword(credentialsId: "${REGISTRY_CREDS_ID}", usernameVariable: 'REGISTRY_USER', passwordVariable: 'REGISTRY_PASSWORD'),
          usernamePassword(credentialsId: "${SMTP_CREDS_ID}", usernameVariable: 'SMTP_USER', passwordVariable: 'SMTP_PASSWORD')
          ]) {
          ansiblePlaybook(
            colorized: true,
            credentialsId: "${ANSIBLE_CREDS_ID}",
            vaultCredentialsId: "${ANSIBLE_VAULT_CREDS_ID}",
            playbook: "${ANSIBLE_PLAYBOOK}",
            extras: "${params.ANSIBLE_EXTRAS} --syntax-check"
          )
          ansiblePlaybook(
            colorized: true,
            credentialsId: "${ANSIBLE_CREDS_ID}",
            vaultCredentialsId: "${ANSIBLE_VAULT_CREDS_ID}",
            playbook: "${ANSIBLE_PLAYBOOK}",
            extras: "${params.ANSIBLE_EXTRAS}"
          )
        }
      }
    }
  }

  post {
    always {
      emailext(
        to: '$DEFAULT_RECIPIENTS',
        subject: '$DEFAULT_SUBJECT',
        body: '$DEFAULT_CONTENT'
      )
    }
  }
}
