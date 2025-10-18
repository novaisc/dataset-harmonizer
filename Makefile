output = output.txt

run:
	@python app.py

output:
	@python app.py > $(output) 2>&1 &

