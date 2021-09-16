#!/usr/bin/python3

from cougarnet.networksched import NetworkEventLoop
from cougarnet.rawpkt import BaseFrameHandler

class Switch(BaseFrameHandler):
    def __init__(self):
        super(Switch, self).__init__()

        # do any initialization here...

    def _handle_frame(self, frame, intf):
        print('Received frame: %s' % repr(frame))

def main():
    switch = Switch()
    event_loop = NetworkEventLoop(switch._handle_frame)
    event_loop.run()

if __name__ == '__main__':
    main()
