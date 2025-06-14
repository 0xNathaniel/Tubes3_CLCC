from typing import Tuple, Dict, List, Union
import random

class RSA:
    def __init__(self, p: int, q: int, e: int = None) -> None:
        if not (self.is_prime(p) and self.is_prime(q)):
            raise ValueError("p and q must be prime numbers.")
        if p == q:
            raise ValueError("p and q cannot be the same.")

        self.p = p
        self.q = q
        self.n = p * q
        self.phi_n = (p - 1) * (q - 1)
        
        if e is not None:
            self.public_key, self.private_key = self.generate_keys_with_e(e)
        else:
            self.public_key, self.private_key = self.generate_keys()

    def is_prime(self, num: int) -> bool:
        if num < 2:
            return False
        for i in range(2, int(num**0.5) + 1):
            if num % i == 0:
                return False
        return True

    def gcd(self, a: int, b: int) -> int:
        while b:
            a, b = b, a % b
        return a

    def extended_gcd(self, a: int, b: int) -> Tuple[int, int, int]:
        if a == 0:
            return b, 0, 1
        gcd_val, x1, y1 = self.extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd_val, x, y

    def modular_inverse(self, a: int, m: int) -> int:
        gcd_val, x, y = self.extended_gcd(a, m)
        if gcd_val != 1:
            raise Exception('Modular inverse does not exist')
        return x % m

    def generate_keys(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        e = random.randrange(2, self.phi_n)
        while self.gcd(e, self.phi_n) != 1:
            e = random.randrange(2, self.phi_n)
        
        d = self.modular_inverse(e, self.phi_n)
        
        # Public key: (n, e), Private key: (n, d)
        return ((self.n, e), (self.n, d))

    def generate_keys_with_e(self, e: int):
        if self.gcd(e, self.phi_n) != 1:
            raise ValueError("e must be coprime with phi_n")
        d = self.modular_inverse(e, self.phi_n)
        return ((self.n, e), (self.n, d))

    def encrypt_text(self, text: str, public_key: Tuple[int, int]) -> List[int]:
        n, e = public_key
        encrypted_chars = [pow(ord(char), e, n) for char in text]
        return encrypted_chars

    def decrypt_text(self, encrypted_chars: List[int], private_key: Tuple[int, int]) -> str:
        n, d = private_key
        decrypted_chars = [chr(pow(char, d, n)) for char in encrypted_chars]
        return "".join(decrypted_chars)

def encrypt_data(data_dict: Dict[str, Union[str, int, float]], rsa_instance: RSA) -> Dict[str, Union[List[int], int, float]]:
    encrypted_dict = {}
    public_key = rsa_instance.public_key
    
    for key, value in data_dict.items():
        if isinstance(value, str):
            encrypted_dict[key] = rsa_instance.encrypt_text(value, public_key)
        else:
            encrypted_dict[key] = value
            
    return encrypted_dict

def decrypt_data(encrypted_dict: Dict[str, Union[List[int], int, float]], rsa_instance: RSA) -> Dict[str, Union[str, int, float]]:
    decrypted_dict = {}
    private_key = rsa_instance.private_key

    for key, value in encrypted_dict.items():
        if isinstance(value, list):
            decrypted_dict[key] = rsa_instance.decrypt_text(value, private_key)
        else:
            decrypted_dict[key] = value
            
    return decrypted_dict

def get_rsa_instance():
    return RSA(61, 53, e=899)