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
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import urlfetch
from google.appengine.ext.webapp import template

import os
from BeautifulSoup import BeautifulSoup
import logging

class MainHandler(webapp.RequestHandler):
    """article list"""
    def get(self):

        url = "http://clien.career.co.kr/cs2/bbs/board.php?bo_table=park"
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
                    logging.info("invalid format: %s"%td)
                    continue
                    
                #logging.info(td)
                #logging.info("#td=%d"% len(td)) #type(td))
                id = td[0].string
                logging.info("id=%s"%id)
                title = td[1].a.string
                logging.info("title=%s"%title)
                
                author_tag = td[2]
                if author_tag.img:
                    image_src = author_tag.img['src']
                    image_src = "http://clien.career.co.kr/cs2" + image_src.replace("..","")
                    author = '<img src="%s" class="ppan"/>'% image_src
                else:
                    author = '<img src="ppan.gif" class="ppan default"/>'
                logging.info("author=%s"%author)
                publish_time = td[3].span['title']
                logging.info("publish_time: %s"%publish_time)
                read = int(td[4].string)
                logging.info("read: %d"% read)
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
            self.response.out.write(template.render(path, {'posts': posts}))
        else:
            logging.info("failed")
                
class ArticleHandler(webapp.RequestHandler):
    """read article & comments"""
    def get(self, board, id):

        url = "http://clien.career.co.kr/cs2/bbs/board.php?bo_table=park"
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
                    logging.info("invalid format: %s"%td)
                    continue
                    
                #logging.info(td)
                #logging.info("#td=%d"% len(td)) #type(td))
                id = td[0].string
                logging.info("id=%s"%id)
                title = td[1].a.string
                logging.info("title=%s"%title)
                
                author_tag = td[2]
                if author_tag.img:
                    image_src = author_tag.img['src']
                    image_src = "http://clien.career.co.kr/cs2" + image_src.replace("..","")
                    author = '<img src="%s" class="ppan"/>'% image_src
                else:
                    author = author_tag.span.string
                logging.info("author=%s"%author)
                publish_time = td[3].span['title']
                logging.info("publish_time: %s"%publish_time)
                read = int(td[4].string)
                logging.info("read: %d"% read)
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
            self.response.out.write(template.render(path, {'posts': posts}))
        else:
            logging.info("failed")

def main():
    application = webapp.WSGIApplication([('/', MainHandler)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
