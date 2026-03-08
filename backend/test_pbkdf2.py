from passlib.context import CryptContext

try:
    pwd_context = CryptContext(schemes=['pbkdf2_sha256'], deprecated='auto')
    test_pass = 'Password123!'
    print(f'Testing with password: {test_pass} (len: {len(test_pass)})')
    hashed = pwd_context.hash(test_pass)
    print(f'Hash successful: {hashed}')
    verified = pwd_context.verify(test_pass, hashed)
    print(f'Verification successful: {verified}')
except Exception as e:
    print(f'Error: {e}')
