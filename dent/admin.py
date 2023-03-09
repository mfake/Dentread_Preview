from django.contrib import admin

from dent.models import Users, Study, Patient, ServiceOrder, Refdoctor, FeedFile, Invoice, RadiologycalServices, ImageAnalysis, ImplantPlanning, Suricalguide, OtherImageFile, IOSFile, Comments, ServiceLog


# Register your models here.
admin.site.register(Invoice)
admin.site.register(FeedFile)
admin.site.register(Refdoctor)
admin.site.register(ServiceOrder)
admin.site.register(Patient)
admin.site.register(Study)
admin.site.register(Users)
admin.site.register(RadiologycalServices)
admin.site.register(ImageAnalysis)
admin.site.register(ImplantPlanning)
admin.site.register(Suricalguide)
admin.site.register(OtherImageFile)
admin.site.register(IOSFile)
admin.site.register(Comments)
admin.site.register(ServiceLog)


