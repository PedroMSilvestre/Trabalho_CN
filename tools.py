from datetime import date, datetime
def currentDateAndHour():
    dateToday = date.today()
    y, m, d = dateToday.year, dateToday.month, dateToday.day
    sy = str(y)
    sm = ""
    sd = ""

    if (m < 10):
        sm = "0" + str(m)
    else:
        sm = str(m)

    if (d < 10):
        sd = "0" + str(d)
    else:
        sd = str(d)

    strYMD = "%s-%s-%s" % (sy, sm, sd)

    timeNow = datetime.now()
    hh, mm, ss = timeNow.hour, timeNow.minute, timeNow.second
    shh = ""
    smm = ""
    sss = ""
    if (hh < 10):
        shh = "0" + str(hh)
    else:
        shh = str(hh)

    if (mm < 10):
        smm = "0" + str(mm)
    else:
        smm = str(mm)

    if (ss < 10):
        sss = "0" + str(ss)
    else:
        sss = str(ss)

    strHMS = "%s:%s:%s" % (shh, smm, sss)

    strRet = "%s %s" % (strYMD, strHMS)

    return strRet
# def currentDateAndHour