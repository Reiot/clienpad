# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import re

# with 1.2, HTML tags are escaped!
# os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
# 
from google.appengine.dist import use_library
use_library('django', '1.2')

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import urlfetch
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from django.utils import simplejson 

from BeautifulSoup import BeautifulSoup, Comment
import logging

# TEST Script
#
#
# >>> from BeautifulSoup import BeautifulSoup
# >>> import urllib
# >>> soup = BeautifulSoup(urllib.urlopen(url).read()
APP_NAME = 'Clien for iPad'
BOARD_CACHE_EXPIRE = 60
POST_CACHE_EXPIRE = 60
ENABLE_MEMCACHE = True
#ENABLE_MEMCACHE = False

BOARDS = [
    dict(
        id = 'park',
        title = u'모두의 공원',
    ),
    dict(
        id = 'image',
        title = u'사진게시판',
    ),
    dict(
        id = 'kin',
        title = u'아무거나 질문',
    ),
    dict(
        id = 'news',
        title = u'새로운 소식',
    ),
    dict(
        id = 'lecture',
        title = u'팁과 강좌',
    ),
    dict(
        id = 'use',
        title = u'사용기 게시판',
    ),
    dict(
        id = 'useful',
        title = u'유용한 사이트',
    ),
    dict(
        id = 'jirum',
        title = u'알뜰 구매',
    ),
    dict(
        id = 'coupon',
        title = u'쿠폰/이벤트',
    ),
    dict(
        id = 'hongbo',
        title = u'직접 홍보',
    ),
    dict(
        id = 'pds',
        title = u'자료실',
    ),
]
SMALL_BOARDS = [
    dict(
        id = 'cm_main',
        title = u'임시소모임',
    ),
    dict(
        id = 'cm_mac',
        title = u'MacLIEN',
    ),
    dict(
        id = 'cm_iphonien',
        title = u'아이포니앙',
    ),
    dict(
        id = 'cm_girl',
        title = u'소녀시대',
    ),
    dict(
        id = 'cm_dia',
        title = u'디아블로',
    ),
    dict(
        id = 'cm_nokien',
        title = u'노키앙',
    ),
    dict(
        id = 'cm_leather',
        title = u'가죽당',
    ),
    dict(
        id = 'cm_bb',
        title = u'블렉베리',
    ),
    dict(
        id = 'cm_wow',
        title = u'WOW',
    ),
    dict(
        id = 'cm_baby',
        title = u'육아당',
    ),
    dict(
        id = 'cm_book',
        title = u'활자중독당',
    ),
    dict(
        id = 'cm_daegu',
        title = u'대구당',
    ),
    dict(
        id = 'cm_havehome',
        title = u'내집마련당',
    ),
    dict(
        id = 'cm_kara',
        title = u'카라당',
    ),
    dict(
        id = 'cm_oversea',
        title = u'바다건너당',
    ),
    dict(
        id = 'cm_sea',
        title = u'Sea마당',
    ),
    dict(
        id = 'cm_mabi',
        title = u'Mabinogien',
    ),
    dict(
        id = 'cm_music',
        title = u'소리당',
    ),
    dict(
        id = 'cm_star',
        title = u'스타당',
    ),
    dict(
        id = 'cm_coffee',
        title = u'클다방',
    ),
    dict(
        id = 'cm_lang',
        title = u'어학당',
    ),
    dict(
        id = 'cm_car',
        title = u'굴러간당',
    ),
    dict(
        id = 'cm_bike',
        title = u'자전거당',
    ),
    dict(
        id = 'cm_andro',
        title = u'안드로메당',
    ),
    dict(
        id = 'cm_tour',
        title = u'여행을떠난당',
    ),
    dict(
        id = 'cm_twit',
        title = u'트윗당',
    ),
    dict(
        id = 'cm_golf',
        title = u'골프당',
    ),
    dict(
        id = 'cm_bear',
        title = u'곰돌이당',
    ),
    dict(
        id = 'cm_swim',
        title = u'퐁당퐁당',
    ),
    dict(
        id = 'cm_app',
        title = u'앱개발자당',
    ),
    dict(
        id = 'cm_movie',
        title = u'영화본당',
    ),
    dict(
        id = 'cm_board',
        title = u'보드게임당',
    ),
    dict(
        id = 'cm_mount',
        title = u'오른당',
    ),
    dict(
        id = 'cm_snow',
        title = u'미끄러진당',
    ),
    dict(
        id = 'cm_photo',
        title = u'찰칵찍당',
    ),
    dict(
        id = 'cm_webos',
        title = u'webOS당',
    ),
    dict(
        id = 'cm_food',
        title = u'맛있겠당',
    ),
    dict(
        id = 'cm_stock',
        title = u'고배당',
    ),
    dict(
        id = 'cm_70',
        title = u'X세대당',
    ),
    dict(
        id = 'cm_fashion',
        title = u'패셔니앙',
    ),
    dict(
        id = 'cm_pic',
        title = u'그림그린당',
    ),
    
]
BOARDS_MAP = dict([(b['id'], b) for b in BOARDS])
BOARDS_MAP.update(dict([(b['id'], b) for b in SMALL_BOARDS if b['id']]))

CONF = dict(
    app_name = APP_NAME,
    theme = "b",
)

def parse_author_image(tag):
    if tag.img:
        image_src = tag.img['src']
        image_src = "http://clien.career.co.kr/cs2" + image_src.replace("..","")
        author = '<img src="%s" class="author ul-li-icon"/>'% image_src
    else:
        author = '<span class="author ul-li-icon">%s</span>'% (
            unicode(tag.span.string),
        )
    return author

def parse_post_id(anchor):
    return re.search('wr_id=(\d+)', anchor['href']).group(1)
    
def parse_post_info(tag):
    post_id = parse_post_id(tag.a)
    logging.debug('id=%s'% post_id)

    title = unicode(tag.a.string)
    logging.debug('title=%s'% title)

    comment_count = unicode(tag.span.string).replace('[','').replace(']','')
    logging.debug('comments=%s'% comment_count)

    return dict(
        id = post_id,
        title = title,
        comment_count = comment_count,
    )
    
def parse_comment(tag):
    # div.reply_head + div.reply_content
    
    author = parse_author_image(tag.ul.li)
    logging.debug('author: %s'% author)
    
    # datetime
    info_li = tag.ul.findAll("li")[1]
    #logging.info(info_li)
    info = unicode(info_li.string).strip().replace("(","").replace(")","")
    
    div_content = tag.findNext('div')
    content = unicode(div_content.contents[0]).strip()
    logging.debug('content: %s'% content)
    
    return dict(
        author = author,
        info = info,
        content = content,
    )

def parse_content(tag, remove_comment=True):

    # modify image URL
    for img in tag.findAll('img'):
        if img['src'].startswith(".."):
            img['src'] = "http://clien.career.co.kr/cs2" + img['src'].replace("..","")
        elif img['src'].startswith("/cs2"):
            img['src'] = "http://clien.career.co.kr" + img['src']
        del img['onclick']
        del img['style']
        
    # remove script & form & textarea
    for exc in tag.findAll(['script', 'form', 'textarea', 'input']):
        exc.extract()
        
    # remove html comment
    for comment in tag.findAll(text=lambda text:isinstance(text, Comment)):
        comment.extract()

    if remove_comment:
        for div in tag.findAll('div', {'class':'reply_head'}):
            div.extract()
        for div in tag.findAll('div', {'class':'reply_content'}):
            div.extract()
        
    ccl = tag.find('div', {'class':'ccl'})
    if ccl:
        ccl.extract()

    # parse sig
    signature_div = tag.find('div', {'class':'signature'})
    if signature_div:
        signature = u''.join([unicode(c) for c in signature_div.dl.dd.contents])
        signature_div.extract()
    else:
        signature = None        

    # unicodify!
    content = [unicode(c) for c in tag.contents]

    return u''.join(content), signature
    
class MainHandler(webapp.RequestHandler):
    """article list"""
    def get(self):
        
        data = BOARDS + SMALL_BOARDS
        
        if self.request.get('format')=='json':
            self.response.headers["Content-Type"] = "application/json"                
            self.response.out.write(simplejson.dumps(data))                
        else:
            path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
            self.response.out.write(template.render(path, dict(
                conf = CONF,
                boards = BOARDS,
                small_boards = SMALL_BOARDS,
            )))
            
class BoardHandler(webapp.RequestHandler):
    """article list"""
    
    def get(self, board_id, page="1"):
        
        board = BOARDS_MAP[board_id]
        
        page = int(page)
        url = "http://clien.career.co.kr/cs2/bbs/board.php?bo_table=%s"% board_id
        if page > 1:
            url += "&page=%d"% page         
         
        data = memcache.get(url) if ENABLE_MEMCACHE else None
        if data:
            logging.debug('cache hit')
        else:
            data = self.parse(url, board, page)                
            if data:
                logging.debug('data:%s'% data)
                memcache.add(url, data, BOARD_CACHE_EXPIRE)
                
        if self.request.get('format')=='json':
            self.response.headers["Content-Type"] = "application/json"                
            self.response.out.write(simplejson.dumps(data))                
        else:
            data['conf'] = CONF            
            path = os.path.join(os.path.dirname(__file__), 'templates', 'board.html')
            self.response.out.write(template.render(path, data))
            
    def parse(self, url, board, page):
        logging.debug("fetching...%s"% url)
        result = urlfetch.fetch(url)
        if result.status_code != 200:
            logging.warn("urlfetch failed: %d"% result.status_code)            
            return {}

        soup = BeautifulSoup(result.content)
        
        posts = []
        if board['id']=="image":
            trs = soup.find("div", {"class": "board_main"}).findAll("tr")
            for i in range(0, len(trs), 2):
                post = self.parse_image_post(trs[i], trs[i+1])  
                if post:      
                    posts.append(post)
        else:
            # skip table header and notice
            for tr in soup.find("div", {"class": "board_main"}).findAll("tr")[2:]:
                post = self.parse_post(tr)  
                if post:      
                    posts.append(post)

        return dict(
            board = board,
            next_page = page + 1,
            posts = posts,
        )
        
    def parse_post(self, tr):
        # some boards have category td, others not. 
        # that's why use td[-N] style.
        td = tr.findAll("td")
        if len(td)<4:
            logging.warn("invalid format: %s"%td)
            return None
        
        post_id = td[0].string
        logging.debug("post_id: %s"% post_id)

        subject_tag = td[-4]    
        if subject_tag.a:
            title = subject_tag.a.string
        else:
            # blocked post has no title. skip.
            return None
        logging.debug("title=%s"%title)
    
        # comment count
        if subject_tag.span:
            comment_count = subject_tag.span.string
            comment_count = comment_count.replace("[","").replace("]","")
        else:
            comment_count = 0
    
        author_tag = td[-3]
        author = parse_author_image(author_tag)
        logging.debug("author=%s"%author)
    
        publish_time_tag = td[-2]
        if publish_time_tag.span:
            publish_time = publish_time_tag.span['title']
            publish_time_short = publish_time_tag.span.string
            logging.debug("publish_time: %s"%publish_time)
        else:
            publish_time = publish_time_short = None
    
        read_count = td[-1].string
        logging.debug("read_count: %s"% read_count)
    
        return dict(
            id = post_id,
            title = title,
            author = author,
            publish_time = publish_time,
            publish_time_short = publish_time_short,
            read_count = read_count,
            comment_count = comment_count,
        )

    def parse_image_post(self, tr1, tr2):

        p_user_info = tr1.find("p", {"class":"user_info"})
        author = parse_author_image(p_user_info)        
        logging.debug("author: %s"% author)

        # date, view, vote
        p_post_info = tr1.find("p", {"class":"post_info"})
        info = p_post_info.string
        logging.debug("info: %s"% info)
            
        div_view_title = tr1.find('div', {'class':'view_title'})
        post_id = parse_post_id(div_view_title.div.h4.span.a)
        logging.debug("post_id: %s"% post_id)

        title = unicode(div_view_title.div.h4.span.a.string)
        logging.debug('title: %s'% title)

        # parse comment first because it will be removed in parse_content()
        div_reply_head = tr2.findAll('div', {'class':'reply_head'})
        comments = [parse_comment(comment) for comment in div_reply_head]
        logging.debug('#comments: %s'% len(comments))

        div_view_content = tr2.find('div', {'class':'view_content'})
        content, unused = parse_content(div_view_content)            
            
        return dict(
            id = post_id,
            title = title,
            author = author,
            info = info,
            content = content,
            comments = comments,
        )
        
class PostHandler(webapp.RequestHandler):
    """read article & comments"""
    def get(self, board_id, post_id):
        board = BOARDS_MAP[board_id]
        url = "http://clien.career.co.kr/cs2/bbs/board.php?bo_table=%s&wr_id=%s"%(board_id, post_id)
        
        data = memcache.get(url) if ENABLE_MEMCACHE else None
        if data:
            logging.debug('cache hit')
        else:
            data = self.parse(url, board)                
            if data:
                #logging_dict(data)
                memcache.add(url, data, POST_CACHE_EXPIRE)
                
        if self.request.get('format')=='json':
            self.response.headers["Content-Type"] = "application/json"                
            self.response.out.write(simplejson.dumps(data))                
        else:
            data['conf'] = CONF
            path = os.path.join(os.path.dirname(__file__), 'templates', 'post.html')
            self.response.out.write(template.render(path, data))
        
        
    def parse(self, url, board):
        logging.debug("fetching...%s"% url)
        result = urlfetch.fetch(url)
        if result.status_code != 200:
            logging.warn("urlfetch failed: %d"% result.status_code)            
            return {}

        soup = BeautifulSoup(result.content)

        div_view_head = soup.find('div', {'class':'view_head'})
        p_user_info = div_view_head.find("p", {"class":"user_info"})
        author = parse_author_image(p_user_info)        
        logging.debug("author: %s"% author)

        # date, view, vote
        p_post_info = div_view_head.find("p", {"class":"post_info"})
        info = unicode(p_post_info.string)
        logging.info("info: %s"% info)
        
        div_view_title = soup.find('div', {'class':'view_title'})
        title = unicode(div_view_title.div.h4.span.string)
        logging.debug('title:%s'% title)

        div_rescontents = soup.find('div', {'class':'resContents'})
        content, signature = parse_content(div_rescontents)
        
        div_reply_head = soup.findAll('div', {'class':'reply_head'})
        comments = [parse_comment(comment) for comment in div_reply_head]

        table_view_board = soup.find('table', {'class':'view_board'})
        td_post_subject = table_view_board.findAll('td', {'class':'post_subject'})
        if len(td_post_subject)==1: # lastest post
            prev = None
            next = parse_post_info(td_post_subject[0])
        else:
            prev = parse_post_info(td_post_subject[0])
            next = parse_post_info(td_post_subject[1])

        logging.debug("prev=%s next=%s"%( prev, next))

        return dict(
            board = board,
            title = title,
            author = author,
            info = info,
            content = content,
            signature = signature,
            comments = comments,
            prev = prev,
            next = next,
        )
        
def main():
    application = webapp.WSGIApplication([
        ('/', MainHandler),
        (r'/([^/]*)', BoardHandler),
        (r'/([^/]*)/page(\d+)', BoardHandler),
        (r'/([^/]*)/(\d*)', PostHandler),
        ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
