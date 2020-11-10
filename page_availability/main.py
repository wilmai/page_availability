import argparse
import os
import yaml
import time
from kafka import KafkaProducer, KafkaConsumer

from .page_poller import PagePoller
from .page_database import PageDatabase
from .conversions import page_request_result_to_json, json_to_page_request_result


def kafka_ingest(config: dict) -> None:

    kproducer = KafkaProducer(
        bootstrap_servers=config['kafka_bootstrap_servers'],
        security_protocol="SSL",
        ssl_cafile=config['kafka_ssl_cafile'],
        ssl_certfile=config['kafka_ssl_certfile'],
        ssl_keyfile=config['kafka_ssl_keyfile'],
        )

    topic = config['kafka_topic']
    def produce_results(result):
        try:
            jsenc = page_request_result_to_json(result)
            kproducer.send(topic, jsenc.encode('utf-8'))
            print("Produced to kafka", result.url, result.status)
        except:
            print("Unable to produce result to kafka")
            raise


    poller = PagePoller(
        request_timeout=config['request_timeout'],
        allow_redirects=config['allow_redirects'],
        polling_cycle_time=config['polling_cycle_time'],
        urls=config['urls'].items(),
        callback=produce_results
        )

    poller.run()


def pg_load(config: dict) -> None:

    rd = KafkaConsumer(
        config['kafka_topic'],
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        bootstrap_servers=config['kafka_bootstrap_servers'],
        security_protocol="SSL",
        ssl_cafile=config['kafka_ssl_cafile'],
        ssl_certfile=config['kafka_ssl_certfile'],
        ssl_keyfile=config['kafka_ssl_keyfile'],
        client_id=config['kafka_client'],
        group_id=config['kafka_group'],
        )

    with PageDatabase(config['db_uri']) as pdb:
        while True:
            print("Polling kafka")
            topics = rd.poll(timeout_ms=1000)
            if len(topics) == 0:
                time.sleep(5.)
            results = []
            for tp, msgs in topics.items():
                for msg in msgs:
                    msg = msg.value.decode('utf-8')
                    if msg.startswith('{'):
                        results.append(json_to_page_request_result(msg))
                    else:
                        print("Kafka message doesn't look like json:", msg)
            pdb.insert(results)

            rd.commit()


def pg_inspect(config: dict) -> None:
    pdb = PageDatabase(config['db_uri'])
    # prints ugly, used for debugging and I don't have time to beautify
    print(pdb.query(limit=config['rows']))


def main() -> None:

    parser = argparse.ArgumentParser()
    parser.add_argument("config")
    args = parser.parse_args()

    # chdir into config directory
    conf_file = args.config
    os.chdir(os.path.dirname(conf_file))
    conf_file = os.path.basename(conf_file)

    try:
        with open(conf_file) as f:
            yml = yaml.safe_load(f)
            if len(yml) != 1:
                print("YAML file invalid")
                return

            if 'kafka_ingest' in yml:
                kafka_ingest(yml['kafka_ingest'])
            elif 'pg_load' in yml:
                pg_load(yml['pg_load'])
            elif 'pg_inspect' in yml:
                pg_inspect(yml['pg_inspect'])
            else:
                print("YAML file invalid")

    except KeyboardInterrupt:
        return
