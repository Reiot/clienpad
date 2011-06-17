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
# os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
# 
# from google.appengine.dist import use_library
# use_library('django', '1.2')

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import urlfetch
from google.appengine.ext.webapp import template


from BeautifulSoup import BeautifulSoup
import logging

# TEST Script
#
#
# >>> from BeautifulSoup import BeautifulSoup
# >>> import urllib
# >>> soup = BeautifulSoup(urllib.urlopen(url).read()

def author_image(tag):
    if tag.img:
        image_src = tag.img['src']
        image_src = "http://clien.career.co.kr/cs2" + image_src.replace("..","")
        author = '<img src="%s" class="ppan"/>'% image_src
    else:
        author = '<img src="ppan.gif" class="ppan default" title="%s" alt="%s"/><span class="author">%s</span>'% (
            tag.span.string,
            tag.span.string,
            tag.span.string,
        )
        # author = '<span class="author ul-li-thumb">%s</span>'% (
        #     tag.span.string,
        # )
    return author

class BoardHandler(webapp.RequestHandler):
    """article list"""
    def get(self, board='park'):

        url = "http://clien.career.co.kr/cs2/bbs/board.php?bo_table=%s"% board
        logging.info("fetching...%s"% url)
        result = urlfetch.fetch(url)
        logging.info("status: %d"% result.status_code)
        if result.status_code == 200:
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
                title = td[1].a.string
                #logging.info("title=%s"%title)
                
                author_tag = td[2]
                author = author_image(author_tag)
                #logging.info("author=%s"%author)
                
                publish_time = td[3].span['title']
                #logging.info("publish_time: %s"%publish_time)
                
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
                    read = read,
                ))
                
            path = os.path.join(os.path.dirname(__file__), 'index.html')
            self.response.out.write(template.render(path, {
                'board': board,
                'posts': posts,
            }))
        else:
            logging.info("failed")
                
class PostHandler(webapp.RequestHandler):
    """read article & comments"""
    def get(self, bo_table, wr_id):
        url = "http://clien.career.co.kr/cs2/bbs/board.php?bo_table=%s&wr_id=%s"%(bo_table, wr_id)
        logging.info("fetching...%s"% url)
        result = urlfetch.fetch(url)
        logging.info("status: %d"% result.status_code)
        if result.status_code == 200:
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
                comment_author = author_image(comment.ul.li)
                #logging.info('author: %s'%comment_author)
                comment_date = None
                comment_content = comment.findNext('div')
                #logging.info('content: %s'%comment_content)
                comments.append(dict(
                    author = comment_author,
                    content = comment_content,
                ))

            post = dict(
                title = title,
                content = content,
                signature = signature,
                comments = comments,
            )

            path = os.path.join(os.path.dirname(__file__), 'post.html')
            self.response.out.write(template.render(path, {'post': post}))
        else:
            logging.info("failed")

def main():
    application = webapp.WSGIApplication([
        ('/', BoardHandler),
        (r'/([^/]*)', BoardHandler),
        (r'/([^/]*)/(\d*)', PostHandler),
        ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
