class TCPSendBuffer(object):
    def __init__(self, seq):
        self.buffer = b''
        self.base_seq = seq
        self.next_seq = self.base_seq
        self.last_seq = self.base_seq

    def bytes_not_yet_sent(self):
        pass

    def bytes_outstanding(self):
        pass

    def put(self, data):
        pass

    def get(self, size):
        pass

    def get_for_resend(self, size):
        pass

    def slide(self, sequence):
        pass


class TCPReceiveBuffer(object):
    def __init__(self, seq):
        self.buffer = {}
        self.base_seq = seq

    def put(self, data, sequence):
        pass

    def get(self):
        pass
