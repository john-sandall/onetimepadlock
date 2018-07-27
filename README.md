# One-Time Padlock

Simple encryption/decryption of files using one-time-passwords and public key cryptography, using command-line tools.

Useful for encrypting passwords & files for transfer across insecure networks. This is a simple Python wrapper around several command-line tools that:
1. Generates a secure one-time key.
2. Encrypts the file to be secured using the one-time key.
3. Encrypts the one-time key using the recipient's public key.
4. Packages both the encrypted file, and the encrypted one-time key, into a single .tgz archive.
5. Cleans up by removing key, encrypted key and encrypted file.

For decryption the reverse process is followed:
1. Extract the compressed archive.
2. Decrypts the encrypted one-time key using your private key.
3. Decrypts the data file using the decrypted one-time key.
4. Cleans up by removing key, encrypted key and encrypted file.

Full credit to [colinstein](https://gist.github.com/colinstein) as this is nothing more than a Python convenience wrapper around his instructions here: https://gist.github.com/colinstein/de1755d2d7fbe27a0f1e


## Install
```
wget https://raw.githubusercontent.com/john-sandall/onetimepadlock/master/secure.py
chmod +x secure.py
```

## Usage
From the command-line:
```
# Encrypt
python secure.py --encrypt -f secret.txt -k /path/to/public/key.pub.pkcs8

# Encrypt using the public key of a GitHub user
curl -sf "https://github.com/GITHUB_USERNAME.keys" | tail -n1 > recipient_key.pub
ssh-keygen -e -f recipient_key.pub -m PKCS8 > recipient_key.pub.pkcs8
python secure.py --encrypt -f secret.txt -k recipient_key.pub.pkcs8
rm recipient_key.pub recipient_key.pub.pkcs8

# Decrypt
python secure.py --decrypt -f secret.tgz -k /path/to/private/key
```

## Manual steps (including generation of .pkcs8 key)
```
# Generate a PKCS8 version of your public key (e.g. id_rsa.pub -> id_rsa.pub.pkcs8)
ssh-keygen -e -f ~/.ssh/id_rsa.pub -m PKCS8 > ~/.ssh/id_rsa.pub.pkcs8

# Encrypt (generate one-time-use password in file `key`, use key to encrypt secret.txt, then use public key to encrypt key file)
openssl rand 192 -out key
openssl aes-256-cbc -in secret.txt -out secret.txt.enc -pass file:key
openssl rsautl -encrypt -pubin -inkey ~/.ssh/id_rsa.pub.pkcs8 -in key -out key.enc
tar -zcvf secret.tgz *.enc
# Can now send secret.tgz ONLY to recipient via insecure network.

# Decrypt
tar -xzvf secret.tgz
openssl rsautl -decrypt -ssl -inkey ~/.ssh/id_rsa -in key.enc -out key
openssl aes-256-cbc -d -in secret.txt.enc -out secret.txt -pass file:key

# Tip: to encrypt an entire directory
tar -zcvf secret_dir.tgz /path/to/directory/
# Then continue as above, replacing secret.txt with secret_dir.tgz
# When decrypting, unpack the archive with following command
tar -xzvf secret_dir.tgz
```
