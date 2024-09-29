import os


def get_esdb_uri():
    return os.environ.get("ESDB_HOST", "esdb://localhost:2113?tls=false")
