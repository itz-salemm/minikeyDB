# Import XML RPC server to receive data
from xmlrpc.server import SimpleXMLRPCServer

# Import XML RPC client to send data
import xmlrpc.client

# Import threading to update other without waiting
import threading
import nodes_config as cfg
import nodes_config as kvNodes

# Import time and random to generate random delay between updates. To get some "real" tests
import time
import random

def node_init(address, port, nodeId, mode, verbose):
    server = SimpleXMLRPCServer((address, port), allow_none=True, logRequests=False)

    if mode == "eventual":
        server.register_instance(EventualNode(address, port, nodeId, verbose))

    print("Node {} started on {}:{}: Using {} consistency ...".format(nodeId, address, port, mode))

    if verbose:
        print("Node {} Verbose Logging Enables!".format(nodeId))
    else:
        print("Node {} Verbose Logging Disabled!".format(nodeId))

    server.serve_forever()


class EventualNode:
    def __init__(self, address, port, nodeId, verbose):
        self.address = address
        self.port = port
        self.nodeId = nodeId
        self.data = {}
        self.other_nodes = []
        self.verbose = verbose

        for node in kvNodes.nodes:
            if node.get("nodeId") == self.nodeId:
                continue
            else:
                self.other_nodes.append(xmlrpc.client.ServerProxy("http://" + node.get("address") + ":" + str(node.get("port"))))

    def put(self, key, value):
        self.data[key] = value
        t = threading.Thread(target=update_others_eventual, args=(self.other_nodes, key, value))
        t.start()

        if self.verbose:
            print("Node {} -> Key {}, value{}".format(self.nodeId, key, value))

    def get(self, key):
        if self.verbose:
            print("Node {} GET -> Key {}".format(self.nodeId, key))
        if self.data.get(key):
            return self.data.get(key)
        else:
            return "NULL"

    def update(self, key, value):
        self.data[key] = value
        if self.verbose:
            print("Node {} Updated! -> Key {}, Value {}".format(self.nodeId, key, value))

    def remove(self, key):
        if self.verbose:
            print("Node {} Remove! -> Key {}".format(self.nodeId, key))
        if self.data.get(key):
            t = threading.Thread(target=update_remove_eventual, args=(self.other_nodes, key,))
            t.start()
            return self.data.pop(key)
        else:
            return "NULL"

    def update_remove_node(self, key):
        if self.data.get(key):
            self.data.pop(key)
        if self.verbose:
            print("Node {} Updated Remove! -> Key {}".format(self.nodeId, key))

def update_others_eventual(other_nodes, key, value):
        for node in other_nodes:
            while True:
                delay = random.uniform(0.2, 1)
                time.sleep(delay)
                try:
                    node.update(key, value)
                    break
                except:
                    continue

def update_remove_eventual(other_nodes, key):
    for node in other_nodes:
        while True:
            delay = random.uniform(0.2, 1)
            time.sleep(delay)
            try:
                node.update_remove(key)
                break
            except:
                continue


#node_init(cfg.nodes[0].get("address"), cfg.nodes[0].get("port"), cfg.nodes[0].get("nodeId"),"eventual", "verbose",)
