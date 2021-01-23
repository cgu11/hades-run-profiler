"""Code sourced from https://github.com/zsennenga/hades_save_editor on 2021-01-23"""

def rpad_bytes(byte_data: bytes, target_length: int) -> bytes:
    byte_length = len(byte_data)

    if byte_length > target_length:
        return byte_data

    return byte_data + b'\0' * (target_length - byte_length)
