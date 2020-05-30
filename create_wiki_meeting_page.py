# Seite anlegen einen Tag nach 1. 3. Freitag im Monat

from datetime import date, timedelta
import requests as req
import logging

# Logging
LOG_FILENAME = 'log_wiki_create.log'
FORMAT = "%(asctime)-15s %(message)s"
logging.basicConfig(filename=LOG_FILENAME,format=FORMAT,level=logging.INFO)

template_text = """
# Treffen DATE_PLACEHOLDER

**Termin:** 19:00 Uhr Start und Neulingsbegrüßung, 19:30 Uhr Eröffnung der Tagesordnung

**Ort:** Hackerspace Bremen e.V. ([Anfahrt](https://www.hackerspace-bremen.de/anfahrt/))

## Tagesordnung
### Neulingsbegrüßung (19:00 – 19:30 Uhr)

- Abfragen:
    - ist jemand neu?
    - hat jemand Fragen?
    - braucht jemand Hilfe?
- Einführung:
    - kurze Vorstellungsrunde
    - Funktionsweise der Freifunk Community
    - wie verschieden können die Beiträge/Funktionen eines Freifunker sein (TOP Aufgaben)
    - Ablauf des Treffens

---

### Top 1: Termine übertragen
- Ins letzte Protokoll gucken und Termine übertragen

### Top 2
...


### Termine
Müssen noch aus dem letzten Protokoll übernommen werden!

## Regelmäßige TOPs
### Aufgaben

- hat jemand Kapazität / möchte jemand helfen?
- ein paar Aufgaben von https://tasks.ffhb.de/ anbieten

### Rechte

- Zustand
- Zufriedenheit
- Änderungen?

### Treffen abschließen

- Info zu Treffen aktualisieren
  - Protokoll aus Pad ins Wiki kopieren
  - neue Wiki-Seite für nächstes Treffen mit Standard-TOPs anlegen
  - [Treffen auf Wiki-Homepage anpassen](https://wiki.bremen.freifunk.net/Home)
  - Topic im IRC anpassen
- Aufräumen!
  - Müll weg
  - Kabel zurück

## Protokoll

Live Kollaboration:

* Schreiblink: https://hackmd.io/AwDgnA7ATArKC0BGGBjAzPALAUzSeARgYgGzxQAmEFFwiKBEKAhkA===?edit
* Side-by-side: https://hackmd.io/AwDgnA7ATArKC0BGGBjAzPALAUzSeARgYgGzxQAmEFFwiKBEKAhkA===?both
* Leselink: https://hackmd.io/AwDgnA7ATArKC0BGGBjAzPALAUzSeARgYgGzxQAmEFFwiKBEKAhkA===?view

# Freifunk Bremen - Protokoll-Pad

### Anwesende
"""

def main():

    d = date.today()
    #d = date(2020, 6, 6) # debug
    
    host = 'https://wiki.bremen.freifunk.net'
    path = "/Treffen"
    #meeting_date = d.strftime("%Y_%m_%d")

    user = 'wellenfunk'
    passwd = 'foobar'
    
    if is_day_after_meeting(d) and meeting_page_is_not_yet_created(user, passwd, host, path, next_1st_and_3rd_friday(d)[0].strftime("%Y_%m_%d")):
        logging.info("Day after Meeting. Let's go!")
        next_two_meetings = next_1st_and_3rd_friday(d)
        logging.info("Next meetings: "+next_two_meetings[0].strftime("%Y_%m_%d")+" "+next_two_meetings[1].strftime("%Y_%m_%d"))
        print("Next meetings: "+next_two_meetings[0].strftime("%Y_%m_%d")+" "+next_two_meetings[1].strftime("%Y_%m_%d"))
        create_meeting_page(next_two_meetings[0], user, passwd, host, path, template_text)
    else:
        logging.info("Nothing done.")
        print("Nothing done.")

    
def is_day_after_meeting(d):

    # check if saturday after 1. or 3. friday
    
    is_saturday = True if (d.weekday() == 5) else False
    was_first_week = True if (d - timedelta(days=1)).day <= 7 else False
    was_third_week = True if (((d - timedelta(days=1)).day >= 15) and ((d - timedelta(days=1)).day < 22)) else False

    return True if (is_saturday and (was_first_week or was_third_week)) else False

def next_1st_and_3rd_friday(d):
    
    # Days until next friday
    days_until_friday = (4 - d.weekday()) % 7

    date_next_friday = d + timedelta(days=days_until_friday)

    next_month = ((d.month % 12) + 1)
    first_day_of_next_month = date(d.year, next_month, 1)
    days_until_friday = (4 - first_day_of_next_month.weekday()) % 7
    date_next_month_friday = first_day_of_next_month + timedelta(days= days_until_friday)


    # Cases for each week
    if (date_next_friday.day <= 7):
        return(date_next_friday, date_next_friday+timedelta(days=14))
    elif(date_next_friday.day > 7 and date_next_friday.day < 15):
        return(date_next_friday+timedelta(days=7), date_next_month_friday)
    elif(date_next_friday.day >= 15 and date_next_friday.day < 22):
        return(date_next_friday, date_next_month_friday)
    else:
        return(date_next_month_friday, date_next_month_friday+timedelta(days=14))
        
def test_print_fridays():
    try:
        for j in range(12):
            for i in range(28):
                d = date(2020, j+1, i+1) # debug
                print(i+1, j+1, next_first_friday(d))
    except ValueError:
        pass

def meeting_page_is_not_yet_created(user, passwd, host, path, page):

    url = host+"/create"+path+"/"+page

    resp_check = req.get(url, auth=(user, passwd))

    title = resp_check.text
    title = title[title.find('<title>') + 7 : title.find('</title>')]

    if title == "Create a new page":
        logging.info("Page not existing.")
        print("Page not existing.")
        return True
    else:
        logging.info("Page is existing. Good bye.")
        print("Page is existing. Good bye.")
        return False

def create_meeting_page(meeting_date, user, passwd, host, path, template_text):

    logging.info("Creating Page.")
    print("Creating Page.")
    demo_title = "aunicornflyingonablueswinginrocketcat"

    create_post_req = {"page":demo_title,
             "path": path,
             "format":"markdown",
             "content":template_text.replace("DATE_PLACEHOLDER", meeting_date.strftime("%d.%m.%Y")),
             "message":"Created+"+demo_title}

    resp_create = req.post(host+"/create", data = create_post_req, auth=(user, passwd))

    # Change Name (BUG: Its not possible to init a page with '_' in its name

    rename_post_req = {"rename":path+"/"+meeting_date.strftime("%Y_%m_%d"),
                         "message":"Renamed+"+demo_title+"+to+"+meeting_date.strftime("%Y_%m_%d")}

    resp_rename = req.post(host+"/rename"+path+"/"+demo_title, data = rename_post_req, auth=(user, passwd))

    logging.info("Page created. Have a nice day.")
    print("Page created. Have a nice day.")

if __name__ == "__main__":
    main()
