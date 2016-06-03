all: tmp/attributes_raw.json tmp/modules_raw.json

tmp/attributes_raw.json: tmp/PS3.3-space-expand.html
	python modules_attributes.py $< $@

tmp/modules_raw.json: tmp/PS3.3-space-expand.html
	python ciod_modules.py $< $@

tmp/PS3.3-space-expand.html: PS3.3.html
	cat $< | sed -e 's/&nbps;/ /g' > $@

clean: 
	rm -f *.pyc tmp/*

install:
	pip install -r requirements.txt