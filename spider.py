# -*- coding = utf-8 -*-
# @Time : 2022/1/20 12:27 AM
# @Author : Jieying Dong (Jessie)
# @File : spider.py
# @Software: PyCharm

from bs4 import BeautifulSoup           # Analyze the website and gain data
import re             # Regular Expression, match words
import urllib.request, urllib.error       # Specify URL and gain the website
import xlwt           # Control Excel
import sqlite3        # Control database
import ssl

def main():
    baseurl = "https://movie.douban.com/top250?start="
    # 1. Gain the website
    datalist = getData(baseurl)
    # 2. Analyze data
    # 3. Store data
    #savepath = "doubanmovie250.xls"
    dbpath = "movie.db"
    #saveData(datalist, savepath)
    #askURL("https://movie.douban.com/top250?start=0")
    saveData2DB(datalist, dbpath)


# video link mode
findLink = re.compile(r'<a href="(.*?)">')      # Create regular expression object -- string mode
# image link mode
findImgSrc = re.compile(r'<img.*src="(.*?)"', re.S)    # re.S ignores newlines
# video name mode
findTitle = re.compile(r'<span class="title">(.*)</span>')
# rating mode
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
# rating people mode
findJudge = re.compile(r'<span>(\d*)人评价</span>')
# description mode
findIng = re.compile(r'<span class="inq">(.*)</span>')
# relate content mode
findBd = re.compile(r'<p class="">(.*?)</p>', re.S)

# Gain the website
def getData(baseurl):
    datalist = []
    for i in range(0, 10):
        url = baseurl + str(i*25)
        html = askURL(url)              # Store the website code
        # Analyze data
        soup = BeautifulSoup(html, "html.parser")
        for item in soup.find_all('div', class_="item"):     # find strings that match standards, then become lists
            # print(item)       # test: all contents in "item"
            data = []           # store all info of a film
            item = str(item)
            # get link about the details of the film
            link = re.findall(findLink, item)[0]       # re lib is used to find specific strings by regular expression
            #print(link)
            data.append(link)                          # add link

            imgSrc = re.findall(findImgSrc, item)[0]
            data.append(imgSrc)                          # add image

            titles = re.findall(findTitle, item)     # can have no english name
            if len(titles) == 2:
                ctitle = titles[0]
                data.append(ctitle)                  # add chinese name
                otitle = titles[1].replace("/", "")      # delete unrelated symbols
                data.append(otitle)                   # add english name
            else:
                data.append(titles[0])
                data.append(" ")                      # english name stays empty

            rating = re.findall(findRating, item)[0]
            data.append(rating)                        # add rating

            judgeNum = re.findall(findJudge, item)[0]
            data.append(judgeNum)                      # add rating people

            inq = re.findall(findIng, item)
            if len(inq) != 0:
                inq = inq[0].replace("。", "")
                data.append(inq)                           # add description
            else:
                data.append(" ")

            bd = re.findall(findBd, item)[0]
            bd = re.sub("<br(\s+)?/>(\s+)?", " ", bd)         # delete <br/>
            bd = re.sub("/", " ", bd)                         # delete /
            data.append(bd.strip())

            datalist.append(data)                             # put all info of one film to the list
    #print(datalist)
    return datalist

# Get a specific URL website
def askURL(url):
    ssl._create_default_https_context = ssl._create_unverified_context
    head = {      # Simulate the request header and send message to the douban server
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
    }      # Tell douban about the type of the web browser -- What kind of content levels that can receive
    req = urllib.request.Request(url=url, headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(req)
        html = response.read().decode("utf-8")
        # print(html)
    except urllib.error.URLError as e:   # e is a object/class
        if hasattr(e, "code"):           # Check whether e object has the code attribute
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    return html


# Save Data
def saveData(datalist, savepath):
    book = xlwt.Workbook(encoding="utf-8", style_compression=0)
    sheet = book.add_sheet("douban move top250", cell_overwrite_ok=True)
    col = ("Movie Link", "Image Link", "Movie Chinese Name", "Movie English Name", "Rating", "Rating Numbers", "Description", "Related Information")
    for i in range(8):
        sheet.write(0, i, col[i])    # column name
    for i in range(250):
        print("%d"%i)
        data = datalist[i]
        for j in range(8):
            sheet.write(i+1, j, data[j])


    book.save(savepath)


def saveData2DB(datalist, dbpath):
    print("...")
    init_db(dbpath)
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    for data in datalist:
        for index in range(len(data)):
            if index == 4 or index == 5:    # pay attention to integer
                continue
            data[index] = '"' + data[index] + '"'

        sql = '''
            insert into movie250(
                info_link, pic_link, cname, ename, score, rated, introduction, info
            )
            values(%s)'''%",".join(data)
        # print(sql)
        cur.execute(sql)
        conn.commit()
    cur.close()
    conn.close()

def init_db(dbpath):
    sql = '''
        create table movie250 
        (
        id integer primary key autoincrement,
        info_link text,
        pic_link text, 
        cname varchar,
        ename varchar,
        score numeric,
        rated numeric,
        introduction text,
        info text
        )
    '''     # Create worksheet
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()

if __name__=="__main__":        # When the function executes
    # Call function
    main()
    # init_db("moivetest.db")
    print("Complete Web Crawler")

