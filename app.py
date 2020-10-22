from bs4 import BeautifulSoup
from flask import Flask, render_template, request
import html
import requests


NO_DATA_FOUND = "תאריך לא חוקי או שלא נמצאו נתונים לתאריך זה"
NO_HOLIDAY_FOUND = "אין חגים וארועים לתאריך זה"
NO_HOLIDAY_DATA = "לוח אירועים שנתי"

app = Flask(__name__)


@app.route('/')
def index_page():
    return render_template(
        'index.html',
    )


@app.route('/results')
def search_date():
    day = request.args.get('day')
    month = request.args.get('month')
    path = f'https://he.wikipedia.org/w/api.php?action=query&titles={day}_{month}&prop=extracts&intro&formatversion=2'
    resp = requests.get(path)
    soup = BeautifulSoup(resp.content, features="html.parser")
    extracted_data = str(soup.find_all("span", class_="s2")[-1])
    extracted_data_stripped = str(extracted_data).replace('<span class="s2">', "").replace('</span>', "")
    final = BeautifulSoup(html.unescape(extracted_data_stripped), features="html.parser")
    events_by_date = births_by_date = holidays_by_date = NO_DATA_FOUND  # default values
    if str(final) == '"missing"':
        return render_template(
            'results.html',
            day=day,
            month=month,
            events_by_date=events_by_date,
            births_by_date=births_by_date,
            holidays_by_date=holidays_by_date,
        )
    final_data = final.find_all("ul")
    events_by_date = str(final_data[0]).replace("\\n", "").replace('\\"', '"')
    if len(final_data) > 1:
        births_by_date = str(final_data[1]).replace("\\n", "").replace('\\"', '"')
    if len(final_data) > 2:
        holidays_by_date = str(final_data[3]).replace("\\n", "").replace('\\"', '"')
        if NO_HOLIDAY_DATA in holidays_by_date:
            holidays_by_date = NO_HOLIDAY_FOUND

    return render_template(
        'results.html',
        day=day,
        month=month,
        events_by_date=events_by_date,
        births_by_date=births_by_date,
        holidays_by_date=holidays_by_date,
    )
