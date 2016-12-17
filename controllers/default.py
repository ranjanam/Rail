# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------
import datetime
timeshift = request.now - request.utcnow
data = []

days={'Sun':0,'Mon':1,'Tue':2,'Wed':3,'Thu':4,'Fri':5,'Sat':6}
def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    return dict()

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)

def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()

@auth.requires_login()
def validatedetails(form):
    selecteddate = datetime.datetime.strptime(form.vars.doj, "%Y-%m-%d").date()
    if form.vars.source == form.vars.dest:
        form.errors = "Source and destination must be different"
        data_url = URL('default', 'traindetails.load',vars=dict())
        response.js = '$.web2py.component("%s", "traindetails")' % data_url
    elif selecteddate<=datetime.datetime.now().date():
        form.errors = "Invalid date"
        data_url = URL('default', 'traindetails.load',vars=dict())
        response.js = '$.web2py.component("%s", "traindetails")' % data_url

@auth.requires_login()
def bookticket():
    return dict()

@auth.requires_login()
def query():
    stations = db(db.station).select()
    list1 = SELECT(*[OPTION(stations[i].name, _value=str(stations[i].id)) for i in range(len(stations))], _name="source", requires=IS_NOT_EMPTY())
    list2 = SELECT(*[OPTION(stations[i].name, _value=str(stations[i].id)) for i in range(len(stations))], _name="dest", requires=IS_NOT_EMPTY())
    table = DIV(DIV(H3('DETAILS', _class="panel-title"), _class="panel-heading"), TABLE(TR(TD('SOURCE'),TD(list1)),TR(TD('DESTINATION'),TD(list2)),TR(TD('DATE'), TD(INPUT(_class='date', _name='doj',widget=SQLFORM.widgets.date.widget, requires=IS_NOT_EMPTY()))), TR(TD( INPUT(_value='submit',_type='submit', _class='btn btn-default'))), _class="table-condensed"), _class="panel panel-info")
    form = FORM(table)
    if form.process(onvalidation=validatedetails,keepvalues=True).accepted:
            data_url = URL('default', 'traindetails.load',vars=dict(source=request.vars.source, dest=request.vars.dest, doj=request.vars.doj))
            response.js = '$.web2py.component("%s", "traindetails")' % data_url
            response.flash=""
    elif form.errors:
            session.flash = form.errors
            response.flash=""
    return dict(form=form)

@auth.requires_login()
def traindetails():
    if request.vars.source:
        doj= datetime.datetime.strptime(request.vars.doj, '%Y-%m-%d').strftime('%a')
        doj=days[doj]
        sources = db((db.route.station_id == request.vars.source)).select(db.route.ALL)
        sources_list=[]
        for s in sources:
            if len(s.dep_day)>0 and s.dep_day[doj] == 1:
                sources_list.append(s)
        sources = sources_list
        dests = db(db.route.station_id == request.vars.dest).select(db.route.ALL)
        availableTrains = []
        for s in sources:
            for d in dests:
                if s.train_id == d.train_id and s.stop_num < d.stop_num and s.train_num == d.train_num:
                    train = db(db.train_details.tno == int(s.train_num[0])).select()
                    coaches = db(db.coach.train_num == s.train_num).select()
                    links=[]
                    for c in coaches:
                        dist= d.dist_from_source - s.dist_from_source
                        data_url = URL('default', 'availabletickets.load', vars=dict(tid=s.train_id[0], source=s.station_id, dest=d.station_id, coach=c.coach_name, doj=request.vars.doj, tno=s.train_num, dist = dist))
                        links.append(A(c.coach_name,_href=data_url, cid='availabletickets'))
                    availableTrains.append(TR(TD(s.train_num[0], _class="col-md-1"), TD(train[0].name, _class="col-md-1"), TD(s.dep_time, _class="col-md-1"), TD(d.arr_time, _class="col-md-1"),TD(d.dist_from_source - s.dist_from_source, _class="col-md-1"), TD(links, _class="col-md-1")))
                    break
        if len(availableTrains) == 0:
            availableTrains = DIV(SPAN('NO TRAINS AVAILABLE'))
            data_url = URL('default', 'availabletickets.load',vars=dict())
            response.js = '$.web2py.component("%s", "availabletickets")' % data_url
        else :
            availableTrains= TABLE(THEAD(TR(TH('TRAIN NUMBER', _class="col-md-1 panel-title"), TH('TRAIN NAME', _class="col-md-1 panel-title"), TH('DEPARTURE TIME ', _class="col-md-1 panel-title"),TH('ARRIVAL TIME', _class="col-md-1 panel-title"), TH('DISTANCE', _class="col-md-1 panel-title"), TH('COACH', _class="col-md-1 panel-title")),_class="panel-heading"), TBODY(availableTrains), _class="table-condensed table-bordered panel panel-info")
            data_url = URL('default', 'availabletickets.load',vars=dict())
            response.js = '$.web2py.component("%s", "availabletickets")' % data_url
        return dict(trains=availableTrains)
    else :
        data_url = URL('default', 'availabletickets.load',vars=dict())
        response.js = '$.web2py.component("%s", "availabletickets")' % data_url
        return dict(trains='')

def getavailableseats(tno, tid, doj, coach, source, dest):
    map = db((db.coach.train_num == tno) & (db.coach.coach_name == coach)).select()
    map = ['F']*(map[0].total_seats)
    rows = db((db.ticket.DOJ == doj) & (db.ticket.coach == coach) & (db.ticket.train_num == tno)).select(orderby=db.ticket.curr_time)
    stops = db((db.route.train_id == tid)&(db.route.train_num == tno)).select()
    source_stop = [s for s in stops if s.station_id[0] == int(source)]
    source_stop = source_stop[0].stop_num
    dest_stop = [s for s in stops if s.station_id[0] == int(dest)]
    dest_stop = dest_stop[0].stop_num
    amount=0
    for r in rows:
        stop1_details = [s for s in stops if s.station_id[0] == r.source_id]
        stop2_details = [s for s in stops if s.station_id[0] == r.dest_id]
        stop1 = stop1_details[0].stop_num
        stop2 = stop2_details[0].stop_num
        if (dest_stop<=stop1 or source_stop>=stop2):
            pass
        elif (source_stop<=stop1 and stop2>=dest_stop) or (stop1<source_stop and source_stop<stop2) or (stop1<dest_stop and dest_stop<stop2):
            if coach == 'A1' :
                seats = db(db.A1.pnr_num == r.id).select()
            elif coach == 'B1':
                seats = db(db.B1.pnr_num == r.id).select()
            elif coach == 'SL':
                seats = db(db.SL.pnr_num == r.id).select()
            for s in seats:
                if s.status=="CONFIRMED":
                    map[s.seat_num-1]='O'
    return map

@auth.requires_login()
def availabletickets():
    if request.vars.tno:
        tno = request.vars.tno
        tid = request.vars.tid
        doj = request.vars.doj
        coach = request.vars.coach
        seats = getavailableseats(tno, tid, doj, coach, request.vars.source, request.vars.dest)
        available = len(seats)-seats.count('O')
        amount = db((db.coach.coach_name == request.vars.coach)&(db.coach.train_num == tno)).select(db.coach.amount)
        amount = (int(request.vars.dist))*(amount[0].amount)
        session.train_id = tid
        session.train_num = tno
        session.doj = doj
        session.source_id = request.vars.source
        session.dest_id = request.vars.dest
        session.coach = coach
        session.amount=amount
        session.dist = request.vars.dist
        if available == 0:
            available="WAITING"
        available = TABLE(THEAD(TR(TH('AVAILABLE', _class="panel-title")),_class="panel-heading"),TBODY(TR(TD(available)), TR(  TD(A('BOOK NOW', _href=URL('default','passengerform.html'))) )), _class="table-condensed panel panel-info")
        cost = LABEL('TOTAL FARE : '+str(amount))
        available = DIV(available, cost)
        return dict(available=available)
    else :
        return dict(available='')

@auth.requires_login()
def checkpassengerdetails(rows):
    i = 1
    global data
    data=[]
    while i<=6:
        pg=ag=gn=""
        if rows.vars['pg-'+str(i)]!=None:
            pg = rows.vars['pg-'+str(i)].strip()
        if rows.vars['ag-'+str(i)]!=None:
            ag = rows.vars['ag-'+str(i)].strip()
        if rows.vars['gn-'+str(i)]!=None:
            gn = rows.vars['gn-'+str(i)].strip()
        if pg and ag and gn!="0":
            if not (ag.isdigit() and pg.isalpha()):
                rows.errors.ag = "Please fill proper details"
            else:
                data.append([pg,ag,gn])
        elif not(pg=="" and ag=="" and gn=="0"):
            rows.errors.pg = "Please fill proper details"
        i+=1
    if len(data)==0:
         rows.errors = "Please fill proper details"

@auth.requires_login()
def passengerform():
    i=1
    rows=[]
    while i<=6:
        rows.append(TR(TD(INPUT(_type="text",_name="pg-"+str(i))), TD(INPUT(_type="text",_name="ag-"+str(i), widget=SQLFORM.widgets.integer.widget )), TD(SELECT(OPTION('Select', _value="0"), OPTION('Male', _value="M"),OPTION('Female', _value="F"), _name="gn-"+str(i)))))
        i=i+1
    train = db(db.train_details.tno == session.train_num).select(db.train_details.name)
    source = db(db.station.id == session.source_id).select(db.station.name)
    dest = db(db.station.id == session.dest_id).select(db.station.name)
    details = TABLE(THEAD(TR(TH('TRAIN DETAILS', _class="panel-title"),TH()),_class="panel-heading"), TBODY(TR(TD('TRAIN NUMBER : '+str(session.train_num)),TD('TRAIN NAME : '+train[0].name)), TR(TD('SOURCE : '+str(source[0].name)),TD('DESTINATION : '+str(dest[0].name))),TR(TD('DATE OF JOURNEY : '+session.doj),TD('COACH :  '+session.coach))), _class="panel panel-info col-md-12 table-condensed")
    rows= FORM(TABLE(THEAD(TR(TH('PASSNGER NAME', _class="col-md-4 panel-title"), TH('AGE', _class="col-md-4 panel-title"), TH('GENDER', _class="col-md-4 panel-title")),_class="panel-heading"), TBODY(rows), _class="table-condensed table-bordered col-md-12 panel panel-info"),INPUT(_value='next',_type='submit', _class='btn btn-default') )
    if rows.process(onvalidation=checkpassengerdetails, keepvalues=True).accepted:
        session.passengers = data
        redirect(URL('default', 'selectbank'))
        session.flash=""
    elif rows.errors:
        session.flash=""
        response.flash="Please fill proper details"
    return dict(table=rows,details=details)

@auth.requires_login()
def validateSelection(form):
    if form.vars.banks=="":
        form.errors = "Please select a bank"

@auth.requires_login()
def selectbank():
    banks = db(db.bank.id>0).select()
    total_pass = len(session.passengers)
    per_ticket_cost = db(db.coach.train_num == session.train_num).select(db.coach.amount)
    per_ticket_cost = per_ticket_cost[0].amount
    total_amount=0
    i=0
    while i<total_pass:
        psngr = session.passengers[i]
        if int(psngr[1])<12:
            total_amount+=0.5*per_ticket_cost*float(session.dist)
        else:
            total_amount+=per_ticket_cost*float(session.dist)
        i+=1
    session.amount=total_amount
    all_banks=[]
    for b in banks:
        all_banks.append(TD(TD(INPUT(_type='radio', _name='banks', _value=b.name+' - '+b.card_type)+b.name+' - '+b.card_type+BR())))
    form=FORM(TABLE(all_banks, _class="table-condensed"), INPUT(_value='next',_type='submit', _class='btn btn-default' ))
    form1=DIV(LABEL('TOTAL FARE:'+str(total_amount)),form)
    if form.process(onvalidation=validateSelection, keepvalues=True).accepted:
        session.bank=form.vars.banks
        redirect(URL('default','bank'))
        session.flash=""
    elif form.errors:
        session.flash=""
        response.flash="Please select a bank"
    return dict(rows=form1)

def gettraindetails(pnr):
    ticket = db(db.ticket.id==pnr).select()
    train_details = db(db.train_details.tno == ticket[0].train_num).select()
    source = db(db.station.id == ticket[0].source_id).select(db.station.name)
    dest = db(db.station.id == ticket[0].dest_id).select(db.station.name)
    details = TABLE(THEAD(TR(TH('TRAIN DETAILS', _class="panel-title"),TH()),_class="panel-heading"), TBODY(TR(TD('TRAIN NUMBER : '+str(train_details[0].tno)),TD('TRAIN NAME : '+train_details[0].name)), TR(TD('SOURCE : '+str(source[0].name)),TD('DESTINATION : '+str(dest[0].name))),TR(TD('DATE OF JOURNEY : '+str(ticket[0].DOJ)),TD('COACH :  '+ticket[0].coach))), _class="panel panel-info col-md-12 table-condensed")
    return details

def getinfo(pnr):
    ticket = db(db.ticket.id==pnr).select()
    if len(ticket) == 0:
        details=DIV('INVALID PNR NUMBER', _class="col-md-12")
        table=""
        return dict(train_info=details, pass_list=table)
    details = gettraindetails(pnr)
    if ticket[0].coach == 'A1':
        passengers = db(db.A1.pnr_num == ticket[0].id).select()
    elif ticket[0].coach == 'B1':
        passengers = db(db.B1.pnr_num == ticket[0].id).select()
    elif ticket[0].coach == 'SL':
        passengers = db(db.SL.pnr_num == ticket[0].id).select()
    pass_list=[]
    i=1
    for p in passengers:
        seatno = p.seat_num if p.seat_num!=0 else "-"
        pass_list.append(TR(TD(i), TD(p.pass_name), TD(p.age), TD(p.gender),TD(seatno), TD(p.status)))
        i+=1
    table = FORM(TABLE(THEAD(TR(TH('SNO', _class="col-md-1 panel-title"), TH('PASSNGER NAME', _class="col-md-3 panel-title"), TH('AGE', _class="col-md-2 panel-title"), TH('GENDER', _class="col-md-2 panel-title"), TH('SEAT_NUM', _class="col-md-2 panel-title"), TH('STATUS', _class="col-md-2 panel-title")),_class="panel-heading"), TBODY(pass_list), _class="table-condensed table-bordered col-md-12 panel panel-info"))
    return dict(train_info=details, pass_list=table)

@auth.requires_login()
def bank():
    form=FORM(H2(session.bank),TABLE(TBODY(TR(TD('CARD NUMBER'), TD(INPUT(_type="text", _name="card-num", requires=IS_NOT_EMPTY()))),TR(TD('NAME ON CARD'), TD(INPUT(_type="text",_name="name-on-card",  requires=IS_NOT_EMPTY()))), TR(TD('VALID THROUGH'), TD(INPUT(_type="text",_name="valid_thru",  requires=IS_NOT_EMPTY()))), TR(TD('CVV'), TD(INPUT(_type="text",_name="cvv",  requires=IS_NOT_EMPTY()))), TR(TD(INPUT(_type="submit", _value="Make Payment")))), _class="table-condensed col-md-4"))
    if form.process().accepted:
        map = getavailableseats(session.train_num, session.train_id, session.doj, session.coach, session.source_id, session.dest_id)
        total_psngrs = len(session.passengers)
        coach=session.coach
        i = k = isWaiting = 0
        while i<total_psngrs and k<len(map):
            while k<len(map) and map[k]=='O':
                k+=1
            if k>=len(map):
                break
            psngr = session.passengers[i]
            psngr.append(k+1)
            psngr.append("CONFIRMED")
            session.passengers[i] = psngr
            k+=1
            i+=1
        while i<total_psngrs:
            isWaiting=1
            psngr = session.passengers[i]
            psngr.append(0)
            psngr.append("WAITING")
            session.passengers[i] = psngr
            i+=1
        stat = "WAITING" if isWaiting else "CONFIRMED"
        now = datetime.datetime.now()-timeshift
        id = db.ticket.insert(user_id=auth.user_id,
                 train_id = int(session.train_id),
                 train_num = int(session.train_num),
                 source_id = int(session.source_id),
                 dest_id = int(session.dest_id),
                 DOJ=session.doj,
                 DOB=datetime.datetime.today().date(),
                 amount = float(session.amount),
                 coach = session.coach,
                 total_pass=total_psngrs,
                 status=stat,
                 curr_time=now)
        if len(db(db.ticket.id == id).select()) !=0:
            if coach == 'A1':
                for p in session.passengers:
                    seatno=p[3]
                    db.A1.insert(seat_num=seatno,
                            pass_name=p[0],
                            age=p[1],
                            gender=p[2],
                            status=p[4],
                            pnr_num=id)
            elif coach == 'B1':
                 for p in session.passengers:
                    seatno=p[3]
                    db.B1.insert(seat_num=seatno,
                            pass_name=p[0],
                            age=p[1],
                            gender=p[2],
                            status=p[4],
                            pnr_num=id)
            else:
                for p in session.passengers:
                    seatno=p[3]
                    db.B1.insert(seat_num=seatno,
                            pass_name=p[0],
                            age=p[1],
                            gender=p[2],
                            status=p[4],
                            pnr_num=id)
            redirect(URL('default', 'pnrstatus', vars=dict(pnr=id)))
        else:
            session.flash = "Error occured"
            response.flash = ""
    return dict(form=form)

def pnrstatus():
    form = FORM(TABLE(TR(TD('PNR NUMBER'), INPUT(_type="text",id="pnr_num",_value=request.vars.pnr, _name="pnr_num", requires=IS_NOT_EMPTY())), TR(TD(INPUT(_type="submit"))), _class="col-md-4 table-condensed"))
    details={'train_info':'', 'pass_list':''}
    if request.vars.pnr:
        details = getinfo(request.vars.pnr)
    if form.process(keepvalues=True).accepted:
        details = getinfo(form.vars.pnr_num)
    response.flash=""
    return dict(form=form, train_info=details['train_info'], pass_list=details['pass_list'])

@auth.requires_login()
def history():
    tickets = db(db.ticket.user_id == auth.user_id).select()
    if len(tickets) == 0:
        table = DIV('NO HISTORY')
        return dict(table=table)
    all_tickets=[]
    i=1
    for t in tickets:
        all_tickets.append(TR(TD(i, _class="col-md-2"),TD(t.id, _class="col-md-2"), TD(A(t.id, _href=URL('default','pnrstatus', vars=dict(pnr=t.id))), _class="col-md-2"), TD(str(t.DOJ), _class="col-md-2"), TD(str(t.DOB), _class="col-md-2"), TD(t.status, _class="col-md-2")))
        i+=1
    table = FORM(TABLE(THEAD(TR(TH('SNO', _class="col-md-2 panel-title"), TH('BOOKING ID', _class="col-md-2 panel-title"), TH('PNR NUMBER ', _class="col-md-2 panel-title"), TH('DATE OF JOURNEY', _class="col-md-2 panel-title"), TH('DATE OF BOOKING', _class="col-md-2 panel-title"), TH('STATUS', _class="col-md-2 panel-title")),_class="panel-heading"), TBODY(all_tickets), _class="table-condensed table-bordered col-md-12 panel panel-info"))
    return dict(table=table)

def validatecancel(form):
    if not form.vars.cancel:
        form.errors="Please select ticket for cancellation"

@auth.requires_login()
def cancelticket():
    tickets = db(db.ticket.user_id == auth.user_id).select()
    if len(tickets) == 0:
        table = DIV('NO HISTORY')
        return dict(pnrlist=table)
    all_tickets=[]
    i=1
    for t in tickets:
        if t.DOJ<datetime.datetime.today().date():
            continue
        all_tickets.append(TR(TD(INPUT(_type='radio', _name='cancel', _value=t.id), _class="col-md-1"),TD(t.id, _class="col-md-2"), TD(A(t.id, _href=URL('default','pnrstatus', vars=dict(pnr=t.id))), _class="col-md-2"), TD(str(t.DOJ), _class="col-md-2"), TD(str(t.DOB), _class="col-md-2"), TD(t.status, _class="col-md-2")))
        i+=1
    if len(all_tickets)>0:
        form = FORM(TABLE(THEAD(TR(TH( _class="col-md-2 panel-title"), TH('BOOKING ID', _class="col-md-2 panel-title"), TH('PNR NUMBER ', _class="col-md-2 panel-title"), TH('DATE OF JOURNEY', _class="col-md-2 panel-title"), TH('DATE OF BOOKING', _class="col-md-2 panel-title"), TH('STATUS', _class="col-md-2 panel-title")),_class="panel-heading"), TBODY(all_tickets), _class="table-condensed table-bordered col-md-12 panel panel-info"), INPUT(_value='cancel ticket',_type='submit', _class='btn btn-default'))
    else:
        form=FORM('NO NEW TICKETS') #change message
    if form.process(onvalidation=validatecancel).accepted:
        redirect(URL('default', 'selectpassengers', vars=dict(ticketid=form.vars.cancel)))
    elif form.errors:
        response.flash="Please select ticket for cancellation"
    return dict(pnrlist=form)

def makelist(ticketid):
    ticket = db(db.ticket.id==ticketid).select()
    if ticket[0].coach == 'A1':
        passengers = db(db.A1.pnr_num == ticket[0].id).select()
    elif ticket[0].coach == 'B1':
        passengers = db(db.B1.pnr_num == ticket[0].id).select()
    elif ticket[0].coach == 'SL':
        passengers = db(db.SL.pnr_num == ticket[0].id).select()
    pass_list=[]
    isCancelled=True
    for p in passengers:
        if p.status == "WAITING":
            seatno = "-"
        else:
            seatno = p.seat_num
        if p.status == "CANCELLED":
            ip = ""
        else:
            isCancelled=False
            ip = INPUT(_type="checkbox", _value=p.id, _name="psngrlist")
        pass_list.append(TR(TD(ip, _class="col-md-1"), TD(p.pass_name, _class="col-md-3"), TD(p.age, _class="col-md-2"), TD(p.gender, _class="col-md-2"),TD(seatno, _class="col-md-2"), TD(p.status, _class="col-md-2")))
    ip = INPUT(_type="submit", _value="cancel") if isCancelled==False else ""
    cancellist = FORM(TABLE(THEAD(TR(TH(_class="col-md-1 panel-title"), TH('PASSENGER NAME', _class="col-md-3 panel-title"), TH('AGE', _class="col-md-2 panel-title"), TH('GENDER', _class="col-md-2 panel-title"), TH('SEAT_NUM', _class="col-md-2 panel-title"), TH('STATUS', _class="col-md-2 panel-title")),_class="panel-heading"), TBODY(pass_list), _class="table-condensed table-bordered col-md-12 panel panel-info"), ip)
    return cancellist

def validate(cancellist):
    if cancellist.vars.psngrlist == None:
        cancellist.errors="Please select passengers"

def cancelledlist():
    ticketid=request.vars.ticketid
    ticket = db(db.ticket.id==ticketid).select()
    trainid = ticket[0].train_id
    train_num = ticket[0].train_num
    DOJ = ticket[0].DOJ
    coach=ticket[0].coach
    cancellist = makelist(ticketid)
    if cancellist.process(onvalidation=validate).accepted:
        if type(cancellist.vars.psngrlist) == list:
            all_data = cancellist.vars.psngrlist
        elif type(cancellist.vars.psngrlist) == str:
            all_data = [cancellist.vars.psngrlist]
        for p in all_data:
            p = int(p)
            if ticket[0].coach == 'A1':
                db(db.A1.id == p).update(status="CANCELLED")
            elif ticket[0].coach == 'B1':
                db(db.B1.id == p).update(status="CANCELLED")
            elif ticket[0].coach == 'SL':
                db(db.SL.id == p).update(status="CANCELLED")
        if ticket[0].coach == 'A1':
            passengers = db(db.A1.pnr_num == ticket[0].id).select()
        elif ticket[0].coach == 'B1':
            passengers = db(db.B1.pnr_num == ticket[0].id).select()
        elif ticket[0].coach == 'SL':
            passengers = db(db.SL.pnr_num == ticket[0].id).select()
        passengers = [p for p in passengers if p.status!="CANCELLED"]
        if len(passengers)==0:
            db(db.ticket.id == ticketid).update(status="CANCELLED")
        waiting_list = db((db.ticket.train_num==train_num)&(db.ticket.DOJ == DOJ)&(db.ticket.coach == coach)&(db.ticket.status=="WAITING")).select(orderby=db.ticket.curr_time)
        occupied_list = db((db.ticket.train_num==train_num)&(db.ticket.DOJ == DOJ)&(db.ticket.coach == coach)&(db.ticket.status!="WAITING")).select(orderby=db.ticket.curr_time)
        tot_map = db((db.coach.train_num == train_num)).select(db.coach.total_seats)
        for w in waiting_list:
            map = ['F']*(tot_map[0].total_seats)
            if coach == 'A1':
                wait_pass = db((db.A1.pnr_num == w.id)&(db.A1.status == "WAITING")).select()
            elif coach == 'B1':
                wait_pass = db((db.B1.pnr_num == w.id)&(db.B1.status == "WAITING")).select()
            elif coach == 'SL':
                wait_pass = db((db.SL.pnr_num == w.id)&(db.SL.status == "WAITING")).select()
            i=0
            stops = db((db.route.train_id == w.train_id)&(db.route.train_num == w.train_num)).select()
            source_stop = [s for s in stops if s.station_id[0] == int(w.source_id)]
            source_stop = source_stop[0].stop_num
            dest_stop = [s for s in stops if s.station_id[0] == int(w.dest_id)]
            dest_stop = dest_stop[0].stop_num
            for o in occupied_list:
                stop1_details = [s for s in stops if s.station_id[0] == o.source_id]
                stop2_details = [s for s in stops if s.station_id[0] == o.dest_id]
                stop1 = stop1_details[0].stop_num
                stop2 = stop2_details[0].stop_num
                if (dest_stop<=stop1 or source_stop>=stop2):
                    pass
                if (source_stop<=stop1 and stop2>=dest_stop) or (stop1<source_stop and source_stop<stop2) or (stop1<dest_stop and dest_stop<stop2):
                    if coach == 'A1':
                        newcancellist = db((db.A1.pnr_num == o.id)).select()
                    elif coach == 'B1':
                        newcancellist = db((db.B1.pnr_num == o.id)).select()
                    elif coach == 'SL':
                        newcancellist = db((db.SL.pnr_num == o.id)).select()
                    for n in newcancellist:
                        if n.status == "CONFIRMED":
                            map[n.seat_num-1] = 'O'
                        elif n.status == "CANCELLED" and  n.is_alloted == False:
                            map[n.seat_num-1] = n.id
            for m in range(len(map)):
                if coach == 'A1':
                    if map[m] == 'F':
                        db(db.A1.id == wait_pass[i].id).update(seat_num = m, status="CONFIRMED")
                        i+=1
                    elif map[m]!='O':
                        num = db(db.A1.id == map[m]).select(db.A1.seat_num)
                        db(db.A1.id == wait_pass[i].id).update(seat_num = num[0].seat_num, status="CONFIRMED")
                        i+=1
                elif coach == 'B1':
                    if map[m] == 'F':
                        db(db.B1.id == wait_pass[i].id).update(seat_num = m, status="CONFIRMED")
                        i+=1
                    elif map[m]!='O':
                        num = db(db.B1.id == map[m]).select(db.B1.seat_num)
                        db(db.B1.id == wait_pass[i].id).update(seat_num = num[0].seat_num, status="CONFIRMED")
                        i+=1
                elif coach == 'SL':
                    if map[m] == 'F':
                        db(db.SL.id == wait_pass[i].id).update(seat_num = m, status="CONFIRMED")
                        i+=1
                    elif map[m]!='O':
                        num = db(db.B1.id == map[m]).select(db.SL.seat_num)
                        db(db.SL.id == wait_pass[i].id).update(seat_num = num[0].seat_num, status="CONFIRMED")
                        i+=1
                if i>=len(wait_pass):
                    wait = wait_pass[0].pnr_num[0]
                    if coach == 'A1':
                        all_pass = db(db.A1.pnr_num == wait).select()
                    elif coach == 'B1':
                        all_pass = db(db.B1.pnr_num == wait).select()
                    elif coach == 'SL':
                        all_pass = db(db.SL.pnr_num == wait).select()
                    all_pass = [a for a in all_pass if a.status=="CANCELLED"]
                    if len(all_pass)==0:
                        db(db.ticket.id == wait).update(status="CONFIRMED")
                    break
        cancellist = makelist(ticketid)
    elif cancellist.errors:
        response.flash=cancellist.errors
    return dict(cancellist=cancellist)

@auth.requires_login()
def selectpassengers():
    ticketid = request.vars.ticketid
    traindetails = gettraindetails(ticketid)
    return dict(traindetails=traindetails)
