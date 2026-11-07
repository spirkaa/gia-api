pipeline {
  agent any

  options {
    buildDiscarder(logRotator(numToKeepStr: '10', daysToKeepStr: '60'))
    parallelsAlwaysFailFast()
    disableConcurrentBuilds()
  }

  triggers {
    cron(BRANCH_NAME == 'main' ? 'H 8 * * 6' : '')
  }

  environment {
    REGISTRY = 'git.devmem.ru'
    REGISTRY_URL = "https://${REGISTRY}"
    REGISTRY_CREDS_ID = 'gitea-user'
    IMAGE_OWNER = 'projects'
    IMAGE_BASENAME = 'gia-api'
    IMAGE_FULLNAME = "${REGISTRY}/${IMAGE_OWNER}/${IMAGE_BASENAME}"
    IMAGE_ALT_TAG = 'latest'
    DOCKERFILE = '.docker/django/Dockerfile'
    LABEL_AUTHORS = 'Ilya Pavlov <piv@devmem.ru>'
    LABEL_TITLE = 'GIA API'
    LABEL_DESCRIPTION = 'GIA API'
    LABEL_URL = 'https://gia-api.devmem.ru'
    LABEL_CREATED = sh(script: "date '+%Y-%m-%dT%H:%M:%S%:z'", returnStdout: true).toString().trim()
    REVISION = GIT_COMMIT.take(7)

    GPG_KEY_CREDS_ID = 'jenkins-gpg-key'
    HELM_CHART_GIT_URL = 'https://git.devmem.ru/projects/helm-charts.git'
  }

  parameters {
    booleanParam(name: 'BUMP_HELM', defaultValue: false, description: 'Bump Helm chart version?')
    booleanParam(name: 'REBUILD', defaultValue: false, description: 'Rebuild this revision image?')
  }

  stages {
    stage('Pre') {
      parallel {
        stage('Run prek (pre-commit)') {
          agent {
            docker {
              image 'ghcr.io/j178/prek:alpine'
              alwaysPull true
              reuseNode true
              args '-v /tmp/.cache:/tmp/.cache --entrypoint=""'
            }
          }
          when {
            beforeAgent true
            not {
              anyOf {
                expression { params.DEPLOY }
                expression { params.BUMP_HELM }
                tag ''
              }
            }
          }
          steps {
            cache(path: "/tmp/.cache/prek", key: "prek-${hashFiles('**/.pre-commit-config.yaml')}") {
              sh '''
                export PREK_HOME=/tmp/.cache/prek
                if ! prek run --all-files --show-diff-on-failure --verbose --color always; then
                  [ -r "${PREK_HOME}/prek.log" ] && cat "${PREK_HOME}/prek.log"
                  exit 1
                fi
              '''
            }
          }
        }

        stage('Run uv audit') {
          when {
            beforeAgent true
            not {
              anyOf {
                expression { params.DEPLOY }
                expression { params.BUMP_HELM }
                tag ''
              }
            }
          }
          agent {
            docker {
              image 'ghcr.io/astral-sh/uv:python3.13-trixie-slim'
              alwaysPull true
              reuseNode true
              args '-e UV_PYTHON_DOWNLOADS=never'
            }
          }
          steps {
            script {
              warnError(message: 'uv audit: known vulnerabilities found in uv.lock (details in stage log)') {
                sh 'uv audit --preview-features audit-command'
              }
            }
          }
        }
      }
    }

    stage('Build') {
      parallel {
        stage('Build api image (k8s)') {
          when {
            not {
              branch 'main'
            }
            not {
              anyOf {
                expression { params.DEPLOY }
                expression { params.REBUILD }
                triggeredBy 'TimerTrigger'
                tag ''
              }
            }
          }
          steps {
            script {
              buildDockerImage(
                dockerFile: "${DOCKERFILE}",
                tag: "${REVISION}-k8s",
                altTag: "${IMAGE_ALT_TAG}-k8s",
                useCache: true,
                cacheFrom: "${IMAGE_FULLNAME}:${IMAGE_ALT_TAG}-k8s",
                pushToRegistry: 'no',
                deleteBuild: 'no',
              )
            }
          }
        }

        stage('Build and push api image (k8s)') {
          when {
            branch 'main'
            not {
              anyOf {
                expression { params.DEPLOY }
                expression { params.REBUILD }
                triggeredBy 'TimerTrigger'
                triggeredBy cause: 'UserIdCause'
                changeRequest()
                tag ''
              }
            }
          }
          steps {
            script {
              buildDockerImage(
                dockerFile: "${DOCKERFILE}",
                tag: "${REVISION}-k8s",
                altTag: "${IMAGE_ALT_TAG}-k8s",
                useCache: true,
                cacheFrom: "${IMAGE_FULLNAME}:${IMAGE_ALT_TAG}-k8s",
              )
            }
          }
        }

        stage('Build and push api image (k8s) (no cache)') {
          when {
            branch 'main'
            anyOf {
              expression { params.REBUILD }
              triggeredBy 'TimerTrigger'
            }
          }
          steps {
            script {
              buildDockerImage(
                dockerFile: "${DOCKERFILE}",
                tag: "${REVISION}-k8s",
                altTag: "${IMAGE_ALT_TAG}-k8s",
              )
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
            expression { params.BUMP_HELM }
            tag ''
          }
        }
      }
      environment {
        APP_IMAGE = "${IMAGE_FULLNAME}:${REVISION}-k8s"
        DB_IMAGE = 'postgres:17-alpine'
      }
      steps {
        script {
          docker.image("${DB_IMAGE}").withRun('-e POSTGRES_USER=dbuser -e POSTGRES_PASSWORD=dbpass') { db ->
            docker.withRegistry("${REGISTRY_URL}", "${REGISTRY_CREDS_ID}") {
              docker.image("${APP_IMAGE}").inside(
                "-e DJANGO_DATABASE_URL=postgres://dbuser:dbpass@db:5432/dbuser \
                -e DJANGO_SETTINGS_MODULE=config.settings.local \
                -e PYTHONPATH=\${WORKSPACE}/gia-api \
                -e PYTHONWARNINGS=always \
                -e PYTHONUNBUFFERED=1 \
                -u root \
                --entrypoint='' \
                --link ${db.id}:db"
                ) {
                  sh 'uv sync --locked --no-dev --group=test'
                  sh 'pytest --cov-report xml:reports/cobertura-coverage.xml --junitxml=reports/junit.xml'
              }
            }
          }
        }
      }
      post {
        always {
          sh "docker rmi ${APP_IMAGE}"
        }
        success {
          junit 'reports/junit.xml'
          recordCoverage tools: [[parser: 'COBERTURA', pattern: 'reports/cobertura-coverage.xml']]
        }
      }
    }

    stage('Bump Helm chart version') {
      when {
        anyOf {
          tag 'v*'
          allOf {
            branch 'main'
            expression { params.BUMP_HELM }
          }
        }
      }
      steps {
        script {
          bumpHelmChartVersion(
            chartName: 'gia',
            imgName: 'gia-api',
            imgRevision: "${REVISION}-k8s"
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
