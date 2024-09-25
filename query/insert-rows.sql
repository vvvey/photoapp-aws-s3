--
-- inserts one user and one asset into respective tables:
--
-- NOTE: userid in users table is automatically generated, so we
-- don't provide a userid. Likewise for assetid in assets table.
--

USE photoapp;

INSERT INTO 
  users(email, lastname, firstname, bucketfolder)
  values('pooja.sarkar@company.com', 'sarkar', 'pooja', 
         '6b0be043-1265-4c80-9719-fd8dbcda8fd4');

INSERT INTO 
  assets(userid, assetname, bucketkey)
  values(80001,
         'A3-mac-2016.JPG',
         '6b0be043-1265-4c80-9719-fd8dbcda8fd4/af986381-55ac-4bf2-85b3-ff4a29047226.jpg');

