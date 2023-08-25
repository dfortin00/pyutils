from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import ec

from cryptography import x509
from cryptography.x509.oid import NameOID

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12

from cryptography.hazmat.backends import default_backend

from stringutils import str_to_bytes

#==============================================================================
# PRIVATE KEYS
#==============================================================================

def generate_private_key(key_type:str, key_size:int) -> rsa.RSAPrivateKey | ec.EllipticCurvePrivateKey:
    """
    Generate either an RSA or EC private key. Key sizes supported: RSA (any), EC (256, 384).

    Args:
        key_type: 'rsa' or 'ec'
        key_size: Key size used with key type

    Returns:
        RSA or EC key object.
    """

    if key_type == 'rsa':
        return rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size
        )
    elif key_type == 'ec':
        if key_size != 256 and key_size != 384:
            raise Exception("generate_csr : elipitical keysize supported are SECP256R1 (256) and SECP384R1 (384) : keySize=" + key_size)

        return ec.generate_private_key(
            curve=(ec.SECP256R1() if key_size == 256 else ec.SECP384R1())
        )
    else:
        raise Exception("generate_csr : key types supported are 'rsa' and 'ec' : keyType=" + key_type)


def private_key_to_pem(key, passphrase:bytes) -> str:
    """
    Convert a private key to a PEM encoded string.

    Args:
        key: Private key object.
        passphrase: Secret key used when encoding private key.

    Returns:
        A PEM encoded string of the private key.
    """

    passphrase = str_to_bytes(passphrase)
    return key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.BestAvailableEncryption(passphrase)
    )


def private_key_to_file(key, privkey_filename:str, passphrase:bytes=None):
    """
    Save a private key to a file.

    Args:
        key: Private key object (RSAPrivateKey or EllipticCurvePrivateKey)
        privkey_filename: Name of the file which will be used to save the private key to disk.
        passphrase: Secret key used when encoding private key
    """

    passphrase = str_to_bytes(passphrase)
    with open(privkey_filename, "wb") as f:
        f.write(private_key_to_pem(key, passphrase))


#==============================================================================
# CERTIFICATE SIGNING REQUESTS
#==============================================================================

def csr_to_pem(csr:x509.CertificateSigningRequest, single_line:bool=False) -> str:
    """
    Convert a x509.CertificateSigningRequest into a PEM encoded string.

    Arg:
        csr: A x509.CertificateSigningRequest object
        single_line: Remove newline characters from PEM string if True.

    Returns:
        A PEM encoded CSR string.
    """

    pem = csr.public_bytes(encoding=serialization.Encoding.PEM)
    pem = pem.decode('utf8')
    return pem if not single_line else pem.replace('\n', "")


def csr_to_file(csr:x509.CertificateSigningRequest, csr_filename:str):
    """
    Convert a CSR to a PEM encoded CSR and write it to a file.

    Args:
        csr: x509.CertificateSigningRequest object
        csr_filename: Name of the file which will be used to save the CSR on disk
    """

    with open(csr_filename, "wb") as f:
        f.write(str.encode(csr_to_pem(csr)))


def generate_csr(
        key_type:str,
        key_size:int,
        cn:str,
        country:str,
        state_or_prov:str,
        locality:str,
        org:str,
        ou:str,
        sans:list=[],
        ):

    """
    Generate an x509 Certificate Signing Request.

    Args:
        key_type: 'rsa' or 'ec'
        key_size: Key size used with key_type
        cn: Common name
        country: Country
        state_or_prov: State or Province
        locality: City
        org: Organization
        ou: Organizational Unit
        sans: List of SANs in string format
        privkey_filename: Optional filename which will be used to save the private key on disk
        passphrase: byte encoded string that will be used as the passphrase of the private key
        csr_filename: Optional filename which will be used to save the csr on disk

    Returns:
        An x509.CertificateSigningRequest object plus the generated private key.
    """

    privkey = generate_private_key(key_type, key_size)

    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, country),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, state_or_prov),
        x509.NameAttribute(NameOID.LOCALITY_NAME, locality),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, org),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, ou),
        x509.NameAttribute(NameOID.COMMON_NAME, cn)
    ]))

    if sans:
        csr = csr.add_extension(x509.SubjectAlternativeName([x509.DNSName(x) for x in sans]), critical=False)

    # Hard code SHA256.
    csr = csr.sign(privkey, hashes.SHA256())

    return csr, privkey

#==============================================================================
# PFX
#==============================================================================

def load_pfx_file(pfx_filename:str, passphrase:bytes):
    """
    Loads a PFX (P12) file and returns the list of certificates along with the private key.

    Args:
        pfx_filename: Filename and path of the .pfx or .p12 file
        passphrase: The secret phrase used when generating the private key

    Returns:
        List of certificates and private key.
    """

    with open(pfx_filename, 'rb') as pfx_file:
        pfx_data = pfx_file.read()

    privkey = None
    certificates = None

    passphrase = str_to_bytes(passphrase)
    (privkey, *certificates) = pkcs12.load_key_and_certificates(pfx_data, password=passphrase, backend=default_backend())

    if len(certificates[1]) > 0:
        return [certificates[0]] + certificates[1], privkey

    return [certificates[0]], privkey

#==============================================================================

def csr_selftest():
    csr, privkey = generate_csr(
        'rsa', 4096, 'mydomain.com', 'CA', 'ON', 'Toronto', 'Big Security, Inc.', 'R&D',
        ["san1.mydomain.com", "san2.mydomain.com"]
    )

    print(csr)
    csr_str = csr_to_pem(csr)
    print(csr_str)

    csr_str = csr_to_pem(csr, single_line=True)
    print(csr_str)

    csr_to_file(csr, "c:\\temp\\csr.pem")
    private_key_to_file(privkey, "c:\\temp\\privkey.pem", "Password!1")


def pfx_selftest():
    certs, privkey = load_pfx_file("c:\\temp\\pfx\\domains.p12", "Password!1")

    print(certs)
    print("Number Certificates : ", len(certs))
    for cert in certs:
        print(cert)

    print(private_key_to_pem(privkey, b"Password!1").decode('utf-8'))


if __name__ == "__main__":
    csr_selftest()
    pfx_selftest()

