Database  userdb  userdb.txt   __SQLDSN__
Database  userdb  LENGTH_EXCEPTION_DEFAULT  truncate_log
Database  userdb  DEFAULT_TYPE  varchar(255)
Database  userdb  COLUMN_DEF   "username=varchar(32) NOT NULL PRIMARY KEY"
Database  userdb  COLUMN_DEF   "password=varchar(20)"
Database  userdb  COLUMN_DEF   "acl=text"
Database  userdb  COLUMN_DEF   "mod_time=varchar(20)"
Database  userdb  COLUMN_DEF   "s_nickname=text"
Database  userdb  COLUMN_DEF   "company=varchar(128)"
Database  userdb  COLUMN_DEF   "fname=varchar(128)"
Database  userdb  COLUMN_DEF   "lname=varchar(128)"
Database  userdb  COLUMN_DEF   "address1=varchar(128)"
Database  userdb  COLUMN_DEF   "address2=varchar(128)"
Database  userdb  COLUMN_DEF   "address3=varchar(128)"
Database  userdb  COLUMN_DEF   "city=varchar(128)"
Database  userdb  COLUMN_DEF   "state=varchar(32)"
Database  userdb  COLUMN_DEF   "zip=varchar(32)"
Database  userdb  COLUMN_DEF   "country=varchar(32)"
Database  userdb  COLUMN_DEF   "phone_day=varchar(32)"
Database  userdb  COLUMN_DEF   "mv_shipmode=varchar(255)"
Database  userdb  COLUMN_DEF   "b_nickname=text"
Database  userdb  COLUMN_DEF   "b_fname=varchar(128)"
Database  userdb  COLUMN_DEF   "b_lname=varchar(128)"
Database  userdb  COLUMN_DEF   "b_address1=varchar(128)"
Database  userdb  COLUMN_DEF   "b_address2=varchar(128)"
Database  userdb  COLUMN_DEF   "b_address3=varchar(128)"
Database  userdb  COLUMN_DEF   "b_city=varchar(128)"
Database  userdb  COLUMN_DEF   "b_state=varchar(32)"
Database  userdb  COLUMN_DEF   "b_zip=varchar(32)"
Database  userdb  COLUMN_DEF   "b_country=varchar(32)"
Database  userdb  COLUMN_DEF   "b_phone=varchar(32)"
Database  userdb  COLUMN_DEF   "mv_credit_card_type=varchar(16)"
Database  userdb  COLUMN_DEF   "mv_credit_card_exp_month=varchar(2)"
Database  userdb  COLUMN_DEF   "mv_credit_card_exp_year=varchar(4)"
Database  userdb  COLUMN_DEF   "p_nickname=text"
Database  userdb  COLUMN_DEF   "email=varchar(128)"
Database  userdb  COLUMN_DEF   "fax=varchar(32)"
Database  userdb  COLUMN_DEF   "phone_night=varchar(32)"
Database  userdb  COLUMN_DEF   "fax_order=varchar(2)"
Database  userdb  COLUMN_DEF   "address_book=TEXT"
Database  userdb  COLUMN_DEF   "accounts=TEXT"
Database  userdb  COLUMN_DEF   "preferences=TEXT"
Database  userdb  COLUMN_DEF   "carts=TEXT"
Database  userdb  COLUMN_DEF   "owner=varchar(20)"
Database  userdb  COLUMN_DEF   "file_acl=TEXT"
Database  userdb  COLUMN_DEF   "db_acl=TEXT"
Database  userdb  COLUMN_DEF   "order_numbers=TEXT"
Database  userdb  COLUMN_DEF   "email_copy=varchar(1)"
Database  userdb  COLUMN_DEF   "mail_list=varchar(64)"
Database  userdb  COLUMN_DEF   "project_id=varchar(20)"
Database  userdb  COLUMN_DEF   "account_id=varchar(20)"
Database  userdb  COLUMN_DEF   "order_dest=varchar(32)"
Database  userdb  COLUMN_DEF   "inactive=varchar(32)"
Database  userdb  DEFAULT      "inactive=''"

# Prevent problems with abstime representation
UserDB    default    time_field    none