# MIT License
# Copyright (c) 2024 Oliver Ribeiro Calazans Jeronimo
# Repository: https://github.com/olivercalazans/simple_server
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software...


import platform, os

class Storage_MixIn:
    DIRECTORY = os.path.dirname(os.path.abspath(__file__))
    if platform.system() == 'Windows': DIRECTORY += '\\server_folder\\'
    elif platform.system() == 'Linux': DIRECTORY += '/server_folder/'
   

    @classmethod
    def get_directory(cls) -> str:
        return cls.DIRECTORY


    @staticmethod
    def create_directory(_directory:str) -> None:
        try:   os.mkdir(_directory)
        except FileExistsError: print('The directory already exists')
        except Exception as error: print(f'Error creating directory: {error}')
        else:  print('Directory created')


    @staticmethod
    def convert_to_string(_data:list) -> str:
        return '<<SEP>>'.join(map(str, _data))


    @staticmethod
    def get_command_list() -> str:
        commands = (
            '/msg....: Private message',
            '/bmsg...: Broadcast message',
            '/files..: Files on the server',
            '/delf...: Delete a file on the server',
            '/downl..: Download from the server',
            '/upl....: Upload to the server',
            '/exit...: Log out'
        )
        return f'<mult>:{Storage_MixIn.convert_to_string(commands)}'


    @staticmethod
    def check_if_the_file_exists(_file_name:str) -> bool:
        if os.path.isfile(_file_name):
            return True
        else:
            return False


    @staticmethod
    def get_file_size(_file_name:str) -> int:
        _file_size = os.path.getsize(_file_name)
        return _file_size


    @staticmethod
    def check_if_the_file_exists(_file_name:str) -> tuple[bool, str]:
        try: 
            _path_to_file = Storage_MixIn.get_directory() + _file_name
            _confimation  = Storage_MixIn.check_if_the_file_exists(_path_to_file)
        except:
            _confimation  = False
            _path_to_file = None
        return (_confimation, _path_to_file)


    @staticmethod
    def get_file_information(_file_name:str) -> str:
        _file_existence, _path_to_file = Storage_MixIn.check_if_the_file_exists(_file_name)
        _result = '<single>:SERVER: file not found'
        if _file_existence:
            _file_size = Storage_MixIn.get_file_size(_path_to_file)
            _result = f'<confirm>:{_file_name}||{_file_size}'
        return _result


    @staticmethod
    def get_file_list_on_the_server() -> str:
        _file_list       = os.listdir(Storage_MixIn.get_directory())
        _files_and_sizes = Storage_MixIn.process_large_file_list(_file_list)
        _result          = f'<mult>:{Storage_MixIn.convert_to_string(_files_and_sizes)}' 
        return _result


    @staticmethod
    def process_large_file_list(_file_names:list, _block_size=10) -> list:
        _file_and_size = list()
        for index in range(0, len(_file_names), _block_size):
            _block = _file_names[index:index + _block_size]
            _file_and_size.extend(Storage_MixIn.process_file_block(_block))
        return _file_and_size
    

    @staticmethod
    def process_file_block(_file_names:list) -> list:
        _file_info = list()
        for file in _file_names:
            try: _file_info.append(f'{os.path.getsize(Storage_MixIn.get_directory() + file)} - {file}')
            except: continue
        return _file_info


    @staticmethod
    def delete_file(_file_name:str) -> str:
        try:    os.remove(Storage_MixIn.get_directory() + _file_name)
        except  FileNotFoundError: _result = 'File not found'
        except: _result = '<single>:SERVER: Error when trying to delete the file'
        else:   _result = f'File {_file_name} deleted'
        return  _result
    

