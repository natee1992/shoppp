from Api.resources import *

from Api.views import *

regitser = Register()
regitser.regist(SessionCodeResource('code'))
regitser.regist(UserResource('userresource'))
