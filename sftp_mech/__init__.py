from sftp_mech import connection_agent as conn_agt
from sftp_mech import portals as prtls

sftp_prtl = prtls.SftpPortal()
sftp_doer = conn_agt.SFTPDoer(sftp_prtl)

