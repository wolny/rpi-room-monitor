from influxdb import InfluxDBClient


class Counter:
    def __init__(self, host, port, dbname):
        self.client = InfluxDBClient(host=host, port=port, database=dbname)

    def increment(self, name, value):
        try:
            point = [{
                "measurement": name,
                "fields": {
                    "value": value
                }
            }]
            self.client.write_points(point)
        except:
            pass