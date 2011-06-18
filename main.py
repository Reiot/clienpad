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
#from google.appengine.dist import use_library
#use_library('django', '1.2')

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import urlfetch
from google.appengine.ext.webapp import template
from django.utils import simplejson 

from BeautifulSoup import BeautifulSoup
import logging

# TEST Script
#
#
# >>> from BeautifulSoup import BeautifulSoup
# >>> import urllib
# >>> soup = BeautifulSoup(urllib.urlopen(url).read()
APP_NAME = 'Clien for iPad'
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
        id = 'cm_havehome',
        title = u'내집마련당',
    ),
    # dict(
    #     id = '',
    #     title = u'',
    # ),
    
]
BOARDS_MAP = dict([(b['id'], b) for b in BOARDS])
BOARDS_MAP.update(dict([(b['id'], b) for b in SMALL_BOARDS]))

CONF = dict(
    app_name = APP_NAME,
    theme = "b",
)
    
def parse_author_image(tag):
    if tag.img:
        image_src = tag.img['src']
        image_src = "http://clien.career.co.kr/cs2" + image_src.replace("..","")
        author = '<img src="%s" class="ppan"/>'% image_src
    else:
        author = '<img src="/static/ppan.gif" class="ppan default" title="%s" alt="%s"/><span class="author">%s</span>'% (
            tag.span.string,
            tag.span.string,
            tag.span.string,
        )
        # author = '<span class="author ul-li-thumb">%s</span>'% (
        #     tag.span.string,
        # )
    return author
         
def parse_post_info(td):
    #<td class="post_subject"><a href="./board.php?bo_table=park&amp;wr_id=6535728&amp;page=">저도 여친에게 알콩달콩 살고 싶다고 말한 적이...</a><span>[4]</span></td>
    
    href = td.a['href']
    post_id =  re.search('wr_id=(\d+)',href).group(1)
    #logging.info('id=%s'% post_id)

    title = td.a.string
    #logging.info('title=%s'% title)

    comments = td.span.string
    comments = comments.replace('[','').replace(']','')
    #logging.info('comments=%s'% comments)

    return dict(
        id = post_id,
        title = title,
        comments = comments,
    )
    
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
    def get(self, board_id='park', page="1"):
        
        board = BOARDS_MAP[board_id]
        
        page = int(page)
        url = "http://clien.career.co.kr/cs2/bbs/board.php?bo_table=%s"% board_id
        if page > 1:
            url += "&page=%d"%page
            
        logging.info("fetching...%s"% url)
        result = urlfetch.fetch(url)
        if result.status_code != 200:
            logging.warn("urlfetch failed: %d"% result.status_code)            
        else:
            soup = BeautifulSoup(result.content)
            posts = []
            # skip table header and notice
            for tr in soup.find("div", {"class": "board_main"}).findAll("tr")[2:]:
                td = tr.findAll("td")
                if len(td)<4:
                    logging.warn("invalid format: %s"%td)
                    continue
                    
                #logging.info(td)
                #logging.info("#td=%d"% len(td)) #type(td))
                id = td[0].string
                #logging.info("id=%s"%id)

                subject_tag = td[1]
                
                title = subject_tag.a.string
                #logging.info("title=%s"%title)
                
                if subject_tag.span:
                    comments = subject_tag.span.string
                    comments = comments.replace("[","").replace("]","")
                else:
                    comments = 0
                
                author_tag = td[2]
                author = parse_author_image(author_tag)
                #logging.info("author=%s"%author)
                
                publish_time_tag = td[3]
                if publish_time_tag.span:
                    publish_time = publish_time_tag.span['title']
                    publish_time_short = publish_time_tag.span.string
                    #logging.info("publish_time: %s"%publish_time)
                else:
                    publish_time = publish_time_short = None
                
                read = int(td[4].string)
                #logging.info("read: %d"% read)
                # read = publish_time.nextSibling
                # for td in tr.findAll("td"):
                #     logging.info(td)
                
                posts.append(dict(
                    id = id,
                    title = title,
                    author = author,
                    publish_time = publish_time,
                    publish_time_short = publish_time_short,
                    read = read,
                    comments = comments,
                ))
            
            data = dict(
                board = board,
                next_page = page+1,
                posts = posts,
            )
            if self.request.get('format')=='json':
                self.response.headers["Content-Type"] = "application/json"                
                self.response.out.write(simplejson.dumps(data))                
            else:
                data['conf'] = CONF
                path = os.path.join(os.path.dirname(__file__), 'templates', 'board.html')
                self.response.out.write(template.render(path, data))
        
class PostHandler(webapp.RequestHandler):
    """read article & comments"""
    def get(self, board_id, post_id):
        board = BOARDS_MAP[board_id]
        url = "http://clien.career.co.kr/cs2/bbs/board.php?bo_table=%s&wr_id=%s"%(board_id, post_id)
        logging.info("fetching...%s"% url)
        result = urlfetch.fetch(url)
        #logging.info("status: %d"% result.status_code)
        if result.status_code != 200:
            logging.warn("urlfetch failed: %d"% result.status_code)            
        else:
            soup = BeautifulSoup(result.content)
            
            title_div = soup.find('div', {'class':'view_title'})
            title = title_div.div.h4.span.string
            #logging.info('title:%s'% title)
            
            content_div = soup.find('div', {'class':'resContents'})
            
            signature_div = content_div.find('div', {'class':'signature'})
            if signature_div:
                signature = signature_div.dl.dd
                signature_div.extract()
            else:
                signature = None
                
            ccl = content_div.find('div', {'class':'ccl'})
            if ccl:
                ccl.extract()
            
            # modify image
            for img in content_div.findAll('img'):
                if img['src'].startswith(".."):
                    img['src'] = "http://clien.career.co.kr/cs2" + img['src'].replace("..","")
                elif img['src'].startswith("/cs2"):
                    img['src'] = "http://clien.career.co.kr" + img['src']
            content = []
            for c in content_div.contents:
                content.append(unicode(c))

            content = u''.join(content)
            #logging.info('content:%s'% content)
            comments = []
            for comment in soup.findAll('div', {'class':'reply_head'}):
                #logging.info('comment: %s'% comment.ul.li)
                comment_author = parse_author_image(comment.ul.li)
                #logging.info('author: %s'%comment_author)
                comment_date = None
                comment_content = comment.findNext('div')
                #logging.info('content: %s'%comment_content)
                comments.append(dict(
                    author = comment_author,
                    content = comment_content,
                ))
                
            view_board = soup.find('table', {'class':'view_board'})
            #logging.info('view_board: %s'% view_board)
            td = view_board.findAll('td', {'class':'post_subject'})
            if len(td)==1: # lastest post
                prev = None
                next = parse_post_info(td[0])
            else:
                prev = parse_post_info(td[0])
                next = parse_post_info(td[1])
                
            #logging.info("prev=%s next=%s"%( prev, next))

            post = dict(
                title = title,
                content = content,
                signature = signature,
                comments = comments,
            )

            path = os.path.join(os.path.dirname(__file__), 'templates', 'post.html')
            self.response.out.write(template.render(path, {
                'conf': CONF,
                'board': board,
                'post': post,
                'prev': prev,
                'next': next,
            }))

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
