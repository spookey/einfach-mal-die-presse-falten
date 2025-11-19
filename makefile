DIR_VENV		:= venv

CMD_BLACK		:= $(DIR_VENV)/bin/black
CMD_ISORT		:= $(DIR_VENV)/bin/isort
CMD_PIP			:= $(DIR_VENV)/bin/pip3
CMD_PYLINT		:= $(DIR_VENV)/bin/pylint
LIB_BSOUP		:= $(DIR_VENV)/lib/python\\*/site-packages/bs4/__init__.py

SOURCES			:= \
					"lib" \
					"frankenpest.py" \


.PHONY: help
help:
	@echo "Einfach mal die Presse falten!"
	@echo "------------------------------"
	@echo
	@echo "venv             create virtualenv"
	@echo "requirements     install requirements into venv"
	@echo "...-dev          ... development requirements ..."
	@echo
	@echo "isort            run isort on code"
	@echo "black            run black on code"
	@echo "pylint           run pylint on code"
	@echo
	@echo "action           run all above"


$(DIR_VENV):
	python3 -m venv "$(DIR_VENV)"
	$(CMD_PIP) install -U pip setuptools
$(LIB_BSOUP): $(DIR_VENV)
	$(CMD_PIP) install -r "requirements.txt"
$(CMD_BLACK) $(CMD_ISORT) $(CMD_PYLINT): $(DIR_VENV)
	$(CMD_PIP) install -r "requirements-dev.txt"

.PHONY: requirements
requirements: $(LIB_BSOUP)
.PHONY: requirements-dev
requirements-dev: $(CMD_BLACK) $(CMD_ISORT) $(CMD_PYLINT)


.PHONY: isort
isort: requirements-dev
	$(CMD_ISORT) --line-length="79" --profile="black" $(SOURCES)

.PHONY: black
black: requirements-dev
	$(CMD_BLACK) --line-length="79" $(SOURCES)

.PHONY: pylint
pylint: requirements-dev
	$(CMD_PYLINT) \
		--disable="missing-class-docstring" \
		--disable="missing-function-docstring" \
		--disable="missing-module-docstring" \
		--output-format="colorized" \
	$(SOURCES)

.PHONY: action
action: isort black pylint
