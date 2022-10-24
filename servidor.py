# saved as greeting-server.py
import Pyro5.api
from Crypto.PublicKey import RSA

@Pyro5.api.expose
class GreetingMaker(object):

    def cadastro(self, referenciaCliente, nome):
        key = RSA.generate(2048)
        public_key = key.publickey().exportKey("PEM")
        private_key = key.exportKey("PEM")

        return public_key

daemon = Pyro5.server.Daemon()         # make a Pyro daemon
ns = Pyro5.api.locate_ns()             # find the name server
uri = daemon.register(GreetingMaker)   # register the greeting maker as a Pyro object
ns.register("Agenda", uri)   # register the object with a name in the name server

print("Ready.")
daemon.requestLoop()                   # start the event loop of the server to wait for calls