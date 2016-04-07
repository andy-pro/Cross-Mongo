# -*- coding: utf-8 -*-

def lexicon():
    return dict(
    _ADD_LINK_ = T('Add link to chain'),
    _ADD_CABLE_ = T('Add cable'),
    _ADMIN_DB_ = T('Direct edit DB'),
    _BACK_ = T('Back'),
    _BACKUP_ = T('Backup DB'),
    _BTNBACK_ = btnBack,
    _CABLES_ = T('Cables'),
    _CANCEL_ = T('Cancel'),
    _CHAIN_ = T('Edit chain'),
    _CLEAR_DB_ = T('Clear DB'),
    _COMMON_DATA_ = T('Common data'),
    _COLOR_ = T('Color'),
    _COUNT_ = T('Count'),
    _CROSS_ = T('Cross'),
    _DB_UPD_ = T('Database update success!'),
    _DEL_ = T('Delete '),
    _DETAILS_ = T('Details'),
    _EDIT_CROSS_ = T('Edit cross'),
    _EDIT_PAIR_ = T('Edit pair'),
    _EDIT_PLINT_ = T('Edit plint'),
    _EDIT_VERT_ = T('Edit vertical'),
    _EDITOR_ = T('Editor'),
    _ERROR_ = T('Error'),
    _IMPORT_ = T('Import DB'),
    _FIND_ = T('Find'),
    _FNDRES_ = T('Found results for "%s"'),
    _FOLLOW_ = T('Follow'),
    _FOR_ALL_ = T('Apply for all'),
    _FOUND_ = T('Found: '),
    _HELP_ = T('Help'),
    _HOME_ = T('Home'),
    _LAST_MOD_ = T('Last modified'),
    _MERGE_ = T('Merge through'),
    _MERGE_DB_ = T('Merge DB'),
    _NEW_CROSS_ = T('New cross'),
    _NEWPL_ = T('New plint'),
    _NEWS_ = T('News'),
    _NOCHANGE_ = T('No changes'),
    _NOT_CROSSED_ = T('Not crossed'),
    _OLDPL_ = T('Existing plint'),
    _PAIR_ = T('Pair'),
    _PAIR_T_ = T('Pair titles'),
    _PLINT_ = T('Plint'),
    _PLINT_T_ = T('Plint title'),
    _REPLACE_ = T('Replace'),
    _RESTORE_ = T('Restore DB'),
    _REM_CD_ = T('Replace remote common data'),
    _SEARCH_ = T('Search'),
    _SET_CABLE_ = T('Set cable'),
    _START_1_ = T('Numeration start 1'),
    _TITLE_ = T('Title'),
    _TOOSHORT_ = T('too short query!'),
    _TOOLS_ = T('Tools'),
    _UKSATSE_ = T('UkSATSE'),
    _VERTICAL_ = T('Vertical'),
    _VERT_T_ = T('Vertical title'),
    _VIEW_ = T('View'),
    _VIEW_VERT_ = T('View vertical'),
    _WRAP_ = T('Wrap text'),
    login = T('Log In'),
    logout = T('Log Out'),
    register = T('Sign Up'),
    request_reset_password = T('Request reset password'),
    profile = T('Profile'),
    change_password = T('Change Password'))

def __a(i):
    return ObjectId(request.args(i))

def cables():
    return dict(cables=dict((str(r['_id']),(r['title'], r['details'], r['color'])) for r in dbcable.find()))

def cross():
    return dict(crosses=[(str(r['_id']), r['title'], [(str(w['_id']), w['title']) for w in dbvert.find({'cross':r['_id']})]) for r in dbcross.find()])

def news():
    request.vars.news = True;
    return vertical()

def fheader(search, rows):
    return T('Found results for "%s"') % search if rows else '"%s" - %s' % (search, response.searchstatus)

def vertical():
    search = request.vars.search or False
    news = request.vars.news or False
    title = cross = ''
    if search:
        rows = search_plints(search, pfset=pdtset)
        header = fheader(search, rows)
    elif news:
        rows = dbplint.find().sort('modon', -1).limit(50)
        header = T('Last modified')
    else:
        vertical = Vertical(__a(0))
        title = vertical.title
        header = vertical.header
        cross = vertical.cross.title
        rows = dbplint.find({'vertical': vertical.oi}).sort('_id', 1)
    xp = __a(1) if request.edit_mode and request.args(1) else 0 # first plint from cable
    s_plint = 0
    plints = []
    cable_map = {}
    for plint in rows:
        cable = plint['cable']
        csoi = str(cable)
        if not s_plint and xp and xp==plint['_id']:
            xp = plint
            s_plint = dict(title=plint['title'], count=0, cable=csoi)
        if s_plint and s_plint['cable'] and s_plint['cable']==csoi:
            s_plint['count'] += 1
        who = get_user_name(plint['modby']) # distribute user name
        tr={'id':str(plint['_id']),
            'title': plint['title'],
            'start1': plint['start1'],
            'comdata': plint['comdata'],
            'modon': plint['modon'],
            'modby':who['soi']}
        if cable and not news:
            tr['cable'] = csoi
            if not cable_map.get(csoi):
                cable = dbcable.find_one({'_id': cable})
                if cable:
                    cable_map[csoi] = cable['title'], cable['details'], cable['color']
        td = []
        idx = 0
        for i in xrange(10):
            pair = plint['pairs'][i]
            ttl = pair['ttl']
            when = pair['mon']
            if news:
                if i and when>old: # searching newest pair
                    old = when
                    idx = i
                else:
                    old = when
            elif request.edit_mode: # in edit mode(see editvertical) pairs whenwho not needed
                td.append(ttl)
            else:
                who = get_user_name(pair['mby']) # distribute user name
                td.append((ttl, when, who['soi'], pair['det']))
        if news:
            td.append((plint['pairs'][idx]['ttl'],idx))
        tr['pairs'] = td
        plints.append(add_root(tr, plint) if search or news else tr)
    result = dict(header=header, plints=plints, users=user_map, vertical=title, cross=cross)
    if not news:
        result['cables'] = cable_map
    if isinstance(xp, dict): # edit vertical mode, plint's group on cable
        result['s_plint'] = s_plint # first plint in group
        if xp['cable']:
            xp = dbplint.find_one({'cable': xp['cable'], 'vertical': {'$ne': vertical.oi}})
            if xp:
                result['chain'] = [add_root(dict(plintId=str(xp['_id']), title=xp['title']), xp)]
    return result

#def plints():
    #return dict(data=[(i.id,i.title,int(i.start1)) for i in db(db.plints.vertical == request.args(0, cast = int)).select(*pfset1, orderby=db.plints.id)])

#def plintspid():    # add pair titles to response
    #return dict(data=[(i.id,i.title,int(i.start1),get_pids(i)) for i in db(db.plints.vertical == request.args(0, cast = int)).select(*pfset2, orderby=db.plints.id)])

def plintscd():    # add common data to response
    #return dict(data=[(str(i['_id']), i['title'], i['start1'], i['comdata']) for i in dbplint.find({'vertical': __a(0)}, pfset1m).sort('_id', 1)])
    return dict(data=[(str(i['_id']), i['title'], i['start1'], i['comdata'], get_pttl_array(i)) for i in dbplint.find({'vertical': __a(0)}).sort('_id', 1)])

def comdict(data):
    return dict(header=data.header, doctitle=data.address, modinfo=data.modified_info, title=data.title, vertical=data.vertical.title, verticalId=str(data.vertical.oi))

@auth.requires_membership('managers')
def editcross():
    if request.vars.new:
        result = (T('New cross'), '', True)
    else:
        data = Cross(__a(0))
        result = (data.header, data.title, False)
    return add_formkey(dict(zip(('doctitle', 'title', 'new'), result)))

@auth.requires_membership('managers')
def editvertical():
    request.edit_mode = True;
    result = vertical()
    result.update(cross())
    return add_formkey(result)

@auth.requires_membership('managers')
def editplint():
    #data = Plint(request.args(0, cast = int))
    data = Plint(__a(0))
    result = comdict(data)
    result.update(dict(pairtitles=get_pttl(data.record),
                       pairdetails=get_pdet(data.record),
                       start1='checked' if data.start1 else '',
                       comdata=data.comdata))
    return add_formkey(result)

@auth.requires_membership('managers')
def editpair():
    result = __getchain()
    result.update(cross())
    return add_formkey(result)

@auth.requires_membership('managers')
def editcables():
    return add_formkey(cables())

def chain():
    request.vars.chain = True
    return __getchain()

def __getchain():
    data = Pair(__a(0), request.args(1, cast = int))
    result = comdict(data)
    result['details'] = data.details
    if request.vars.chain:
        q = data.title
        linkId = data.soi + str(data.index)
        pairs = []
        if test_query(q):
            rows = search_plints(q, like=False)  # exact matching
            for plint in rows:
                for i in xrange(10):
                    if plint['pairs'][i]['ttl'] == q:
                        pairs.append(add_link(plint, i, linkId))
            pairs.sort(key = lambda tr: tr['pch'])
        else:
            pairs.append(add_link(data.record, data.index, linkId))
        result['chain'] = pairs
        result['chain_mode'] = True
    return result

@auth.requires_membership('managers')
def editfound():
    return add_formkey(vertical())

@auth.requires_membership('administrators')
def restore():
    return add_formkey(dict())

def add_formkey(data):
    s = request.function
    data.update(dict(formname=s, formkey=formUUID(s)))
    return data

def add_root(tr, plint):
    oi = plint['cross']
    tr['crossId'] = str(oi)
    tr['cross'] = dbcross.find_one({'_id': oi})['title']
    oi = plint['vertical']
    tr['verticalId'] = str(oi)
    tr['vertical'] = dbvert.find_one({'_id': oi})['title']
    return tr

def add_link(plint, i, linkId=False):
    pair = plint['pairs'][i]
    soi = str(plint['_id'])
    tr = dict(plintId=soi, pairId=i, plint=plint['title'], start1=plint['start1'], comdata=plint['comdata'],
              pdt=pair['det'],
              pch=pair['pos'],
              par=pair['par'],
              clr=pair['clr']
    )
    if linkId and linkId == soi + str(i):
        tr['edited'] = True
    return add_root(tr, plint)

def viewfound():
    #search = request.vars.search
    plints = search_plints(pfset=['pairs.ttl'])
    q = request.vars.ulsearch
    chains = []
    for plint in plints:
        pairs = plint['pairs']
        for i in xrange(10):
            title = pairs[i]['ttl']
            if title and q in title.lower():
                exist = False
                for chain in chains:
                    if chain['title'] == title:
                        exist = True
                        chain['chain'].append(add_link(plint, i))
                if not exist:
                    chains.append({
                        'title': title,
                        'chain': [add_link(plint, i)]
                    })
    chains.sort(key = lambda chain: chain['title'])
    for chain in chains:
        chain['chain'].sort(key = lambda link: link['pch'])
    return dict(doctitle=fheader(request.vars.search, plints), chains=chains)

def test_query(q):
    try:
        uq = unicode(q, 'utf-8')
    except:
        uq = q
    res = len(uq) > 2 # search query is long enough
    if res:
        request.vars.usearch = uq
        request.vars.ulsearch = uq.lower()
    return res

def search_plints(q=None, like=True, pfset=ptset):
    q = q or request.vars.search
    if test_query(q):
        if like:
            q = request.vars.ulsearch
            re = {'$regex': q, '$options': 'i'}
            result = dbplint.find({'$or': [dict([(k, re)]) for k in pfset]})
            #queries = [db.plints[field].contains(q) for field in pfset]
            #queries = [db.plints[field].contains(q, case_sensitive=False) for field in pfset] # case_sensitive=True in mongo causes an error
            #queries = [db.plints[field].contains(q, case_sensitive=False) for field in pfset] # case_sensitive=True in mongo causes an error
        else:
            result = dbplint.find({'pairs.ttl': q})
            #queries = [db.plints[field] == q for field in pfset]
        #query = reduce(lambda a, b: (a | b), queries)
        #print query
        #result = db(query).select(orderby=db.plints.cross)  # sort by crosses
        response.searchstatus = 'OK' if result else T('not found!')
        return result
    else:
        response.searchstatus = T('too short query!')
        return []


def livesearch():
    plints = search_plints(request.vars.search, pfset=pdtset) # search in plint common data, pair titles and details
    q = request.vars.ulsearch
    words = []
    def check_word(doc, f):
        w = doc[f]
        if w and q in w.lower() and w not in words:
            words.append(w)
    for plint in plints:
        check_word(plint, 'comdata')
        for i in xrange(10):
            pair = plint['pairs'][i]
            check_word(pair, 'ttl')
            check_word(pair, 'det')
    words.sort()
    return dict(search=words)

def formUUID(formname):
    from gluon.utils import web2py_uuid
    formkey = web2py_uuid()
    keyname = '_formkey[%s]' % formname
    session[keyname] = list(session.get(keyname, []))[-9:] + [formkey]
    return formkey

def json_to_utf(input):
    import json
    from gluon.storage import Storage
    def byteify(input):
        if isinstance(input, dict):
            return Storage({byteify(key):byteify(value) for key,value in input.iteritems()})
        elif isinstance(input, list):
            return [byteify(element) for element in input]
        elif isinstance(input, unicode):
            return input.encode('utf-8')
        else:
            return input
    return byteify(json.loads(input))

@auth.requires_membership('managers')
def update():
    vars = request.vars
    #print vars.userId
    #print user_id
    try:
        msg = ''
        formname = vars.formname
        formkey = vars.formkey
        keyname = '_formkey[%s]' % formname
        formkeys = list(session.get(keyname, []))
        if formkey and formkeys and formkey in formkeys:  # check if user tampering with form and void CSRF
            session[keyname].remove(formkey)
        else:
            msg = T('Session expired!')
            raise   # usage of 'raise Exception(value)' calls 'TypeError ... is not JSON serializable' error
        if not auth.user:
            msg = T('UNAUTHORIZED!')
            raise
        #if int(vars.userId) != int(auth.user.id):
        if vars.userId != user_id:
            msg = T('Access error!')
            raise
    except:
        return dict(status=False, details=msg if msg else T('Unexpected error!'))

    result = dict(status=True, show=True)
    changed = False
    try:
        if formname == 'editcross':
            # save formData from Edit Cross Controller
            if vars.new:
                data = {'title': vars.title}
                idx = dbcross.replace_one(data, data, True).upserted_id
                changed = bool(idx)
                if idx: result['location'] = 'editcross/'+str(idx)
            else:
                cross = Cross(__a(0))
                if vars.delete:
                    cross.delete()
                    changed = True
                    result['location'] = '' # this will redirect to home page index/#
                else:
                    vt = cross.update(vars)
                    changed = bool(vt)
                    if ObjectId.is_valid(vt):
                        result['location'] = 'editvertical/' + str(vt)
        elif formname == 'editvertical':
            # save formData from Edit Vertical Controller
            vertical = Vertical(request.args(0))
            vars = json_to_utf(vars.vertical)
            if vars.delete:
                vertical.delete()
                changed = True
                result['location'] = ''
            else:
                changed = vertical.update(vars)
                result['location'] = 'vertical/' + str(vertical.index)
        elif formname == 'editplint':
            plint = Plint(request.args(0))
            if vars.delete:
                plint.delete()
            else:
                changed = plint.update(vars)
        elif formname == 'editpair' or formname == 'editfound':
            plints = json_to_utf(vars.plints)
            for i in plints:
                if plint_update(i, {}, plints[i]):
                    changed = True
        elif formname == 'editcables':
            cables = json_to_utf(vars.cables)
            for i in cables:
                idx = i.id
                if i.delete:
                    #db(db.cables.id==idx).delete()
                    del db.cables[idx]
                    changed = True
                else:
                    #db.cables[i.pop('id', 0)] = i
                    if idx:
                        d = db.cables[idx].as_dict()
                        del d['id']
                        del i['id']
                        if cmp(d, i)!=0:
                            db.cables[idx] = i
                            changed = True
                    else:
                        db.cables[0] = i    # insert new
                        changed = True
        elif formname == 'restore':
            f = vars.upload.file
            #print vars
            if vars.txt == 'true':
                import txt_to_db
                f = txt_to_db.import_from_txt1(f, get_tb_fields())
            # gluon\packages\dal\pydal\base.py, line 1075
            # gluon\packages\dal\pydal\objects.py, line 826
            db.import_from_csv_file(f, restore = not bool(vars.merge))
            msg = T('Database restored')
            result['location'] = ''
        else:
            pass
    except:
        msg = T('Error')
        result['status'] = False
        result['location'] = ''
    result['details'] = msg if msg else T('Database update success!') if changed else T('No changes')
    if result.has_key('location'):
        result['location'] = start_path + result['location']
    return result

def user():
    action = request.args(0) or 'login'
    if action != 'logout' and action != 'reset_password':
        _next = request.env.http_web2py_component_location
        #form = getattr(auth, action)(onaccept=lambda form: response.headers.update({'web2py-component-command': "document.location='%s'" % _next}))
        #form = getattr(auth, action)(onaccept=lambda form: response.headers.update())
        form = getattr(auth, action)()
        title = ''
        script = ''
        if action == 'login':
            title = T('Log In')
            if not 'register' in auth.settings.actions_disabled:
                form.add_button(T('Sign Up'), URL('default', 'user/register'), _class='btn btn-default')
            if not 'request_reset_password' in auth.settings.actions_disabled:
                form.add_button(T('Lost Password'), URL('default', 'user/request_reset_password'), _class='btn btn-default')
        elif action == 'register':
            title = T('Sign Up')
            script = 'web2py_validate_entropy(jQuery("#auth_user_password"),100);'
        elif action =='change_password':
            script = 'web2py_validate_entropy(jQuery("#no_table_new_password"),100);'
        if not title:
            title = T(action.replace('_',' ').title())
        return PFORM(title, form, script)

def error():
    response.view='default/error.html'
    codes = ('401','UNAUTHORIZED'), ('403','Access denied'), ('404','Not found'), ('500','Internal server error')
    code = request.args(0) or ''
    msg = request.args(1) or 'Unknown error'
    res = dict(code=code, msg=msg)
    for code, msg in codes:
        if res['code']==code:
            res['msg'] = msg
    return res

#def sqlite_csv_to_mongo():


