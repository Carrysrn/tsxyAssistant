import web

from webapi import score
urls = (
    '/', 'Hello',
    '/tsxy', 'score'
)

class Hello:
    def GET(self):
        return 'Success'

app = web.application(urls, globals())
application = app.wsgifunc()
# app.run()
# web.config.debug = True
