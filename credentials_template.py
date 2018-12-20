import cx_Oracle # https://oracle.github.io/odpi/doc/installation.html#odpi-c-installation
# For a general overview of cx_Oracle: https://cx-oracle.readthedocs.io/en/latest/
user = 'sys'                            # whatever username you use for your db
password = 'password here'
host = 'IP address here'
sid = 'SID name to identify DB here'
port = 1521                             # whatever port number you use
mode = cx_Oracle.SYSDBA                 # whatever mode you use