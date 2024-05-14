import binascii
import os
from datetime import datetime, timedelta, timezone

import paramiko
from OpenSSL import crypto

import eventbus
from eventbus import Event, EventBus, event_type, post, subscribe
from eventbus.event import put_cert

from ..env import get_env

CERT_DIR = "/home/letsencrypt/live"

DEFAULT_TIMEOUT = 1e-6 if get_env().ENVIRONMENT == "test" else 10


def ssh(
    cmd, *, host="172.17.0.1", port=22222, user="root", pwd="", timeout: float = DEFAULT_TIMEOUT
) -> tuple[str, str]:
    """exec command on host, return results"""
    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, user, pwd, timeout=timeout)
        _, stdout, stderr = ssh.exec_command(cmd)
        return (stdout.read().decode(), stderr.read().decode())


def domain(tree_id: str) -> str:
    """Return domain for tree_id"""
    return f"{tree_id}.ws.leaf49.org"


def create_certificate(
    tree_id, dry_run=False, propagation_seconds=10, timeout: float = DEFAULT_TIMEOUT
) -> tuple[str, str, str]:
    """Create/renew let's encrypt certificate

    Example:
        create_certificate("my_tree.ws.leaf49.org")

    Returns:
        (stdout, stderr, cmd)
        The certificates are at letsencrypt/live/{domain}

    Important:
        A record must exist for the domain.

        Adding *.ws.leaf49.org as a public hostname to
        CloudFlare/ZeroTrust/Networks/Tunnels
        does the trick for the above example.

    Note: Blocking. Takes ~propagation_seconds to execute.
    """

    # balena volume names
    try:
        vol = ssh("ls /var/lib/docker/volumes", timeout=timeout)[0].split("\n")
    except TimeoutError:
        return ("", "", "")
    volumes = {
        "/opt/cloudflare": [v for v in vol if v.endswith("_cloudflare")][0],
        "/etc/letsencrypt": [v for v in vol if v.endswith("_letsencrypt")][0],
        "/var/log/letsencrypt": [v for v in vol if v.endswith("_letsencrypt-log")][0],
    }

    # create/renew certificate
    cmd = "balena-engine run \\\n"
    for k, v in volumes.items():
        cmd += f"  -v /var/lib/docker/volumes/{v}/_data:{k} \\\n"
    cmd += "  certbot/dns-cloudflare \\\n"
    cmd += "  certonly \\\n"
    cmd += "  --server https://acme-v02.api.letsencrypt.org/directory \\\n"
    cmd += "  --non-interactive --dns-cloudflare --agree-tos \\\n"
    cmd += "  --dns-cloudflare-credentials /opt/cloudflare/credentials \\\n"
    cmd += f"  -m {os.getenv('CF_EMAIL')} \\\n"
    cmd += f"  -d {domain(tree_id)} \\\n"
    if dry_run:
        cmd += "  --dry-run \\\n"
    cmd += f"  --dns-cloudflare-propagation-seconds {propagation_seconds}"
    out, err = ssh(cmd, timeout=timeout)
    return (out, err, cmd)


def expires(tree_id) -> datetime:
    """Return expiry date for certificate for domain.

    The certificate must have been created before with create_certificate."""
    try:
        with open(f"{CERT_DIR}/{domain(tree_id)}/cert.pem", "rb") as f:
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, f.read())
        return datetime.strptime(cert.get_notAfter().decode(), "%Y%m%d%H%M%SZ")  # type: ignore
    except FileNotFoundError:
        return datetime(1970, 1, 1, tzinfo=timezone.utc)


def valid(tree_id) -> timedelta:
    """Return how much longer certificate is valid."""
    return expires(domain(tree_id)) - datetime.now(timezone.utc)


def get_version(tree_id: str, timeout: float = DEFAULT_TIMEOUT) -> str:
    if valid(tree_id) < timedelta(days=30):
        # renew certificate
        create_certificate(tree_id, timeout=timeout)
    return expires(tree_id).replace(microsecond=0).isoformat()[:-6]


def get_cert(tree_id, file_name, timeout) -> str:
    """Return certificate in base64 format.

    Examples:
        get_cert("my_tree_id", "cert.pem")
        get_cert("my_tree_id", "privkey.pem")

    Decode with:
        binascii.a2b_base64(cert.encode())
    """
    path = f"{CERT_DIR}/{domain(tree_id)}/{file_name}"
    if not os.path.exists(path):
        create_certificate(tree_id, timeout=timeout)
    try:
        with open(path, "rb") as f:
            pem = f.read()
        cert_pem = crypto.load_certificate(crypto.FILETYPE_PEM, pem)
        cert_der = crypto.dump_certificate(crypto.FILETYPE_ASN1, cert_pem)
    except FileNotFoundError:
        cert_der = b""
    return binascii.b2a_base64(cert_der).decode()


def get_certificates(tree_id: str, timeout: float = DEFAULT_TIMEOUT) -> dict:
    return {
        "tree_id": tree_id,
        "domain": f"{tree_id}.ws.{get_env().DOMAIN}",
        "cert": get_cert(tree_id, "cert.pem", timeout=timeout),
        "privkey": get_cert(tree_id, "privkey.pem", timeout=timeout),
        "version": get_version(tree_id, timeout=timeout),
    }


class Certificates(EventBus):
    """Tree certificates."""

    def __init__(self):
        subscribe(self)

    async def post(self, event: Event) -> None:
        et = event["type"]
        if et == event_type.GET_CERT:
            tree_id = eventbus.tree_id(event["src"])
            await post(put_cert(event, cert=get_certificates(tree_id)))
