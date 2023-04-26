CMD_BLACK		:=	black
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
	@echo "isort            run isort on code"
	@echo "black            run black on code"
	@echo "lint             run pylint on code"


define _isort
	$(CMD_ISORT) \
		--line-width="79" \
		--profile="black" \
	$(1)
endef

.PHONY: isort
isort:
	$(call _isort,"$(DIR_LIB)" "$(SCR_FRP)" "$(SCR_LVZ)")


define _black
	$(CMD_BLACK) \
		--line-length="79" \
	$(1)
endef

.PHONY: black
black:
	$(call _black,"$(DIR_LIB)" "$(SCR_FRP)" "$(SCR_LVZ)")


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
