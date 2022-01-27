#_*_ coding: utf-8 _^_
#-*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from bs4 import BeautifulSoup
from urllib.request import urlopen
from werkzeug.utils import secure_filename
import urllib
# import pymysql
import json
import time, os
from socket import *
import threading
import sqlite3

global socket_data

def connect_db(db_info):
    database = pymysql.connect(
        host    = db_info[0],
        port    = int(db_info[1]),
        user    = db_info[2],
        passwd  = db_info[3],
        db      = db_info[4],
        charset = 'utf8'
    )
    return database

def connect_db_sqlite():
    database = sqlite3.connect("jandy.db", isolation_level=None, check_same_thread=False)
    return database

project_path = {os.getcwd()}

# db_info = []
# with open('db_info', 'r', encoding='utf8') as f:
#     for row in f.readlines():
#         db_info.append(row.strip())

# db = connect_db(db_info)
db = connect_db_sqlite()

today = time.localtime()

UPLOAD_FOLDER = f'{project_path}\\files'
UPLOAD_FOLDER_DB = f'{project_path}\\static\\user_img'

ALLOWED_EXTENSIONS = set(['zip','jpg','jpeg','gif','png', 'PNG', 'JPG', 'JPEG', 'GIF'])

app = Flask(__name__)
app.config.from_object('config')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER_DB'] = UPLOAD_FOLDER_DB

app.secret_key = app.config['SECRET_KEY']

def id_exist(user_id):
    if len(user_id) < 6 :
        return 0
    
    else:
        db = connect_db_sqlite()
        try:
            # with db.cursor() as cursor:
            #     id_result = 0
            #     cursor.execute(f'select EXISTS(select id from users where id="{user_id}") as success')
            #     id_result = cursor.fetchone()[0]
            cursor = db.cursor()
            id_result = 0
            cursor.execute(f'select EXISTS(select id from users where id="{user_id}") as success')
            id_result = cursor.fetchone()[0]
        finally:
            pass
            
        return id_result

def pw_chk(user_id, user_pw):
    # with db.cursor() as cursor:
    cursor = db.cursor()
    sql_qur = f'select pw from users where id="{user_id}"'
    cursor.execute(sql_qur)

    pw_list = cursor.fetchone()
    db_pw = pw_list[0]
    
    db.commit()

    if user_pw == db_pw:
        return 1
    else:
        return 0

def get_in_db(user_id, what):
    if len(user_id) < 6 :
        return 0
    
    else:
        db = connect_db_sqlite()
        db_result = None

        cursor = db.cursor()
        db_result = 0

        if what == "nickname":
            sql_qur = f"select nickname from users where id=\"{user_id}\""

        elif what == "password":
            sql_qur = f"select pw from users where id=\"{user_id}\""

        elif what == "name":
            sql_qur = f"select name from users where id=\"{user_id}\""

        elif what == "img":
            sql_qur = f"select img_name from users where id=\"{user_id}\""

        cursor.execute(sql_qur)
        db_result = cursor.fetchone()[0]

        db.commit()

        return db_result

@app.route("/", methods = ['POST', 'GET'])
def home_page ():
    id_result = 0

    if 'ss_user_id' not in session:
        session["ss_user_id"] = ""

    if request.method == 'POST': #로그아웃 버튼 눌렀을 때
        session['ss_user_id'] = ""
        return render_template("index.html", session_stat = session["ss_user_id"])
    
    if session["ss_user_id"] and len(session["ss_user_id"]) >= 6:
        id_result = id_exist(session["ss_user_id"])
    
    if id_result == 1:
        nickname = get_in_db(session["ss_user_id"], "nickname")
        img = get_in_db(session["ss_user_id"], "img")

        return render_template("index.html", session_stat = session["ss_user_id"], nickname=nickname, img=img)

    return render_template("index.html", session_stat = "0")


@app.route("/login", methods = ['GET','POST'])
def login_page():
    if request.method=='GET':
        return redirect('/')

    elif request.method == 'POST' :

        login_stat = 0

        user_id = request.form['user_id']
        user_pw = request.form['user_pw']

        id_result = id_exist(user_id)

        if id_result == 1:
            if pw_chk(user_id, user_pw):
                session['ss_user_id'] = user_id
                login_stat = 10
            else:
                login_stat = 5

        else:
            login_stat = 0

        if login_stat == 10:
            session['ss_user_id'] = user_id
            return redirect('/')
            #return render_template("index.html",session_stat=session['ss_user_id'],nickname=nickname)

        elif login_stat==5:
            return "<script> alert('비밀번호가 올바르지 않습니다.') </script>"+render_template('index.html')
            #return redirect("/")

        elif login_stat==0:
            return "<script> alert('존재하지 않는 아이디입니다.') </script>"+render_template('index.html')

    else :
        return "잘못된 접근"


@app.route("/idchk",methods=['POST'])
def idchk_page():

    if request.method == 'POST':
        input_id = request.form['input_id']

        if input_id == None:
            return render_template('regist.html')

        elif len(input_id) < 6: #글자수 적을때
            return json.dumps({'sql_result':'2'})

        sql_result = id_exist(input_id)

        if sql_result == 1: #이미 존재할 때
            return json.dumps({'sql_result':'1'})
            
        else: #정상
            return json.dumps({'sql_result':'0'})


@app.route("/regist",methods=['POST','GET'])
def regist_page():

    if request.method == 'POST':
        db = connect_db_sqlite()

        nick = request.form['nick']
        user_id = request.form['id']
        user_pw = request.form['pw']
        user_name = request.form['name']

        # with db.cursor() as cursor:
        #     sql_qur = 'INSERT INTO users (id,pw,nickname,name) VALUES (%s, PASSWORD("%s"), %s, %s)'
        #     cursor.execute(sql_qur, (user_id, user_pw, nick, user_name))

        #     db.commit()
        cursor = db.cursor()
        sql_qur = f'INSERT INTO users (id,pw,nickname,name) VALUES ("{user_id}", "{user_pw}", "{nick}", "{user_name}")'
        cursor.execute(sql_qur)

        db.commit()

        session['ss_user_id'] = user_id
        return "<script>alert('JANDY 회원가입이 완료되었습니다!');window.location.replace('/')</script>"+\
render_template('index.html',session_stat=user_id,nickname=nick,img = get_in_db(user_id,'img'))

    return render_template('regist.html')

@app.route("/account",methods=['GET','POST'])
def account():
    if 'ss_user_id' not in session:
        return redirect('/')
    if not id_exist(session['ss_user_id']):
        return redirect('/')

    if request.method=='POST':

        if 'pw' in request.form:
            user_id = session['ss_user_id']
            user_pw = request.form['pw']

            if pw_chk(user_id,user_pw):
                nick = get_in_db(user_id,'nickname')
                name = get_in_db(user_id,'name')
                img = get_in_db(user_id,'img')

                return render_template('account.html',user_ok='yes',user_id=user_id,nick=nick,name=name,img=img)
            else:
                return '<script>alert("비밀번호가 틀렸습니다.")</script>'+render_template('account.html',user_ok='no')

        elif 'ch_pw' in request.form:

            user_id = session['ss_user_id']
            pw = request.form['ch_pw']
            name = request.form['name']
            nick = request.form['nick']

            if 'file_sin_db' in request.files:
                img = request.files.getlist('file_sin_db')[0]

                if allowed_file(img.filename):

                    filename = secure_filename(img.filename)
                    img.save(os.path.join(app.config['UPLOAD_FOLDER_DB'], filename))
                else:
                    return render_template('account.html')+'<script>alert("올바르지 않은 파일 형식입니다.")</script>'
            else:
                filename = None

            cursor = db.cursor()
            sql_qur = 'update users set pw=PASSWORD("%s"), nickname=%s, name=%s, img_name=%s where id=%s'
            cursor.execute(sql_qur, (pw,nick,name,filename,user_id))

            db.commit()
            return redirect('/')

    return render_template('account.html',user_ok='no')


@app.route("/findid",methods=['GET','POST'])
def find_id():

    if request.method == 'POST':
        user_name = request.form['name']
        result_id = []

        cursor = db.cursor()
        sql_qur = 'select id from users where name=%s'
        result_count = cursor.execute(sql_qur, (user_name))

        result_all = cursor.fetchall()

        for i in range(result_count):
            result_id.append(result_all[i][0])

        for i in range(len(result_id)):
            temp = result_id[i]

            result_id[i] = temp[:1] + '***' + temp[4:]

        db.commit()

        return render_template('find_id.html', name_chk='yes',\
user_name = user_name, result_id=result_id, result_count = result_count)

    return render_template('find_id.html', name_chk='no')


@app.route("/findpw",methods=['GET','POST'])
def find_pw():

    if request.method == 'POST':
        if 'name' in request.form:
            user_name = request.form['name']

            if id_exist(user_name):
                return render_template('find_pw.html', name_chk='yes', user_name = user_name, id_result='')
            else:
                return render_template('find_pw.html', name_chk='no', id_result='no')

        if 'pw' in request.form:
            user_pw = request.form['pw']
            user_id = request.form['user_name']

            cursor = db.cursor()

            sql_qur = 'update users set pw = password("%s") where id=%s'
            cursor.execute(sql_qur, (user_pw, user_id))

            db.commit()

            return redirect("/")

    return render_template('find_pw.html', name_chk='no', id_result='')

@app.route("/weather")
def weather():
    city = ["내덕2동 ","오창 ","내수읍 "]
    weather_txt = city
    for i in range(3) :
        search = urllib.parse.quote(city[i] + '날씨')    #quote함수는 url에 한글로 검색요청을 할 때 사용
        url = 'https://search.naver.com/search.naver?ie=utf8&query='+ search
        html = urlopen(url)
        soup = BeautifulSoup(html, "html.parser")
        while True:
            if today.tm_wday == 0 :
                wday = '월'
                break
            if today.tm_wday == 1 :
                wday = '화'
                break
            if today.tm_wday == 2 :
                wday = '수'
                break
            if today.tm_wday == 3 :
                wday = '목'
                break
            if today.tm_wday == 4 :
                wday = '금'
                break
            if today.tm_wday == 5 :
                wday = '토'
                break
            if today.tm_wday == 6 :
                wday = '일'
                break
        weather_txt[i] = ('%s월 %s일 (%s) ' %(today.tm_mon, today.tm_mday, wday) + \
city[i] + soup.find('span', class_='todaytemp').text + '℃')
    return render_template('weather.html',weather_txt = weather_txt)

@app.route("/time_weather")
def weather2():
    def time_weather(city) :
        time_weather_txt = []
        for i in range(3) :
            search = urllib.parse.quote(city[i] + '날씨')
            url = 'https://search.naver.com/search.naver?ie=utf8&query='+ search
            html = urlopen(url)
            soup = BeautifulSoup(html, "html.parser")
            temp = list()
            for name in soup.find("ul", {"class":"list_area"}).find_all("dd", {"class":"weather_item _dotWrapper"}):
                name = name.text
                time_weather_txt.append(name)
        w_ochang = list(range(8))
        w_nesu = list(range(8))
        w_naedeok = list(range(8))
        j=0
        for i in range(8) :
            w_naedeok[j] = time_weather_txt[i]
            j+=1
        j=0
        for i in range(8,16) :
            w_ochang[j] = time_weather_txt[i]
            j+=1
        j=0
        for i in range(16,24) :
            w_nesu[j] = time_weather_txt[i]
            j+=1
        return (w_ochang, w_nesu, w_naedeok)

    def time_city(city) :
        j = 0
        time_city_txt = []
        search = urllib.parse.quote(city[1] + '+날씨')
        html = urlopen('https://search.naver.com/search.naver?ie=utf8&query='+ search)
        soup = BeautifulSoup(html, "html.parser")
        temp = list()
        for name in soup.find("ul", {"class":"list_area"}).findAll("dd", {"class":"item_time"}):
            if name.find(class_='tomorrow_icon'):
                name = name.text
                name = ["00시"]
                time_city_txt+=name
            else:
                name = name.text
                time_city_txt.append(name)

        return time_city_txt

    def time_weather_state(city) :
        time_weather_state_txt = []
        for i in range(3) :
            search = urllib.parse.quote(city[i] + '날씨')
            url = 'https://search.naver.com/search.naver?ie=utf8&query='+ search
            html = urlopen(url)
            soup = BeautifulSoup(html, "html.parser")
            temp = list()
            for name in soup.find("ul", {"class":"list_area"}).find_all("dd", {"class":"item_condition"}):
                name = name.text
                time_weather_state_txt.append(name)
        w_ochang_state = list(range(8))
        w_nesu_state = list(range(8))
        w_naedeok_state = list(range(8))
        j=0
        for i in range(8) :
            w_naedeok_state[j] = time_weather_state_txt[i]
            j+=1
        j=0
        for i in range(8,16) :
            w_ochang_state[j] = time_weather_state_txt[i]
            j+=1
        j=0
        for i in range(16,24) :
            w_nesu_state[j] = time_weather_state_txt[i]
            j+=1
        return (w_ochang_state, w_nesu_state, w_naedeok_state)

    city_txt = ["내덕2동 ","오창 ","내수읍 "]
    (w_ochang, w_nesu, w_naedeok) = time_weather(city_txt)
    time_city_txt = time_city(city_txt)
    (w_ochang_state, w_nesu_state, w_naedeok_state) = time_weather_state(city_txt)

    return render_template('time_weather.html',time_city_txt = \
time_city_txt, w_naedeok = w_naedeok, w_ochang = \
w_ochang, w_nesu = w_nesu, w_naedeok_state = w_naedeok_state, w_nesu_state = \
w_nesu_state, w_ochang_state = w_ochang_state)

@app.route("/news")
def news():
    def ytn_news() :
        ytn_news_txt = []
        ytn_news_txt_url = []
        url = 'https://www.ytn.co.kr/news/news_quick.html'
        html = urlopen(url)
        soup = BeautifulSoup(html, "html.parser")
        for name in soup.find("div", {"id":"area_popnews"}).find_all("li", {"":""}):
            name = name.text
            ytn_news_txt.append(name)
        for name in soup.find("div", {"id":"area_popnews"}).find_all("a", {"":""}):
            name = name.get("href")
            ytn_news_txt_url.append(name)
        return ytn_news_txt, ytn_news_txt_url
    def time_news() :
        time_news_txt = []
        url = 'https://www.daum.net/'
        html = urlopen(url)
        soup = BeautifulSoup(html, "html.parser")
        for name in soup.find("ol", {"class":"list_hotissue issue_row"}).find_all("a", {"tabindex":"-1"}):
            name = name.text
            time_news_txt.append(name)
        return time_news_txt

    time_news_txt = time_news()
    ytn_news_txt, ytn_news_txt_url = ytn_news()
    return render_template('news.html', time_news_txt = time_news_txt, ytn_news_txt = ytn_news_txt, ytn_news_txt_url = ytn_news_txt_url)

@app.route("/english")
def english():
    def today_english() :
        today_english_txt = []
        url = 'https://endic.naver.com/?sLn=kr'
        html = urlopen(url)
        soup = BeautifulSoup(html, "html.parser")
        for name in soup.find("ul", {"class":"component_today_word"}).find_all("a", {"class":"word_link"}):
            name = name.text
            today_english_txt.append(name)
        return today_english_txt

    def today_english_mean() :
        today_english_mean_txt = []
        url = 'https://endic.naver.com/?sLn=kr'
        html = urlopen(url)
        soup = BeautifulSoup(html, "html.parser")
        for name in soup.find("ul", {"class":"component_today_word"}).find_all("div", {"class":"txt_trans"}):
            name = name.text
            today_english_mean_txt.append(name)
        return today_english_mean_txt

    today_english_txt = today_english()
    today_english_mean_txt = today_english_mean()

    return render_template('english.html', today_english_txt = \
today_english_txt, today_english_mean_txt = today_english_mean_txt)


@app.route("/logout")
def logout():
    session.pop('ss_user_id')
    return redirect(url_for("home_page"))


def allowed_file(filename):
    if '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS:
        return True

    else:
        return False

@app.route("/upload", methods=["GET","POST"])
def upload():
    if request.method=="POST":

        file_path = "local"

        if request.files.getlist("file_sin"):
            files = request.files.getlist("file_sin")

        elif request.files.getlist("file_mul"):
            files = request.files.getlist("file_mul")

        elif request.files.getlist("file_sin_db"):
            files = request.files.getlist("file_sin_db")
            file_path = "db"

        for i in range(0,len(files)):
            if allowed_file(files[i].filename):
                filename = secure_filename(files[i].filename)

                if file_path == "local":
                    files[i].save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                elif file_path == "db":
                    files[i].save(os.path.join(app.config['UPLOAD_FOLDER_DB'], filename))

                    cursor = db.cursor()
                    sql_qur = 'update users set img_name=%s, img_url=%s where id="123456"'
                    cursor.execute(sql_qur, (filename,"temp"))
                    db.commit()

                return render_template("file_upload.html") + \
"<script>alert('파일이 성공적으로 업로드되었습니다.')</script>"
            else:
                return render_template("file_upload.html") + \
"<script>alert('업로드 할 수 없는 확장자가 있습니다.')</script>"

    return render_template("file_upload.html")


@app.route("/cafe",methods=['GET','POST'])
def cafe_page():
    if 'ss_user_id' not in session:
        return redirect(url_for('home_page'))

    elif not(id_exist(session['ss_user_id'])):
        return redirect(url_for('home_page'))

    if request.method=="GET":
        db = connect_db_sqlite()
        pass

    if request.method=="POST":
        db = connect_db_sqlite()
        post_list = []

        cursor = db.cursor()
        cursor.execute('select max(idx) from post')
        last = cursor.fetchall()[0][0]
        last = last+1 if last else 1


        if 'last' in request.form: #글 불러온거
            if request.form['last'] != 0:
                last = request.form['last']

                if last == "-1":
                    cursor = db.cursor()
                    cursor.execute('select max(idx) from post')
                    last = cursor.fetchall()[0][0]
                    last = last+1 if last else 1

        if 'title' in request.form: # 글 작성
            if 'title' != '':
                title = request.form['title']
                contain = request.form['contain']
                user_id = session['ss_user_id']
                #user_nick = get_in_db(session['ss_user_id'],'nickname')
                #time = datetime.now().strftime("%Y년 %m월 %d일 %H:%M:%S".encode('unicode-escape').decode()).encode().decode('unicode-escape')

                cursor = db.cursor()
                sql_qur = f'INSERT INTO post (title,contain,id,time) values ("{title}", "{contain}", "{user_id}", DATETIME(\'now\',\'localtime\'))'
                cursor.execute(sql_qur)
                db.commit()
            return redirect('/cafe')

        if 'give_heart_user' in request.form:# 하트, 댓글 개수 전송
            post_idx = int(request.form['give_heart_user'])
            
            cursor = db.cursor()
            cursor.execute(f'SELECT heart FROM post WHERE idx={post_idx}')
            heart_user_list = cursor.fetchone()[0]
            heart_list = []

            if heart_user_list != None:
                heart_list = heart_user_list.split(",")
                
            return jsonify(heart_list = heart_list)

        if 'heart' in request.form: # 하트 누른거
            if request.form['heart'] != None:
                heart_list = request.form['heart'].split(",")

                cursor = db.cursor()
                post_idx = int(heart_list[1])

                cursor.execute(f'SELECT heart FROM post WHERE idx={post_idx}')
                heart_user_list = cursor.fetchone()[0]
                if heart_user_list == None: heart_user_list=[]
                else: heart_user_list = heart_user_list.split(",")
                
                if heart_list[0] == "off":
                    heart_user_list.remove(session['ss_user_id'])
                    
                    if heart_user_list == []: cursor.execute('update post set heart=NULL where idx=%d'%(post_idx))
                    else:
                        heart_user_str = ','.join(heart_user_list)
                        cursor.execute('update post set heart="%s" where idx=%d'%(heart_user_str, post_idx))
                elif heart_list[0] == "on":
                    heart_user_list.append(session['ss_user_id'])
                    
                    heart_user_str = ','.join(heart_user_list)
                    cursor.execute('update post set heart="%s" where idx=%d'%(heart_user_str,post_idx))

                heart_list = heart_user_list
                db.commit()
        
        if 'comment' in request.form: # 댓글 작성
            if 'comment' != '':
                contain = request.form['comment']
                post_idx = request.form['post_idx']
                
                user_id = session['ss_user_id']
                user_nick = get_in_db(session['ss_user_id'], 'nickname')
                
                cursor = db.cursor()
                sql_qur = f'INSERT INTO comment (id, contain, time) values ("{user_id}", "{contain}", DATETIME(\'now\',\'localtime\'))'
                cursor.execute(sql_qur)
                
                cursor.execute('select last_insert_rowid()')
                comments_idx = cursor.fetchone()[0]
                
                cursor.execute(f'select comment from post where idx={post_idx}')
                origin_idx = cursor.fetchone()[0]
                print(f"origin_idx : {origin_idx}")
                if origin_idx != None:
                    comments_idx = str(origin_idx) + "," + str(comments_idx)
                print(f"comments_idx : {comments_idx}")
                cursor.execute(f'update post set comment="{comments_idx}" where idx={post_idx}')
                db.commit()
                return jsonify(new_comment = comments_idx)

        if 're_comment' in request.form: # 답글 작성
            if 're_comment' != '':
                contain = request.form['re_comment']
                cmt_idx = request.form['cmt_idx']
                
                user_id = session['ss_user_id']
                user_nick = get_in_db(session['ss_user_id'], 'nickname')
                
                cursor = db.cursor()
                sql_qur = f'INSERT INTO comment (id, contain, time)\
                            VALUES (\
                                "{user_id}",\
                                "{contain}",\
                                DATETIME(\'now\',\'localtime\')\
                            )'
                cursor.execute(sql_qur)
                
                cursor.execute('select last_insert_rowid()')
                comments_idx = cursor.fetchone()[0]
                
                cursor.execute('select comment from comment where idx=%s'%(cmt_idx))
                origin_idx = cursor.fetchone()[0]
                
                if origin_idx != None:
                    comments_idx = str(origin_idx) + "," + str(comments_idx)
                
                cursor.execute(f'update comment set comment="{comments_idx}" where idx={cmt_idx}')
                db.commit()
                return jsonify(new_comment = comments_idx)

        if 'idx_list_delete' in request.form: # 댓글 삭제
            if 're_comment' != '':
                idx_list = request.form['idx_list_delete'].split(",")
                self_idx = idx_list[0]
                parent_idx = idx_list[1]
                post_idx = idx_list[2]
                
                user_id = session['ss_user_id']
                user_nick = get_in_db(session['ss_user_id'], 'nickname')
                
                cursor = db.cursor()
                cursor.execute('select comment from comment where idx=%s'%(self_idx))
                children_idx = cursor.fetchone()[0]
                
                #이 부분은 댓글 자체를 DB에서 지우는 부분
                if children_idx != None: #자신에게 답글이 달려있는 경우
                    cursor.execute('select comment from comment where idx=%s'%(self_idx))
                    children_idx = cursor.fetchone()[0].split(",")

                    for rec in children_idx:
                        cursor.execute('delete from comment where idx=%s'%(rec))

                cursor.execute('delete from comment where idx=%s'%(self_idx))


                #이 부분은 게시글에서 댓글 목록 수정하는부분
                if parent_idx != "None": #답글인 경우
                    cursor.execute('select comment from comment where idx=%s'%(parent_idx))
                    children_idx = cursor.fetchone()[0].split(",")
                    children_idx.remove(self_idx)
                    children_idx = ",".join(children_idx)
                    if children_idx == '':
                        cursor.execute('update comment set comment=NULL where idx=%s'%(parent_idx))
                    else:
                        cursor.execute('update comment set comment="%s" where idx=%s'%(children_idx, parent_idx))

                elif parent_idx == "None": #댓글인 경우
                    cursor.execute('select comment from post where idx=%s'%(post_idx))
                    children_idx = cursor.fetchone()[0].split(",")
                    children_idx.remove(self_idx)
                    children_idx = ",".join(children_idx)
                    if children_idx == '':
                        cursor.execute('update post set comment=NULL where idx=%s'%(post_idx))
                    else:
                        cursor.execute('update post set comment="%s" where idx=%s'%(children_idx, post_idx))
                
                db.commit()
                
                return jsonify(None)

        if 'idx_list_modi' in request.form: # 댓글 수정
            if 're_comment' != '':
                idx_list = request.form['idx_list_modi'].split(",")
                self_idx = idx_list[0]
                parent_idx = idx_list[1]
                post_idx = idx_list[2]
                
                user_id = session['ss_user_id']
                user_nick = get_in_db(session['ss_user_id'], 'nickname')
                '''
                with db.cursor() as cursor:
                    
                    cursor.execute('select comment from comment where idx=%s'%(self_idx))
                    children_idx = cursor.fetchone()[0]
                    
                    #이 부분은 댓글 자체를 DB에서 지우는 부분
                    if children_idx != None: #자신에게 답글이 달려있는 경우
                        cursor.execute('select comment from comment where idx=%s'%(self_idx))
                        children_idx = cursor.fetchone()[0].split(",")

                        for rec in children_idx:
                            cursor.execute('delete from comment where idx=%s'%(rec))

                    cursor.execute('delete from comment where idx=%s'%(self_idx))


                    #이 부분은 게시글에서 댓글 목록 수정하는부분
                    if parent_idx != "None": #답글인 경우
                        cursor.execute('select comment from comment where idx=%s'%(parent_idx))
                        children_idx = cursor.fetchone()[0].split(",")
                        children_idx.remove(self_idx)
                        children_idx = ",".join(children_idx)
                        if children_idx == '':
                            cursor.execute('update comment set comment=NULL where idx=%s'%(parent_idx))
                        else:
                            cursor.execute('update comment set comment="%s" where idx=%s'%(children_idx, parent_idx))

                    elif parent_idx == "None": #댓글인 경우
                        cursor.execute('select comment from post where idx=%s'%(post_idx))
                        children_idx = cursor.fetchone()[0].split(",")
                        children_idx.remove(self_idx)
                        children_idx = ",".join(children_idx)
                        if children_idx == '':
                            cursor.execute('update post set comment=NULL where idx=%s'%(post_idx))
                        else:
                            cursor.execute('update post set comment="%s" where idx=%s'%(children_idx, post_idx))
                    
                    db.commit()
                '''
                return jsonify(None)

        if 'get_comment' in request.form: #댓글 목록 가져오기
            if request.form['get_comment'].isdigit():
                post_idx = int(request.form['get_comment'])
            else:
                return jsonify(comment_list = None)
            
            cursor = db.cursor()
            cursor.execute(f'select comment from post where idx={post_idx}')
            comment_idx = cursor.fetchone()
            comment_idx = comment_idx[0]
            comment_list = []
            
            if comment_idx is not None:
                comment_idx = comment_idx.split(",")
                for i in comment_idx:
                    cursor.execute(f'select c.*, u.nickname, u.img_name from comment c join users u on c.id=u.id where idx={i}')
                    comment = cursor.fetchone()
                    comment = list( comment )
                    c = comment[2]
                    
                    d = c.split(" ")[0].split("-")
                    t = c.split(" ")[1].split(":")
                    comment[2] = f"{d[0]}년 {d[1]}월 {d[2]}일 {t[0]}:{t[1]}:{t[2]}"
                    # comment[2] = str(c.year) + "년 " + str(c.month) + "월 " + str(c.day)\
                    # + "일 " + str(c.hour) + ":" + str("%02d"%c.minute)#+ ":" + str("%02d"%c.second)
                    comment_list.append(list(comment))
                
            return jsonify(json.dumps({"comment_list":comment_list}))
            
        if 'get_re_comment' in request.form: #답글 목록 가져오기
            if request.form['get_re_comment'].isdigit():
                cmt_idx = int(request.form['get_re_comment'])
            else:
                return jsonify(comment_list = None)
            
            cursor = db.cursor()
            cursor.execute(f'select comment from comment where idx={cmt_idx}')
            comment_idx = cursor.fetchone()[0]
            re_comment_list = []
            
            if comment_idx is not None:
                comment_idx = comment_idx.split(",")
                for i in comment_idx:
                    #cursor.execute('select * from comment where idx=%s'%(i))
                    cursor.execute('select c.*, u.nickname, u.img_name from comment c join users u on c.id=u.id where idx=%s'%(i))
                    comment = list(cursor.fetchone())
                    c = comment[2]
                    
                    d = c.split(" ")[0].split("-")
                    t = c.split(" ")[1].split(":")
                    comment[2] = f"{d[0]}년 {d[1]}월 {d[2]}일 {t[0]}:{t[1]}:{t[2]}"
                    # comment[2] = str(c.year) + "년 " + str(c.month) + "월 " + str(c.day)\
                    # + "일 " + str(c.hour) + ":" + str("%02d"%c.minute)#+ ":" + str("%02d"%c.second)
                    re_comment_list.append(list(comment))
                
            return jsonify(json.dumps({"re_comment_list":re_comment_list}))
            
        else:#게시글 목록 가져오기
            if post_list == []:
                cursor = db.cursor()
                cursor.execute(f'select p.*, u.nickname, u.img_name from post p join users u \
                on p.id=u.id where p.idx < {last} order by p.idx desc limit 10')
                temp_list = cursor.fetchall()

                for t in temp_list:
                    post_list.append(list(t))

                if post_list == None:
                    return jsonify(post = '0')

            print(f"post_list : {post_list}")
            for i in range(len(post_list)):
                d = post_list[i][3].split(" ")[0].split("-")
                t = post_list[i][3].split(" ")[1].split(":")
                post_list[i][3] = f"{d[0]}년 {d[1]}월 {d[2]}일 {t[0]}:{t[1]}:{t[2]}"
                

            return jsonify(post = post_list, last = last)

    user_nick = get_in_db(session['ss_user_id'],'nickname')
    user_img = get_in_db(session['ss_user_id'],'img')
    if user_img == None: user_img="null"

    return render_template('cafe.html', user_nick=user_nick, user_img=user_img\
, user_id=session['ss_user_id'])

@app.route("/cube",methods=['GET'])
def cube_page():
    pass

    return render_template('cube.html')
    
def thread1() :
    global socket_data
    socket_data = ['', '', '', '', '', '', '', '', '','']
    
    port = 1234

    serverSock = socket(AF_INET, SOCK_STREAM)
    serverSock.bind(('', port))
    serverSock.listen(1)

    while True :
        print('%d번 포트로 접속 대기중...'%port)

        connectionSock, addr = serverSock.accept()

        print(str(addr), 'connection.')

        recvData = connectionSock.recv(1024)
        data = recvData.decode('utf-8')

        print("gdgd\n\n\n{0}\n\n\n".format(data))

        if data == "passwd_c" :
            #socket_data[0] = "현재비밀번호 바꿀비밀번호 현재포트"
            connectionSock.send(socket_data[0].encode('utf-8'))

        elif data == "port_c" :
            #socket_data[1] = "현재 포트,바꿀 포트"
            connectionSock.send(socket_data[1].encode('utf-8'))

        elif data == "policy_c" :
            #socket_data[2] = "현재비밀번호,,현재포트,,옵션 ex)0 1 2 3 4 5,,값 ex)off 30 5 5 low 5"
            connectionSock.send(socket_data[2].encode('utf-8'))

        elif data == "get_info" :
            recvData = connectionSock.recv(1024)
            socket_data[3] = recvData.decode('utf-8')

        elif data == "passwd_check" :
            #socket_data[4] = "체크할 비밀번호"
            connectionSock.send(socket_data[4].encode('utf-8'))

            recvData = connectionSock.recv(1024)
            socket_data[5] = recvData.decode('utf-8')

        elif data == "policy_output" :
            #socket_data[6] = "현재비밀번호 현재포트"
            connectionSock.send(socket_data[6].encode('utf-8'))

            recvData = connectionSock.recv(1024)
            socket_data[7] = recvData.decode('utf-8')
                           
        elif data == "install" :
            #socket_data[8] = "설치 버전 ex) 5.7 or 8.0"
            connectionSock.send(socket_data[8].encode('utf-8'))

            recvData = connectionSock.recv(1024)
            socket_data[9] = recvData.decode('utf-8')

        elif data == "quit" :
            return
                         
        else :
            pass
            
            
@app.route("/install",methods=['GET', 'POST'])
def install_page():
    #global socket_data
    if request.method == 'GET':
        #session.clear()
    
        print("\n\n\n\n\n\n")
        for i in session:
            print(i, " : ", session[i])
        print("\n\n\n\n\n\n")
    
        if 'ssh_id' in session and session['ssh_id'] != None: #로그인 상태일 때
            
            ssh_ip = session['ssh_ip']
            ssh_id = session['ssh_id']
            ssh_pw = session['ssh_pw']
            ssh_port = session['ssh_port']
            path = "./"
            
            result = os.system("plink %s@%s -pw %s -P %s -batch test"%(ssh_id, ssh_ip, ssh_pw, ssh_port))
            '''
            with open('return.output', 'r', newline='', encoding="utf8") as f:
                result = f.read().split(" ")
                #result = result
                    
            os.system("del return.output")
            '''

            if result == 1:
            #if result[1] != "granted.":
                login_stat = 10
                #thr = threading.Thread (target = thread1, args = ())
                #thr.start ()
                
                #command1 = "python client.py quit"
                #os.system("plink %s -l %s -pw %s -P %s -batch %s"%(ssh_ip, ssh_id, ssh_pw, ssh_port, command1))

                target = "./install_page/client.py"
                os.system("pscp -pw %s -P %s %s %s@%s:%s"%(ssh_pw, ssh_port, target, ssh_id, ssh_ip, path))

                thr = threading.Thread (target = thread1, args = ())
                thr.start ()
                
                command = "python client.py get_info"
                
                os.system("plink %s -l %s -pw %s -P %s -batch %s"%(ssh_ip, ssh_id, ssh_pw, ssh_port, command))
                
                mysql_info = socket_data[3].split("\n")
                pw_policy = socket_data[6].split("\n")
                
                session['mysql_first_pw'] = mysql_info[0]
                session['mysql_ver'] = mysql_info[1]
                session['mysql_port'] = mysql_info[2].split("/")[0]
                session['mysql_active_chk'] = mysql_info[3]
                
                return render_template('install.html', login_stat = login_stat, ssh_id=ssh_id, ssh_port=ssh_port, ssh_ip=ssh_ip,\
mysql_port = session['mysql_port'], mysql_ver = session['mysql_ver'], mysql_first_pw = session['mysql_first_pw'], \
mysql_active_chk = session['mysql_active_chk'])
            

    if request.method == 'POST': #로그아웃 버튼 눌렀을 때
        session['ssh_id'] = None
        return redirect("/install")
    
    return render_template("install.html", login_stat = "0")

@app.route("/install_login", methods=['GET', 'POST'])
def install_login():
    global socket_data
    
    if request.method=='GET':
        return redirect('/install')

    elif request.method == 'POST' :
        if 'ssh_id' in request.form:
            path = "./"
            ssh_ip = request.form['ssh_ip']
            ssh_id = request.form['ssh_id']
            ssh_pw = request.form['ssh_pw']
            ssh_port = request.form['ssh_port']

            result = 0

            if len(ssh_ip.split(".")) != 4:
                return "<script>alert('올바르지 않은 IP입니다.');"\
+"window.location.replace('/install')</script>"+render_template('install.html')

            if ssh_port.isdigit() and int(ssh_port)>0 and int(ssh_port)<65536:
                #result = os.system("plink %s@%s -pw %s -P %s -batch test"%(ssh_id, ssh_ip, ssh_pw, ssh_port))
                result = os.system("plink %s@%s -pw %s -P %s -batch pwd > return.output"%(ssh_id, ssh_ip, ssh_pw, ssh_port))
                
                with open('return.output', 'r', newline='', encoding="utf8") as f:
                    result = f.read()
                        
                os.system("del return.output")
                
            login_stat = 0

            #if result == 1:
            if result != "":
                login_stat = 10
                
                #thr = threading.Thread (target = thread1, args = ())
                #thr.start ()
                
            else:
                login_stat = 0

            if login_stat == 10: #로그인 성공
                session['ssh_id'] = ssh_id
                session['ssh_pw'] = ssh_pw
                session['ssh_ip'] = ssh_ip
                session['ssh_port'] = ssh_port
                return redirect("/install")
                '''
                return "<script>window.location.replace('/install')</script>" + render_template('install.html', login_stat=login_stat, ssh_id=ssh_id, ssh_port=ssh_port,\
                ssh_ip=ssh_ip, mysql_port = session['mysql_port'], mysql_ver = session['mysql_ver'],\
                mysql_first_pw = session['mysql_first_pw'], mysql_active_chk = session['mysql_active_chk'])
                '''
            elif login_stat == 0:
                return "<script>alert('입력이 올바르지 않거나, 서버에 접속할 수 없습니다.');"\
+"window.location.replace('/install')</script>" + render_template('install.html')

        if "mysql_install" in request.form: #mysql 설치 기능
            ver = request.form['mysql_install']
            if 'ssh_id' in session:
                ssh_id = session['ssh_id']
                ssh_pw = session['ssh_pw']
                ssh_ip = session['ssh_ip']
                ssh_port = session['ssh_port']
                command2 = "python client.py install"
                
                socket_data[8] = ver
                
                os.system("plink %s -l %s -pw %s -P %s -batch %s"%(ssh_ip, ssh_id, ssh_pw, ssh_port, command2))
                
                mysql_install_output = socket_data[9].replace("\n", "")
            
            return jsonify(mysql_install_output = mysql_install_output)
    
        if "is_pw_correct" in request.form: #mysql 비밀번호 맞는지 확인
            now_pw = request.form['is_pw_correct']
            command = "python client.py passwd_check"
            
            if 'ssh_id' in session:
                ssh_id = session['ssh_id']
                ssh_pw = session['ssh_pw']
                ssh_ip = session['ssh_ip']
                ssh_port = session['ssh_port']
                
                socket_data[4] = now_pw
                os.system("plink %s -l %s -pw %s -P %s -batch %s"%(ssh_ip, ssh_id, ssh_pw, ssh_port, command))
                pw_correct = socket_data[5].replace("\n", "")
                
            return jsonify(pw_correct = pw_correct)
    
        if "get_policy" in request.form: #mysql 비밀번호 정책 가져오기
            mysql_port = session['mysql_port']
            now_pw = request.form['get_policy']
            
            socket_data[6] = now_pw + " " + mysql_port
            command = "python client.py policy_output"
            
            if 'ssh_id' in session:
                ssh_id = session['ssh_id']
                ssh_pw = session['ssh_pw']
                ssh_ip = session['ssh_ip']
                ssh_port = session['ssh_port']
                
                os.system("plink %s -l %s -pw %s -P %s -batch %s"%(ssh_ip, ssh_id, ssh_pw, ssh_port, command))
                pw_policy = socket_data[7]
                
            return jsonify(pw_policy = pw_policy)
    
        if "db_new_pw" in request.form: #비밀번호 바꿨을 때
            db_now_pw = request.form['db_now_pw']
            db_new_pw = request.form['db_new_pw']

            socket_data[0] = db_now_pw + " " + db_new_pw + " " + session['mysql_port']
            print(socket_data[0])
            command = "python client.py pw_change"
                    
            if 'ssh_id' in session:
                ssh_id = session['ssh_id']
                ssh_pw = session['ssh_pw']
                ssh_ip = session['ssh_ip']
                ssh_port = session['ssh_port']
                
                os.system("plink %s -l %s -pw %s -P %s -batch %s"%(ssh_ip, ssh_id, ssh_pw, ssh_port, command))
            return redirect("/install")
    
        if "pw_length" in request.form: #비밀번호 정책 변경
            db_policy_pw = request.form['db_policy_pw']
            
            if "check_name" in request.form:
                check_name = request.form['check_name']
            else: check_name = ""
            
            if "policy" in request.form:
                policy = request.form['policy']
            else: policy = ""
            
            pw_length = request.form['pw_length']
            case_count = request.form['case_count']
            num_count = request.form['num_count']
            special_count = request.form['special_count']
            
            policy_list = [check_name, pw_length, case_count, num_count, policy, special_count]
            policy_options = []
            policy_values = []
            
            for i in range(len(policy_list)):
                if policy_list[i] == "":
                    continue
                policy_options.append(str(i))
                policy_values.append(policy_list[i])
                
            policy_options = " ".join(policy_options)
            policy_values = " ".join(policy_values)
            
            #socket_data[2] = "현재비밀번호,,현재포트,,옵션 ex)0 1 2 3 4 5,,값 ex)off 30 5 5 low 5"
            socket_data[2] = "%s,,%s,,%s,,%s"%(db_policy_pw, session['mysql_port'], policy_options, policy_values)
            command = "python client.py policy_change"
            
            if 'ssh_id' in session:
                ssh_id = session['ssh_id']
                ssh_pw = session['ssh_pw']
                ssh_ip = session['ssh_ip']
                ssh_port = session['ssh_port']
                
                os.system("plink %s -l %s -pw %s -P %s -batch %s"%(ssh_ip, ssh_id, ssh_pw, ssh_port, command))
            
            return redirect("/install")
    
        if "new_port" in request.form: #포트 바꿨을 때
            now_port = session['mysql_port']
            new_port = request.form['new_port']

            socket_data[1] = "%s,%s"%(now_port, new_port)
            command = "python client.py port_change"

            if 'ssh_id' in session:
                ssh_id = session['ssh_id']
                ssh_pw = session['ssh_pw']
                ssh_ip = session['ssh_ip']
                ssh_port = session['ssh_port']
                
                os.system("plink %s -l %s -pw %s -P %s -batch %s"%(ssh_ip, ssh_id, ssh_pw, ssh_port, command))
            
            return redirect("/install")
    
        if "get_command" in request.form: #커맨드 직접 입력
            command = request.form['get_command'] + " > return.output"
            
            if 'ssh_id' in session:
                id = session['ssh_id']
                pw = session['ssh_pw']
                ip = session['ssh_ip']
                port = session['ssh_port']
                
                os.system("plink %s -l %s -pw %s -P %s -batch %s"%(ip, id, pw, port, command))
                os.system("pscp -pw %s -P %s %s@%s:./return.output ./"%(pw, port, id, ip))
                os.system("plink %s -l %s -pw %s -P %s -batch rm -f return.output"%(ip, id, pw, port))
                
                with open('return.output', 'r', newline='', encoding="utf8") as f:
                    print_result = f.read()#.replace('\n', '\r\n')
                    
                os.system("del return.output")
            
                return jsonify(print_result = print_result)

    else :
        return "잘못된 접근"

    return redirect('/install')


if __name__ == "__main__":
    app.debug = True,
    app.run(
        use_reloader=False,
        host = 'localhost',
        port=5003
    )