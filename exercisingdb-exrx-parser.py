#!/usr/bin/python
import glob
import json
import os
import re
import ssl
import traceback
import urllib2

import sqlite3
import time
from bs4 import BeautifulSoup, NavigableString

def read(f):
    with open(f) as fi:
        return [i.strip() for i in fi.readlines()]

def write(f,c):
    with open(f,'w+') as fi:
        fi.write(c)

class ExerciseObj:
    def __init__(self,url):
        vv= ExerciseDB.getSoup(url)
        html = vv.select('article > div.ad-banner-block')[0]
        self.url=url
        self.name=html.select('h1.page-title').get_text().strip()
        self.gifurl=html.select('img.img-responsive')[0].attrs['src']
        self.video=html.select('iframe')[0].attrs['src']
        classification=html.select('table')[0]
        v=1
        self.classifications={}
        for tr in classification.select('tr'):
            if not tr: continue
            for td in tr.select('td'):
                if v%2==0: b=td.get_text().strip()
                else: a=td.get_text().strip()
                v+=1
            self.classifications[a]=b

        instructions={}
        v=False
        k=''; vv =''
        for i in html.select('div > div')[0]:
            if isinstance(i, NavigableString):
                continue
            if 'Instructions' in i:
                v=True
                continue
            if not v: continue
            if 'strong' in str(i) or 'h2' in str(i):
                if k:
                    instructions[k]=vv
                k=i.getText().strip()
                vv=''
            else: vv+=str(i.get_text())
        comments=''
        v=False
        for i in html.select('div > div')[0]:
            if isinstance(i, NavigableString):
                continue
            if 'Comments' in i:
                v=True
                continue
            if not v: continue
            comments+=str(i.get_text())
            instructions['Comments']=comments
        self.instructions=instructions
        muscles={}
        for i in html.select('div > div')[1]:
            if isinstance(i, NavigableString):
                continue
            if 'strong' in str(i):
                k=i.get_text().strip()
            if 'ul' in str(i):
                v=i.select('a')
                muscles[k]=[{j.get_text():j.attrs['href']} for j in v]
        self.muscles=muscles

    def get_map(self):
        return {
                    'Instructions':self.instructions,
                    'Muscles':self.muscles,
                    'Classifications':self.classifications,
                    'GifURL':self.gifurl,
                    'VideoURL':self.video
                }

class ExerciseDB:
    ### START Utility methods ###
    @staticmethod
    def getWebContent(url):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
               'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
               'Accept-Encoding': 'none',
               'Accept-Language': 'en-US,en;q=0.9',
               'cache-control': 'no-cache',
               'Connection': 'keep-alive'}
        try:
            response = urllib2.urlopen(urllib2.Request(url, headers=hdr),
                                       context=ctx, timeout=100)
        except:
            response = urllib2.urlopen(urllib2.Request(url.replace('../../','../'),
                                                       headers=hdr),
                                       context=ctx, timeout=100)
        contents=response.read()
        return contents

    @staticmethod
    def getSoup(url):
        try:
            return BeautifulSoup(ExerciseDB.getWebContent(url), 'html.parser')
        except:
            traceback.print_exc()
            print(url)
    ### END Utility methods ###

    baseurl ="https://exrx.net/Lists/"
    def __init__(self):
        categories = self.getExercisesURLs(self.baseurl+'Directory')
        all_links=[]
        for i in categories:
            all_links.extend(self.getExercisesURLs(self.baseurl+i))
        for link in all_links:
            self.getExerciseData(self.baseurl+link)

    def getExercisesURLs(self,url):
        path='exercises/'
        try:
            os.mkdir(path)
        except: pass
        f=url.replace('/','_').replace('.','_').replace(':','_')
        if os.path.exists(f):
            fi=read(f)
            if fi:
                return fi
        vv= ExerciseDB.getSoup(url)
        v=vv.select('article > div.container a')
        if not v:
            v = vv.select('article > div.ad-banner-block a')
        r = re.compile(r'#.*$')
        s = set()
        for i in v:
            if 'href' not in i.attrs: continue
            if 'http' in i.attrs['href']: continue
            s.add(r.sub('',i.attrs['href']))
        write(path+f,'\n'.join(list(s)))
        time.sleep(2)
        return list(s)

    def getExerciseData(self,url):
        f=url.replace('/','_').replace('.','_').replace(':','_')
        if os.path.exists(f):
            try:
                with open(f) as fil:
                    return json.load(fil)
            except ValueError:
                return None
        try:
            time.sleep(2)
            eo=ExerciseObj(url)
        except:
            print url
            # write(f,str(None))
            return None
        with open(f,'w') as fil:
            json.dump(eo.get_map(),fil)
        return eo.get_map()



class SQLlite3:
    def __init__(self):
        self._get_conn()

    def query(self,sql):
        cur = self._get_conn().cursor()
        cur.execute(sql)
        if sql.startswith('insert into '):
            self._get_conn().commit()
            return cur.lastrowid
        rows = cur.fetchall()
        return rows

    def _get_conn(self,database="./workoutapp.sqllite"):
        timeout = 30
        if not database:
            raise Exception(
                'sqlite3 config option "sqlite3.database" is missing')
        if not timeout:
            raise Exception(
                'sqlite3 config option "sqlite3.timeout" is missing')
        # LOGGER.info('Connecting the sqlite3 database: %s timeout: %s', database, timeout)
        self.conn = sqlite3.connect(database, timeout=float(timeout), isolation_level=None)
        # createTables(conn)
        return self.conn

    def _close_conn(self):
        '''
        Close the sqlite3 database connection
        '''
        # LOGGER.debug('Closing the sqlite3 database connection')
        self.conn.commit()
        self.conn.close()

def getV(dic,k):
    return dic[k].replace('\n','\\n').replace('\'','\'\'') if k in dic else ''

def write_data_to_sqllite():
    ie="insert into exercise(name,type,group_name,videourl,gifurl) " \
       "values('{0}','{1}','{2}','{3}','{4}');"
    se="select id from exercise " \
       "where name = '{0}' and type = '{1}' and group_name = '{2}' and videourl = '{3}' and gifurl = '{4}';"
    ic="insert into classifications(utility, mechanics, force, function, intensity) " \
       "values('{0}','{1}','{2}','{3}','{4}');"
    sc="select id from classifications " \
       "where utility = '{0}' and mechanics = '{1}' and force = '{2}' and function = '{3}' and intensity = '{4}';"
    iec="insert into exercise_classifications(classification_id, exercise_id) " \
        "values('{0}','{1}');"
    ii="insert into instructions(preparation, execution, easier, comments) " \
       "values('{0}','{1}','{2}','{3}');"
    si="select id from instructions " \
       "where preparation = '{0}' and execution = '{1}' and easier = '{2}' and comments = '{3}';"
    iei="insert into exercise_instructions(instructions_id, exercise_id) " \
        "values('{0}','{1}');"
    im="insert into muscles(name, link) " \
       "values('{0}','{1}');"
    sm="select id from muscles " \
       "where name = '{0}' and link = '{1}';"
    iem="insert into exercise_muscles(muscles_type, muscle_Id, exercise_id) " \
        "values('{0}','{1}','{2}');"
    sql = SQLlite3()
    with open('exerceisedb-create.sql') as f:
        s=f.readlines()
    for q in ''.join(s).split(';'):
        sql.query(q)
    for file in glob.glob("exercises/https___exrx_net_*"):
        try:
            with open(file) as fil:
                l=json.load(fil)
            name=file.split('____')[-1].replace('_',' ').strip().split(" ")
            if len(name) < 3:
                name.insert(1,'Null')
            c=l['Classifications']
            i=l['Instructions']
            m=l['Muscles']
            try:
                eid=sql.query(ie.format(name[2],name[0],name[1],l['VideoURL'],l['GifURL']))
            except:
                v=sql.query(se.format(name[2],name[0],name[1],l['VideoURL'],l['GifURL']))
                try: eid=v[0][0]
                except:
                    eid=v
            try:
                cid=sql.query(ic.format(getV(c,'Utility:'),getV(c,'Mechanics:'),getV(c,'Force:'),getV(c,'Function:'),getV(c,'Intensity:')))
            except:
                v=sql.query(sc.format(getV(c,'Utility:'),getV(c,'Mechanics:'),getV(c,'Force:'),getV(c,'Function:'),getV(c,'Intensity:')))
                try: cid=v[0][0]
                except:
                    cid=v
            try:
                iid=sql.query(ii.format(getV(i,'Preparation'),getV(i,'Execution'),getV(i,'Easier'),getV(i,'Comments')))
            except:
                v=sql.query(si.format(getV(i,'Preparation'),getV(i,'Execution'),getV(i,'Easier'),getV(i,'Comments')))
                try: iid=v[0][0]
                except:
                    iid=v
            try:
                sql.query(iei.format(iid,eid))
            except:
                pass
            try:
                sql.query(iec.format(cid,eid))
            except:
                pass
            for t,mus in m.iteritems():
                for muscl in mus:
                    for muscle,link in muscl.iteritems():
                        try:
                            mid=sql.query(im.format(muscle,link))
                        except:
                            v=sql.query(sm.format(muscle,link))
                            try: mid=v[0][0]
                            except:
                                mid=v
                        try:
                            sql.query(iem.format(t,mid,eid))
                        except:
                            pass
        except Exception as e:
            if 'No JSON object could be decoded' not in e:
                print e

    sql._close_conn()

if __name__ == '__main__':
    edb = ExerciseDB()
    write_data_to_sqllite()