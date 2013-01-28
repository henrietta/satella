from satella.channels.sockets.sockets import Socket, ServerSocket
from satella.channels.subtypes import FileDescriptorChannel
from satella.channels.exceptions import ChannelFailure, DataNotAvailable, ChannelClosed, \
                                        UnderlyingFailure

import socket

from ssl import SSLError

class SSLSocket(Socket):
    def read(self, count, less=False, peek=False):
        """
        Performs a SSL read.

        You ask why there is a method ripped out from L{satella.channels.sockets.sockets.Socket}
        only so that you can change a few lines?

        Here's the answer.

        SSL returns SSLError on timeouts. SSLError is a subclass of socket.error, not socket.timeout.
        This behaviour is a bug but it will not be backported into earlier Python versions
        (see http://bugs.python.org/issue10272 ).

        We need to intercept SSLError, check if it's a timeout and then raise suitable
        exception.
        """
        if not self.active: 
            # If we cannot satisfy the request, we need to raise an exception
            # because we will never be able to do so
            if len(self.rx_buffer) == 0:  # this would always fail
                raise ChannelClosed, 'channel closed'

            if len(self.rx_buffer) >= count:
                # if we can safely satisfy the request right away, do it
                return FileDescriptorChannel.read(self, count, less, peek)
            else:
                # we cannot satisfy all of the request, only less might save us now
                # from raising an exception
                if less:
                    return FileDescriptorChannel.read(self, count, less, peek)   
                else:
                    raise ChannelClosed, 'channel closed`'            

        if self.blocking:
            while len(self.rx_buffer) < count:  # We might spend some time here
                try:
                    s = self.socket.recv(count-len(self.rx_buffer))
                except SSLError as e:
                    # strerror is available under PyPy, and message under CPython
                    serr = e.strerror or e.message
                    if 'timed out' in serr:    # timeout
                        raise DataNotAvailable, 'ssl timeout'
                    else:       # something else
                        raise UnderlyingFailure, 'socket recv failed'                

                except socket.error:
                    self.close()
                    raise UnderlyingFailure, 'socket recv failed'                
                except socket.timeout:
                    raise DataNotAvailable, 'timeout on recv'

                self.rx_buffer.extend(s)

                if len(s) == 0:
                    self.close()
                    # The channel has been closed right now. Invoke a recursive
                    # call to this function, it will do the necessary checking, 
                    # because now it will be true that self.active == False
                    return self.read(count, less, peek)

                if less:    # a single recv passed, we can return with less data
                    return FileDescriptorChannel.read(self, count, less, peek)

        return FileDescriptorChannel.read(self, count, less, peek)

    def write(self, *args, **kwargs):
        try:
            return Socket.write(self, *args, **kwargs)
        except SSLError:
            self.close()
            raise ChannelFailure, 'SSL failure'


class SSLServerSocket(ServerSocket):
    def __init__(self, socket):
        """@type socket: SSL-wrapped server socket"""
        ServerSocket.__init__(self, socket)

    def read(self):
        try:
            # try to accept it and repack it into a SSLSocket channel
            return SSLSocket(ServerSocket.read(self).get_underlying_object())
        except SSLError:
            raise DataNotAvailable, 'SSL failure'