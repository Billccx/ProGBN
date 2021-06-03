# -*- coding: utf-8 -*-
"""
-------------------------------------------------
# @Project  :GBN_Pro
# @File     :configuration
# @Date     :2021/6/3 13:21
# @Author   :CuiChenxi
# @Email    :billcuichenxi@163.com
# @Software :PyCharm
-------------------------------------------------
"""
import random
MAX_SEQ=7
ErrorRate=0.1
LostRate=0.1
def RandomDecide(p):
    x=random.randint(1,100)
    if(x<=100*p): return True
    else: return False

