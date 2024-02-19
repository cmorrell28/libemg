from abc import ABC, abstractmethod
from collections import namedtuple
import socket
from copy import deepcopy


class Controller(ABC):
    def __init__(self, ip_address, port) -> None:
        # Not sure if we want the user to handle creating the socket and binding or we want to hide that in here...
        # Probably have them handle this so it's a bit more extendable, but that depends if there's a use case for other socket families.
        # If every use case would just use this socket then we can probably just hide it here. Either that or add some parameters so they can pass in their own socket if desired.
        receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        receiver_socket.bind((ip_address, port))
        self.receiver_socket = receiver_socket

    def receive_data(self):
        data, _ = self.receiver_socket.recvfrom(1024)
        data = str(data.decode('utf-8'))
        return data
    
    @abstractmethod
    def parse_data(self):
        raise NotImplementedError("parse_data method not implemented for Controller.")


class ClassifierController(Controller):
    def __init__(self, ip_address, port) -> None:
        super().__init__(ip_address, port)
        self.field_names = ['input_class', 'velocity']

    def _format_data(self, data):
        # Hasn't been tested yet but this is the idea
        field_names = deepcopy(self.field_names)[:len(data)]
        ControllerData = namedtuple('ControllerData', field_names)
        return ControllerData(*data)

    def parse_data(self):
        data = self.receive_data()
        parsed_data = data.split(' ')
        # We could also just assign fields to this class if we wanted instead of passing back namedtuples
        return self._format_data(parsed_data)



