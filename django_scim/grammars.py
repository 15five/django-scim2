from plyplus import Grammar


USER_GRAMMAR = Grammar("""
  start: logical_or;

  ?logical_or: logical_or op_or logical_and | logical_and;
  ?logical_and: logical_and op_and expr | expr;

  ?expr: un_string_expr | un_expr | bin_expr | '\(' logical_or '\)';

  ?bin_expr: (bin_string_expr | bin_passwd_expr | bin_pk_expr | bin_date_expr | bin_bool_expr);

  un_string_expr: (string_field | password) pr;
  un_expr: (date_field | bool_field) pr;
  bin_string_expr: string_field string_op t_string;
  bin_passwd_expr: password eq t_string;
  bin_pk_expr: pk eq t_string;
  bin_date_expr: date_field date_op t_date;
  bin_bool_expr: bool_field eq t_bool;

  ?string_op: eq | co | sw;
  ?date_op: eq | gt | ge | lt | le;

  ?op_or: '(?i)or';
  ?op_and: '(?i)and';
  pr: '(?i)pr';
  eq: '(?i)eq';
  co: '(?i)co';
  sw: '(?i)sw';
  gt: '(?i)gt';
  ge: '(?i)ge';
  lt: '(?i)lt';
  le: '(?i)le';

  ?string_field: username | first_name | last_name | email | external_id;
  ?date_field: date_joined;
  ?bool_field: is_active;

  username: '(?i)userName';
  external_id: '(?i)externalId';
  first_name: '(?i)name\.givenName' | '(?i)givenName';
  last_name: '(?i)name\.familyName' | '(?i)familyName';
  password: '(?i)password';
  pk: '(?i)id';
  date_joined: '(?i)meta\.created' | '(?i)created';
  email: '(?i)emails\.value' | '(?i)emails';
  is_active: '(?i)active';

  t_string: '"(?:[^"\\\\]|\\\\.)*"' ;
  t_date: '"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[Zz]?"';
  t_bool: 'false' | 'true';

  SPACES: '[ ]+' (%ignore);
  """)


GROUP_GRAMMAR = Grammar("""
  start: logical_or;

  ?logical_or: logical_or op_or logical_and | logical_and;
  ?logical_and: logical_and op_and expr | expr;

  ?expr: un_string_expr | bin_expr | '\(' logical_or '\)';

  ?bin_expr: (bin_string_expr | bin_pk_expr);

  un_string_expr: string_field pr;
  bin_string_expr: string_field string_op t_string;
  bin_pk_expr: pk eq t_string;

  ?string_op: eq | co | sw;

  ?op_or: '(?i)or';
  ?op_and: '(?i)and';
  pr: '(?i)pr';
  eq: '(?i)eq';
  co: '(?i)co';
  sw: '(?i)sw';

  ?string_field: name;

  name: '(?i)displayName' | '(?i)name';
  pk: '(?i)id';

  t_string: '"(?:[^"\\\\]|\\\\.)*"';

  SPACES: '[ ]+' (%ignore);
  """)
