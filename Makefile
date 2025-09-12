.PHONY: demo-up demo-reset sign test web

demo-up:
	cd icn-node && docker-compose up -d
	python3 -m venv icn-node/venv || true
	. icn-node/venv/bin/activate && pip install -r icn-node/requirements.txt
	. icn-node/venv/bin/activate && alembic -c icn-node/alembic.ini upgrade head
	python3 scripts/demo_seed.py
	@echo "--- Demo ready. Try:"
	@echo "make web  # to open the mini viewer"

demo-reset:
	cd icn-node && docker-compose down -v
	rm -rf .demo
	mkdir -p .demo
	$(MAKE) demo-up

sign:
	python3 tools/sign.py --file $${FILE} --org $${ORG}

test:
	. icn-node/venv/bin/activate && pytest -q

web:
	cd icn-web && npm install && npm run dev -- --host | cat


