# page_availability

## py -m page_availability runtime/kafka_ingest.yml
Poll a list of urls and ingest the data into kafka

## py -m page_availability runtime/pg_load.yml
Consume page availability data from kafka and load into postgresql

## py -m page_availability runtime/pg_inspect.yml
Print out records from postgresql for debugging
