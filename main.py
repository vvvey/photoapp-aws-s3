#
# Main program for photoapp program using AWS S3 and RDS to
# implement a simple photo application for photo storage and
# viewing.
#
# Authors:
#   Vuthy Vey
#   Prof. Joe Hummel (initial template)
#   Northwestern University


import datatier  # MySQL database access
import awsutil  # helper functions for AWS
import boto3  # Amazon AWS

import uuid
import pathlib
import logging
import sys
import os

from configparser import ConfigParser

import matplotlib.pyplot as plt
import matplotlib.image as img


###################################################################
#
# prompt
#
def prompt():
  """
  Prompts the user and returns the command number
  
  Parameters
  ----------
  None
  
  Returns
  -------
  Command number entered by user (0, 1, 2, ...)
  """
  print()
  print(">> Enter a command:")
  print("   0 => end")
  print("   1 => stats")
  print("   2 => users")
  print("   3 => assets")
  print("   4 => download")
  print("   5 => download and display")
  print("   6 => upload")
  print("   7 => add user")

  cmd = int(input())
  return cmd


###################################################################
#
# stats
#
def stats(bucketname, bucket, endpoint, dbConn):
  """
  Prints out S3 and RDS info: bucket name, # of assets, RDS 
  endpoint, and # of users and assets in the database
  
  Parameters
  ----------
  bucketname: S3 bucket name,
  bucket: S3 boto bucket object,
  endpoint: RDS machine name,
  dbConn: open connection to MySQL server
  
  Returns
  -------
  nothing
  """
  #
  # bucket info:
  #
  print("S3 bucket name:", bucketname)

  assets = bucket.objects.all()
  print("S3 assets:", len(list(assets)))

  #
  # MySQL info:
  #
  print("RDS MySQL endpoint:", endpoint)

  sql = """
  select now();
  """

  row = datatier.retrieve_one_row(dbConn, sql)
  if row is None:
    print("Database operation failed...")
  elif row == ():
    print("Unexpected query failure...")
  else:
    print(row[0])

  sql_user = """
  SELECT COUNT(*) FROM users;
  """
  count = datatier.retrieve_one_row(dbConn, sql_user)
  num_user = count[0]
  print("# of user: " + str(num_user))

  sql_asset = """
  SELECT COUNT(*) FROM assets;
  """
  count = datatier.retrieve_one_row(dbConn, sql_asset)
  num_asset = count[0]
  print("# of asset: " + str(num_asset))

def users(dbConn):
  
  sql_alluser = """
  SELECT * FROM users
  ORDER BY userid DESC;
  """

  rows = datatier.retrieve_all_rows(dbConn, sql_alluser)
  for r in rows:
    (id, email, first, last, folder) = r
    print("User id: " + str(id))
    print("  Email: " + email)
    print("  Name: " + first + " " + last)
    print("  Folder: " + folder)

def assets(dbConn):
  
  sql_allassets = """
  SELECT * FROM assets
  ORDER BY assetid DESC;
  """

  rows = datatier.retrieve_all_rows(dbConn, sql_allassets)
  for r in rows:
    (id, userid, origname, bucketkey) = r
    print("Asset id: " + str(id))
    print("  User id: " + str(userid))
    print("  Original Name: " + origname)
    print("  Key name: " + bucketkey)

def download(bucket, asset_id, download_path, dbConn, display=False):
  sql_findasset = """
  SELECT assetname, bucketkey FROM assets
  WHERE assetid = %s;
  """
  row = datatier.retrieve_one_row(dbConn, sql_findasset, parameters=(str(asset_id)))
  
  if len(row) > 0: 
    (assetname, key) = row
   
    try:
        # Download the file
        filename = awsutil.download_file(bucket, key)
        print("Downloaded from S3 and saved as: " + filename)

        if display==True:
          image = img.imread(filename)
          plt.imshow(image)
          plt.show()
    except Exception as e:
        print(f"Error downloading file: {e}")
  else:
    print("No such asset ...")

def upload(filename, userid, bucket, dbConn):
  sql_user_bucket = """
  SELECT bucketfolder FROM users
  WHERE userid = %s;
  """
  sql_insert_asset = """
  INSERT INTO assets (userid, assetname, bucketkey)
  VALUES (%s, %s,%s);
  """
  user_info = datatier.retrieve_one_row(dbConn, sql_user_bucket, parameters=(str(userid)))
 
  if len(user_info) > 0:
    bucket_folder = user_info[0]
    bucket_key = bucket_folder+"/"+filename

    awsutil.upload_file(filename, bucket, bucket_key)

    params = (str(userid), filename, bucket_key)
    datatier.perform_action(dbConn, sql_insert_asset, parameters=params)

    sql_last_id = """
    SELECT LAST_INSERT_ID();
    """
    asset_id = datatier.retrieve_one_row(dbConn, sql_last_id)
    print("Recorded in RDS under user id " + str(asset_id))

  else:
    print("No such user....")

def addUser(email, last, first, dbConn):
  sql_adduser = """
    INSERT INTO 
    users(email, lastname, firstname, bucketfolder)
    values(%s, %s, %s, %s);
  """
  params = (email, last, first, str(uuid.uuid4()))
  datatier.perform_action(dbConn, sql_adduser, parameters=params)
  
  sql_last_id = """
  SELECT LAST_INSERT_ID();
  """
  user_id = datatier.retrieve_one_row(dbConn, sql_last_id)[0]
  print("Recorded in RDS under user id " + str(user_id))

#########################################################################
# main
#
print('** Welcome to PhotoApp **')
print()

# eliminate traceback so we just get error message:
sys.tracebacklimit = 0

#
# what config file should we use for this session?
#
config_file = 'photoapp-config.ini'

print("What config file to use for this session?")
print("Press ENTER to use default (photoapp-config.ini),")
print("otherwise enter name of config file>")
s = input()

if s == "":  # use default
  pass  # already set
else:
  config_file = s

#
# does config file exist?
#
if not pathlib.Path(config_file).is_file():
  print("**ERROR: config file '", config_file, "' does not exist, exiting")
  sys.exit(0)

#
# gain access to our S3 bucket:
#
s3_profile = 's3readwrite'

os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file

boto3.setup_default_session(profile_name=s3_profile)

configur = ConfigParser()
configur.read(config_file)
bucketname = configur.get('s3', 'bucket_name')

s3 = boto3.resource('s3')
bucket = s3.Bucket(bucketname)

#
# now let's connect to our RDS MySQL server:
#
endpoint = configur.get('rds', 'endpoint')
portnum = int(configur.get('rds', 'port_number'))
username = configur.get('rds', 'user_name')
pwd = configur.get('rds', 'user_pwd')
dbname = configur.get('rds', 'db_name')

dbConn = datatier.get_dbConn(endpoint, portnum, username, pwd, dbname)

if dbConn is None:
  print('**ERROR: unable to connect to database, exiting')
  sys.exit(0)

#
# main processing loop:
#
cmd = prompt()

while cmd != 0:
  #
  if cmd == 1:
    stats(bucketname, bucket, endpoint, dbConn)
  elif cmd == 2:
    users(dbConn)
  elif cmd == 3:
    assets(dbConn)
  elif cmd == 4:
    print("Enter asset id > ")
    asset_id = int(input())
    dir = os.getcwd()
    download(bucket, asset_id, dir+"/download", dbConn)
  elif cmd == 5:
    print("Enter asset id > ")
    asset_id = int(input())
    dir = os.getcwd()
    download(bucket, asset_id, dir+"/download", dbConn, display=True)
  elif cmd == 6:
    print("Enter filename >")
    filename = str(input())
    dir = os.getcwd()

    if not os.path.isfile(dir+"/"+filename):
      logging.error(" Local file " + filename + " does not exist ...")
      cmd = prompt()
      continue

    print("Enter user id >")
    userid = int(input())

    upload(filename, userid, bucket, dbConn)

  elif cmd == 7:
      print("Enter user's email >")
      email = str(input())
      print("Enter user's last (family) name > ")
      last = str(input())
      print("Enter user's first (given) name > ")
      first = str(input())
      
      addUser(email, last, first, dbConn)
  else:
    print("** Unknown command, try again...")
  #
  cmd = prompt()

#
# done
#
print()
print('** done **')
