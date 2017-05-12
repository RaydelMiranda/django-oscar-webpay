import re

error_number_pattern = re.compile(r'(\d+)')

def extract_soap_exception_code_from_message_error(message):
    return int(error_number_pattern.search(message).group())