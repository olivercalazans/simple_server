import socket, threading, os, platform, time, sys

class Client:
    DIRECTORY = os.path.dirname(os.path.abspath(__file__))
    if platform.system() == 'Windows': DIRECTORY += '\\client_folder\\'
    elif platform.system() == 'Linux': DIRECTORY += '/client_folder/'

    METHOD_DICTIONARY = {
        "<close>":     lambda self, arguments=None: self.logout(),
        "<mult>":      lambda self, arguments=None: self.display_multiple_lines(arguments) if arguments else ' ',
        "<single>":    lambda self, arguments=None: self.display_single_line(arguments) if arguments else ' ',
        "<confirm>":   lambda self, arguments=None: self.confirm_receiving_file(arguments) if arguments else '',
        "<send_file>": lambda self, arguments=None: self.prepare_information_to_send_file(arguments) if arguments else ''
        }


    def __init__(self, ip='localhost', port=10000) -> None:
        self._connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connection.connect((ip, port))
        self._stop_flag = False
        self.create_directory(self.get_directory())
        threading.Thread(target=self.receive_from_server).start()


    @staticmethod
    def create_directory(_directory:str) -> None:
        try:   os.mkdir(_directory)
        except FileExistsError: print('The directory already exists')
        except Exception as error: print(f'Error creating directory: {error}')
        else:  print('Directory created')


    @classmethod
    def get_directory(cls):
        return cls.DIRECTORY


    def get_request(self) -> None:
        while not self._stop_flag:
            time.sleep(0.5)
            print('-' * 50)
            _request = input('>')
            self.send_request(_request)


    def send_request(self, _request:str) -> None:
        _key_method, _argument = self.separating_function_from_arguments(_request)
        match _key_method:
            case '/upl': self.get_file_information(_argument)
            case _:      self._connection.sendall(_request.encode())


    def stop_thread(self) -> None:
        self._stop_flag = True


    def logout(self) -> None:
        self.stop_thread()
        sys.exit()


    def receive_from_server(self) -> None:
        try:
            while not self._stop_flag:
                _key_method, _arguments = self.separating_function_from_arguments(self._connection.recv(1024).decode())
                self.METHOD_DICTIONARY[_key_method](self, _arguments)
        except Exception as error:
            print(f'ERROR: {error}')


    @staticmethod
    def separating_function_from_arguments(_string:str) -> list:
        _function_key, _args = (_string.split(':', 1) + [None])[:2]
        return _function_key, _args


    @staticmethod
    def display_multiple_lines(_message:str):
        _message = _message.split('<<SEP>>')
        for line in _message:
            print(line)
    

    @staticmethod
    def display_single_line(_message:str) -> None:
        print(f'\n{_message}')


    @staticmethod
    def display_progress(_message:str, _amount_of_data:int, _total_size:int) -> None:
        sys.stdout.write(f'\r{_message}: {_amount_of_data}/{_total_size}')
        sys.stdout.flush()


    def confirm_receiving_file(self, _file_name_and_size:str) -> str:
        _file_name, _file_size = (_file_name_and_size.split('||', 1))
        _file_size             = int(_file_size)
        self._connection.sendall(f'<conf>:{_file_name_and_size}'.encode())
        self.receive_file(_file_name, _file_size)


    def receive_file(self, _file_name:str, _file_size:int) -> None:
        try:   self.write_file(_file_name, _file_size)
        except Exception as error: print(f'ERROR: {error}')
        else:  print(f'\nFile received ({_file_name})')


    def write_file(self, _file_name:str, _file_size:int) -> None:
        _received_data = 0
        with open(self.get_directory() + _file_name, 'wb') as file:
            while _received_data < _file_size:
                _data = self._connection.recv(1024)
                file.write(_data)
                _received_data += len(_data)
                self.display_progress('Received data', _received_data, _file_size)


    def get_file_information(self, _file_name:str):
        _file_existence = self.check_if_the_file_exists(self.get_directory() + _file_name)
        if not _file_existence:
            print(f'File not found: {_file_name}')
        else: 
            self.send_file_name_and_size(_file_name)


    @staticmethod
    def check_if_the_file_exists(_file_name:str) -> bool:
        if os.path.isfile(_file_name):
            return True
        else:
            return False


    def send_file_name_and_size(self, _file_name:str) -> None:
        _file_size = os.path.getsize(self.get_directory() + _file_name)
        self._connection.sendall(f'<file_inf>:{_file_name}||{_file_size}'.encode())


    def prepare_information_to_send_file(self, _file_name_and_size:str):
        _file_name, _file_size = _file_name_and_size.split('||', 1)
        _file_size = int(_file_size)
        self.send_file(_file_name, _file_size)


    def send_file(self, _file_name:str, _file_size:int) -> None:
        with open(self.get_directory() + _file_name , 'rb') as file:
            _sent_data = 0
            while _sent_data < _file_size:
                _data = file.read(1024)
                self._connection.send(_data)
                _sent_data += len(_data)
                self.display_progress('Sent data', _sent_data, _file_size)



if __name__ == '__main__':
    client = Client()
    client.get_request()
