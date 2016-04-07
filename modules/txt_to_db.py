# -*- coding: utf-8 -*-

def import_from_txt1(fl, tb_fields):
    """
    convert txt file to cStringIO file in csv format
    """
    import cStringIO
    import csv

    #datenow = str(request.now.date())
    #dateold = datetime.date(2014, 11, 12)
    dateold = '2014-11-12'
    dateplint = dateold
    datepair = dateold
    crosses = []
    verticals = []
    plints = []
    csvfile = cStringIO.StringIO()
    writer = csv.writer(csvfile)    # by default, delimeter=',' and quotechar='"'

    cyr_to_lat = lambda s: s#.replace('БМ', 'BM').replace('БКТ', 'BKT').replace('М', 'M').replace('К', 'K').replace('Р', 'P')
    readstring = lambda: fl.readline().strip()
    readint = lambda: int(readstring())

    def fnc():
        for i in xrange(readint()):
            writer.writerow([i+1, readstring()])   # cross_index, cross_title
            crosses.append([i+1, readint()])  # cross_index, vertical count in cross

    def fnv():
        x = 1
        for cross in crosses:
            for i in xrange(cross[1]):    # cross[1] is a vertical_count
                writer.writerow([x, cross[0], readstring()])  # vertical_index, cross_index, vertical_title
                verticals.append([cross[0], x, readint(), readstring()])   # cross_index, vertical_index, plint count in vertical, start 1
                x += 1

    def fnp():
        for vertical in verticals:
            for i in xrange(vertical[2]):   # vertical[1] is a plint_count
                plints.append([vertical[0], vertical[1], cyr_to_lat(readstring()), vertical[3]])  # cross_index, vertical_index, plint_title, start 1
        x = 1
        for plint in plints:
            sp = []
            for i in xrange(10):
                spx = [readstring(), datepair, 1, '', 0, False, 0]  # pid(pair_title), pmodon, pmodby=1, pdt='', pch=0, par=False, clr=0
                s1 = fl.readline()   # pair loop, not used
                if i == 0: sp0 = spx
                else: sp = sp + spx
            s1 = readstring()   # common data
            start1 = (readstring()=='0') ^ (plint[3]=='0')   # start inverse?
            sp = sp + sp0 if start1 else sp0 + sp
            #                id   cross   vertical    title       start1 comdata modon  modby  cable
            writer.writerow([x, plint[0], plint[1], plint[2], str(start1), s1, dateplint, 1, '<NULL>'] + sp)
            x += 1

    fncs = fnc, fnv, fnp

    for i, tbs in enumerate(tb_fields):
        writer.writerows([['TABLE ' + tbs[0]], ['%s.%s' % (tbs[0], tb) for tb in tbs[1]]])
        fncs[i]()
        writer.writerows([[], []])

    writer.writerow(['END'])
    csvfile.seek(0)
    #for line in csvfile: print line,
    return csvfile

def __auth_init():
    import cStringIO
    csvfile = cStringIO.StringIO()
    print >> csvfile, '''TABLE auth_user
auth_user.id,auth_user.first_name,auth_user.last_name,auth_user.email,auth_user.password,auth_user.registration_key,auth_user.reset_password_key,auth_user.registration_id
1,Михаил,Савицкий,savitsky@uksatse.aero,"pbkdf2(1000,20,sha512)$ab7d02f116d714dd$2a2f048389d30db05274e221df73de35aa5d2fd9",,,
2,Мария,Рурак,m.rurak@ukr.net,"pbkdf2(1000,20,sha512)$bfa3d63a49577dd3$eea273beefe59c90309221c56379fce03e641579",,,
3,Андрей,Проценко,andy.pro.1972@gmail.com,"pbkdf2(1000,20,sha512)$9c63288394bb888a$653f13a60a38f2481804ac384ccacdccf56b646c",,,
4,Тарас,Гейниш,taras@uksatse.aero,"pbkdf2(1000,20,sha512)$8f342fa3ad90a64f$8c7783685d48a311debe642a0e36e0fae713c947",,,
5,Евгений,Киндрак,kindrak@uksatse.aero,"pbkdf2(1000,20,sha512)$8e77dcb4bfcea787$b598bb56624276e2b37a2866f7f9a943b2b773c1",,,
6,Иван,Мочернюк,ivan@uksatse.aero,"pbkdf2(1000,20,sha512)$961483daab2b5dca$96670a2828238793b11612d61d914913d4b7a244",,,
7,Иван,Побран,pobran@uksatse.aero,"pbkdf2(1000,20,sha512)$a3eda1f228332659$1dd0468f8b4916f77a8461da083cba81db6aca0b",,,


TABLE auth_group
auth_group.id,auth_group.role,auth_group.description
1,users,Viewing records only
2,managers,Viewing and editing records
3,administrators,Backup and restore database


TABLE auth_membership
auth_membership.id,auth_membership.user_id,auth_membership.group_id
1,1,1
2,1,2
3,2,1
4,2,2
5,3,1
6,3,2
7,3,3
8,4,1
9,4,2
10,5,1
11,5,2
12,6,1
13,6,2
14,7,1
15,7,2


END
'''
    csvfile.seek(0)
    return csvfile
