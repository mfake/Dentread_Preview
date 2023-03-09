"""smartdent URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from dent import views
from django.urls import include
from django.contrib.auth import views as auth_views  



urlpatterns = [
    path('admin/', admin.site.urls),
    path( r'upload/<int:id>', views.upload, name = 'jfu_upload' ),
    path ('pdf/<int:id>', views.render_pdf_view, name='pdf'),
    path ('word/<int:id>', views.render_word_view, name='word'),
    path ('files/<int:id>', views.files, name='files'),
    path ('inviteClinic/', views.inviteClinic, name='inviteClinic'),
    path ('clinicInvitation', views.clinicInvitation, name='clinicInvitation'),
    path ('labWalletInfo', views.labWalletInfo, name='labWalletInfo'),
    path ('addToWalletBalance', views.addToWalletBalance, name='addToWalletBalance'),
    path ('activateSubscription', views.activateSubscription, name='activateSubscription'),
    path ('handlerMethod/', views.handlerMethod, name='handlerMethod'),
    
    path ('addToWalletClinic', views.addToWalletClinic, name='addToWalletClinic'),
    path ('handlerProcess/', views.handlerProcess, name='handlerProcess'),
    
    path ('markAllAsRead', views.markAllAsRead, name='markAllAsRead'),
    path ('joinLabInvitation/<int:id>/<str:invScr>', views.joinLabInvitation, name='joinLabInvitation'),
    path ('updateOrder/<int:id1>/<int:id2>', views.updateOrder, name='updateOrder'),
    path ('updateOrderImage/<int:id1>/<int:id2>', views.updateOrderImage, name='updateOrderImage'),
    path ('updateOrderGuide/<int:id1>/<int:id2>', views.updateOrderGuide, name='updateOrderGuide'),
    path ('updateOrderDigitalLab/<int:id1>/<int:id2>', views.updateOrderDigitalLab, name='updateOrderDigitalLab'),
    path ('updateOrderPlanning/<int:id1>/<int:id2>', views.updateOrderPlanning, name='updateOrderPlanning'),
    path ('orderPickup/<int:id>', views.orderPickup, name='orderPickup'),
    path ('orderPickupAvailablity/<int:id>', views.orderPickupAvailablity, name='orderPickupAvailablity'),
    path ('dataApprove/<int:id>', views.dataApprove, name='dataApprove'),
    path ('settleAccount', views.settleAccount, name='settleAccount'),
    path ('requestForImage/<int:pk>', views.requestForImage, name='requestForImage'),

    path ('fabricationComplete/<int:id>', views.fabricationComplete, name='fabricationComplete'),
    path ('fabricationCompleteSurgi/<int:id>', views.fabricationCompleteSurgi, name='fabricationCompleteSurgi'),
    
    # Lab Order Requires
    path ('allLabOrderItems/<int:id>', views.allLabOrderItems, name='allLabOrderItems'),
    path ('allLabMaterial/<int:id1>/<int:id2>', views.allLabMaterial, name='allLabMaterial'),
    path ('allLabOrderItem/<int:id1>/<int:id2>/<int:id3>', views.allLabOrderItem, name='allLabOrderItem'),
    path ('manageOrderItems/', views.manageOrderItems, name='manageOrderItems'),
    path ('addOrderItems', views.addOrderItems, name='addOrderItems'),
    path ('addFootNotes', views.addFootNotes, name='addFootNotes'),
    path ('removeLabOrderItem/<int:id>', views.removeLabOrderItem, name='removeLabOrderItem'),
    path ('editOrderItem/<int:id>', views.editOrderItem, name='editOrderItem'),
    path ('editExtraItem/<int:id>', views.editExtraItem, name='editExtraItem'),
    path ('removeExtraItem/<int:id>', views.removeExtraItem, name='removeExtraItem'),
    path ('requestForOtp', views.requestForOtp, name='requestForOtp'),
    path ('editAdmin/<int:id>', views.editAdmin, name='editAdmin'),
    path ('filess/<int:id>', views.filess, name='filess'),
    path ('self', views.self, name='self'),
    path('', views.login_dentread, name='login_dentread'),
    path('index', views.index, name='index'),
    path('index_radio', views.index_radio, name='index_radio'),
    path('index_dent/<int:id>', views.index_dent, name='index_dent'),
    path('mainSettings', views.mainSettings, name='mainSettings'),
    path('allShipment', views.allShipment, name='allShipment'),
    
    path('editBranchLab/<int:id>', views.editBranchLab, name='editBranchLab'),
    path('editBranchClinic/<int:id>', views.editBranchClinic, name='editBranchClinic'),
    
    path('image_Orders/<int:id>', views.image_Orders, name='image_Orders'),
    path('radiological_Details/<int:id1>/<int:id2>', views.radiological_Details, name = 'radiological_Details'),
    path('case_Details/<int:id1>/<int:id2>', views.case_Details, name = 'case_Details'),
    path('case_DetailsGuide/<int:id1>/<int:id2>', views.case_DetailsGuide, name = 'case_DetailsGuide'),
    path('case_DetailsLab/<int:id1>/<int:id2>', views.case_DetailsLab, name = 'case_DetailsLab'),
    
    path('case_DetailsPlanning/<int:id1>/<int:id2>', views.case_DetailsPlanning, name = 'case_DetailsPlanning'),
    path('planning_Orders/<int:id>', views.planning_Orders, name='planning_Orders'),
    path('remark/<int:id>', views.remark, name='remark'),
    path('add_invest/<int:id>', views.add_invest, name='add_invest'),
    path('addservice_order_image/<int:id1>/<int:id2>/<int:id3>', views.addservice_order_image, name='addservice_order_image'),
    path('addservice_order_planning/<int:id1>/<int:id2>/<int:id3>', views.addservice_order_planning, name='addservice_order_planning'),
    path('orthancdownload/<int:id>', views.orthancdownload, name='orthancdownload'),
    path('orthancdownloadImage/<int:id>', views.orthancdownloadImage, name='orthancdownloadImage'),
    path('orthancdownloadGuide/<int:id>/<str:myreq>', views.orthancdownloadGuide, name='orthancdownloadGuide'),
    path('orthancdownloadPlanning/<int:id>', views.orthancdownloadPlanning, name='orthancdownloadPlanning'),
    path('downloadDicommm/<int:id>', views.downloadDicommm, name='downloadDicommm'),
    path('index_today', views.index_today, name='index_today'),


    path('orthanctest', views.orthanctest, name='orthanctest'),

    path('updateNotificationRead/<int:id>/<path:hyper>', views.updateNotificationRead, name='updateNotificationRead'),

    path('index_yesterday', views.index_yesterday, name='index_yesterday'),
    path('cstlogin', views.cstlogin, name='cstlogin'),
    path('get_selfpt', views.get_selfpt, name='get_selfpt'),
    path('plsummary', views.plsummary, name='plsummary'),
    path('cstloginhandle', views.cstloginhandle, name='cstloginhandle'),
    path('cstdashboard', views.cstdashboard, name='cstdashboard'),
    path('referpt', views.referpt, name='referpt'),
    path('addreferpt_radio', views.addreferpt_radio, name='addreferpt_radio'),
    path('allrefpt', views.allrefpt, name='allrefpt'),
    path('allrefpt_dent', views.allrefpt_dent, name='allrefpt_dent'),
    path ('reftopt/<int:id>', views.reftopt, name='reftopt'),
    path ('reftopt_dent/<int:id>', views.reftopt_dent, name='reftopt_dent'),
    path ('refptservice_order/<int:id>', views.refptservice_order, name='refptservice_order'),
    path('uploaddcm', views.uploaddcm, name='uploaddcm'),
    path('download_file/<int:id>', views.download_file, name='download_file'),
    path('download_imaging/<int:id>', views.download_imaging, name='download_imaging'),
    path('download_file_dent/<int:id>', views.download_file_dent, name='download_file_dent'),

    path ('adddcmfiles/<int:id>', views.adddcmfiles, name='adddcmfiles'),
    path ('addclinicfiles/<int:id>', views.addclinicfiles, name='addclinicfiles'),
    path ('adddcmpt/<int:id>', views.adddcmpt, name='adddcmpt'),
    path ('edit_user/<int:id>', views.edit_user, name='edit_user'),
    path ('edit_user_dent/<int:id>', views.edit_user_dent, name='edit_user_dent'),
    path ('edit_user_clinic/<int:id>', views.edit_user_clinic, name='edit_user_clinic'),
    path ('download/<int:id>', views.download, name='download'),
    path ('userdetails/<int:id>', views.userdetails, name='userdetails'),

    path ('token', views.token, name='token'),

    path('logouthandle', views.logouthandle, name='logouthandle'),
    path('createpatient', views.createpatient, name='createpatient'),
    path('createpatient_vid', views.createpatient_vid, name='createpatient_vid'),
    path('createdoctor', views.createdoctor, name='createdoctor'),
    path('createdoctor_modal', views.createdoctor_modal, name='createdoctor_modal'),
    path('createuser', views.createuser, name='createuser'),
    path('createuser_dent', views.createuser_dent, name='createuser_dent'),
    path('createorganaization', views.createorganaization, name='createorganaization'),
    path('createstudy', views.createstudy, name='createstudy'),
    path('createstudy_modal', views.createstudy_modal, name='createstudy_modal'),
    path('orginvoices/<int:id>', views.orginvoices, name='orginvoices'),
    
    # Admin Updates For All Services Are Here
    path('adminUpdates/<int:id1>/<int:id2>', views.adminUpdates, name='adminUpdates'),
    path('adminUpdatesImage/<int:id1>/<int:id2>', views.adminUpdatesImage, name='adminUpdatesImage'),
    path('adminUpdatesPlanning/<int:id1>/<int:id2>', views.adminUpdatesPlanning, name='adminUpdatesPlanning'),
    path('adminUpdatesGuide/<int:id1>/<int:id2>', views.adminUpdatesGuide, name='adminUpdatesGuide'),


    path('createstudy_dent', views.createstudy_dent, name='createstudy_dent'),
    path('patientdetails/<int:pk>', views.patientdetails, name='patientdetails'),
    path('patientdetails_dent/<int:id>', views.patientdetails_dent, name='patientdetails_dent'),
    path('delete_refpt/<int:id>', views.delete_refpt, name='delete_refpt'),
    path('adminComment/<int:id1>/<int:id2>', views.adminComment, name='adminComment'),
    path('adminCommentImage/<int:id1>/<int:id2>', views.adminCommentImage, name='adminCommentImage'),
    path('adminCommentPlanning/<int:id1>/<int:id2>', views.adminCommentPlanning, name='adminCommentPlanning'),
    path('adminCommentGuide/<int:id1>/<int:id2>', views.adminCommentGuide, name='adminCommentGuide'),
    path('adminCommentLab/<int:id1>/<int:id2>', views.adminCommentLab, name='adminCommentLab'),

    # Redirect Services Are Here
    path('refer_dentread/<int:id1>/<int:id2>', views.refer_dentread, name='refer_dentread'),
    path('refer_services/<int:pk>/<int:id2>', views.refer_services, name='refer_services'),
    path('refer_service/<int:pk>/<int:id2>', views.refer_service, name='refer_service'),
    
    #All Refer Services Are Here
    path('refer_RadiologicalService/<int:id1>/<int:id2>', views.refer_RadiologicalService, name='refer_RadiologicalService'),
    path('refer_ImageAnalysis/<int:id1>/<int:id2>', views.refer_ImageAnalysis, name='refer_ImageAnalysis'),
    path('refer_ImplantPlanning/<int:id1>/<int:id2>', views.refer_ImplantPlanning, name='refer_ImplantPlanning'),
    path('refer_dentlab/<int:id1>/<int:id2>', views.refer_dentlab, name='refer_dentlab'),
    path('editDentlab/<int:id1>/<int:id2>', views.editDentlab, name='editDentlab'),
    path('refer_surgident/<int:id1>/<int:id2>', views.refer_surgident, name='refer_surgident'),
    

    path('orthancdownloadGuideSecond/<int:id>', views.orthancdownloadGuideSecond, name='orthancdownloadGuideSecond'),

    # All Order Comment
    path('radioOrderComment/<int:id1>/<int:id2>', views.radioOrderComment, name='radioOrderComment'),
    path('imageOrderComment/<int:id1>/<int:id2>', views.imageOrderComment, name='imageOrderComment'),
    path('guideOrderComment/<int:id1>/<int:id2>', views.guideOrderComment, name='guideOrderComment'),
    path('planningOrderComment/<int:id1>/<int:id2>', views.planningOrderComment, name='planningOrderComment'),
    path('labOrderComment/<int:id1>/<int:id2>', views.labOrderComment, name='labOrderComment'),
    
    path('clinicComment/<int:id>', views.clinicComment, name='clinicComment'),
    path('clinicCommentImage/<int:id>', views.clinicCommentImage, name='clinicCommentImage'),
    path('clinicSideCommment/<int:id>', views.clinicSideCommment, name='clinicSideCommment'),
    path('uploadOtherFiles/<int:pk>/<int:id1>/<int:id2>', views.uploadOtherFiles, name='uploadOtherFiles'),

    path('delete_ImageAnalysisId/<int:id>', views.delete_ImageAnalysisId, name='delete_ImageAnalysisId'),
    path('delete_ImplantPlanningId/<int:id>', views.delete_ImplantPlanningId, name='delete_ImplantPlanningId'),
    path('delete_RadiologicalId/<int:id>', views.delete_RadiologicalId, name='delete_RadiologicalId'),
    path('delete_GuideId/<int:id>', views.delete_GuideId, name='delete_GuideId'),

    path('review_order/<int:id1>/<int:id2>', views.review_order, name='review_order'),
    path('reviewLabOrder/<int:id1>/<int:id2>', views.reviewLabOrder, name='reviewLabOrder'),
    path('checkForReview/<int:id1>/<int:id2>', views.checkForReview, name='checkForReview'),
    
    path('review_PlanningOrder/<int:id1>/<int:id2>', views.review_PlanningOrder, name='review_PlanningOrder'),
    path('review_RadioOrder/<int:id1>/<int:id2>', views.review_RadioOrder, name='review_RadioOrder'),
    path('review_GuideOrder/<int:id1>/<int:id2>', views.review_GuideOrder, name='review_GuideOrder'),

    path("edit_Image/<int:id1>/<int:id2>", views.edit_Image, name="edit_Image"),
    path("edit_Planning/<int:id1>/<int:id2>", views.edit_Planning, name="edit_Planning"),
    path("edit_Radio/<int:id1>/<int:id2>", views.edit_Radio, name="edit_Radio"),
    path("edit_Surgident/<int:id1>/<int:id2>", views.edit_Surgident, name="edit_Surgident"),

    path('labOrderCommentClinic/<int:id>', views.labOrderCommentClinic, name='labOrderCommentClinic'),
    path('add_appointment', views.add_appointment, name='add_appointment'),
    path('patientdetail', views.patientdetail, name='patientdetail'),
    path('delete_pros/<int:id>', views.delete_pros, name='delete_pros'),
    path('deleteOrder/<int:id>', views.deleteOrder, name='deleteOrder'),
    
    path('uploadguide_data/<int:id>', views.uploadguide_data, name='uploadguide_data'),

    path('directTargetedStatus/<str:service>/<str:status>/<str:date>', views.directTargetedStatus, name='directTargetedStatus'),
    path('directTargetedStatusToLab/<str:service>/<str:status>/<str:date>/<str:item>', views.directTargetedStatusToLab, name='directTargetedStatusToLab'),
    path('directTargetedStatusToDentread/<str:service>/<str:status>/<str:date>', views.directTargetedStatusToDentread, name='directTargetedStatusToDentread'),
    
    path('lab_status/<int:id>', views.lab_status, name='lab_status'),
    path('surgi_status/<int:id>', views.surgi_status, name='surgi_status'),
    path('radiological_status/<int:id>', views.radiological_status, name='radiological_status'),
    path('imageAnalysis_status/<int:id>', views.imageAnalysis_status, name='imageAnalysis_status'),
    path('implantPlanning_status/<int:id>', views.implantPlanning_status, name='implantPlanning_status'),
    path('guideStatus/<int:id>', views.guideStatus, name='guideStatus'),
    path('DigitalLabStatus/<int:id>', views.DigitalLabStatus, name='DigitalLabStatus'),
    
    path('update_order/<int:id>', views.update_order, name='update_order'),
    path('update_surgi/<int:id>', views.update_surgi, name='update_surgi'),
    path('view_orderdent/<int:id>', views.view_orderdent, name='view_orderdent'),
    path('view_surgident/<int:id>', views.view_surgident, name='view_surgident'),
    path('downloadios/<int:id>', views.downloadios, name='downloadios'),
    path('downloadOtherImage/<int:id>', views.downloadOtherImage, name='downloadOtherImage'),
    path('cancel_case/<int:id>', views.cancel_case, name='cancel_case'),
    path('post_comment/<int:id>', views.post_comment, name='post_comment'),
    path('lab_post_comment/<int:id>', views.lab_post_comment, name='lab_post_comment'),
    path('radio_post_comment/<int:id>', views.radio_post_comment, name='lab_post_comment'),
    path('image_post_comment/<int:id>', views.image_post_comment, name='image_post_comment'),
    path('implantPlanning_post_comment/<int:id>', views.implantPlanning_post_comment, name='implantPlanning_post_comment'),
    path('guidePostComment/<int:id>', views.guidePostComment, name='guidePostComment'),
    path('digitalLabComment/<int:id>', views.digitalLabComment, name='digitalLabComment'),

    path('updateUnit/<int:pk>/<int:unit>/<int:id>', views.updateUnit, name='updateUnit'),

    path('lab_orders/<int:id>', views.lab_orders, name='lab_orders'),

    path('guide_orders/<int:id>', views.guide_orders, name='guide_orders'),
    path('service_ordering', views.service_ordering, name='service_ordering'),
    path('createservice_order', views.createservice_order, name='createservice_order'),
    path('addpatient', views.addpatient, name='addpatient'),
    path('orgprofile', views.orgprofile, name='orgprofile'),
    path('orgprofile_dent', views.orgprofile_dent, name='orgprofile_dent'),
    path('orgprofile_clinic', views.orgprofile_clinic, name='orgprofile_clinic'),
    path('editorgprofile_clinic', views.editorgprofile_clinic, name='editorgprofile_clinic'),
    path('editorgprofile_cust/<int:id>', views.editorgprofile_cust, name='editorgprofile_cust'),
    path('editorgprofile', views.editorgprofile, name='editorgprofile'),
    path('editorgprofile_dent', views.editorgprofile_dent, name='editorgprofile_dent'),

    path('service_order_print/<int:pk>/<int:id>', views.service_order_print, name='service_order_print'),
    path('viewRadiologyReport/<int:pk>/<int:id>', views.viewRadiologyReport, name='viewRadiologyReport'),
    
    path('download_report_radio/<int:pk>/<int:id>', views.download_report_radio, name='download_report_radio'),
    path('download_report_image/<int:pk>/<int:id>', views.download_report_image, name='download_report_image'),
    path('download_report_planning/<int:pk>/<int:id>', views.download_report_planning, name='download_report_planning'),
    # path('downloadStlLab/<int:pk>/<int:id>', views.downloadStlLab, name='downloadStlLab'),


    path('add_org', views.add_org, name='add_org'),
    path('showpatients', views.showpatients, name='showpatients'),
    # path('currently_added_patients', views.currently_added_patients, name='showpatients'),
    
    path('showpatients_dent', views.showpatients_dent, name='showpatients_dent'),
    path('allusers', views.allusers, name='allusers'),
    path('allusers_dent', views.allusers_dent, name='allusers_dent'),
    path('allusers_clinic', views.allusers_clinic, name='allusers_clinic'),
    path('allorg', views.allorg, name='allorg'),
    path('showdoctors', views.showdoctors, name='showdoctors'),
    path('showstudies', views.showstudies, name='showstudies'),
    path('showstudies_dent', views.showstudies_dent, name='showstudies_dent'),
    path('doctor_detail/<int:id>', views.doctor_detail, name='doctor_detail'),
    path('createcompany', views.createcompany, name='createcompany'),
    path('addinvoice', views.addinvoice, name='addinvoice'),
    path('business', views.business, name='business'),
    path('business_yesterday', views.business_yesterday, name='business_yesterday'),
    path('business_thisweek', views.business_thisweek, name='business_thisweek'),
    path('tinymce/', include('tinymce.urls')),
    path('addservice_order/<int:id>', views.addservice_order, name='addservice_order'),
    path('addservice_order_radio/<int:id>', views.addservice_order_radio, name='addservice_order_radio'),
    path('orgdetails/<int:id>', views.orgdetails, name='orgdetails'),


    path('addservice_order_dent/<int:id1>/<int:id2>/<int:id3>', views.addservice_order_dent, name='addservice_order_dent'),

    path('addfilesGuide/<int:pk>/<int:id>', views.addfilesGuide, name='addfilesGuide'),
    path('addfilesGuideDigital/<int:pk>/<int:id>', views.addfilesGuideDigital, name='addfilesGuideDigital'),
    path('addfilesGuideDigitalAgain/<int:id1>/<int:id2>', views.addfilesGuideDigitalAgain, name='addfilesGuideDigitalAgain'),
    path('addfiles/<int:pk>/<int:id>', views.addfiles, name='addfiles'),
    path('addfilesImage/<int:pk>/<int:id>', views.addfilesImage, name='addfilesImage'),
    path('addfilesPlanning/<int:pk>/<int:id>', views.addfilesPlanning, name='addfilesPlanning'),
    path('addinventory/<int:id>', views.addinventory, name='addinventory'),
    path('delete_patient/<int:id>', views.delete_patient, name='delete_patient'),
    path('delete_patient_dent/<int:id>', views.delete_patient_dent, name='delete_patient_dent'),
    path('delete_user/<int:id>', views.delete_user, name='delete_user'),
    path('edit_patient/<int:id>', views.edit_patient, name='edit_patient'),
    path('edit_patient_dent/<int:id>', views.edit_patient_dent, name='edit_patient_dent'),
    path('edit_invoice/<int:id>', views.edit_invoice, name='edit_invoice'),
    path('edit_invoice_dent/<int:id>', views.edit_invoice_dent, name='edit_invoice_dent'),
    path('edit_doctor/<int:id>', views.edit_doctor, name='edit_doctor'),
    path('edit_study/<int:id>', views.edit_study, name='edit_study'),
    path('edit_study_dent/<int:id>', views.edit_study_dent, name='edit_study_dent'),
    path('edit_pack/<int:id>', views.edit_pack, name='edit_pack'),
    path('edit_module/<int:id>', views.edit_module, name='edit_module'),
    path('delete_invoice/<int:id>', views.delete_invoice, name='delete_invoice'),
    path('delete_doctor/<int:id>', views.delete_doctor, name='delete_doctor'),
    path('delete_pack/<int:id>', views.delete_pack, name='delete_pack'),
    path('delete_study/<int:id>', views.delete_study, name='delete_study'),
    path('delete_module/<int:id>', views.delete_module, name='delete_module'),
    path('delete_org/<int:id>', views.delete_org, name='delete_org'),
    path('delete_inv_item/<int:id>', views.delete_inv_item, name='delete_inv_item'),
    path('delete_item/<int:id>', views.delete_item, name='delete_item'),
    path('delete_expense/<int:id>', views.delete_expense, name='delete_expense'),
    path('invoice_print/<int:id>', views.invoice_print, name='invoice_print'),
    path('service_ordering/<int:id>', views.service_ordering, name='service_ordering'),
    path('service_ordering_radio/<int:id>', views.service_ordering_radio, name='service_ordering_radio'),
    
    path('service_ordering_dent/<int:id1>/<int:id2>/<int:id3>', views.service_ordering_dent, name='service_ordering_dent'),
    path('service_ordering_image/<int:id1>/<int:id2>/<int:id3>', views.service_ordering_image, name='service_ordering_image'),
    path('createGuideReport/<int:id1>/<int:id2>/<int:id3>', views.createGuideReport, name='createGuideReport'),
    
    
    path('service_ordering_planning/<int:id1>/<int:id2>/<int:id3>', views.service_ordering_planning, name='service_ordering_planning'),
    path('upload/<int:id>', views.upload, name='upload'),
    path('label_print/<int:id>', views.label_print, name='label_print'),
    path('edit_appointment/<int:id>', views.edit_appointment, name='edit_appointment'),
    path('self_appointment', views.self_appointment, name='self_appointment'),
    path('allcstpatient', views.allcstpatient, name='allcstpatient'),
    path('cstptservice_order/<int:id>', views.cstptservice_order, name='cstptservice_order'),
    path('cancelOrder/<int:id>', views.cancelOrder, name='cancelOrder'),
    
    path('ajaxUrl/', views.ajaxUrl, name='ajaxUrl'),
    path('file_delete/<int:id>', views.file_delete, name='file_delete'),
    path('ios_delete/<int:id>', views.ios_delete, name='ios_delete'),
    path('feedFile_delete/<int:id>', views.feedFile_delete, name='feedFile_delete'),
    path('dcmfile_delete/<int:id>', views.dcmfile_delete, name='dcmfile_delete'),
    path('add_user', views.add_user, name='add_user'),
    path('add_user_dent', views.add_user_dent, name='add_user_dent'),
    path('additem', views.additem, name='additem'),
    path('index_search', views.index_search, name='index_search'),
    path('patient_search', views.patient_search, name='patient_search'),
    path('myprofile_clinic', views.myprofile_clinic, name='myprofile_clinic'),
    path('myprofile_radio', views.myprofile_radio, name='myprofile_radio'),
    path('myprofile', views.myprofile, name='myprofile'),
    path('myprofile_dent', views.myprofile_dent, name='myprofile_dent'),
    path('editprofile', views.editprofile, name='editprofile'),
    path('editprofile_dent', views.editprofile_dent, name='editprofile_dent'),
    path('editprofile_radio', views.editprofile_radio, name='editprofile_radio'),
    path('editprofile_clinic', views.editprofile_clinic, name='editprofile_clinic'),

    path('download_file_radio/<int:id>', views.download_file_radio, name='download_file_radio'),
    path('refer_dent', views.refer_dent, name='refer_dent'),
    path('refer_case', views.refer_case, name='refer_case'),
    path('add_patient/<int:id>', views.add_patient, name='add_patient'),
    path('sendmail_clinic/<int:id1>/<int:id2>', views.sendmail_clinic, name='sendmail_clinic'),
    path('sendmail_ImageService/<int:id1>/<int:id2>', views.sendmail_ImageService, name='sendmail_ImageService'),
    path('sendmail_ImplantPlanning/<int:id1>/<int:id2>', views.sendmail_ImplantPlanning, name='sendmail_ImplantPlanning'),
    path('add_patient_only', views.add_patient_only, name='add_patient_only'),

    path('saveitem', views.saveitem, name='saveitem'),
    path('allitems', views.allitems, name='allitems'),
    path('assign/<int:id>', views.assign, name='assign'),
    path('main_pdf/<int:id>', views.main_pdf, name='main_pdf'),
    path('pdfReport/<int:id1>/<int:id2>', views.pdfReport, name='pdfReport'),
    path('myMail', views.myMail, name='myMail'),
    path('sendmail/<int:id>', views.sendmail, name='sendmail'),
    path('sendmail_radio/<int:id1>/<int:id2>/<int:id3>', views.sendmail_radio, name='sendmail_radio'),
    path('sendmail_image/<int:id1>/<int:id2>/<int:id3>', views.sendmail_image, name='sendmail_image'),
    path('sendmail_planning/<int:id1>/<int:id2>/<int:id3>', views.sendmail_planning, name='sendmail_planning'),
    
    path('cust_summary', views.cust_summary, name='cust_summary'),
    path('addexpenses', views.addexpenses, name='addexpenses'),
    path('allexpenses', views.allexpenses, name='allexpenses'),
    path('allinvoices', views.allinvoices, name='allinvoices'),
    path('getservice_order', views.getservice_order, name='getservice_order'),
    path('r', views.getservice_order, name='getservice_order'),
    path('todo', views.todo, name='todo'),
    path('dent_invoices', views.dent_invoices, name='dent_invoices'),
    path('self', views.self, name='self'),


    path('invoices', views.invoices, name='invoices'),
    path('cstbusiness_dent', views.cstbusiness_dent, name='cstbusiness_dent'),
    path('cstbusiness_radio', views.cstbusiness_radio, name='cstbusiness_radio'),
    path('delete_dcm', views.delete_dcm, name='delete_dcm'),
    path('cstlogouthandle', views.cstlogouthandle, name='cstlogouthandle'),
    path('assign_case', views.assign_case, name='assign_case'),
    path('assign_case_dent/<int:id>', views.assign_case_dent, name='assign_case_dent'),
    path('assign_case_image/<int:id>', views.assign_case_image, name = 'assign_case_image'),
    path('assignCaseGuide/<int:id>', views.assignCaseGuide, name = 'assignCaseGuide'),
    path('assignCaseLab/<int:id>', views.assignCaseLab, name = 'assignCaseLab'),
    path('saveShipmentDetails/<int:id>', views.saveShipmentDetails, name = 'saveShipmentDetails'),
    path('createShipmentOrder/<int:id>', views.createShipmentOrder, name = 'createShipmentOrder'),
    path('requestForAWB/<int:id>', views.requestForAWB, name = 'requestForAWB'),
    path('generatePickUp/<int:id>', views.generatePickUp, name = 'generatePickUp'),
    
    path('assign_case_planning/<int:id>', views.assign_case_planning, name = 'assign_case_planning'),
    path('filter', views.filter, name='filter'),
    path('posturl', views.posturl, name='posturl'),
    path('marksent/<int:id>', views.marksent, name='marksent'),
    path('service_order_delete/<int:id>', views.service_order_delete, name='service_order_delete'),
    path('check_pdf', views.check_pdf, name='check_pdf'),
    path('drprofile', views.drprofile, name='drprofile'),
    path('inventory', views.inventory, name='inventory'),
    path('ref_invoices', views.ref_invoices, name='ref_invoices'),
    path('checkCreatePdf/<int:id1>/<int:id2>', views.checkCreatePdf, name='checkCreatePdf'),
    path('updateservice_order/', views.updateservice_order, name='updateservice_order'),
    path('updateservice_orders/<int:id1>/<int:id2>', views.updateservice_orders, name='updateservice_order'),
    path('driveresp/', views.driveresp, name='driveresp'),
    path('render_pdf_view/<int:id>', views.render_pdf_view, name='render_pdf_view'),
    path('add_inv_item', views.add_inv_item, name='add_inv_item'),
    path('addsign', views.addsign, name='addsign'),
    path('appointments', views.appointments, name='appointments'),
    path('delete_appointment/<int:id>', views.delete_appointment, name='delete_appointment'),
    path('appoint_patient/<int:id>', views.appoint_patient, name='appoint_patient'),

    path ('login_dentread', views.login_dentread, name='login_dentread'),
    path ('reg_choose_prof', views.reg_choose_prof, name='reg_choose_prof'),
    path ('imaging_reg', views.imaging_reg, name='imaging_reg'),
    path ('clinic_reg', views.clinic_reg, name='clinic_reg'),
    path ('lab_reg', views.lab_reg, name='lab_reg'),
    path ('radio_reg', views.radio_reg, name='radio_reg'),
    path ('login_imaging', views.login_imaging, name='login_imaging'),
    path ('login_clinic', views.login_clinic, name='login_clinic'),
    path ('branchServiceDetails/<int:id>', views.branchServiceDetails, name='branchServiceDetails'),
    path ('login_radio', views.login_radio, name='login_radio'),
    path ('login_lab', views.login_lab, name='login_lab'),
    path ('lab_order', views.lab_order, name='lab_order'),
    path ('allinvites', views.allinvites, name='allinvites'),
    path ('login_domain', views.login_domain, name='login_domain'),
    path ('dashboard_imaging', views.dashboard_imaging, name='dashboard_imaging'),
    path ('dashboard_clinic', views.dashboard_clinic, name='dashboard_clinic'),
    path ('dashboard_domain', views.dashboard_domain, name='dashboard_domain'),
    path ('domain', views.domain, name='domain'),
    path ('all_imaging', views.all_imaging, name='all_imaging'),
    path ('all_clinic', views.all_clinic, name='all_clinic'),
    path ('all_radio', views.all_radio, name='all_radio'),

    path ('domain_reg', views.domain_reg, name='domain_reg'),
    path ('all_settings', views.all_settings, name='all_settings'),


    path ('addmodule', views.addmodule, name='addmodule'),
    path ('allmodules', views.allmodules, name='allmodules'),

    path ('addpack', views.addpack, name='addpack'),
    path ('allpacks', views.allpacks, name='allpacks'),

    path ('dentread_services', views.dentread_services, name='dentread_services'),
    path ('imaging_services', views.imaging_services, name='imaging_services'),
    path ('mysubs_imaging', views.mysubs_imaging, name='mysubs_imaging'),
    path ('buysubs_imaging', views.buysubs_imaging, name='buysubs_imaging'),
    path ('dent_services', views.dent_services, name='dent_services'),
    path ('uploaddcm_radio', views.uploaddcm_radio, name='uploaddcm_radio'),
    path('addOtherImages/<int:id>', views.addOtherImages, name='uploadotherimages'),


    path ('radiology_services/<int:id>', views.radiology_services, name='radiology_services'),
    path ('lab_services/<int:id>', views.lab_services, name='lab_services'),
    path ('guide_services/<int:id>', views.guide_services, name='guide_services'),
    path ('image_services/<int:id>', views.image_services, name='image_services'),
    path('implant_services/<int:id>', views.implant_services, name='implant_services'),

    # Upload Files From Here
    path ('addiosfiles/<int:id>', views.addiosfiles, name='addiosfiles'),
    path ('uploadimage/<int:pk>', views.uploadimage, name='uploadimage'),
    path ('updateimageFile/<int:pk>', views.updateimageFile, name='updateimageFile'),
    path ('uploadImageAnalysis/<int:pk>/<int:id1>', views.uploadImageAnalysis, name='uploadImageAnalysis'),
    path ('uploadGuideData/<int:pk>/<int:id1>', views.uploadGuideData, name='uploadGuideData'),
    path ('updateImageAnalysisFile/<int:pk>/<int:id1>', views.updateImageAnalysisFile, name='updateImageAnalysisFile'),
    path ('uploadPlanningImage/<int:pk>/<int:id1>', views.uploadPlanningImage, name='uploadPlanningImage'),
    path ('updatePlanningImage/<int:pk>', views.updatePlanningImage, name='updatePlanningImage'),
    path ('updateGuideImage/<int:pk>/<int:id1>', views.updateGuideImage, name='updateGuideImage'),
    
    # View Uploaded Image Files
    path ('viewImage/<int:pk>', views.viewImage, name='viewImage'),
    path ('viewUploadedImage/<int:pk>', views.viewUploadedImage, name='viewUploadedImage'),
    path ('viewUploadedGuideData/<int:pk>/<int:id1>', views.viewUploadedGuideData, name='viewUploadedGuideData'),
    path ('viewPlanningImage/<int:pk>', views.viewPlanningImage, name='viewPlanningImage'),
    path ('viewGuideImage/<int:pk>/<int:id1>', views.viewGuideImage, name='viewGuideImage'),

    path ('downloadLabPlanPdf/<int:pk>/<int:id1>/<int:id2>', views.downloadLabPlanPdf, name='downloadLabPlanPdf'),

    
    
    path ('ViewImagePDF/<int:pk>/<int:id>', views.ViewImagePDF, name='ViewImagePDF'),
    path ('ViewGuidePDF/<int:pk>/<int:id>', views.ViewGuidePDF, name='ViewGuidePDF'),
    path ('ViewGuideLabPDF/<int:pk>/<int:id>', views.ViewGuideLabPDF, name='ViewGuideLabPDF'),

    path ('ViewPlanningPDF/<int:pk>/<int:id>', views.ViewPlanningPDF, name='ViewPlanningPDF'),
    path ('ViewRadioImagePDF/<int:pk>/<int:id>', views.ViewRadioImagePDF, name='ViewRadioImagePDF'),
    path ('viewGuideData/<int:pk>/<int:id1>', views.viewGuideData, name='viewGuideData'),
    path ('viewReUploadedLabData/<int:pk>/<int:id1>/<int:id2>', views.viewReUploadedLabData, name='viewReUploadedLabData'),
    
   
    path('downloadGuidePdf/<int:pk>/<int:id1>/<int:id2>', views.downloadGuidePdf, name='downloadGuidePdf'),
    path('downloadStlLab/<int:pk>/<int:id1>/<int:id2>', views.downloadStlLab, name='downloadStlLab'),
    path('downloadStlDigitalLab/<int:pk>/<int:id1>/<int:id2>', views.downloadStlDigitalLab, name='downloadStlDigitalLab'),

    path ('uploadGuideDataAgain/<int:id1>/<int:id2>', views.uploadGuideDataAgain, name='uploadGuideDataAgain'),
    # path ('uploadLabDataAgain/<int:id>', views.uploadLabDataAgain, name='uploadLabDataAgain'),
    
    path ('uploadDcmFile/<int:pk>', views.uploadDcmFile, name='uploadDcmFile'),
    path ('updateDcmFileRadio/<int:pk>', views.updateDcmFileRadio, name='updateDcmFileRadio'),
    path ('uploadGuideDcmFileAgain/<int:pk>/<int:id>', views.uploadGuideDcmFileAgain, name='uploadGuideDcmFileAgain'),
    path ('updateDcmFileImage/<int:pk>', views.updateDcmFileImage, name='updateDcmFileImage'),
    path ('planningDcmFileUpload/<int:pk>', views.planningDcmFileUpload, name='planningDcmFileUpload'),
    path ('guideDcmFileUpload/<int:pk>', views.guideDcmFileUpload, name='guideDcmFileUpload'),
    path ('guideDcmFileUploadSecond/<int:pk>', views.guideDcmFileUploadSecond, name='guideDcmFileUploadSecond'),
    path ('guideDcmFileUploadSecondAgain/<int:pk>/<int:id>', views.guideDcmFileUploadSecondAgain, name='guideDcmFileUploadSecondAgain'),
    
    path ('profileDetails', views.profileDetails, name='profileDetails'),
    path ('changeUserPwd', views.changeUserPwd, name='changeUserPwd'),
    path ('editUserProfile', views.editUserProfile, name='editUserProfile'),
    path ('editMyProfile/<int:id>', views.editMyProfile, name='editMyProfile'),
    
    path ('editBranchProfile/<int:id>', views.editBranchProfile, name='editBranchProfile'),
    path ('editManagerDetails/<int:id1>/<int:id2>', views.editManagerDetails, name='editManagerDetails'),
    
    path ('fullBranchDetails/<int:id>', views.fullBranchDetails, name='fullBranchDetails'),
    path('viewStl/<int:id>/<int:id1>/<int:id2>/<str:site>/<str:fileName>', views.viewStl, name='viewStl'),

    # path ('payment/<int:id>', views.payment, name='payment'),
    path ('refer_partner/<int:id>', views.refer_partner, name='refer_partner'),
    path ('partner_order/<int:id1>/<int:id2>', views.partner_order, name='partner_order'),
    
    #Update Status
    path ('updateFileStatusFirst/<int:id1>/<int:id2>', views.updateFileStatusFirst, name='updateFileStatusFirst'),
    path ('updateFileStatusSecond/<int:id1>/<int:id2>', views.updateFileStatusSecond, name='updateFileStatusSecond'),
    path ('iosFileStatusGuide/<int:id1>/<int:id2>', views.iosFileStatusGuide, name='iosFileStatusGuide'),
    # path ('feedFileStatus/<int:id1>/<int:id2>', views.feedFileStatus, name='feedFileStatus'),

    path ('addfilesGuideAgain/<int:pk>/<int:id1>/<int:id2>', views.addfilesGuideAgain, name='addfilesGuideAgain'),

    path('orderDeliver/<int:id1>/<int:id2>', views.orderDeliver, name='orderDeliver'),
    path('orderDeliverDigital/<int:id1>/<int:id2>', views.orderDeliverDigital, name='orderDeliverDigital'),

    path('orderDispatch/<int:id1>/<int:id2>', views.orderDispatch, name='orderDispatch'),
    path('orderDispatchDigital/<int:id1>/<int:id2>', views.orderDispatchDigital, name='orderDispatchDigital'),

    path ('uploadGuideDesign/<int:pk>/<int:id1>', views.uploadGuideDesign, name='uploadGuideDesign'),

    path ('uploadGuideDesignAgain/<int:pk>/<int:id1>/<int:id2>', views.uploadGuideDesignAgain, name='uploadGuideDesignAgain'),

    path ('viewGuideDesignAPI/<int:pk>/<int:id1>', views.viewGuideDesignAPI, name='viewGuideDesignAPI'),

    path('downloaGuideDesign/<int:pk>/<int:id1>/<int:id2>', views.downloaGuideDesign, name='downloaGuideDesign'),

    path ('accountStatement', views.accountStatement, name='accountStatement'),
    path ('partnerBusinessReport', views.partnerBusinessReport, name='partnerBusinessReport'),
    path ('iosFileStatus/<int:id1>/<int:id2>', views.iosFileStatus, name='iosFileStatus'),
    path ('feedFileStatus/<int:pk>/<int:id>', views.feedFileStatus, name='feedFileStatus'),
    path ('feedFileDigitalStatus/<int:id1>/<int:id2>', views.feedFileDigitalStatus, name='feedFileDigitalStatus'),
    # Notification
    path("notification", views.notification, name = "notification"),
    path("notificationNumber", views.notificationNumber, name = "notificationNumber"),
    
    # API For Dicom Data
    path ('dicomAPI/<int:pk>', views.dicomAPI, name='dicomAPI'),
    path ('planningDicomAPI/<int:pk>/<int:id1>', views.planningDicomAPI, name='planningDicomAPI'),
    path ('imageDicomAPI/<int:pk>/<int:id1>', views.imageDicomAPI, name='imageDicomAPI'),
    path ('guideDicomAPI/<int:pk>/<int:id1>', views.guideDicomAPI, name='guideDicomAPI'),

    path ('accept_invite/<int:id>', views.accept_invite, name='accept_invite'),
    path ('holdOrder/<int:id>', views.holdOrder, name='holdOrder'),
    
    path ('deny_invite/<int:id>', views.deny_invite, name='deny_invite'),
    path ('addcentre_radio', views.addcentre_radio, name='addcentre_radio'),
    path ('allcentres_radio', views.allcentres_radio, name='allcentres_radio'),
    path ('goback', views.goback, name='goback'),
    path ('reset_pwd', views.reset_pwd, name='reset_pwd'),
    path ('pwdChange', views.pwdChange, name='pwdChange'),
    path ('addUserClinicNew', views.addUserClinicNew, name='addUserClinicNew'),
    
    path ('editcentre_radio/<int:id>', views.editcentre_radio, name='editcentre_radio'),
    path ('deletecentre_radio/<int:id>', views.deletecentre_radio, name='deletecentre_radio'),
    path ('adddcmfiles_radio/<int:id>', views.adddcmfiles_radio, name='adddcmfiles_radio'),
    path ('inviteuser_imaging', views.inviteuser_imaging, name='inviteuser_imaging'),

    path ('addExtraItems/<int:id1>/<int:id2>/<int:id3>/<int:units>/<str:requestFor>', views.addExtraItems, name='addExtraItems'),
    path('imageDataManagement', views.imageDataManagement, name='imageDataManagement'),
    

    path ('addextuser', views.addextuser, name='addextuser'),
    path ('validateuser', views.validateuser, name='validateuser'),

    path ('driveindex', views.driveindex, name='driveindex'),
    path ('payNowStatusCode', views.payNowStatusCode, name='payNowStatusCode'),
    
    path ('manageReport/<int:id>', views.manageReport, name='manageReport'),
    path ('manageReportImage/<int:id>', views.manageReportImage, name='manageReportImage'),
    path ('manageReportPlanning/<int:id>', views.manageReportPlanning, name='manageReportPlanning'),
    path ('manageReportGuide/<int:id>', views.manageReportGuide, name='manageReportGuide'),
    path ('manageReportDigitalLab/<int:id>', views.manageReportDigitalLab, name='manageReportDigitalLab'),
    path('lineOrderDetails/<int:id1>/<int:id2>', views.lineOrderDetails, name='lineOrderDetails'),
    path('lineOrderDetailsLab/<int:id1>/<int:id2>', views.lineOrderDetailsLab, name='lineOrderDetailsLab'),
    path('lineOrderDetailsDigitalLab/<int:id1>/<int:id2>', views.lineOrderDetailsDigitalLab, name='lineOrderDetailsDigitalLab'),
    path('lineOrderDetailsDigital/<int:id1>/<int:id2>', views.lineOrderDetailsDigital, name='lineOrderDetailsDigital'),

    path ('uploadLabData/<int:pk>/<str:target>', views.uploadLabData, name='uploadLabData'),
    path ('deleteIos/<int:pk>/<str:target>', views.deleteIos, name='deleteIos'),
    path ('uploadLabDataAgain/<int:id1>/<int:id2>', views.uploadLabDataAgain, name='uploadLabDataAgain'),
    path ('viewLabImage/<int:pk>/<int:id1>', views.viewLabImage, name='viewLabImage'),

    path('editLineOrderItem/<int:id1>/<int:id2>/<int:id3>', views.editLineOrderItem, name='editLineOrderItem'),
    path('editRadioOrderItem/<int:id1>/<int:id2>/<int:id3>', views.editRadioOrderItem, name='editRadioOrderItem'),
    path('editImageOrderItem/<int:id1>/<int:id2>/<int:id3>', views.editImageOrderItem, name='editImageOrderItem'),
    path('editPlanningOrderItem/<int:id1>/<int:id2>/<int:id3>', views.editPlanningOrderItem, name='editPlanningOrderItem'),
    path('editSurgiOrderItem/<int:id1>/<int:id2>/<int:id3>', views.editSurgiOrderItem, name='editSurgiOrderItem'),


    path('updatePreferredData/<int:id>/<str:data>', views.updatePreferredData, name='updatePreferredData'),
    path('updatePickupReq/<int:id>/<str:data>', views.updatePickupReq, name='updatePickupReq'),

    path ('submitOrderPayNow/<int:id>', views.submitOrderPayNow, name='submitOrderPayNow'),
    path ('shipmentHistory/<int:id>', views.shipmentHistory, name='shipmentHistory'),

    path('handlerequest/', views.handlerequest, name='handlerequest'),
    path('generateLabel/<int:id>', views.generateLabel, name='generateLabel'),
    path('generateMenifest/<int:id>', views.generateMenifest, name='generateMenifest'),
    
    path('tempid/', views.tempid, name='tempid'),
    path('addBranch', views.addBranch, name='addBranch'),
    path('create_new_branch', views.create_new_branch, name='create_new_branch'),
    path('all_patients', views.all_patients, name='all_patients'),
    path('search_patient', views.search_patient, name='search_patient'),
    path('newBranchClinic', views.newBranchClinic, name='newBranchClinic'),
    path('newBranchLab', views.newBranchLab, name='newBranchLab'),
    path('addBranchClinic', views.addBranchClinic, name='addBranchClinic'),
    path('addBranchLab', views.addBranchLab, name='addBranchLab'),
    path('invoiceForClinic', views.invoiceForClinic, name='invoiceForClinic'),
    path('editPrice/<int:id>/<int:price>/<str:service>', views.editPrice, name='editPrice'),
    
    path('requestForInvoice/<str:patient>/<int:id>', views.requestForInvoice, name='requestForInvoice'),
    path('requestForInvoiceLab/<str:patient>/<int:id>', views.requestForInvoiceLab, name='requestForInvoiceLab'),
    path('enablePaymentOption/<int:id>', views.enablePaymentOption, name = 'enablePaymentOption'),
    # SubMaterial
    path ('findSubMaterial/<int:id1>/<int:id2>', views.findSubMaterial, name='findSubMaterial'),
    #Password Reset For The User
    path('password_reset/',auth_views.PasswordResetView.as_view(template_name="Password/pwdResetFirst.html"),name='password_reset'),
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(template_name="Password/pwdResetSecond.html"),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name="Password/pwdResetThird.html"),name='password_reset_confirm'),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(template_name="Password/pwdResetFourth.html"),name='password_reset_complete'),

# Manage All Payments From Here 
    path ('firstLOG/<int:id1>/<int:id2>', views.firstLOG, name='firstLOG'),
    path ('payUsingWallet/<int:id1>/<int:id2>', views.payUsingWallet, name='payUsingWallet'),
    path ('payUsingFreeService/<int:id1>/<int:id2>', views.payUsingFreeService, name='payUsingFreeService'),
    
#StlViewer
    path ('requestForStlFile/<int:id>', views.requestForStlFile, name='requestForStlFile'),
    path ('renderSTLFile/<int:pk>', views.renderSTLFile, name='renderSTLFile'),
    path ('reverseEngineering/<int:id1>/<int:id2>', views.reverseEngineering, name='reverseEngineering'),
# view Planning File
    path ('requestPlanningFile/<int:id1>/<int:id2>', views.requestPlanningFile, name='requestPlanningFile'),
    path ('reverseEngg/<int:id1>/<int:id2>/<int:id3>', views.reverseEngg, name='reverseEngg'),
    path ('renderPlanningFile/<int:pk>', views.renderPlanningFile, name='renderPlanningFile'),
    path ('viewLabStlImage/<int:id>/<str:site>', views.viewLabStlImage, name='viewLabStlImage'),
# Surgical Guide
    path ('requestGuidePlanFile/<int:id1>/<int:id2>', views.requestGuidePlanFile, name='requestGuidePlanFile'),
    path ('reverseEnggGuide/<int:id1>/<int:id2>/<int:id3>', views.reverseEngg, name='reverseEnggGuide'),
    
    path ('surgicalGuideFile/<int:id1>/<int:id2>', views.surgicalGuideFile, name='surgicalGuideFile'),
    path ('prepareTheNextFile/<int:id1>/<int:id2>/<int:id3>', views.prepareTheNextFile, name='prepareTheNextFile'),
    path ('renderIntoDesignFile/<int:pk>', views.renderIntoDesignFile, name='renderIntoDesignFile'),

]
from django.conf.urls import handler404, handler500
# handling the 404 error
handler404 = 'dent.views.error_404_view'
