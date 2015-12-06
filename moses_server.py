from subprocess import Popen, PIPE
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler


class MosesTranslator(object):
    def __init__(self, moses_options):
        process = Popen(moses_options, stdout=PIPE, stdin=PIPE)
        self.process = process

    def translate(self, text):
        self.process.stdin.write('%s\n' % text)
        return self.process.stdout.readline()

    def terminate(self):
        self.process.stdin.close()
        self.process.wait()


def initialize_xmlrpc_server(func_list):
    """
    Parameters:
        func_list: list of (function, registered name)
    """
    # Restrict to a particular path.
    class RequestHandler(SimpleXMLRPCRequestHandler):
        rpc_paths = ('/RPC2',)

    # Create server
    server = SimpleXMLRPCServer(("localhost", 8000),
                                requestHandler=RequestHandler)
    server.register_introspection_functions()

    for func, name in func_list:
        server.register_function(func, name)

    # Run the server's main loop
    server.serve_forever()


def main():
    moses_jb2en = MosesTranslator(['mosesdecoder/bin/moses', '-f', 'train.jb-en/model/moses.ini'])
    moses_en2jb = MosesTranslator(['mosesdecoder/bin/moses', '-f', 'train.en-jb/model/moses.ini'])
    initialize_xmlrpc_server([(moses_jb2en.translate, 'translate_jb2en'),
                              (moses_en2jb.translate, 'translate_en2jb')])

if __name__ == '__main__':
    main()
