#!/usr/bin/env python3
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

import base64

# Generate an Ed25519 private key
private_key = ed25519.Ed25519PrivateKey.generate()

# Derive the corresponding public key
public_key = private_key.public_key()

# You can then serialize these keys for storage or transmission
# Serialize private key (raw format, no encryption)
private_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PrivateFormat.Raw,
    encryption_algorithm=serialization.NoEncryption()
)

# Serialize public key (raw format)
public_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PublicFormat.Raw
)

private_bytes_b64 = base64.b64encode(private_bytes).decode('utf-8')
public_bytes_b64 = base64.b64encode(public_bytes).decode('utf-8')

with open('secrets/private_key.pem', 'w') as f:
    label = "PRIVATE KEY"
    f.write(f"-----BEGIN {label}-----\n")
    f.write(private_bytes_b64 + "\n")
    f.write(f"-----END {label}-----\n")


with open('secrets/public_key.pem', 'w') as f:
    label = "PUBLIC KEY"
    f.write(f"-----BEGIN {label}-----\n")
    f.write(public_bytes_b64 + "\n")
    f.write(f"-----END {label}-----\n")
