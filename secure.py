"""
Simple encryption/decryption of files using one-time-passwords and public key cryptography, using command-line tools.

Reference: https://gist.github.com/colinstein/de1755d2d7fbe27a0f1e
"""

import argparse
from subprocess import call
import tarfile


def encrypt(file, key):
    encrypted_file = file + '.enc'
    call(['openssl', 'rand', '192', '-out', 'key'])
    call(['openssl', 'aes-256-cbc', '-in', file, '-out', encrypted_file, '-pass', 'file:key'])
    call(['openssl', 'rsautl', '-encrypt', '-pubin', '-inkey', key, '-in', 'key', '-out', 'key.enc'])
    call(['tar', '-zcvf', 'secret.tgz', encrypted_file, 'key.enc'])
    call(['rm', 'key'])
    call(['rm', 'key.enc'])
    call(['rm', encrypted_file])


def decrypt(file, key):
    tar = tarfile.open(file)
    encrypted_file = [f.name for f in tar if f.name != 'key.enc'][0]
    call(['tar', '-xzvf', file])
    call(['openssl', 'rsautl', '-decrypt', '-ssl', '-inkey', key, '-in', 'key.enc', '-out', 'key'])
    call(['openssl', 'aes-256-cbc', '-d', '-in', encrypted_file, '-out', encrypted_file[:-4], '-pass', 'file:key'])
    call(['rm', 'key'])
    call(['rm', 'key.enc'])
    call(['rm', encrypted_file])


if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Simple encryption/decryption of files using one-time-passwords and public key cryptography.'
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-e', '--encrypt', help='Use to encrypt a file', action='store_true')
    group.add_argument('-d', '--decrypt', help='Use to decrypt a file', action='store_true')
    parser.add_argument('-f', '--file', help='Path to file to be encrypted/decrypted', required=True)
    parser.add_argument('-k', '--key', help='Path to key (public for encrypt, private for decrypt)', required=True)
    args = vars(parser.parse_args())

    # Check at least one of encrypt or decrypt is specified
    if not args['encrypt'] and not args['decrypt']:
        raise parser.error('One of -d/--decrypt or -e/--encrypt must be set.')

    if args['encrypt']:
        encrypt(file=args['file'], key=args['key'])
    elif args['decrypt']:
        decrypt(file=args['file'], key=args['key'])
