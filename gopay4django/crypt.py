# -*- coding: utf-8 -*-
from binascii import unhexlify
from hashlib import sha1
from Crypto.Cipher import DES3
from django.conf import settings
from pyDes import triple_des

"""
Copyright (c) 2012, Vladimír Linhart
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above
      copyright notice, this list of conditions and the following
      disclaimer in the documentation and/or other materials provided
      with the distribution.
    * Neither the name of the author nor the names of other
      contributors may be used to endorse or promote products derived
      from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

class GoCrypt(object):
    """ takes care of hashing, encryption and decrypting of commands"""

    def __init__(self, secret=settings.GOPAY_SECRET_KEY):
        self.secret = secret

    def hash(self, string):
        h = sha1()
        h.update(string.encode('utf-8'))
        return h.hexdigest()

    def encrypt(self, command):
        hashed_command = self.hash(command)
        des = DES3.new(self.secret, DES3.MODE_ECB)
        result = des.encrypt(hashed_command)
        print result
        print dir(result)
        print result.encode('hex')
        return result.encode('hex')

    def encrypt_pydes(self, command):
        hashed_command = self.hash(command)
        des = triple_des(self.secret)
        result = des.encrypt(hashed_command)
        return result.encode('hex')

    def decrypt(self, encrypted_data):
        des = DES3.new(self.secret, DES3.MODE_ECB)
        return des.decrypt(unhexlify(encrypted_data)).rstrip('\x00')

    def decrypt_pydes(self, encrypted_data):
        des = triple_des(self.secret)
        return des.decrypt(unhexlify(encrypted_data)).rstrip('\x00')