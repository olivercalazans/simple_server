# MIT License
# Copyright (c) 2024 Oliver Ribeiro Calazans Jeronimo
# Repository: https://github.com/olivercalazans/simple_server
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software...


from abc import ABC, abstractmethod

class Strategy(ABC):
    @abstractmethod
    def execute(self, server, arguments=None):
        pass


class Command_List_Strategy(Strategy):
    def execute(self, _server, _client_port:int, _arguments:str):
        _result = _server.get_command_list()
        return ('svc', _result)


class Private_Message_Strategy(Strategy):
    def execute(self, _server, _client_port:int, _arguments:str):
        _result = _server.prepare_private_message(_client_port, _arguments)
        return ('pvt', _result)
    

class Broadcast_Message_Strategy(Strategy):
    def execute(self, _server, _client_port:int, _arguments:str):
        _result = _server.prepare_broadcast_message(_client_port, _arguments)
        return ('bdc', _result)


class File_List_On_The_Server_Strategy(Strategy):
    def execute(self, _server, _client_port:int, _arguments:str):
        _result = _server.get_file_list_on_the_server()
        return ('svc', _result)


class Delete_File_Strategy(Strategy):
    def execute(self, _server, _client_port:int, _arguments:str):
        _result = _server.delete_file(_arguments)
        return ('svc', _result)


class Send_File_Name_And_Size_Strategy(Strategy):
    def execute(self, _server, _client_port:int, _arguments:str):
        _result = _server.get_file_information(_arguments)
        return ('svc', _result)


class Send_File_To_Client_Strategy(Strategy):
    def execute(self, _server, _client_port:int, _arguments:str):
        _result = _server.separete_file_infomation(_arguments)
        return ('sfl', _result)
    

class Receive_File_From_Client_Strategy(Strategy):
    def execute(self, _server, _client_port:int, _arguments:str):
        _result = _server.separete_file_infomation(_arguments)
        return ('recv_file', _result)
