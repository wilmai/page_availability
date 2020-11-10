
# maybe setup a venv before running this
#py -m venv venv
#source venv/bin/activate

py setup.py develop
pytest tests.py

# pick one
py -m page_availability runtime/kafka_ingest.yml
#py -m page_availability runtime/pg_load.yml
#py -m page_availability runtime/pg_inspect.yml
