import cx_Oracle                # https://oracle.github.io/odpi/doc/installation.html#odpi-c-installation
                                # For a general overview of cx_Oracle: https://cx-oracle.readthedocs.io/en/latest/
import credentials as creds     # import credentials_template as creds # @todo
from random import randint
from math import ceil, floor, pow
import string
from os import environ

env = environ.get('ENV')
debug = True if env == 'DEBUG' else False
maxBytesPerInsert = pow(2, 27)            # 128 MiB

dsn = cx_Oracle.makedsn(creds.host, creds.port, sid = creds.sid)

def connectionTest(): # this prints out the version of the DB
  con = cx_Oracle.connect(user = creds.user, password = creds.password, dsn = dsn, mode = creds.mode)
  if debug:
    print(con.version)
  con.close()

# @todo not currently working, get error about connection mode
def subscribe():
  def subscriptionCB(message):
    if debug:
      print('subscription message:', message)
  con = cx_Oracle.connect(user = creds.user, password = creds.password, dsn = dsn, mode = cx_Oracle.SYSOPER)
  con.subscribe(namespace = cx_Oracle.SUBSCR_NAMESPACE_DBCHANGE, protocol = cx_Oracle.SUBSCR_PROTO_OCI, callback = subscriptionCB)
  con.close()


# https://www.oracle.com/technetwork/articles/dsl/tuininga-cx-oracle-084866.html
def executeQueryTest():
  con = cx_Oracle.connect(user = creds.user, password = creds.password, dsn = dsn, mode = creds.mode)
  cur = con.cursor()

  # https://learncodeshare.net/2015/06/02/select-crud-using-cx_oracle/
  randNum = randint(1, 1e4)
  randInsert = "insert into riyad values ('chicken', 'cinnamon', :specialNum)"
  cur.execute(randInsert, {'specialNum':randNum}) # https://cx-oracle.readthedocs.io/en/latest/cursor.html#Cursor.execute

  select = 'select * from riyad'
  cur.execute(select)
  res = cur.fetchall()
  con.commit() # https://cx-oracle.readthedocs.io/en/latest/connection.html#Connection.commit
  if debug:
    print(res)

def createTableIfNotExists(tableName, cur):
   # unsafe string interpolation if SQL injection is a possibility... but that's far out to worry about (we have root access anyway)
  createTable = '''declare
      c int;
    begin
      select count(*) into c from user_tables where table_name = upper('{tableName}');
      if c = 0 then
          execute immediate 'CREATE TABLE {tableName}(aclob clob)';
      end if;
    end;'''.format_map(locals())
  cur.execute(createTable)

def insertClob(tableName: str, clob, cur: cx_Oracle.Cursor):
  """
  Inserts no more than 4GiB of data into the DB at a time.
  Args:
    clob (clob): https://doc.ispirer.com/sqlways/Output/SQLWays-1-124.html – The CBLOB data type stores character large objects. CLOB can store up to 4 gigabytes of character data.
  """
  if debug:
    print('running insertClob with maxBytesPerInsert: ', maxBytesPerInsert)
  if len(clob) > maxBytesPerInsert:
    clob = generateClob(maxBytesPerInsert)

  clobInsert = 'insert into {tableName} values (:clob)'.format_map(locals())
  cur.execute(clobInsert, {'clob':clob})
  if debug:
    print('returning from insertClob with maxBytesPerInsert: ', maxBytesPerInsert)


def generateClob(numBytes: int):
  if debug:
    print('running generateClob with numBytes: ', numBytes)
  numBytes = int(numBytes)
  clobBuilder = [None] * numBytes
  for i in range(numBytes):
    clobBuilder[i] = string.printable[randint(0, 99)]
  if debug:
    print('returning from generateClob with numBytes: ', numBytes)
  return ''.join(clobBuilder)

# @todo properly test this – why does it take ~30min to upload ~1GiB of data to a remote VM instance?
def executeQueryBatch(tableName: str, numBytes: int, numQueries: int):
  """
  Args:
    tableName (str): The table to insert randomly generated CLOBs into (will ultimately create the table if it doesn't).
    numBytes (int): The total number of bytes to write into the database.
    numQueries (int): The total number of queries to write into the database (each query shall be of size ~numBytes/numQueries).
  """
  if numQueries > numBytes:
    numQueries = numBytes
  clobSize = floor(numBytes / numQueries)
  if clobSize > maxBytesPerInsert:
    clobSize = maxBytesPerInsert
  totalBytesWritten = 0

  if debug:
    print('Running executeQueryBatch with numBytes: ', numBytes, ', numQueries: ', numQueries, ', maxBytesPerInsert: ', maxBytesPerInsert)

  con = cx_Oracle.connect(user = creds.user, password = creds.password, dsn = dsn, mode = creds.mode)
  cur = con.cursor()

  createTableIfNotExists(tableName, cur)
  con.commit()

  i = 0

  while i < numQueries:
    insertClob(tableName, generateClob(clobSize), cur)
    totalBytesWritten += clobSize
    if debug:
      print('main while-loop – i: ', i, ', clobSize: ', clobSize, ', totalBytesWritten: ', totalBytesWritten)
    con.commit()
    i += 1
  
  while totalBytesWritten < numBytes:
    clobSize = numBytes - totalBytesWritten
    if clobSize > maxBytesPerInsert:
      clobSize = maxBytesPerInsert
    insertClob(tableName, generateClob(clobSize), cur)
    totalBytesWritten += clobSize
    if debug:
      print('secondary while-loop – i: ', i, ', clobSize: ', clobSize, ', totalBytesWritten: ', totalBytesWritten)
    con.commit()
    i += 1

  con.close()


# subscribe()
connectionTest()
executeQueryTest()
executeQueryBatch('test_clobs', int(pow(2, 22)), 10)        # 4 MiB total
# executeQueryBatch('test_clobs', int(pow(2, 33)), 6)       # 8 GiB total
# executeQueryBatch('test_clobs', int(pow(2, 36)), 6)       # 64 GiB total
# executeQueryBatch('test_clobs', int(pow(2, 37)), 6)       # 128 GiB total
# executeQueryBatch('test_clobs', int(pow(2, 38)), 6)       # 256 GiB total