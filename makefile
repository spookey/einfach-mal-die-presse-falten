CMD_ISORT		:=	isort
CMD_PYLINT		:=	pylint

DIR_LIB			:=	lib
SCR_FRP			:=	frankenpest.py
SCR_LVZ			:=	leipziger_vollzeitung.py


.PHONY: help
help:
	@echo "Einfach mal die Presse falten!"
	@echo "------------------------------"
	@echo
	@echo "sort             run isort on code"
	@echo "lint             run pylint on code"


define _isort
	$(CMD_ISORT) -cs -fss -m=5 -y -rc $(1)
endef

.PHONY: sort
sort:
	$(call _isort,"$(DIR_LIB)" "$(SCR_FRP)" "$(SCR_LVZ)")



define PYLINT_MESSAGE_TEMPLATE
{C} {path}:{line}:{column} - {msg}
  ↪  {category} {module}.{obj} ({symbol} {msg_id})
endef
export PYLINT_MESSAGE_TEMPLATE

define _lint
	$(CMD_PYLINT) \
		--disable "C0111" \
		--msg-template="$$PYLINT_MESSAGE_TEMPLATE" \
		--output-format="colorized" \
			$(1)
endef

.PHONY: lint
lint:
	$(call _lint,"$(DIR_LIB)" "$(SCR_FRP)" "$(SCR_LVZ)")
