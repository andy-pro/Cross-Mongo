# -*- coding: utf-8 -*-

def index():
    return dict()

@auth.requires_membership('administrators')
def restore():
    response.view='default/index.html'
    return dict()

def user():
    response.view='default/index.html'
    action = request.args(0)
    return dict(form=auth()) if action == 'logout' or action == 'reset_password' else dict()
    #return dict(form=auth())

def error():
    response.view='default/index.html'
    return dict()

#@auth.requires_login()
@request.restful()
def api():
    response.view = 'generic.'+request.extension
    def GET(*args,**vars):
        patterns = 'auto'
        parser = db.parse_as_rest(patterns,args,vars)
        if parser.status == 200:
            return dict(content=parser.response)
        else:
            raise HTTP(parser.status,parser.error)
    #def POST(table_name,**vars):
        #return db[table_name].validate_and_insert(**vars)
    #def PUT(table_name,record_id,**vars):
        #return db(db[table_name]._id==record_id).update(**vars)
    #def DELETE(table_name,record_id):
        #return db(db[table_name]._id==record_id).delete()
    return locals()

@auth.requires_membership('administrators')
def backupvertical():
    import cStringIO
    from gluon import contenttype
    stream=cStringIO.StringIO()
    vertical = Vertical(request.args(0, cast = int))
    print >> stream, 'TABLE plints'
    db(db.plints.vertical == vertical.index).select(orderby=db.plints.id).export_to_csv_file(stream)
    print >> stream, '\n\nEND'
    response.headers['Content-Type'] = contenttype.contenttype('.csv')
    filename = 'cross-%s-vertical-%s-%s.csv' % (vertical.cross.title, vertical.title, request.now.date())
    response.headers['Content-disposition'] = 'attachment; filename=' + filename.replace(' ', '_')
    return stream.getvalue()

@auth.requires_membership('administrators')
def backup():
    import cStringIO
    from gluon import contenttype
    json = request.vars.json
    stream=cStringIO.StringIO()
    for table in tables:
        print >> stream, 'TABLE ' + table
        table = db(db[table].id).select()
        if json:
            print >> stream, table.as_json()
        else:
            table.export_to_csv_file(stream)
        print >> stream, '\n'
    print >> stream, 'END'
    #db.export_to_csv_file(stream)  # all tables
    response.headers['Content-Type'] = contenttype.contenttype('.csv')
    response.headers['Content-disposition'] = 'attachment; filename=dbcross-%s.csv' % request.now.date()
    return stream.getvalue()

# fill db with user accounts, make this function non private for using: def auth_init():
#def auth_init():
def __auth_init():
    import txt_to_db
    f = txt_to_db.__auth_init()
    db.import_from_csv_file(f, restore = True)
    session.flash = 'Auth tables initialized'
    redirect(URL('default', 'index'))

# init all db tables from file, make this function non private for using: def db_init():
def db_init():
#def __db_init():
    import os
    try:
        f = open(os.path.join(request.folder, 'private', 'tables.csv'), 'r')
        db.import_from_csv_file(f, {}, restore = True)
        __db_convert()
        msg = 'All tables initialized'
    except:
        msg = 'Error initialization'
    session.flash = msg
    redirect(URL('default', 'index'))

def __db_convert():

    #cyr_to_lat = lambda s: s.replace('БМ', 'BM').replace('БКТ', 'BKT').replace('М', 'M').replace('К', 'K').replace('Р', 'P')
    cyr_to_lat = lambda s: s.replace('М', 'M')

    for cable in dbcable.find():
        oi = cable['_id']
        try:
            pd = {
                'title': cable['title'].strip(),
                'details': cable['details'].strip(),
                'color': int(cable['color'])
            }
            dbcable.replace_one({'_id': oi}, pd)
        except:
            print 'Error for cable', oi

    for plint in dbplint.find():
        oi = plint['_id']
        try:
            pd = {
                'vertical': plint['vertical'],
                'title': cyr_to_lat(plint['title'].strip()),
                'start1': int(plint['start1']),
                'comdata': plint['comdata'].strip(),
                'mon': plint['modon'],
                'mby': plint['modby'],
                'cable': None if str(plint['cable']) == '000000000000000000000000' else plint['cable'],
                'pairs': []
            }
            for i in xrange(10):
                pf = pairfields[i]
                pd['pairs'].append({
                    'ttl': plint[pf[0]].strip(),
                    'mon': plint[pf[1]],
                    'mby': plint[pf[2]],
                    'det': plint[pf[3]].strip(),
                    'pos': int(plint[pf[4]]),
                    'par': int(plint[pf[5]]),
                    'clr': int(plint[pf[6]])
                })
            #dbplint.update({'_id': oi}, pd) # DEPRECATED
            dbplint.replace_one({'_id': oi}, pd)
        except:
            print 'Error for plint', oi
    return 'Database converted!'

def __truncate_db():
    for c in dbm.collection_names(False):
        dbm.drop_collection(c)
    return 'Database cleared!'

@auth.requires_membership('administrators')
def cleardb():
    #for table in reversed(tables): db[table].truncate()
    __truncate_db()
    session.flash = T('Database cleared')
    redirect(URL('default', 'index'))

def find_air_plint():
    l = [p['_id'] for p in dbplint.find({'vertical': {'$nin': [i['_id'] for i in dbvert.find()]}})]
    #print l
    return '%i plints found' % len(l)

def find_air_vertical():
    l = [p['_id'] for p in dbvert.find({'cross': {'$nin': [i['_id'] for i in dbcross.find()]}})]
    #print l
    return '%i verticals found' % len(l)

def del_air_plint():
    result = dbplint.delete_many({'vertical': {'$nin': [i['_id'] for i in dbvert.find()]}})
    return 'Delete %i plints' % result.deleted_count

def del_air_vertical():
    result = dbvert.delete_many({'cross': {'$nin': [i['_id'] for i in dbcross.find()]}})
    return 'Delete %i plints' % result.deleted_count

@cache.action()
def download():
    return response.download(request, db)

def call():
    return service()
