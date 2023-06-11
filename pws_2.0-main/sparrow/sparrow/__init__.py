from __future__ import absolute_import, unicode_literals


import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sparrow.settings")
django.setup()

# import schedule
# from base.util import Util
# from django.conf import settings
# from eda import api
# from inventory import scheduler_view
# import os
# import logging


# # schedule.run_continuously()
# # schedule.every(120).seconds.do(api.sch_thread_test)

# # # schedule.every(8).hours.do(Util.refresh_digikey_tokens)

# # # schedule.every(8).seconds.do(scheduler_view.run_notifications)

# # if settings.IS_VERIFIED_COMP:        
# #     logger = logging.getLogger("applog")
# #     logger.info("My name is Info2")
# #     schedule.every(10).seconds.do(api.request_supliers_price_job)
