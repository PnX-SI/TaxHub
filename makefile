
develop:
	@/bin/bash -c "source venv/bin/activate&&python server.py runserver"


prod:
	@/bin/bash -c "./gunicorn_start.sh"

prod-stop:
	@kill `cat $(APP_NAME).pid`&&echo "Terminé."


shell:
	@/bin/bash -c "source $(VENV)/bin/activate&&python server.py shell"
