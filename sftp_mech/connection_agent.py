import os.path
from stat import S_ISDIR

from dotenv import load_dotenv

import dir_nav as nv
# Maybe temporary?
from sftp_mech import portals


# TODO: Open new channels for separate users over single transport session
# From Paramiko - paramiko.transport.Transport:
#       ** Multiple channels can be multiplexed across a single session **


class SFTPDoer:

    def __init__(self, transport: portals.SftpPortal):

        load_dotenv(os.getenv('MM_ENV_FILE'))

        # Init Navver and set default dir context to 'remote' i.e. server-side directories
        self.nvr = nv.nvr
        self.nvr.flip_rorl()
        dir_tuple = ('/', '/content', '/',
                     (("cli_dwnlds", os.getenv("DWNL_DIR"), 0),
                      ("srv_symlns", os.getenv("SRV_SYMS")),
                      ("srv_root", os.getenv("SRV_ROOT")))
                     )

        self.nvr.est_dirs(dir_tuple)
        print(self.nvr.recall("srv_symlns"))

        self.sftp_portal = transport.sftp_portal()
        self.portal_action = self.sftp_portal.get_channel()
        self.xch_dir('/')


        # self.curr_dir = self.nvr.get_cwd()
        # self.sftp_portal.chdir(self.nvr.getcwd())
        # self.nvr.savepath("cli_dwnlds", os.getenv("DWNL_DIR"), 0)
        # self.nvr.savepath("srv_symlns", os.getenv("SRV_SYMS"))
        # self.nvr.savepath("srv_root", os.getenv("SRV_ROOT"))

        # self.client_dest_dir = self.nvr.recall("cli_dwnlds")
        # self.sSlnks = self.nvr.recall("srv_symlns", 1)

    # TODO: Get starting directory from environ or conf file
    # Variable for destination folder for downloaded folders.

    def xcwd(self):

        return self.sftp_portal.getcwd()

    def xch_dir(self, path=None):
        if path is None:
            print('No such path. No action performed')
            return
        else:
            print('\n'+self.nvr.getcwd())
            self.sftp_portal.chdir(self.nvr.move(path))
            print(f"--> {self.nvr.getcwd()}")

    def xls_iter(self, path=None):
        if path is None:
            path = self.nvr.getcwd()
        else:
            path = os.fspath(path)

        # listdir_iter has parameter 'read-aheads=50'
        # maybe useful for pagination
        return self.sftp_portal.listdir_iter(path)

    def xls_attr(self, path=None):
        if path is None:
            path = self.nvr.getcwd()
        else:
            path = os.fspath(path)

        return self.sftp_portal.listdir_attr(path)

    def xls(self, path=None):
        if path is None:
            path = self.nvr.getcwd()
        else:
            path = os.fspath(path)

        for file in self.sftp_portal.listdir_attr(path):
            if S_ISDIR(file.st_mode):
                print(str(file.filename) + "/")
            else:
                print(str(file.filename))

    def xls_blunt(self, path=None):
        if path is None:
            path = self.nvr.getcwd()
        else:
            path = os.fspath(path)

        return self.sftp_portal.listdir(path)

    # Download target to client download folder
    def xget(self, target, dwnld_path=None):
        if dwnld_path is None:
            dwnld_path = self.nvr.recall("cli_dwnlds", 0)
        else:
            dwnld_path = os.fspath(dwnld_path)

        target_name = target.split('/')[-1]
        dest = os.path.join(dwnld_path, target_name)

        self.sftp_portal.get(target, localpath=dest)

    # From Paramiko:
    #       ** Copy a remote file (remotepath) from the SFTP server and write to an open file or file-like object **
    def xget_fopen(self, target, file_obj):
        self.sftp_portal.getfo(target, file_obj)
        return file_obj

    # From Paramiko:
    #       ** Open a file on the remote server. A file-like object is returned. **
    def xfopen(self, target):
        return self.sftp_portal.open(target, 'r')

    # Make and store a symlink for easy access later, marked w/ given id.
    def xmk_slink(self, target, link_id):

        new_slink = os.path.join(self.nvr.recall("srv_symlns"), link_id)
        if os.path.exists(new_slink):
            print('\nLink w/ that id exists\n')
            return

        if os.path.exists(self.nvr.recall("srv_symlns")):
            self.sftp_portal.symlink(target, link_id)
        else:
            self.sftp_portal.mkdir(self.nvr.recall("srv_symlns"))
            self.xmk_slink(target, link_id)

    def xread_slink(self, link_id):
        return self.sftp_portal.readlink(os.path.join(self.nvr.recall("srv_symlns"), link_id))

    def get_portal_actor(self):
        return self.sftp_portal

    def __del__(self):
        self.get_portal_actor().get_channel().close()
