#!/bin/bash

#This is dockyard script authored by Rajesh Yogeshwar on Feb 27, 2017

#Exporting local.yml as it hold environment variables for development
export COMPOSE_FILE=local.yml

dir="$PWD"
cur=${PWD##*/}


if [ "$1" == "generate_tenant_migrations" ]; then
	echo -e "Executing makemigrations followed by migrate..."
	docker-compose -f local.yml run django python manage.py makemigrations administrator common personnel competence leaves claims benefits learning performance succession 


elif [ "$1" == "migrate_shared_schemas" ]; then
	echo -e "Executing makemigrations followed by migrate..."
	docker-compose -f local.yml run django python manage.py makemigrations customer
	docker-compose -f local.yml run django python manage.py migrate_schemas --shared


elif [ "$1" == "migrate_tenant_schemas" ]; then
	echo -e "Executing makemigrations followed by migrate..."
	docker-compose -f local.yml run django python manage.py makemigrations common administrator personnel competence leaves claims benefits learning performance succession reports
	docker-compose -f local.yml run django python manage.py migrate_schemas --tenant --executor=parallel


elif [ "$1" == "showmigrations" ]; then
	echo -e "Showing migrations..."
	docker-compose -f local.yml run django python manage.py showmigrations


elif [ "$1" == "shell" ]; then
	echo -e "Opening ipython..."
	docker-compose -f local.yml run django python manage.py shell_plus --ipython


elif [ "$1" == "build" ]; then
	echo -e "Building container..."
	docker-compose -f local.yml build --no-cache


elif [ "$1" == "down" ]; then
	echo -e "Stopping and removing down your containers, networks, volumes, and images created by up"
	docker-compose -f local.yml down


elif [ "$1" == "up" ]; then
	echo -e "Starting containers..."
	docker-compose -f local.yml up --build


elif [ "$1" == "qup" ]; then
	echo -e "Starting containers..."
	docker-compose -f local.yml up -d
	docker logs ocr_receipt_scanner_django_1 --tail 300 --follow


elif [ "$1" == "createsuperuser" ]; then
	docker-compose -f local.yml run django python manage.py createsuperuser


elif [ "$1" == "createuser" ]; then
	docker-compose -f local.yml run django python manage.py createuser


elif [ "$1" == "collectstatic" ]; then
	docker-compose -f local.yml run django python manage.py collectstatic --noinput
	

elif [ "$1" == "removeconts" ]; then
	docker rm `docker ps -aq -f status=exited`

elif [ "$1" == "open_django_container" ]; then
	docker exec -i -t rhombus_django_1 bash

elif [ "$1" == "open_db_container" ]; then
	docker exec -i -t rhombus_postgres_1 bash

elif [ "$1" == "myup" ]; then
	docker-compose up -f local.yml -d
	docker logs rhombus_django_1 --tail 1 --follow

#Custom startapp to put new apps inside root folder
elif [ "$1" == "startapp" ]; then
	echo -e "Creating new app ${@:2}"
	mkdir -p $cur/"${@:2}"
	touch $cur/"${@:2}"/apps.py $cur/"${@:2}"/models.py $cur/"${@:2}"/urls.py $cur/"${@:2}"/views.py $cur/"${@:2}"/__init__.py

elif [ "$1" == "getownership" ]; then
	echo -e "Getting ownership"
	sudo chown -R ${USER}:${USER} ../ocr_receipt_scanner/


elif [ "$1" == "makemigrations" ]; then
	echo -e "Running migrations"
	docker-compose -f local.yml run django python manage.py makemigrations


elif [ "$1" == "makemessages" ]; then
	echo -e "Running makemessages"
	docker-compose -f local.yml run django python manage.py makemessages -l fr
	docker-compose -f local.yml run django python manage.py compilemessages


elif [ "$1" == "tenant_shell" ]; then
	echo -e "Running schema specific command"
	docker-compose -f local.yml run django python manage.py tenant_command shell_plus --ipython --schema="$2"


elif [ "$1" == "checkimports" ]; then
	echo -e "Running importchecker"
	docker-compose -f local.yml run django importchecker "$2"


elif [ "$1" == "deletemigrations" ]; then
	sudo chown -R ${USER}:${USER} ../rhombus/
	echo -e "Deleting Migrations Folders"
	sudo rm -rf rhombus/administrator/migrations/
	sudo rm -rf rhombus/bizamp/migrations/	
	sudo rm -rf rhombus/benefits/migrations/
	sudo rm -rf rhombus/common/migrations/
	sudo rm -rf rhombus/competence/migrations/
	sudo rm -rf rhombus/claims/migrations/
	sudo rm -rf rhombus/customer/migrations/
	sudo rm -rf rhombus/learning/migrations/
	sudo rm -rf rhombus/leaves/migrations/
	sudo rm -rf rhombus/personnel/migrations/
	sudo rm -rf rhombus/performance/migrations/
	sudo rm -rf rhombus/succession/migrations/
	sudo rm -rf rhombus/reports/migrations/


elif [ "$1" == "test" ]; then
	echo -e "Executing test cases..."
	docker-compose -f local.yml run django python manage.py test tenant_schemas.test services --keepdb --settings=config.settings.test


elif [ "$1" == "stopcontainers" ]; then
	docker stop `docker ps -aq`

elif [ "$1" == "copy_ipython_config" ]; then
	docker-compose -f local.yml run django ipython profile create
    docker cp ipython_config.py rhombus_django_1:/root/.ipython/profile_default/ipython_config.py

elif [ "$1" == "copy_ipython_config" ]; then
	docker-compose -f local.yml run django ipython profile create
	docker cp ipython_config.py rhombus_django_1:/root/.ipython/profile_default/ipython_config.py


elif [ "$1" == "newservice" ]; then
	if [ -z "${@:2}" ]; then
		
		echo -e "Please provide a service name"

	else

		echo -e "Creating new service ${@:2}"
		mkdir -p services/"${@:2}"
		touch services/"${@:2}"/apis.py services/"${@:2}"/serializers.py services/"${@:2}"/urls.py
		echo "import logging

from rhombus.common.responses import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.views import JSONWebTokenAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_jwt.authentication import JSONWebTokenAuthentication


logger = logging.getLogger(__name__)" >> services/"${@:2}"/apis.py

		echo "import serpy

from django.utils.translation import gettext as _
from rest_framework_jwt.settings import api_settings
		" >> services/"${@:2}"/serializers.py

		echo "import services.${@:2}.apis as api_views

from django.conf import settings
from django.conf.urls import url

app_name = '${@:2}'

urlpatterns = []" >> services/"${@:2}"/urls.py

	fi
else
	echo -e "This command is not yet supported"

fi