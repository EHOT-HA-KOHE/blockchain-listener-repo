
address = "kjfghwkjgj"
dex_name = "radium"
network = "SOL"
created_at = "23.08.2001"

token_info = {
    'address': address, 
    'dex_name': dex_name, 
    'network': network,
    'created_at': created_at,
}

def func_1(*args, **kwargs):
    func_2(kwargs)

def func_2(*args, **kwargs):
    print(f'{kwargs = }')
    print(f'funk_2 {address=}')
    print(f'funk_2 {dex_name=}')
    

if __name__ == '__main__':
    func_1(token_info)