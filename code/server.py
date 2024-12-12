# MIT License
# Copyright (c) 2024 Oliver Ribeiro Calazans Jeronimo
# Repository: https://github.com/olivercalazans/simple_server
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software...


import socket, threading
from strategy import *
from storage import *


class Server(Storage_MixIn):
    STRATEGY_DICTIONARY = {
        "/?":         Command_List_Strategy(),
        "/files":     File_List_On_The_Server_Strategy(),
        "/delf":      Delete_File_Strategy(),
        "/downl":     Send_File_Name_And_Size_Strategy(),
        "/upl":       Receive_File_From_Client_Strategy(),
        "/msg":       Private_Message_Strategy(),
        "/bmsg":      Broadcast_Message_Strategy(),
        "<conf>":     Send_File_To_Client_Strategy(),
        "<file_inf>": Receive_File_From_Client_Strategy()
    }

    FORWARDING_DICTIONARY = {
        "svc":       lambda self, *args: self.send_message(*args) if args else '',
        "pvt":       lambda self, *args: self.check_if_there_is_message(*args) if args else '',
        "bdc":       lambda self, *args: self.check_if_there_are_more_than_one_client(*args) if args else '',
        "sfl":       lambda self, *args: self.send_file_to_client(*args) if args else '',
        "recv_file": lambda self, *args: self.receive_file_from_client(*args) if args else ''
    }


    def __init__(self) -> None:
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('localhost', 10000))
        self._server_socket.listen(4)
        self._clients_list = dict()
        self._lock = threading.Lock()
        self.create_directory(Storage_MixIn.get_directory())
        print(f'THE SERVER IS RUNNING: {self._server_socket.getsockname()}\n')


    def receive_client(self) -> None:
        while True:
            _client_socket, _client_address = self._server_socket.accept()
            self.add_client_to_the_list(_client_socket, _client_address)
            print(f'New log in: {_client_address}')
            threading.Thread(target=self.handle_client, args=(_client_address, _client_socket,)).start()


    def add_client_to_the_list(self, _client_socket:object, _client_address:tuple[str, int]) -> None:
        with self._lock:
            self._clients_list[_client_address] = _client_socket


    def remove_client_from_the_list(self, _client_address:tuple[str, int]) -> None:
        with self._lock:
            if _client_address in self._clients_list:
                del self._clients_list[_client_address]


    def close_connection(self, _client_port:int) -> None:
        _client_address, _client_socket = self.get_client_address_and_socket(_client_port)
        if _client_socket:
            self.send_message(_client_socket, '<close>')
            _client_socket.close()
        self.remove_client_from_the_list(_client_address)
        print(f'Connection with {_client_address} closed.')

    
    def get_client_address_and_socket(self, _client_port:int) -> tuple[str, int]:
        with self._lock:
            for client_address, client_socket in self._clients_list.items():
                if client_address[1] == _client_port:
                    return (client_address, client_socket)


    def handle_client(self, _client_address:tuple[str, int], _client_socket:object) -> None:
        try:   
            self.loop_to_receive_data_from_clients(_client_address, _client_socket)
        except (ConnectionResetError, OSError): 
            print(f'Client {_client_address[1]} disconnected abruptly.')
        except Exception as error:
            print(f'Error with client {_client_address}: {error}')
            self.send_message(_client_socket, '<single>:SERVER: There is something wrong in your request')
        finally:
            self.remove_client_from_the_list(_client_address)
            try:   _client_socket.close()
            except OSError: print(f'Error closing socket for {_client_address}')


    def loop_to_receive_data_from_clients(self, _client_address:tuple[str, int], _client_socket:object) -> None:
        while True:
            _received_data          = _client_socket.recv(1024).decode()
            _method_key, _arguments = self.separate_function_from_arguments(_received_data)
            _forward_flag, _data    = self.check_if_the_method_exists(_client_address[1], _method_key, _arguments)
            if _forward_flag == '/exit': break
            print(f'{_client_address[1]}> {_method_key}')
            self.get_forward_dictionary().get(_forward_flag, lambda *args: None)(self, _client_socket, _data)


    @staticmethod
    def separate_function_from_arguments(_string:str) -> tuple[str, str]:
        _method_key, _args = (_string.split(':', 1) + [None])[:2]
        return (_method_key, _args)


    def check_if_the_method_exists(self, _client_port:int, _method_key:str, _arguments:str) -> tuple[str, str]:
        if _method_key == '/exit' or _method_key in self.get_strategy_dictionary():
            _forward_flag, _data = self.get_result(_client_port, _method_key, _arguments)
        else:
            _forward_flag, _data = 'svc', '<single>:SERVER: Command not found'
        return (_forward_flag, _data)


    def get_result(self, _client_port:int, _method_key:str, _arguments:str) -> tuple[str, str]:
        match _method_key:
            case '/exit':
                self.close_connection(_client_port)
                _forward_flag, _data = _method_key, None
            case _:
                _strategy = self.get_strategy_dictionary().get(_method_key)
                _forward_flag, _data = _strategy.execute(self, _client_port, _arguments)
        return (_forward_flag, _data)


    @classmethod
    def get_strategy_dictionary(cls) -> dict:
        return cls.STRATEGY_DICTIONARY


    @classmethod
    def get_forward_dictionary(cls) -> dict:
        return cls.FORWARDING_DICTIONARY


    @staticmethod
    def send_message(_client_socket:object, _data:str) -> None:
        _client_socket.sendall(_data.encode())


    def prepare_private_message(self, _client_port:int, _message:str='') ->str:
        try:    _target_client, _message = _message.split(':', 1)
        except: _target_client, _message = _client_port, '<single>:SERVER: Client ID or message is empty'
        else:   _message = f'<single>:({_client_port})> {_message}'
        _message = f'{_target_client}:{_message}' 
        return _message
    

    def check_if_there_is_message(self, _client_socket:object, _client_and_message:str) -> None:
         _client_port, _message = _client_and_message.split(':', 1)
         if not _message: self.send_message(_client_socket, '<single>:SERVER: Empty messages can not be sent')
         else: self.check_if_the_client_id_is_valid(_client_socket, _client_port, _message)


    def check_if_the_client_id_is_valid(self, _client_socket:object, _client_port:str, _message:str) -> None:
        try:    _client_port = int(_client_port)
        except: self.send_message(_client_socket, '<single>:SERVER: User ID invalid')
        else:   self.check_if_the_client_is_logged_now(_client_socket, _client_port, _message)


    def check_if_the_client_is_logged_now(self, _client_socket:object, _target_client_id:int, _message:str) -> None:
        _target_client_socket  = next((client_socket for (ip, port), client_socket in self._clients_list.items() if port == _target_client_id), None)
        if not _target_client_socket: _target_client_socket, _message = _client_socket, '<single>:SERVER: The client is not logged now'
        self.send_message(_target_client_socket, _message)

    
    def prepare_broadcast_message(self, _client_port:int, _message:str) -> str:
        _message = f'<single>:({_client_port})BROAD> {_message}'
        return _message


    def check_if_there_are_more_than_one_client(self, _client_socket:object, _message:str) -> None:
        if len(self._clients_list) > 1: self.send_broadcast_message(_message)
        else: self.send_message(_client_socket, '<single>:SERVER: You are the only one logged now')


    def send_broadcast_message(self, _message:str) -> None:
        with self._lock:
            for client_socket in self._clients_list.values():
                self.send_message(client_socket, _message)


    @staticmethod 
    def separete_file_infomation(_file_name_and_size:str) -> tuple[str, int]:
        _file_name, _file_size = (_file_name_and_size.split('||'))
        _file_size = int(_file_size)
        return (_file_name, _file_size)


    def send_file_to_client(self, _client_socket:object, _file_name_and_size:tuple[str, int]) -> None:
        _file_name, _file_size = _file_name_and_size
        with open(self.get_directory() + _file_name, 'rb') as file:
            _sent_data = 0
            while _sent_data < _file_size:
                _data = file.read(1024)
                _client_socket.send(_data)
                _sent_data += len(_data)


    def receive_file_from_client(self, _client_socket:object, _file_name_and_size:tuple[str, int]) -> None:
        _file_name, _file_size = _file_name_and_size
        _result = '<single>:SERVER: File received'
        self.send_message(_client_socket, f'<send_file>:{_file_name}||{_file_size}')
        try:    self.write_file(_client_socket, _file_name, _file_size)
        except: _result = '<single>:SERVER: error while receiving the file'
        else:   _result = '<single>:SERVER: file received'
        self.send_message(_client_socket, _result)


    def write_file(self, _client_socket:object, _file_name:str, _file_size:int) -> None:
        with open(self.get_directory() + _file_name, 'wb') as file:
            _received_data = 0
            while _received_data < _file_size:
                _data = _client_socket.recv(1024)
                file.write(_data)
                _received_data += len(_data)



if __name__ == '__main__':
    server = Server()
    server.receive_client()
