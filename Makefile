venv: requirements.txt
	virtualenv -p python2.7 venv
	venv/bin/pip install -r requirements.txt

run: venv
	FLASK_APP=abetterurltoday.py venv/bin/flask run

.PHONY: clean

clean:
	rm -rf venv
