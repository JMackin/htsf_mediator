import os
from dotenv import load_dotenv
import paramiko as pmiko
# Maybe temporary?
from paramiko.ssh_exception import SSHException
# TODO implement security measures and hashing for storing keys on server


# Sftp portal should be called just once at the server startup, and only closed when necessary.
# Each instantiation creates a new authed transport session which adds up quickly.
# Before cycling the session, the instance should be deleted with 'del' to ensure the connections are closed.

class SftpPortal:
    class ConnectionBuilder:
        load_dotenv(os.getenv("MM_ENV_FILE"))
        # TODO key hashing, maybe implementing an secrets manager or database tied to server hardware

        def get_sftp_key(self):

            keypwd_file = os.getenv("SFTP_KYP")
            keyfile = os.getenv("SFTP_KEY")

            with open(keypwd_file, "r") as kpwd_file:
                keypwd = kpwd_file.readline()

            with open(keyfile, "r") as key:
                pk = pmiko.ed25519key.Ed25519Key.from_private_key(key, password=keypwd[:-1])

            return pk

        def build_ssh_transport(self):

            sftp_key = self.get_sftp_key()
            username = os.getenv("HOST_UNAME")
            host_ip = os.getenv("HOST_IP")
            host_port = int(os.getenv("HOST_PORT"))

            ssh_conn = pmiko.client.SSHClient()
            ssh_conn.set_missing_host_key_policy(pmiko.client.AutoAddPolicy())

            try:
                ssh_conn.connect(hostname=host_ip, port=host_port, username=username, pkey=sftp_key)
            except SSHException as auth_except:

                print(f"Failed to establish connection.\n \
                        Parameters used:\n \
                        \thost: {host_ip}\n \
                        \tport: {host_port}\n \
                        \tusername: {username}\n \
                        \tpkey: \n \
                        \t - key: {os.getenv('SFTP_KEY')}\n \
                        \t - pass: \n \
                       ")
                print(f"{auth_except.__str__()}")
                return None

            return ssh_conn

    def sftp_portal(self):
        new_client = self.ssh_transport.open_sftp()
        return new_client

    def get_transport(self):
        return self.ssh_transport

    def get_chanId(self):
        pass
        # return self.channel_id

    def is_open(self, portal):
        return portal.get_channel().is_active()

    def ready_to_read(self, portal):
        return portal.get_channel().recv_ready()

    def __init__(self):
        self.ssh_transport = self.ConnectionBuilder().build_ssh_transport()
        # self.channel_id = self.ssh_transport.channel_id
        # print(f"Opened portal. Channel ID: {self.channel_id}")

    def __del__(self):
        if self.ssh_transport.get_transport().active:
            self.ssh_transport.close()

    def __delete__(self, portal):
        if portal.isinstance():
            if self.ssh_transport.get_transport().active:
                self.ssh_transport.close()
