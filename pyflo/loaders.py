import pycouchdb
import pycouchdb.exceptions


class GraphSource:
    def __init__(self, config=None):
        self.config = config

    def __contains__(self, item):
        return False

    def load_graph(self, graph_id):
        return None


class CouchDBSource(GraphSource):
    def __init__(self, config):
        super().__init__(config)
        server = pycouchdb.Server(config["url"])
        self.db = server.database(config["db"])

    def __contains__(self, item_id):
        try:
            self.db.get(item_id)
            return True
        except pycouchdb.exceptions.NotFound:
            return False

    def load_graph(self, graph_id):
        try:
            return self.db.get(graph_id)["specification"]
        except pycouchdb.exceptions.NotFound:
            return None