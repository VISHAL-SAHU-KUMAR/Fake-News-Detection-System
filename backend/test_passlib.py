from passlib.context import CryptContext
import sys

try:
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    test_pass = 'Password123!'
    print(f'Testing with password: {test_pass} (len: {len(test_pass)})')
    hashed = pwd_context.hash(test_pass)
    print(f'Hash successful: {hashed}')
except Exception as e:
    print(f'Error during hash: {e}')
    import traceback
    traceback.print_exc()
