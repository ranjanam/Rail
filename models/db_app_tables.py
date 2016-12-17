# -*- coding: utf-8 -*-
db.define_table('station',
                Field('id', type='id'),
                Field('name','string'))

db.define_table('train_details',
                Field('tno', 'integer', notnull=True),
                Field('name', 'string', notnull=True),
                Field('source_id', 'list:reference station' , requires=IS_IN_DB(db, 'station.id'), notnull=True),
                Field('dest_id', 'list:reference station', requires=IS_IN_DB(db, 'station.id'), notnull=True),
                Field('speed', 'double', notnull=True),
                primarykey=['tno'])

db.define_table('train',
               Field('tid', 'integer', notnull=True),
               Field('num', 'list:reference train_details' , requires=IS_IN_DB(db, 'train_details.tno')))

db.define_table('coach',
                Field('train_num', 'list:reference train_details' , requires=IS_IN_DB(db, 'train_details.tno'), notnull=True),
                Field('coach_name', 'string', notnull=True),
                Field('total_seats', 'string', notnull=True),
                Field('amount', 'double', notnull=True))

db.define_table('ticket',
                 Field('id', type='id'),
                 Field('user_id', db.auth_user, notnull=True),
                 Field('train_id', 'reference train', notnull=True),
                 Field('train_num', 'reference train_details', notnull=True),
                 Field('source_id', 'reference station',notnull=True),
                 Field('dest_id', 'reference station', notnull=True),
                 Field('DOJ', 'date',  notnull=True,requires = IS_DATE(format=T('%Y-%m-%d'))),
                 Field('DOB', 'date', notnull=True, requires = IS_DATE(format=T('%Y-%m-%d'))),
                 Field('amount', 'double', notnull=True),
                 Field('coach', 'string', notnull=True),
                 Field('total_pass', 'integer', notnull=True),
                 Field('status', 'string', notnull=True),
                 Field('curr_time', 'datetime', notnull=True))

db.define_table('route',
                Field('train_id','list:reference train',requires=IS_IN_DB(db,db.train.tid), notnull=True),
                Field('train_num','list:reference train',requires=IS_IN_DB(db, db.train_details.tno), notnull=True),
                Field('stop_num', 'integer', notnull=True),
                Field('station_id', 'list:reference station' , requires=IS_IN_DB(db, db.station.id), notnull=True),
                Field('arr_day', 'list:integer'),
                Field('dep_day', 'list:integer'),
                Field('arr_time', 'time', widget=SQLFORM.widgets.time.widget),
                Field('dep_time', 'time', widget=SQLFORM.widgets.time.widget),
                Field('dist_from_source', 'integer', notnull=True))
db.define_table('A1',
                Field('seat_num', 'integer', notnull=True),
                Field('pass_name', 'string', notnull=True),
                Field('age', 'string', notnull=True),
                Field('gender', 'string', notnull=True),
                Field('status', 'string', notnull=True),
                Field('pnr_num', 'list:reference ticket',notnull=True),
               Field('is_alloted', 'boolean', default=False))
db.define_table('B1',
                Field('seat_num', 'integer', notnull=True),
                Field('pass_name', 'string', notnull=True),
                Field('age', 'string', notnull=True),
                Field('gender', 'string', notnull=True),
                Field('status', 'string', notnull=True),
                Field('pnr_num', 'list:reference ticket',notnull=True),
               Field('is_alloted', 'boolean', default=False))
db.define_table('SL',
                Field('seat_num', 'integer', notnull=True),
                Field('pass_name', 'string', notnull=True),
                Field('age', 'string', notnull=True),
                Field('gender', 'string', notnull=True),
                Field('status', 'string', notnull=True),
                Field('pnr_num', 'list:reference ticket',notnull=True),
               Field('is_alloted', 'boolean', default=False))
db.define_table('bank',
                Field('card_type', 'string', notnull=True),
                Field('name', 'string', notnull=True))
