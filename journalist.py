# -*- coding: utf-8 -*-
import os, time, datetime
import web
import config, crypto, store

urls = (
  '/', 'index',
  '/reply/', 'reply',
  '/([a-f0-9]+)/', 'col',
  '/([a-f0-9]+)/([0-9]+\.[0-9]+(?:_msg|_doc|)\.gpg)', 'doc'
)

render = web.template.render(config.JOURNALIST_TEMPLATES_DIR, base='base')

class index:
    def GET(self):
        dirs = os.listdir(config.STORE_DIR)
        cols = []
        for d in dirs:
            if not os.listdir(store.path(d)): continue
            cols.append(web.storage(name=d, codename=crypto.displayid(d), date=
              str(datetime.datetime.fromtimestamp(
                os.stat(store.path(d)).st_mtime
              )).split('.')[0]
            ))
        cols.sort(lambda x,y: cmp(x.date, y.date), reverse=True)

        web.header('Cache-Control', 'no-cache, no-store, must-revalidate')
        web.header('Pragma', 'no-cache')
        web.header('Expires', '-1')
        return render.index(cols)

class col:
    def GET(self, sid):
        fns = os.listdir(store.path(sid))
        docs = []
        for f in fns:
            docs.append(web.storage(
              name=f, 
              date=str(datetime.datetime.fromtimestamp(float(store.cleanname(f)))).split('.')[0]
            ))
        docs.sort(lambda x,y: cmp(x.date, y.date))
        
        haskey = bool(crypto.getkey(sid))

        web.header('Cache-Control', 'no-cache, no-store, must-revalidate')
        web.header('Pragma', 'no-cache')
        web.header('Expires', '-1')
        return render.col(docs, sid, haskey, codename=crypto.displayid(sid))
 
class doc:
    def GET(self, sid, fn):
        web.header('Content-Disposition', 'attachment; filename="' + 
          crypto.displayid(sid).replace(' ', '_') + '_' + fn + '"')

        web.header('Cache-Control', 'no-cache, no-store, must-revalidate')
        web.header('Pragma', 'no-cache')
        web.header('Expires', '-1')
        return file(store.path(sid, fn)).read()

class reply:
    def GET(self):
        raise web.seeother('/')
    
    def POST(self):
        i = web.input('sid', 'msg')
        crypto.encrypt(crypto.getkey(i.sid), i.msg, output=
          store.path(i.sid, 'reply-%s.gpg' % time.time())
        )

        web.header('Cache-Control', 'no-cache, no-store, must-revalidate')
        web.header('Pragma', 'no-cache')
        web.header('Expires', '-1')
        return render.reply(i.sid)
        

web.config.debug = False
app = web.application(urls, locals())
application = app.wsgifunc()

if __name__ == "__main__":
    app.run()
