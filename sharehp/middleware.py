# -*- coding: utf-8 -*-
import cache

# build request xmanuser
class LoginSessionMiddleWare(object):
    def process_request(self, request):
        request.xmanuser = {'login': False}
        session_id = request.COOKIES.get('id')

        if session_id:
            session_data = cache.get_login_session(session_id)
            if session_data:
                request.xmanuser['login'] = True
                request.xmanuser.update(session_data)
			
		
		
