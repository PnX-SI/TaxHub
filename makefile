HOST=0.0.0.0
PORT=8000
VENV=venv
WORKERS=4
APP_NAME=taxhub

develop:
	@/bin/bash -c "source $(VENV)/bin/activate&&python server.py runserver -d -r -h $(HOST) -p $(PORT)"


prod:
	@/bin/bash -c "source $(VENV)/bin/activate&&gunicorn --daemon --error-log /tmp/errors.log -w $(WORKERS) -b '$(HOST):$(PORT)' -n '$(APP_NAME)' server:app"&&echo "Serveur activé sur '$(HOST):$(PORT)'"


prod-stop:
	@kill `ps hx|grep $(APP_NAME)|cut -d' ' -f1`&&echo "Terminé"


shell:
	@/bin/bash -c "source $(VENV)/bin/activate&&python server.py shell"
