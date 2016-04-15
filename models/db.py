# -*- coding: utf-8 -*-

import pymongo
from bson.objectid import ObjectId

start_path = '/cross/default/index/';   # URL function give wrong result for ajax.json request!!! (add '.json')
#request.requires_https() # all HTTP requests to be redirected to HTTPS, uncomment this line

from gluon.contrib.appconfig import AppConfig # private/appconfig.ini
myconf = AppConfig()

#db = DAL(myconf.take('db.uri'), pool_size=myconf.take('db.pool_size', cast=int), check_reserved=['common'], migrate_enabled=False)
#db = DAL(myconf.take('db.uri'), pool_size=myconf.take('db.pool_size', cast=int), check_reserved=['common'], migrate_enabled=True)

client = pymongo.MongoClient('localhost', 8001)
dbm = client.cross
dbauth = dbm.auth_user
dbcable = dbm.cables
dbcross = dbm.crosses
dbvert = dbm.verticals
dbplint = dbm.plints

## gluon/packages/dal/pydal/objects.py line 954:  curr_id = self.insert(**dict(items)) returns None if adapter_args={"safe":False}
#db = DAL('mongodb://localhost:8001/cross', pool_size=1, check_reserved=['mongodb_nonreserved'], adapter_args={"safe":False})
db = DAL('mongodb://localhost:8001/cross', pool_size=1, check_reserved=['mongodb_nonreserved'])

#db = DAL("mongodb://<user>:<password>@<host>.mongohq.com:<port>/ming", check_reserved=["mongodb_nonreserved"], adapter_args={"safe":False})

response.generic_patterns = ['*'] if request.is_local else ['*.json']   # for *.json give generic view
response.formstyle = myconf.take('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.take('forms.separator')

## (optional) optimize handling of static files
response.optimize_css = 'concat,minify,inline'
response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'

from gluon.tools import Auth, Service, PluginManager

auth = Auth(db)
service = Service()
plugins = PluginManager()

auth.define_tables(username=False, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.take('smtp.server')
mail.settings.sender = myconf.take('smtp.sender')
mail.settings.login = myconf.take('smtp.login')
mail.settings.tls = True

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True
auth.settings.create_user_groups = None
auth.settings.everybody_group_id = 1

#========= define tables ================================
#print 'db.py exec'
tables = 'cables', 'crosses', 'verticals', 'plints'
db.define_table('cables',
                #Field('hid', length=40, default=''),
                Field('title', length=40, default=''),
                Field('details', length=80, default=''),
                Field('color', 'integer', default=0))
db.define_table('crosses', Field('title', length=40))
db.define_table('verticals', Field('cross', db.crosses), Field('title', length=40))
selfields = []
pairfields = []
pairnames = []
pdtset = []
pfset1 = ('pid','pmodon','pmodby','pdt','pch','par','clr')    # must be 3 symbols
pfset2 = []
for i in xrange(1, 11):
    fnames = [name+`i` for name in pfset1]
    pairfields.append(fnames)
    pairnames.append(fnames[0])
    pdtset.append(fnames[3])
    plintfields = Field(fnames[0], length=80, default='')   # pid, pair title
    pfset2.append(plintfields)
    selfields.append(plintfields)
    #selfields.append(Field(fnames[1], 'date', default=request.now.date()))   # pmodon, modify date
    selfields.append(Field(fnames[1], 'datetime', default=request.now))   # pmodon, modify date
    selfields.append(Field(fnames[2], db.auth_user, default=auth.user))   # pmodby, modify author
    selfields.append(Field(fnames[3], length=80, default=''))   # pdt, pair details
    selfields.append(Field(fnames[4], 'integer', default=0))   # pch, position in chain
    selfields.append(Field(fnames[5], 'boolean', default=False))   # par, parallel presence
    selfields.append(Field(fnames[6], 'integer', default=0))   # clr, pair color, default is #fff, white
plintfields = ('title','start1','comdata','modon','modby','cable')
db.define_table('plints',
                Field('cross', db.crosses),
                Field('vertical', db.verticals),
                Field(plintfields[0], length=40, default=''),  # title
                Field(plintfields[1], 'boolean', default=True),  # start1
                Field(plintfields[2], length=40, default=''),  # comdata
                #Field(plintfields[3], 'date', default=request.now.date()),  # modon
                Field(plintfields[3], 'datetime', default=request.now),  # modon
                Field(plintfields[4], db.auth_user, default=auth.user),  # modby
                Field(plintfields[5], db.cables),  # cable
                *selfields)
# pairfields - [[pid1,pmodon1,pmodby1,pdt1,pch1,par1], [pid2,pmodon2,pmodby2,pdt2,pch2,par2], ...]
# pairnames - [pid1, ..., pid10]
#pairtitles = pairnames + [plintfields[2]] # [pid1, ..., pid10, comdata]

pfset1 = [db.plints.id, db.plints.title, db.plints.start1, db.plints.comdata] # pydal fields
pfset1m = {'title': 1, 'start1': 1, 'comdata': 1} # mongo projection set1


pfset2 = pfset1 + pfset2 # pydal fields
#pdtset = pairtitles + pdtset # [pid1, ..., pid10, comdata, pdt1, ..., pdt10]
ptset = ['comdata', 'pairs.ttl']
pdtset = ['comdata', 'pairs.ttl', 'pairs.det']

user_map = {}  # global dictionary, cashe type, contains printable user name

# ========== app global functions ==========
def get_user_name(oi):
    soi = str(oi)
    if oi:
        who = user_map.get(soi)
        if not who:
            rec = dbauth.find_one({'_id': oi})
            who = rec['first_name'] + ' ' + rec['last_name']
            user_map[soi] = who
    else:
        who = ''
    return dict(who=who, soi=soi)

def get_tb_fields():
    fields = (('id','title'), ('id','cross','title'), ('id','cross','vertical')+plintfields+tuple(sum(pairfields,[])))
    #return zip(tables, fields)
    return zip(('crosses', 'verticals', 'plints'), fields)

#get_pids = lambda rec: '\n'.join(rec(pairtitles[i]) or '' for i in xrange(10))
#get_pdts = lambda rec: '\n'.join(rec(pairfields[i][3]) or '' for i in xrange(10))

get_pttl = lambda rec: '\n'.join(p['ttl'] or '' for p in rec['pairs'])
get_pdet = lambda rec: '\n'.join(p['det'] or '' for p in rec['pairs'])

get_pttl_array = lambda rec: [p['ttl'] or '' for p in rec['pairs']]

#get_whenwho = lambda: dict(modon=request.now.date(), modby=user_id)
#get_whenwho = lambda: dict(modon=request.now, modby=user_id)

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

user_id = '%X'%auth.user.id if auth.user else False
#user_id = ObjectId(auth.user.id) if auth.user else ''
is_admin = auth.has_membership('administrators')

#if auth.user:
    #print auth.user.id, auth.user.first_name
    #print 'managers', auth.has_membership('managers')
    #print 'administrators', auth.has_membership('administrators')

if is_admin:
    response.headers['Admin'] = True
response.headers['User-Id'] = user_id
btnBack = XML('<button type="button" class="close" aria-hidden="true" onclick="history.back();return false;" title="%s (Esc)">&times;</button>' % T("Back"))
PFORM = lambda title, form, script='': DIV(DIV(DIV(title, btnBack, _class="panel-heading"), DIV(form, _class="panel-body"), _class="panel panel-info"), SCRIPT('$("div.panel input:visible:first").focus();', script, _type='text/javascript'), _class="container cont-mid")
itext = lambda c, t: I(_class='glyphicon glyphicon-'+c) + ' ' + t

if not request.ajax:
    response.title = request.application.replace('_',' ').title()
    response.subtitle = ''
    response.meta.author = 'Andrey Protsenko <andy.pro.1972@gmail.com>'
    response.meta.description = 'Cross management application'
    response.meta.keywords = 'web2py, web2spa, single page application, python, framework, javascript, ajax, jquery, andy-pro'
    response.meta.generator = 'Web2py Web Framework'
    response.crossmenu = [
        ('', False, A(B('CROSS'), XML('&trade;&nbsp;'), _class='navbar-brand web2spa',_href=URL('default', 'index'))),
        ('', False, A(B(T('News')), _class="nav navbar-nav web2spa", _href=URL('default', 'index/news'))),
        ('', False, A(LABEL(INPUT(_type='checkbox', _id='chainMode'), T('Edit chain')), _class='inmenu'))
    ]

    if auth.has_membership('managers'):
        toolsmenu = [('', False, A(itext('th-list', T('New cross')), _class='web2spa', _href=URL('default', 'index/editcross', vars={'new':'true'}))),
                     ('', False, A(itext('random', T('Cables')), _class='web2spa', _href=URL('default', 'index/editcables')))]
        if is_admin:
            #response.headers['Admin'] = True
            hr = LI(_class="divider")
            toolsmenu += [hr, (itext('upload', T('Backup DB')+' (csv)'), False, URL('default', 'backup')),
                (itext('upload', T('Backup DB')+' (json)'), False, URL('default', 'backup', vars={'json':'true'})), hr,
                ('', False, A(itext('download', T('Restore DB')), _class='web2spa', _href=URL('default', 'restore'))),
                ('', False, A(itext('plus', T('Merge DB')), _class='web2spa', _href=URL('default', 'restore', vars={'merge':'true'}))),
                ('', False, A(itext('import', T('Import DB')), _class='web2spa', _href=URL('default', 'restore', vars={'txt':'true'}))), hr,
                #('Test', False, URL('default', 'test')), hr,
                #('', False, A('Test', _class='web2spa', _href=URL('default', 'index/vertical'))), hr,
                (itext('warning-sign', T('Direct edit DB')), False, URL('appadmin', 'index')),
                (itext('remove', T('Clear DB')), False, 'javascript:app.db_clear()'), hr,
                (itext('cog', 'RESTful API'), False, URL('default', 'api/patterns'))]
        response.toolsmenu = [(T('Tools'), False, '#', toolsmenu)]


def init_item(self, dbitem, oi):
    self.oi = oi
    self._id = {'_id': oi}
    self.record = dbitem.find_one(self._id)
    if not self.record: raise HTTP(404)
    self.soi = str(oi)
    _rec = self.record
    self.title = _rec['title']
    return _rec

# ========== Class Cross ==========
class Cross:
    def __init__(self, oi):
        _rec = init_item(self, dbcross, oi)
        self.header = T('Cross')+' '+self.title

    def update(self, vars):
        changed = False
        if vars.title != self.title:
            dbcross.update_one(self._id, {'$set': {'title': vars.title}})
            changed = True
        vt = vars.verticaltitle
        data = {'title': vt, 'cross': self.oi}
        vt = dbvert.replace_one(data, data, True).upserted_id if vt else None  # return id of new record
        return vt or changed

    def delete(self):
        rows = dbvert.find({'cross': self.oi})
        for r in rows:
            v = r['_id']
            dbplint.delete_many({'vertical': v})
            dbvert.delete_one({'_id': v})
        dbcross.delete_one(self._id)
## end class Cross

# ========== Class Vertical ==========
class Vertical:
    def __init__(self, oi):
        _rec = init_item(self, dbvert, oi)
        self.cross = Cross(_rec['cross'])
        self.header = self.cross.header + ', %s %s' % (T('Vertical'), self.title)

    def delete(self):
        dbplint.delete_many({'vertical': self.oi})
        dbvert.delete_one(self._id)

    def update(self, vars):
        changed = False
        if vars.has_key('cable'):
            cable = vars['cable']
            cable_oi = ObjectId(cable['_id'])
            if cable.has_key('set'):
                dbcable.update_one({'_id': cable_oi}, {'$set': cable['set']})
                changed = True
        else:
            cable_oi = None
        if self.title != vars['title']:
            dbvert.update_one(self._id, {'$set': {'title': vars['title']}})
            changed = True

        for plint in vars['plints']:
            if plint.has_key('cable'):
                plint['cable'] = cable_oi
            xp = dbplint.find_one({'title':plint['title'], 'vertical': self.oi})
            if xp:
                if plint_update(xp, plint):
                    changed = True
            else:  # if plint not exist then create it
                self.insert_new_plint(plint)
                changed = True
        for plint in vars['rplints']:
            if plint.has_key('cable'):
                plint['cable'] = cable_oi
            if plint_update(None, plint):
                changed = True
        return changed

    def insert_new_plint(self, plint):
        mon = request.now
        mby = ObjectId(user_id)
        plint['pairs'] = []
        for i in xrange(10):
            ttl = 'pairs.%i.ttl'%i
            plint['pairs'].append({'ttl':plint[ttl], 'mon':mon, 'mby':mby, 'det':'', 'pos':0, 'par':0, 'clr':0})
            del plint[ttl]
        plint.update({'vertical':self.oi, 'mon':mon, 'mby':mby})
        plint['cable'] = plint.get('cable', None)
        dbplint.insert_one(plint)
### end class Vertical

# ========== Class Plint ==========
class Plint:
    def __init__(self, oi):
        _rec = init_item(self, dbplint, oi)
        self.vertical = Vertical(_rec['vertical'])
        self.cross = self.vertical.cross
        self.titles = self.cross.title, self.vertical.title,  self.title
        self.header = self.vertical.header + ', %s %s' % (T('Plint'), self.title)
        self.address = '%s %s %s' % self.titles
        self.modified_info = '%s %s, %s' % (T('Last modified'), _rec['mon'], get_user_name(_rec['mby'])['who'])
        self.comdata = _rec['comdata']
        self.start1 = _rec['start1']

    #get_pair_titles = lambda self: [self.record(pairtitles[i]) for i in xrange(10)]
    #get_fieldset = lambda self, f: [self.record('%s%i' % (f,i)) or '' for i in xrange(1,11)]
    #get_fieldstring = lambda self, f: '\n'.join(self.get_fieldset(f)).rstrip()

    def delete(self):
        dbplint.delete_one(self._id)

    def update(self, vars):
        plint = {'title':vars.title, 'start1':int(bool(vars.start1)), 'comdata':vars.comdata}
        ttls = vars.pairtitles.splitlines()
        dets = vars.pairdetails.splitlines()
        ttll = len(ttls)
        detl = len(dets)
        for i in xrange(10):
            pre = 'pairs.%i.'%i
            plint[pre+'ttl'] = ttls[i] if ttll > i else ''
            plint[pre+'det'] = dets[i] if detl > i else ''
        return plint_update(self.record, plint, bool(vars.merge), vars.mergechar or '')
#### end class Plint

def plint_update(xp=None, plint=None, merge=False, mergechar=''):
    #dbplint.update_one({'_id': oi}, {'$set': {'title': vars.title}})
    """
    xp - record '_id' (str), ObjectId, dict or None
    plint - dict with plint data, must contains '_id' if xp=None
    merge - boolean, if True, new pair title merge with existing
    mergechar - 'old title' + mergechar + 'new title'
    """

    def add_wh(pre=''): # add whenwho info
        pd[pre + 'mon'] = mon
        pd[pre + 'mby'] = mby

    if not isinstance(xp, dict):
        if not isinstance(xp, ObjectId):
            if not xp:
                xp = plint.pop('_id')
            xp = ObjectId(xp)
        xp = dbplint.find_one({'_id': xp})

    changed = False
    if xp:
        mon = request.now
        mby = ObjectId(user_id)
        pd = {}
        for mkey in plint:
            src = plint[mkey]
            if mkey.startswith('pairs'):
                fp = mkey.split('.')
                i = int(fp[1])
                fk = fp[2]
                dst = xp['pairs'][i][fk]
                if (fk=='ttl' or fk=='det'):
                    src = src.strip()
                    dst = dst.strip()
                    if merge:
                        src = (dst + mergechar + src)
                if src != dst:
                    pd[mkey] = src
                    add_wh('pairs.%i.'%i)
            elif src != xp[mkey]:
                pd[mkey] = src
        if len(pd.keys()):
            add_wh()
            dbplint.update_one({'_id': xp['_id']}, {'$set': pd})
            changed = True
    return changed

# ========== Class Pair ==========
class Pair:
    def __init__(self, _plint, _pair):
        if _pair>9 or _pair<0: raise HTTP(404)
        self.plint = Plint(_plint)
        _rec = self.plint.record
        self.record = _rec
        #self.oi = _rec.oi
        self.oi = _plint
        self.soi = self.plint.soi
        self.index = _pair
        self.vertical = self.plint.vertical
        #f = pairfields[_pair-1]
        pf = _rec['pairs'][_pair]
        self.title = pf['ttl']
        self.details = pf['det']
        self.pos = pf['pos']
        self.par = pf['par']    # parallel flag
        self.header = self.plint.header + ', %s %s' % (T('Pair'), _pair + _rec['start1'])
        self.address = self.title + ' ' + self.plint.address
        self.modified_info = '%s %s, %s' % (T('Last modified'), pf['mon'], get_user_name(pf['mby'])['who'])
        self.pair = pf
##### end class Pair
