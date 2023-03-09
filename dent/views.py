# from asyncio.windows_events import NULL
from fileinput import filename
from itertools import count
from multiprocessing import context
from pydoc import locate
import pytz
from unicodedata import name
from urllib import response
from xml.dom.minidom import Comment
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.db.models import Max
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.contrib import messages
from django.db.models import Sum, F, ExpressionWrapper, DateTimeField, DurationField, Avg, fields
from django.db.models.functions import Extract
from django.db.models.functions import ExtractMonth, ExtractYear
from django.core import mail
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db.models import Q
from dateutil.relativedelta import *
from django.contrib.auth.models import Group
import razorpay
import html2text
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.mail import get_connection, send_mail
from django.core.mail.message import EmailMessage
from requests.exceptions import ConnectionError

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from .models import *

import os
from .serializers import NotificationSerializers, OtherImageFileSerializers
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders
from docx import Document
from htmldocx import HtmlToDocx
from django.utils.html import strip_tags
import requests


topcat=Topcat.objects.filter(status="Active")

def render_word_view(request, id):
    service_order = ServiceOrder.objects.get(id=id)

    patient = Patient.objects.get(pid=service_order.pid)

    document = Document()
    my_string = service_order.text

    document.add_paragraph(my_string)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = 'attachment; filename=download.docx'
    document.save(response)

    return response


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path = result[0]
    else:
        sUrl = settings.STATIC_URL  # Typically /static/
        sRoot = settings.STATIC_ROOT  # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL  # Typically /media/
        mRoot = settings.MEDIA_ROOT  # Typically /home/userX/project_static/media/

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
           
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))                       
        else:
            return uri

    # make sure that file exists
    
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path


def check_pdf(request):
    service_order = ServiceOrder.objects.get(id=90)

    patient = Patient.objects.get(pid=service_order.pid)

    return render(request, 'dsc_template.html', {'patient': patient, 'service_order': service_order})


def render_pdf_view(request, id):
    service_order = ServiceOrder.objects.get(id=id)

    patient = Patient.objects.get(pid=service_order.pid)

    template_path = 'MainPDF.html'
    context = {'patient': patient, 'service_order': service_order}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    # response['Content-Disposition'] = 'attachment; filename="service_order.pdf"'
    fname = 'filename=' + patient.name + ".pdf"
    response['Content-Disposition'] = fname
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
        html, dest=response, link_callback=link_callback)
    # if error then show some funy view
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


def default(request):
    return render(request, 'login.html')


def self(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        age = request.POST.get('age')

        self_pt = Self(name=name, email=email, contact=contact, age=age,  rdate=date.today())
        self_pt.save()

        return render(request, 'reg.html', {'self_pt': self_pt, 'name': name})

    return render(request, 'Pt_self_reg.html')


def get_selfpt(request):
    if request.method == "POST":
        vid = request.POST.get('vid')

        pt = Self.objects.get(vid=vid)
        request.session['vid'] = vid

        return redirect('/createpatient_vid')


def domain(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        today = datetime.today()
        required_date = today - timedelta(weeks=1)
        dateDiff = required_date - today
        shipRocketAuth = ShipRocketAuth.objects.get(id=1)
        if user is not None:
            login(request, user)
            admin = Users.objects.get(username=username)
            to_date = today.date()
            from_date = admin.last_login
            delta = ''
            checkdate = ''
            if from_date:
                delta =  to_date - from_date
                checkdate = delta.days
            if admin.last_login == None or admin.last_login == '':
                admin.last_login = today
                url = "https://apiv2.shiprocket.in/v1/external/auth/login"
                payload = json.dumps({"email": shipRocketAuth.username, "password": shipRocketAuth.password})
                headers = {'Content-Type': 'application/json'}
                response = requests.request("POST", url, headers=headers, data=payload)
                data = response.json()
                shipRocketAuth.token = data["token"]
                shipRocketAuth.save()
            elif admin.last_login != None and checkdate == 7 or checkdate == 8:
                admin.last_login = today
                url = "https://apiv2.shiprocket.in/v1/external/auth/login"
                payload = json.dumps({"email": shipRocketAuth.username, "password": shipRocketAuth.password})
                headers = {'Content-Type': 'application/json'}
                response = requests.request("POST", url, headers=headers, data=payload)
                data = response.json()
                shipRocketAuth.token = data["token"]
                shipRocketAuth.save()
            else:
                admin.last_login = admin.last_login
            admin.save()
            return redirect('/login_domain')
        else:
            context = {'message': 'Invalid Credentials', 'class': 'danger'}
            return render(request, 'domain_login.html', context)

    return render(request, 'domain_login.html')


def addBranch(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    topcat = Topcat.objects.filter(status='Active')
    branch = Branch.objects.filter(orgid= org)

    if request.method == 'POST':
        branch_name = request.POST.get('branchname')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zipcode = request.POST.get('zipcode')
        country = request.POST.get('country')
        branch_email = request.POST.get('branchemail')
        mobile = request.POST.get('branchcontact')
        status = request.POST.get('status')
        first_name = request.POST.get('fname')
        last_name = request.POST.get('lname')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        username = request.POST.get('email')
        password = request.POST.get('password')
        branch = Branch(orgid = org, branch_name = branch_name, city = city, state = state, zipcode = zipcode, adress = str(city)+', ' + str(state)+'('+str(zipcode)+')' , country = country, email = branch_email, mobile = mobile, status = status)
        branch.save()


        ur = Users(first_name = first_name, last_name = last_name, name = str(first_name) +" "+ str(last_name), email = email, contact = contact, password = password, usertype = "Manager", username = email, orgid = org, department="Manager", status="Active")
        checkusr = Users.objects.filter(username=username).first()
        if checkusr:
            context = {'message': 'Manager details already exists', 'usr': usr, 'org': org, 'topcat': topcat, 'class': 'danger', 'page': 'Registration'}
            return render(request, 'new_branch.html', context)
        else:
            usr = Users(first_name = first_name, last_name = last_name, name = str(first_name)+ " "+str(last_name), email = email, contact = contact, password = password, usertype = "Manager", username = email, orgid = org, department="Manager", status="Active")
            usr.save() 


        user = User.objects.create_user(username, email, password)
        user.save()
        branch.regby_email = usr.email
        branch.regby_userid = usr.id
        branch.ctperson_name = usr.name
        branch.manager = usr.name
        branch.save()
        # usr = authenticate(username = username, password = password)
        # login(request, usr)
        return redirect('/create_new_branch')
    page = "Registration"
    data = {'page': page, 'usr': usr, 'org': org, 'topcat': topcat, 'branch': branch}
    return render(request, 'new_branch.html', data)

def addBranchClinic(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    topcat = Topcat.objects.filter(status='Active')
    branch = Organisation.objects.filter(parent_id = org)
    if request.method == 'POST' and  request.FILES:
        doc = request.FILES
        logo = doc['propic']
        branch_name = request.POST.get('branchname')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('zipcode')
        country = request.POST.get('country')
        branch_email = request.POST.get('branchemail')
        branch_contact = request.POST.get('branchcontact')
        first_name = request.POST.get('fname')
        email = request.POST.get('email')
        user_contact = request.POST.get('contact')
        username = request.POST.get('email')
        password = request.POST.get('password')
        new_branch = Organisation(parent_id = org.id, orgname = branch_name, orgtype= "Dental Clinic Branch", city = city, state = state, pincode = pincode, address = address , country = country, email = branch_email, contact = branch_contact, status = "Active", logo = logo)
        new_branch.save()
        checkusr = Users.objects.filter(username=username).first()
        checkMobile = Users.objects.filter(contact=user_contact).first()
        if checkusr:
            context = {'message': 'Manager details already exists', 'usr': usr, 'org': org, 'topcat': topcat, 'class': 'danger', 'page': 'Registration'}
            return render(request, 'newBranchClinic.html', context)
        elif checkMobile:
            context = {'message': 'Manager details already exists', 'usr': usr, 'org': org, 'topcat': topcat, 'class': 'danger', 'page': 'Registration'}
            return render(request, 'newBranchClinic.html', context)
        else:
            usr = Users(parent_orgid = org.id, name = first_name, email = email, contact = user_contact, password = password, usertype = "Manager", username = email, orgid = new_branch, department="Manager", status="Active")
            usr.save()
        user = User.objects.create_user(username, email, password)
        user.save()
        new_branch.regby_email = usr.email
        new_branch.regby_userid = usr.id
        new_branch.ctperson_name = usr.name
        new_branch.manager = usr.name
        new_branch.managerId = usr.id
        new_branch.admin = usr.id
        new_branch.save()
        return redirect('/newBranchClinic')
    page = "Registration"
    data = {'page': page, 'usr': usr, 'org': org, 'topcat': topcat, 'branch': branch}
    return render(request, 'addBranchClinic.html', data)

def addBranchLab(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    topcat = Topcat.objects.filter(status='Active')
    branch = Organisation.objects.filter(parent_id = org)

    if request.method == 'POST':
        branch_name = request.POST.get('branchname')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('zipcode')
        country = request.POST.get('country')
        branch_email = request.POST.get('branchemail')
        branch_contact = request.POST.get('branchcontact')
        status = request.POST.get('status')
        first_name = request.POST.get('fname')
        last_name = request.POST.get('lname')
        email = request.POST.get('email')
        user_contact = request.POST.get('contact')
        username = request.POST.get('email')
        password = request.POST.get('password')
        new_branch = Organisation(parent_id = org.id, orgname = branch_name, orgtype= "Dental Lab Branch", city = city, state = state, pincode = pincode, address = str(city)+', ' + str(state)+'('+str(pincode)+')' , country = country, email = branch_email, contact = branch_contact, status = status)
        new_branch.save()
        
        checkusr = Users.objects.filter(username=username).first()
        if checkusr:
            context = {'message': 'Manager details already exists', 'usr': usr, 'org': org, 'topcat': topcat, 'class': 'danger', 'page': 'Registration'}
            return render(request, 'newBranchLab.html', context)
        else:
            usr = Users(first_name = first_name, parent_orgid = org.id, last_name = last_name, name = str(first_name)+ " "+str(last_name), email = email, contact = user_contact, password = password, usertype = "Manager", username = email, orgid = new_branch, department="Manager", status="Active")
            usr.save() 


        user = User.objects.create_user(username, email, password)
        user.save()
        new_branch.regby_email = usr.email
        new_branch.regby_userid = usr.id
        new_branch.ctperson_name = usr.name
        new_branch.manager = usr.name
        new_branch.save()
        return redirect('/newBranchLab')
    page = "Registration"
    data = {'page': page, 'usr': usr, 'org': org, 'topcat': topcat, 'branch': branch}
    return render(request, 'newBranchLab.html', data)

def editBranchLab(request, id):
    usr = Users.objects.get(username=request.user)
    branch = Organisation.objects.get(id=id)
    if request.method == 'POST':
        orgname = request.POST.get('branchname')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('zipcode')
        country = request.POST.get('country')
        email = request.POST.get('branchemail')
        contact = request.POST.get('branchcontact')
        status = request.POST.get('status')
        branch.orgname = orgname
        branch.city = city
        branch.state = state
        branch.pincode = pincode
        branch.country = country
        branch.email = email
        branch.contact = contact
        branch.status = status
        branch.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def editBranchClinic(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    editBranch = Organisation.objects.get(id=id)
    users = Users.objects.filter(parent_orgid = org.id)
    topcat = Topcat.objects.filter(status="Active")
    branch = Organisation.objects.filter(parent_id = org.id)
    if request.method == 'POST':
        editBranch.orgname = request.POST.get('branchname')
        editBranch.city = request.POST.get('city')
        editBranch.state = request.POST.get('state')
        editBranch.pincode = request.POST.get('zipcode')
        editBranch.country = request.POST.get('country')
        editBranch.email = request.POST.get('branchemail')
        editBranch.contact = request.POST.get('branchcontact')
        editBranch.status = request.POST.get('status')
        editBranch.save()
        return redirect('/newBranchClinic')
    context= {'usr': usr, 'org': org, "topcat": topcat,'users': users, 'branch': branch, 'editBranch': editBranch}
    return render(request, 'editBranchClinic.html', context)

def newBranchClinic(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    users = Users.objects.filter(parent_orgid = org.id)
    topcat = Topcat.objects.filter(status="Active")
    branch = Organisation.objects.filter(parent_id = org.id)
    context= {'usr': usr, 'org': org, "topcat": topcat,'users': users, 'branch': branch}
    # return render(request, 'newBranchClinic.html', context)
    return render(request, 'BranchProfileClinic.html', context)

def newBranchLab(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    users = Users.objects.filter(parent_orgid = org.id)
    include = ['Implant Surgical Guide', 'Digital Lab Services']
    topcat = Topcat.objects.filter(topcat__in = include)
    branch = Organisation.objects.filter(parent_id = org.id)
    context= {'usr': usr, 'org': org, "topcat": topcat,'users': users, 'branch': branch}
    return render(request, 'LabOrder/newBranchLab.html', context)


def create_new_branch(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    
    if org.orgtype == 'Dental Clinic' or org.orgtype == 'Dental Clinic Branch':
        topcat = Topcat.objects.filter(status='Active')
    elif org.orgtype == 'Domain Owner':
        exclude = ['Digital Lab Services']
        topcat = Topcat.objects.filter(status = 'Active').exclude(topcat__in = exclude)
    else:
        exclude = ['Radiological Report', 'Image Analysis Report', 'Implant Planning Report']
        topcat = Topcat.objects.filter(status='Active').exclude(topcat__in = exclude)
    branch = Branch.objects.filter(orgid=org)
    context= {'usr': usr, 'org': org, "topcat": topcat, 'branch': branch}
    return render(request, 'new_branch.html', context)



def login_domain(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    exclude = ['Digital Lab Services']
    topcat = Topcat.objects.filter(status="Active").exclude(topcat__in = exclude)
    get_service_order=ServiceOrder.objects.filter(reforgid = org.id)
    today=datetime.today()
    main_service_order = get_service_order.filter(date=today)
    btnchecked = 'todayFunction'
    if request.method == 'POST':
        check1 = ""
        check2 = ""
        check3 = ""
        query_date = request.POST.get('query_date')
        filter_branch = request.POST.get('filter')
        if filter_branch != 0:
            main_org_id = filter_branch
        
        # if filter:
        get_service_order=ServiceOrder.objects.filter(orgid=main_org_id)
        main_service_order = get_service_order.filter(date=today)
        if str(query_date)=="today":
            query_data = today
            check1 = 'checked'
        if str(query_date)=="yesterday":
            check2 = 'checked'
            btnchecked = 'yesterdayFunction'
            query_data=today - timedelta(days=1)
            main_service_order=get_service_order.filter(date=query_data)
        if str(query_date)=="thisweek":
            check3= 'checked'
            btnchecked = 'thisweekFunction'
            query_data = today - timedelta(weeks=1)
            main_service_order=get_service_order.filter(Q(date__gte=query_data))
        radio_data = main_service_order.filter(refstudy='Radiological Report')
        radio_pending = radio_data.filter(status='Pending').count()
        radio_inprogress = radio_data.filter(status='In Process').count()
        radio_completed = radio_data.filter(status='Completed').count()
        radio_total = radio_data.count()
        radio_context = {'radio_pending': radio_pending, 'radio_inprogress': radio_inprogress, 'radio_completed': radio_completed, 'radio_total':radio_total}
        
        image_data = main_service_order.filter(refstudy='Image Analysis Report')
        image_pending = image_data.filter(status='Pending').count()
        image_inprogress = image_data.filter(status='In Process').count()
        image_completed = image_data.filter(status='Completed').count()
        image_total = image_data.count()
        image_context = {'image_pending': image_pending, 'image_inprogress': image_inprogress, 'image_completed': image_completed, 'image_total':image_total}
        
        planning_data = main_service_order.filter(refstudy='Implant Planning Report')
        planning_pending = planning_data.filter(status='Pending').count()
        planning_inprogress = planning_data.filter(status='In Process').count()
        planning_completed = planning_data.filter(status='Completed').count()
        planning_total = planning_data.count()
        
        guideData = main_service_order.filter(refstudy='Implant Surgical Guide')
        guide_pending = guideData.filter(status='Submit Order').count()
        guide_inprogress = guideData.filter(Q(status='Validate Data') | Q(status='Share Design') | Q(status='Review Design') | Q(status='Share Plan') | Q(status='Review Plan') | Q(status='Order Dispatched') | Q(status='Deliver Order')).count()
        guide_completed = guideData.filter(status='Order Completed').count()
        guide_onhold = guideData.filter(status='Order Onhold').count()
        guide_cancelled = guideData.filter(status='Order Cancelled').count()
        guide_total = guideData.count()
        
        guide_context = {'guide_pending': guide_pending, 'guide_onhold': guide_onhold, 'guide_cancelled': guide_cancelled, 'guide_inprogress': guide_inprogress, 'guide_completed': guide_completed, 'guide_total':guide_total}
        
        today=datetime.today()
        appointment = Appointment.objects.all().filter(orgid=org).count()
        patient = Patient.objects.all().filter(orgid=org).count()
        business = ServiceOrder.objects.all().filter(orgid=org).aggregate(Sum('ref_price'))
        amount=business['ref_price__sum']
        data = {'usr': usr, 'main_org_id': main_org_id, 'message': 'You have signed in successfully', 'page': 'Dashboard', 'btnchecked': btnchecked,
                'org':org,'topcat':topcat, 'appointment':appointment,'patient': patient, 'amount': amount, 'planning_pending': planning_pending,
                'planning_inprogress': planning_inprogress, 'planning_completed': planning_completed, 'planning_total': planning_total, 'image_pending': image_pending,
                'image_inprogress': image_inprogress, 'image_completed': image_completed, 'image_total':image_total, 'radio_pending': radio_pending,
                'radio_inprogress': radio_inprogress, 'radio_completed': radio_completed, 'radio_total':radio_total,'guide_pending': guide_pending,
                'guide_onhold': guide_onhold, 'guide_cancelled': guide_cancelled, 'guide_inprogress': guide_inprogress, 'guide_completed': guide_completed, 'guide_total':guide_total}
        return render(request, 'domain_dashboard.html', data)
            

    radio_data = main_service_order.filter(refstudy='Radiological Report')
    radio_pending = radio_data.filter(status='Pending').count()
    radio_inprogress = radio_data.filter(status='In Process').count()
    radio_completed = radio_data.filter(status='Completed').count()
    radio_total = radio_data.count()
    radio_context = {'radio_pending': radio_pending, 'radio_inprogress': radio_inprogress, 'radio_completed': radio_completed, 'radio_total':radio_total}
    
    image_data = main_service_order.filter(refstudy='Image Analysis Report')
    image_pending = image_data.filter(status='Pending').count()
    image_inprogress = image_data.filter(status='In Process').count()
    image_completed = image_data.filter(status='Completed').count()
    image_total = image_data.count()
    image_context = {'image_pending': image_pending, 'image_inprogress': image_inprogress, 'image_completed': image_completed, 'image_total':image_total}
    
    
    planning_data = main_service_order.filter(refstudy='Implant Planning Report')
    planning_pending = planning_data.filter(status='Pending').count()
    planning_inprogress = planning_data.filter(status='In Process').count()
    planning_completed = planning_data.filter(status='Completed').count()
    planning_total = planning_data.count()
    planning_context = {'planning_pending': planning_pending, 'planning_inprogress': planning_inprogress, 'planning_completed': planning_completed, 'planning_total': planning_total}
    
    guideData = main_service_order.filter(refstudy = 'Implant Surgical Guide')
    guide_pending = guideData.filter(status='Pending').count()
    guide_inprogress = guideData.filter(status='In Process').count()
    guide_completed = guideData.filter(status = 'Completed').count()
    guide_onhold = guideData.filter(status='Order Onhold').count()
    guide_cancelled = guideData.filter(status='Order Cancelled').count()
    guide_total = guideData.count()
    guide_context = {'guide_pending': guide_pending, 'guide_onhold': guide_onhold, 'guide_cancelled': guide_cancelled, 'guide_inprogress': guide_inprogress, 'guide_completed': guide_completed, 'guide_total':guide_total}
    
    data = {'message': 'You have signed in successfully', 'page': 'Dashboard', 'usr': usr, 'topcat': topcat,  'planning_pending': planning_pending,
            'planning_inprogress': planning_inprogress, 'planning_completed': planning_completed, 'planning_total': planning_total, 'image_pending': image_pending,
            'image_inprogress': image_inprogress, 'image_completed': image_completed, 'image_total':image_total, 'radio_pending': radio_pending,
            'radio_inprogress': radio_inprogress, 'radio_completed': radio_completed, 'radio_total':radio_total, 'btnchecked': btnchecked, 'guide_pending': guide_pending,
            'guide_onhold': guide_onhold, 'guide_cancelled': guide_cancelled, 'guide_inprogress': guide_inprogress, 'guide_completed': guide_completed, 'guide_total':guide_total}
    return render(request, 'domain_dashboard.html', data)


def dashboard_domain(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    topcat = Topcat.objects.filter(status="Active")
    data = {'page': 'Dashboard', 'usr': usr, 'topcat': topcat}
    return render(request, 'domain_dashboard.html', data)

def all_patients(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    exclude = ['Digital Lab Services']
    topcat = Topcat.objects.filter(status="Active").exclude(topcat__in = exclude)
    patient= Patient.objects.all()
    data={'usr': usr, 'org': org, 'topcat': topcat, 'patient': patient}    
    return render(request, 'all_patients.html', data)


def all_imaging(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    exclude = ['Dental Clinic Branch', 'Dental Lab Branch', 'Imaging Centre Branch']
    centre = Organisation.objects.all().exclude(orgtype__in = exclude)
    for i in centre:
        users = Users.objects.filter(orgid=i)
        i.users = users.count()
    exclude = ['Digital Lab Services']
    topcat = Topcat.objects.filter(status="Active").exclude(topcat__in = exclude)
    subscription = Subscriptions.objects.all()
    pack = Pack.objects.filter(status = 'Active')
    details = PackDetails.objects.all()
    data = {'usr': usr, 'org': org,'topcat': topcat, 'centre': centre, 'pack': pack, 'details': details, 'subscription': subscription}
    return render(request, 'all_imaging_centres.html', data)


def all_clinic(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    centre = Organisation.objects.filter(orgtype="Dental Clinic")
    for i in centre:
        users = Users.objects.filter(orgid=i)
        i.users = users.count()
    data = {'usr': usr, 'org': org, 'centre': centre}
    return render(request, 'all_dental_clinics.html', data)


def all_radio(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    centre = Organisation.objects.filter(orgtype="Radiologist")
    for i in centre:
        users = Users.objects.filter(orgid=i)
        i.users = users.count()
    data = {'usr': usr, 'org': org, 'centre': centre}
    return render(request, 'all_radiologists.html', data)


def logouthandle(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    gotOrgId = org.id
    gotUserName = usr.name
    gotUserId = usr.id
    eventLog = EventLog(eventCode = 'DRET-0004', event = 'Logout Successfull' , log = str(gotUserName) + ' Loggedout Successfully.', orgId = gotOrgId, userId = gotUserId, time = datetime.now())
    try:
        eventLog.save()
    except Exception as e:
        message = e
    logout(request)
    context = {'message': 'You have successfully logged out', 'class': 'success', 'page': 'Signin'}
    return render(request, 'login_dentread.html', context)


def cstlogouthandle(request):
    logout(request)
    messages.success(request, "You have Successfully Logged Out")
    return redirect('/cstlogin')


def filter(request):
    if request.method == "POST":
        day = request.POST.get('day')
        case = request.POST.get('case')
        mycase = str(case)
        myday = str(day)
        if myday == "today":
            fdate = date.today()
        elif myday == "yesterday":
            fdate = date.today() + datetime.timedelta(days=-1)

        request.session[fdate] = fdate

        return redirect('/index')

    request.session[''] = fdate
    return redirect('/index')


from datetime import date, datetime, timedelta


def index_today(request):
    usr = Users.objects.get(username=request.user)
    depart = str(usr.department)
    if depart == "Radiologist(Ext)":
        rep = ServiceOrder.objects.filter(repby=usr.name)
    else:
        today = date.today()

        rep = ServiceOrder.objects.filter(date=today)

    radio = Users.objects.filter(department__icontains="Radiologist")
    usr = Users.objects.all()
    for i in rep:
        for u in usr:
            if u.email == i.docemail:
                i.portal = "Yes"
                i.save()
    dcm = Dcmfile.objects.all()
    for i in dcm:
        matchid = i.repid
        try:
            rt = ServiceOrder.objects.get(repid=matchid)
            rgdate = rt.date
            expdate = rgdate + timedelta(days=2)
            today = date.today()
            if expdate <= today:
                if len(i.file) > 0:
                    os.remove(i.file.path)
                i.delete()

        except ServiceOrder.DoesNotExist:
            dm = "hi"
    for i in rep:
        rp = ServiceOrder.objects.filter(pid=i.pid).count()
        if (rp > 1):
            i.st = "badge badge-primary"
    techs = Users.objects.filter(usertype="Internal").filter(department="Technician")
    return render(request, 'Dashboard.html', {'radio': radio, 'rep': rep, 'techs': techs})


def index(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    branch = Organisation.objects.filter(parent_id = org.id)
    rep = ServiceOrder.objects.filter(Q(orgid=org) | Q(repby=usr.name)).exclude(reforgid__isnull=True)
    
    stlFile = IOSFile.objects.filter(orgid = org)
    checkStl = ''
    for i in rep:
        for j in stlFile:
            if i.repid == j.repid:
                checkStl = 'True'
    icon = ''
    currency = ''
    if org.country == 'IN':
        currency = 'price'
        icon = '<i class="fa-solid fa-indian-rupee-sign"></i>'
    else:
        currency = 'dollarPrice'
        icon = '<i class="fa-solid fa-dollar-sign"></i>'
    
    for i in rep:
        if i.reforgid:
            i.reforgid = Organisation.objects.get(id=i.reforgid).orgname
            i.repby = i.reforgid
        if i.status == "Completed" or i.status == "Sent":
            i.menuclass = ""
        else:
            i.menuclass = "disabled"
        if i.StudyInstanceUID:
            i.down = ""
        else:
            i.down = "disabled"
        if i.status == "For Review":
            i.status = "In Process"
        if i.status == "Report Completed":
            i.status = "In Process"
        if i.status == 'Completed':
            i.invoice = ""
        else:
            i.invoice = "disabled"
            
    if request.method == "POST":
        search = request.POST.get('search')
        users = request.POST.get('users')
        if search:
            if org.orgtype == "Dental Clinic":
                rep = ServiceOrder.objects.filter(Q(orgid=org) | Q(repby=usr.name) | Q(parent_orgid = org.id)).exclude(refstudy__isnull=True).filter(Q(name__icontains=search) | Q(status__icontains=search) | Q(date__icontains=search) | Q(patient_id__icontains=search))     
            else:
                rep = ServiceOrder.objects.filter(Q(orgid=org) | Q(repby=usr.name)).exclude(refstudy__isnull=True).filter(Q(name__icontains=search) | Q(status__icontains=search) | Q(date__icontains=search) | Q(patient_id__icontains=search)) 
        if users:
            rep = ServiceOrder.objects.filter(Q(orgid=users) | Q(parent_orgid = users) | Q(repby=usr.name)).exclude(refstudy__isnull=True)
        
        for i in rep:
            if i.reforgid:
                i.reforgid = Organisation.objects.get(id=i.reforgid).orgname
                i.repby = i.reforgid
            if i.status == "For Review":
                i.status = "In Process"
            if i.status == "Report Completed":
                i.status = "In Process"
        page = "Reporting Dash"
        data = {'usr': usr, 'org': org, 'rep': rep, 'topcat': topcat, 'page': page, 'icon': icon, 'currency': currency, 'branch': branch}
        return render(request, "Dashboard.html", data)
    users = Users.objects.filter(Q(orgid=org)| Q(reforgid=org.id))
    radio = users.filter(Q(department__icontains="Radiologist")| Q(department__icontains="Admin"))
    context = {'stlFile': stlFile, 'checkStl': checkStl, 'usr': usr, 'org': org,'icon': icon, 'currency': currency, 'branch': branch, 'rep': rep, 'topcat': topcat,'page': 'Reporting Dash', 'radio': radio}
    return render(request, 'Dashboard.html', context)

def directTargetedStatus(request, service, status, date):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    branch = Organisation.objects.filter(parent_id = org.id)
    getStatus = status
    getService = service
    date = date
    main_rep = ServiceOrder.objects.filter(orgid=org).filter(Q(refstudy__gte=service)).filter(status=status).exclude(reforgid__isnull=True)
    today=datetime.today()
    if str(status)=="total":
        main_rep = ServiceOrder.objects.filter(orgid=org).filter(refstudy=service).exclude(reforgid__isnull=True)
    else:
        main_rep = ServiceOrder.objects.filter(orgid=org).filter(refstudy=service).filter(status=status).exclude(reforgid__isnull=True)
    query_data=''
    if str(date)=="Today":
        query_data = today
        rep = main_rep.filter(date=query_data)
    if str(date)=="Yesterday":
        query_data=today - timedelta(days=1)
        rep = main_rep.filter(Q(date__gte=query_data))
    if str(date)=="This Week":
        query_data = today - timedelta(weeks=1)
        rep = main_rep.filter(Q(date__gte=query_data))  
    icon = ''
    currency = ''
    #Handle Currency
    if org.country == 'IN':
        currency = 'price'
        icon = '<i class="fa-solid fa-indian-rupee-sign"></i>'
    else:
        currency = 'dollarPrice'
        icon = '<i class="fa-solid fa-dollar-sign"></i>'
    
    # Menupulate Status
    for i in rep:
        if i.status == "For Review":
            i.status = "In Process"
        if i.status == "Report Completed":
            i.status = "In Process"
            
    if request.method == "POST":
        search = request.POST.get('search')
        users = request.POST.get('users')
        if search:
            if org.orgtype == "Dental Clinic":
                rep = ServiceOrder.objects.filter(Q(orgid=org) | Q(repby=usr.name) | Q(parent_orgid = org.id)).exclude(refstudy__isnull=True).filter(Q(name__icontains=search) | Q(status__icontains=search) | Q(date__icontains=search) | Q(patient_id__icontains=search))     
            else:
                rep = ServiceOrder.objects.filter(Q(orgid=org) | Q(repby=usr.name)).exclude(refstudy__isnull=True).filter(Q(name__icontains=search) | Q(status__icontains=search) | Q(date__icontains=search) | Q(patient_id__icontains=search)) 
        if users:
            rep = ServiceOrder.objects.filter(Q(orgid=users) | Q(parent_orgid = users) | Q(repby=usr.name)).exclude(refstudy__isnull=True)
        
        for i in rep:
            if i.status == "For Review":
                i.status = "In Process"
            if i.status == "Report Completed":
                i.status = "In Process"
        page = "Reporting Dash"
        data = {'usr': usr, 'org': org, 'rep': rep, 'topcat': topcat, 'page': page, 'icon': icon, 'currency': currency, 'branch': branch}
        return render(request, "Dashboard.html", data)
    data = {'usr': usr, 'org': org, 'rep': rep, 'topcat': topcat,'icon': icon, 'currency': currency, 'branch': branch}
    return render(request, 'Dashboard.html', data)

def directTargetedStatusToLab(request, service, status, date, item):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    branch = Organisation.objects.filter(parent_id = org.id)
    include = ['Implant Surgical Guide', 'Digital Lab Services']
    topcat = Topcat.objects.filter(status = 'Active').filter(topcat__in = include)
    users = Users.objects.filter(orgid=org)
    radio = users.filter(department__icontains="Technician")
    firstCat = Topcat.objects.filter(topcat = 'Digital Lab Services')
    for i in firstCat:
        mycat = Topcat.objects.get(id=i.id)
    main_rep = ServiceOrder.objects.filter(reforgid=org.id).filter(Q(refstudy__gte=service)).filter(status=status).exclude(reforgid__isnull=True)
    date = date
    today = datetime.today()
    
    status = status
    if str(service) == 'Implant Surgical Guide' and status == 'total':
        main_rep = ServiceOrder.objects.filter(reforgid=org.id).filter(Q(refstudy__gte=service)).exclude(reforgid__isnull=True)
    if str(service) == 'Digital Lab Services' and status == 'Pending':
        status = 'Submit Order'
    elif str(service) == 'Digital Lab Services' and status == 'In Process':
        status = 'Validate Data' or 'Share Design' or 'Review Design' or 'Share Plan' or 'Review Plan' or 'Order Dispatched' or 'Deliver Order'
    elif str(service) == 'Digital Lab Services' and status == 'Completed':
        status = 'Order Delivered'
    else:
        status = status
    
    if str(service) == 'Digital Lab Services':
        labOrder = Prosthetic.objects.filter(reforgid = org.id).filter(item = item).filter(status = status)
        for i in labOrder:
            main_rep = ServiceOrder.objects.filter(repid = i.repid)
    if str(service) == 'Digital Lab Services' and status == 'total':
        labOrder = Prosthetic.objects.filter(reforgid = org.id).filter(item = item)
        for i in labOrder:
            main_rep = ServiceOrder.objects.filter(repid = i.repid)
    query_data=''
    rep = []
    if str(date)=="Today":
        query_data = today
        rep = main_rep.filter(date=query_data)              
    if str(date)=="Yesterday":
        query_data=today - timedelta(days=1)
        rep = main_rep.filter(Q(date__gte=query_data))
    if str(date)=="This Week":
        query_data = today - timedelta(weeks=1)
        rep = main_rep.filter(Q(date__gte=query_data))
    
    data = {'usr': usr, 'org': org, 'topcat': topcat, 'rep': rep, 'radio': radio, 'mycat': mycat}
    if str(service) == 'Digital Lab Services':
        return render(request, 'LabOrder/DashboardDigitalLab.html', data)
    else:
        return render(request, 'LabOrder/Dashboard_lab.html', data)


def directTargetedStatusToDentread(request, service, status, date):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    branch = Organisation.objects.filter(parent_id = org.id)
    exclude = ['Digital Lab Services']
    topcat = Topcat.objects.filter(status = 'Active').exclude(topcat__in = exclude)
    if str(service) == 'Radiological Report':
        firstCat = Topcat.objects.filter(topcat='Radiological Report')
    elif str(service) == 'Image Analysis Report':
        firstCat = Topcat.objects.filter(topcat='Image Analysis Report')
    elif str(service) == 'Implant Surgical Guide':
        firstCat = Topcat.objects.filter(topcat='Implant Surgical Guide')
    else:
        firstCat = Topcat.objects.filter(topcat='Implant Planning Report')
    for i in firstCat:
        mycat = Topcat.objects.get(id=i.id)
    users = Users.objects.filter(orgid=org)
    if str(service) == 'Radiological Report':
        radio = users.filter(department__icontains="Radiologist")
    elif str(service) == 'Image Analysis Report':
        radio = users.filter(department__icontains="Technician")
    else:
        radio = users.filter(department__icontains="Technician")
    date = date
    main_rep = ServiceOrder.objects.filter(reforgid=org.id).filter(Q(refstudy__gte = service)).filter(status = status).exclude(reforgid__isnull=True)
    today = datetime.today()
    if str(status) == "total":
        main_rep = ServiceOrder.objects.filter(reforgid = org.id).filter(Q(refstudy__gte = service)).exclude(reforgid__isnull=True)
    query_data =''
    if str(date) == "Today":
        query_data = today
        rep = main_rep.filter(date = query_data)
    if str(date) == "Yesterday":
        query_data = today - timedelta(days=1)
        rep = main_rep.filter(Q(date__gte = query_data))
    if str(date)=="This Week":
        query_data = today - timedelta(weeks=1)
        rep = main_rep.filter(Q(date__gte = query_data))    
        page = "Reporting Dash"
    for i in rep:
        i.refby = Organisation.objects.get(id=i.orgid_id).orgname
        
    context = {'usr': usr, 'org': org, 'rep': rep, 'topcat': topcat, 'radio': radio, 'mycat': mycat}
    if str(service) == 'Radiological Report':
        return render(request, 'Dashboard_dent.html', context)
    elif str(service) == 'Image Analysis Report':
        return render(request, 'Admin_Orders/image_Order.html', context)
    elif str(service) == 'Implant Surgical Guide':
        return render(request, 'LabOrder/Dashboard_lab.html', context)
    else:
        return render(request, 'Admin_Orders/planning_Order.html', context)

def refer_dent(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    rep = ServiceOrder.objects.filter(orgid=org).filter(status="Pending")
    dcmfiles = Dcmfile.objects.filter(orgid=org)
    for i in rep:
        dcm = dcmfiles.filter(repid=i.repid).first()
        if i.refpt_orgid:
            i.referto = Organisation.objects.get(id=i.refpt_orgid).orgname
        if dcm:
            i.dcm = dcm
        else:
            print("no")
    dent_org=Organisation.objects.get(orgtype="Domain Owner")
    studies=Study.objects.filter(orgid=dent_org)
    users = Users.objects.filter(orgid=org)

    return render(request, 'refer_dent.html', {'usr': usr, 'org': org, 'rep': rep, 'page': 'Reporting Dash', 'studies':studies})

def index_radio(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    rep = ServiceOrder.objects.filter(orgid=org)
    for i in rep:
        study=Study.objects.get(id=i.study)
        i.study=study.title+"_"+study.maincat
        org=Organisation.objects.get(id=i.refpt_orgid)
        i.referby=org.orgname
        
    users = Users.objects.filter(orgid=org)

    radio = users.filter(department__icontains="Radiologist")

    return render(request, 'Dashboard_radio.html', {'usr': usr, 'org': org, 'rep': rep, 'page': 'Reporting Dash', 'radio': radio})


def index_dent(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    rep = ServiceOrder.objects.filter(reforgid=org.id).filter(refstudy="Radiological Report")
    for i in rep:
        i.refby=Organisation.objects.get(id=i.orgid_id).orgname
    include = ['Radiological Report', 'Image Analysis Report', 'Implant Planning Report', 'Implant Surgical Guide']    
    topcat = Topcat.objects.filter(topcat__in = include)
    users = Users.objects.filter(orgid=org)
    radio = users.filter(department__icontains="Radiologist")
    mycat = topcat.get(id=id)
    return render(request, 'Dashboard_dent.html', {'usr': usr, 'org': org, 'rep': rep, 'page': 'Reporting Dash', 'radio': radio,'topcat':topcat, 'mycat': mycat})

def guide_orders(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    rep = ServiceOrder.objects.filter(reforgid=org.id).filter(refstudy="Implant Surgical Guide")
    for i in rep:
        i.refby=Organisation.objects.get(id=i.orgid_id).orgname
    users = Users.objects.filter(orgid=org)
    radio = users.filter(department__icontains="Technician")
    mycat = Topcat.objects.get(id=id)
    include = ["Implant Surgical Guide", "Digital Lab Services"]
    include2 = ["Digital Lab Services"]
    page = ''
    if org.orgtype == 'Domain Owner':
        topcat = Topcat.objects.filter(status = 'Active').exclude(topcat__in = include2)
        page = 'LabOrder/DashboardLab.html'
    else:
        topcat = Topcat.objects.filter(topcat__in = include)
        page = 'LabOrder/Dashboard_lab.html'
    return render(request, page,{'usr': usr, 'org': org, 'rep': rep, 'page': 'Reporting Dash', 'radio': radio,'mycat': mycat,'topcat': topcat})

def lab_orders(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    rep = ServiceOrder.objects.filter(reforgid=org.id).filter(refstudy="Digital Lab Services")
    for i in rep:
        i.refby=Organisation.objects.get(id=i.orgid_id).orgname
    users = Users.objects.filter(orgid=org)
    radio = users.filter(department__icontains="Technician")
    mycat = Topcat.objects.get(id=id)
    include = ["Implant Surgical Guide", "Digital Lab Services"]
    topcat = Topcat.objects.filter(topcat__in = include)
    return render(request, 'LabOrder/DashboardDigitalLab.html', {'usr': usr, 'org': org, 'rep': rep, 'page': 'Reporting Dash', 'radio': radio,'mycat': mycat,'topcat': topcat})


def image_Orders(request, id):
    usr = Users.objects.get(username = request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    rep = ServiceOrder.objects.filter(reforgid = org.id).filter(refstudy = 'Image Analysis Report')
    for i in rep:
        i.refby = Organisation.objects.get(id = i.orgid_id).orgname
    include= ['Radiological Report', 'Image Analysis Report', 'Implant Planning Report', 'Implant Surgical Guide']    
    topcat = Topcat.objects.filter(topcat__in = include)
    users = Users.objects.filter(orgid = org)
    radio = users.filter(department__icontains="Technician")
    mycat = topcat.get(id = id)
    context = {'usr': usr, 'org': org, 'rep': rep, 'radio': radio, 'users': users,'topcat':topcat, 'mycat': mycat}
    return render(request, 'Admin_Orders/image_Order.html', context)

def planning_Orders(request, id):
    usr = Users.objects.get(username = request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    include = ['Radiological Report', 'Image Analysis Report', 'Implant Planning Report', 'Implant Surgical Guide']    
    topcat = Topcat.objects.filter(topcat__in = include)
    mycat = topcat.get(id=id)
    rep = ServiceOrder.objects.filter(reforgid = org.id).filter(refstudy = 'Implant Planning Report')
    for i in rep:
        i.refby = Organisation.objects.get(id = i.orgid_id).orgname
    users = Users.objects.filter(orgid = org)
    radio = users.filter(department__icontains="Technician")
    context = {'usr': usr, 'org': org,'topcat': topcat, 'mycat': mycat, 'rep': rep, 'radio': radio, 'users': users}
    return render(request, 'Admin_Orders/planning_Order.html', context)

def view_orderdent(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order=ServiceOrder.objects.get(id=id)
    patient=Patient.objects.get(id=service_order.pid)
    pros=Prosthetic.objects.filter(repid=service_order.id)
    if request.method == 'POST':
        status = request.POST.get('status')
        service_order.status=status
        service_order.save()
        return redirect('/view_orderdent/'+str(service_order.id))

    data={'usr':usr, 'org':org, 'service_order':service_order, 'patient':patient, 'pros':pros}
    return render(request, 'view_orderdent.html', data)

def view_surgident(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order=ServiceOrder.objects.get(id=id)
    patient=Patient.objects.get(id=service_order.pid)
    pros=Suricalguide.objects.filter(repid=service_order.id)
    if request.method == 'POST':
        status = request.POST.get('status')
        service_order.status=status
        service_order.save()
        return redirect('/view_orderdent/'+str(service_order.id))

    data={'usr':usr, 'org':org, 'service_order':service_order, 'patient':patient, 'pros':pros}
    return render(request, 'view_surgident.html', data)


def update_order(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    pros=Prosthetic.objects.get(id=id)
    if request.method == 'POST':
        status = request.POST.get('status')
        comment = request.POST.get('comment')
        tracking = request.POST.get('tracking')
        pros.status=status
        pros.comment=comment
        pros.tracking=tracking
        pros.save()
        return redirect('/view_orderdent/'+str(pros.repid))


    data={'usr':usr, 'org':org,'pros':pros}
    return render(request, 'pros_form.html', data)

def update_surgi(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    pros=Suricalguide.objects.get(id=id)
    if request.method == 'POST':
        status = request.POST.get('status')
        comment = request.POST.get('comment')
        tracking = request.POST.get('tracking')
        pros.status=status
        pros.comment=comment
        pros.tracking=tracking
        pros.save()
        return redirect('/view_surgident/'+str(pros.repid))
    if request.method == "POST" and 'planning' in request.FILES:
        doc = request.FILES
        planning = doc['planning']
        status = request.POST.get('status')
        comment = request.POST.get('comment')
        tracking = request.POST.get('tracking')
        pros.status=status
        pros.comment=comment
        pros.tracking=tracking
        pros.planning=planning
        pros.save()
        return redirect('/view_surgident/'+str(pros.repid))


    data={'usr':usr, 'org':org,'pros':pros}
    return render(request, 'surgi_form.html', data)



def index_search(request):
    if request.method == "POST":
        search = request.POST.get('search')
        usr = Users.objects.get(username=request.user)

        depart = str(usr.department)
        if depart == "Radiologist(Ext)":
            rep = ServiceOrder.objects.filter(repby=usr.name)
        else:
            last_month = datetime.today() - timedelta(days=30)
            rep = ServiceOrder.objects.filter(Q(text__icontains=search))

        radio = Users.objects.filter(department__icontains="Radiologist")
        usr = Users.objects.all()
        for i in rep:
            for u in usr:
                if u.email == i.docemail:
                    i.portal = "Yes"
                    i.save()
        dcm = Dcmfile.objects.all()
        for i in dcm:
            matchid = i.repid
            try:
                rt = ServiceOrder.objects.get(repid=matchid)
                rgdate = rt.date
                expdate = rgdate + timedelta(days=2)
                today = date.today()
                if expdate <= today:
                    if len(i.file) > 0:
                        os.remove(i.file.path)
                    i.delete()

            except ServiceOrder.DoesNotExist:
                dm = "hi"
        for i in rep:
            rp = ServiceOrder.objects.filter(pid=i.pid).count()
            if (rp > 1):
                i.st = "badge badge-primary"
        techs = Users.objects.filter(usertype="Internal").filter(department="Technician")
        return render(request, 'Dashboard.html', {'radio': radio, 'rep': rep, 'techs': techs})


def index_yesterday(request):
    usr = Users.objects.get(username=request.user)
    depart = str(usr.department)
    if depart == "Radiologist(Ext)":
        rep = ServiceOrder.objects.filter(repby=usr.name)
    else:
        today = date.today()
        yesterday = today + timedelta(days=-1)
        rep = ServiceOrder.objects.filter(date=yesterday)

    radio = Users.objects.filter(department__icontains="Radiologist")
    usr = Users.objects.all()
    for i in rep:
        for u in usr:
            if u.email == i.docemail:
                i.portal = "Yes"
                i.save()
    dcm = Dcmfile.objects.all()
    for i in dcm:
        matchid = i.repid
        try:
            rt = ServiceOrder.objects.get(repid=matchid)
            rgdate = rt.date
            expdate = rgdate + timedelta(days=2)
            today = date.today()
            if expdate <= today:
                if len(i.file) > 0:
                    os.remove(i.file.path)
                i.delete()
        except ServiceOrder.DoesNotExist:
            dm = "hi"
    for i in rep:
        rp = ServiceOrder.objects.filter(pid=i.pid).count()
        if (rp > 1):
            i.st = "badge badge-primary"
    techs = Users.objects.filter(usertype="Internal").filter(department="Technician")

    return render(request, 'Dashboard.html', {'radio': radio, 'rep': rep, 'techs': techs})


def addexpenses(request):
    if request.method == "POST":
        expensetype = request.POST.get('expensetype')
        month = request.POST.get('month')
        remark = request.POST.get('remark')
        amount = request.POST.get('amount')
        locate = request.POST.get('locate')
        expense = Expenses(expensetype=expensetype, month=month, remark=remark, amount=amount, locate=locate)
        expense.save()
        return redirect('/allexpenses')

    else:
        org = Organisation.objects.all
        return render(request, 'addexpenses.html', {'org': org})


def createpatient(request):

    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    doctor = Refdoctor.objects.filter(orgid=org)
    if request.method == "POST":
        rdate = request.POST.get('rdate')
        locate = request.POST.get('locate')
        regby = request.user
        pid = request.POST.get('pid')
        name = request.POST.get('name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        address_1 = request.POST.get('address_1')
        address_2 = request.POST.get('address_2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        medih = request.POST.get('medih')
        refdoctor = request.POST.get('refdoctor')
        docid = request.POST.get('docid')

        centre = str(locate)
        checkid = Patient.objects.filter(orgid=usr.orgid_id)
        try:

            max_pid = checkid.aggregate(Max('pid'))['pid__max']
            new_pid = checkid.get(pid=max_pid)
            myid = new_pid.pid + 1
        except Patient.DoesNotExist:
            myid = 1

        if Patient.objects.filter(contact=contact).exists():
            checkpt = Patient.objects.filter(contact=contact)
            if checkpt.filter(name=name).exists():
                return render(request, 'exist.html')

            else:
                patient = Patient(rdate=rdate, pid=myid, locate=locate, regby=regby, contact=contact, name=name,
                                  age=age, gender=gender, email=email,
                                  address_1=address_1, address_2=address_2, city=city, state=state, zip_code=zip_code,
                                  medih=medih, refdoctor=refdoctor,
                                  docid=docid, orgid=org)
                patient.save()

                request.session['pid'] = myid

                return redirect('/addinvoice')
        else:
            patient = Patient(rdate=rdate, pid=myid, locate=locate, regby=regby, contact=contact, name=name, age=age,
                              gender=gender, email=email,
                              address_1=address_1, address_2=address_2, city=city, state=state, zip_code=zip_code,
                              medih=medih, refdoctor=refdoctor,
                              docid=docid, orgid=org)
            patient.save()

            request.session['pid'] = myid
            return redirect('/addinvoice')

    return render(request, 'CreatePatient.html', {'doctor': doctor, 'org': org, 'usr': usr, 'page': 'Add Patient'})


def token(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    doctors = Refdoctor.objects.filter(orgid=org)
    studies = Study.objects.filter(orgid=org)
    if request.method == "POST":
        token = request.POST.get('token')
        self= Self.objects.get(id=token)
        return render(request, 'CreatePatient.html',
                      {'doctors': doctors, 'org': org, 'usr': usr, 'page': 'Add Patient', 'studies': studies, 'self':self})



def createpatient_vid(request):
    vid = request.session['vid']
    pt = Self.objects.get(vid=vid)
    doctor = Refdoctor.objects.all
    patient = Patient.objects.all
    org = Organisation.objects.all
    return render(request, 'CreatePatient.html', {'doctor': doctor, 'patient': patient, 'org': org, 'pt': pt})


def createdoctor(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    if request.method == "POST":

        rdate = request.POST.get('rdate')
        docid = request.POST.get('docid')

        regby = request.user

        name = request.POST.get('name')
        referby = request.POST.get('referby')

        gender = request.POST.get('gender')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        address_1 = request.POST.get('address_1')
        address_2 = request.POST.get('address_2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')

        clinic = request.POST.get('clinic')
        clcontact = request.POST.get('clcontact')


        doctor = Refdoctor(locate=org.orgname, regby=regby, contact=contact, name=name,
                           gender=gender, email=email,
                           address_1=address_1, address_2=address_2, city=city, state=state, zip_code=zip_code,
                            clinic=clinic,
                           clcontact=clcontact, referby=referby, orgid=org)
        doctor.save()
        return redirect('/showdoctors')

    return render(request, 'CreateDoctor.html', {'org': org, 'usr': usr, 'page': 'Add Doctor'})

def createdoctor_modal(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    if request.method == "POST":

        rdate = request.POST.get('rdate')
        locate = request.POST.get('locate')
        regby = request.user

        name = request.POST.get('name')
        referby = request.POST.get('referby')

        gender = request.POST.get('gender')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        address_1 = request.POST.get('address_1')
        address_2 = request.POST.get('address_2')
        clinic = request.POST.get('clinic')
        clcontact = request.POST.get('clcontact')

        doctor = Refdoctor(rdate=rdate, locate=locate, regby=regby, contact=contact, name=name,
                           gender=gender, email=email,
                           address_1=address_1, address_2=address_2,  clinic=clinic,
                           clcontact=clcontact, referby=referby, orgid=org)
        doctor.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, 'CreateDoctor.html', {'org': org, 'usr': usr, 'page': 'Add Doctor'})

def additem(request):
    return render(request, 'additem.html')


def goback(request):
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def createuser(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    return render(request, 'CreateUser.html', {'org': org, 'usr': usr, 'page': 'Add User'})


def createuser_dent(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    return render(request, 'CreateUser_dent.html', {'org': org, 'usr': usr, 'page': 'Add User'})


def createorganaization(request):
    return render(request, 'CreateOrganaization.html')


def createstudy(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    topcat = Topcat.objects.filter(status="Active")
    if request.method == "POST":
        topcat = request.POST.get('topcat')
        title = request.POST.get('title')
        maincat = request.POST.get('maincat')
        subcat = request.POST.get('subcat')
        price = request.POST.get('price')

        study = Study(topcat=topcat,title=title, maincat=maincat, subcat=subcat, price=price, orgid=org)
        study.save()
        return redirect('/showstudies')
    return render(request, 'CreateStudy.html', {'usr': usr, 'org': org, 'page': 'Add Study', 'topcat':topcat})

def createstudy_modal(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    if request.method == "POST":
        title = request.POST.get('title')
        maincat = request.POST.get('maincat')
        subcat = request.POST.get('subcat')
        price = request.POST.get('price')

        study = Study(title=title, maincat=maincat, subcat=subcat, price=price, orgid=org)
        study.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return render(request, 'CreateStudy.html', {'usr': usr, 'org': org, 'page': 'Add Study'})


def createstudy_dent(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    topcat=Topcat.objects.filter(status="Active")
    if request.method == "POST":
        topcat= request.POST.get('topcat')
        title = request.POST.get('title')
        maincat = request.POST.get('maincat')
        subcat = request.POST.get('subcat')
        price = request.POST.get('price')
        dollarPrice = request.POST.get('dollarPrice')
        study = Study(topcat=topcat, title=title, maincat=maincat, subcat=subcat, price=price, dollarPrice = dollarPrice, orgid=org)
        study.save()
        return redirect('/showstudies_dent')
    return render(request, 'CreateStudy_dent.html', {'usr': usr, 'org': org, 'page': 'Add Study','topcat':topcat})




def addmodule(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    if request.method == "POST":
        code = request.POST.get('code')
        head = request.POST.get('head')
        pack = request.POST.get('pack')
        module = Modules(code=code, head=head, pack=pack)
        module.save()
        return redirect('/allmodules')
    return render(request, 'addmodule.html', {'usr': usr, 'org': org, 'page': 'Add Module'})


def allmodules(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    module = Modules.objects.all
    return render(request, 'allmodules.html', {'usr': usr, 'org': org, 'page': 'All Modules', 'module': module})


def addpack(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    module = Modules.objects.all()
    if request.method == "POST":
        scans = request.POST.get('scans')
        validity = request.POST.get('validity')
        status = request.POST.get('status')
        price = request.POST.get('price')
        type = request.POST.get('type')
        applied = request.POST.get('applied')
        pack = Pack(scans=scans, validity=validity, status=status, price=price, type=type,
                    applied=applied)
        pack.save()
        return redirect('/allpacks')
    return render(request, 'addpack.html', {'usr': usr, 'org': org, 'page': 'Add Module', 'module': module})


def allpacks(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    pack = Pack.objects.all
    return render(request, 'allpacks.html', {'usr': usr, 'org': org, 'page': 'All Packs', 'pack': pack})


def patientdetails(request, pk):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    patient = Patient.objects.get(id=pk)
    study = Study.objects.filter(orgid=org)
    service_orders = ServiceOrder.objects.filter(orgid=org)
    service_order = service_orders.filter(pid=patient.id).exclude(reforgid__isnull=True)
    
    icon = ''
    currency = ''
    if org.country == 'IN':
        currency = 'price'
        icon = '<i class="fa-solid fa-indian-rupee-sign"></i>'
    else:
        currency = 'dollarPrice'
        icon = '<i class="fa-solid fa-dollar-sign"></i>'
    
    for i in service_order:
        if i.status == "For Review":
            i.status = "In Process"
        if i.status == "Report Completed":
            i.status = "In Process"
        if i.reforgid:
            i.reforgid = Organisation.objects.get(id=i.reforgid).orgname
            i.repby = i.reforgid
    
    context = {'patient': patient, 'study': study, 'service_order': service_order, 'icon': icon, 'currency': currency, 'service_orders': service_orders, 'page': 'Patient Detail', 'usr':usr,'org':org, 'topcat':topcat}
    return render(request, 'PatientDetails.html', context)

def firstLOG(request, id1, id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = id1)
    mycat = Maincat.objects.get(id=id2)
    patient = Patient.objects.get(id=service_order.pid)
    domain = Organisation.objects.get(orgtype="Domain Owner")
    if service_order.refstudy != 'Digital Lab Services' and service_order.refstudy != 'Implant Surgical Guide':
        service_order.reforgid = domain.id
    else:
        service_order.reforgid = service_order.referTo
    service_order.paymentStatus = 'Unpaid'
    service_order.status = 'Pending'
    service_order.save()
    service_log = ServiceLog(orgid = org, patient=patient.name, repid = service_order.id,sodrid = service_order.order_id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy,log = "CREATE SERVICE ORDER", message = 'Created a service order')
    
    if service_order.refstudy == 'Radiological Report':
        notificationClinic = Notification(orgid = org, sendTo = org.id, serviceOrderId = service_order.id, sent = True, service = 'Radiological Report', user = usr.name, event = 'ORDER SUBMITTED', details = 'You have successfully submitted the order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/manageReport/'+str(service_order.id))
        notificationLab = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Radiological Report', user = usr.name, event = 'ORDER RECEIVED', details = 'You have recieved a new order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/index_dent/1')
        notificationLab.save()
        notificationClinic.save()
    if service_order.refstudy == 'Image Analysis Report':
        notificationClinic = Notification(orgid = org, sendTo = org.id, serviceOrderId = service_order.id, sent = True, service = 'Image Analysis Report', user = usr.name, event = 'ORDER SUBMITTED', details = 'You have successfully submitted the order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/manageReportImage/'+str(service_order.id))
        notificationLab = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Image Analysis Report', user = usr.name, event = 'ORDER RECEIVED', details = 'You have recieved a new order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/image_Orders/2')
        notificationLab.save()
        notificationClinic.save()
    if service_order.refstudy == 'Implant Planning Report':
        notificationClinic = Notification(orgid = org, sendTo = org.id, serviceOrderId = service_order.id, sent = True, service = 'Implant Planning Report', user = usr.name, event = 'ORDER SUBMITTED', details = 'You have successfully submitted the order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/manageReportPlanning/'+str(service_order.id))
        notificationLab = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Implant Planning Report', user = usr.name, event = 'ORDER RECEIVED', details = 'You have recieved a new order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/planning_Orders/3')
        notificationLab.save()
        notificationClinic.save()
    if service_order.refstudy == 'Implant Surgical Guide':
        notificationClinic = Notification(orgid = org, sendTo = org.id, serviceOrderId = service_order.id, sent = True, service = 'Implant Surgical Guide', user = usr.name, event = 'ORDER SUBMITTED', details = 'You have successfully submitted the order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/manageReportGuide/'+str(service_order.id))
        notificationLab = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Implant Surgical Guide', user = usr.name, event = 'ORDER RECEIVED', details = 'You have recieved a new order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/guide_orders/4')
        notificationLab.save()
        notificationClinic.save()
    if service_order.refstudy == 'Digital Lab Services' and service_order.preferredData == 'digitalData':
        notificationClinic = Notification(orgid = org, sendTo = org.id, serviceOrderId = service_order.id, sent = True, service = 'Digital Lab Services', user = usr.name, event = 'ORDER SUBMITTED', details = 'You have successfully submitted the order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/manageReportDigitalLab/'+str(service_order.id))
        notificationLab = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Digital Lab Services', user = usr.name, event = 'ORDER RECEIVED', details = 'You have recieved a new order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/lab_orders/5')
        notificationLab.save()
        notificationClinic.save()
    if service_order.refstudy == 'Digital Lab Services' and service_order.preferredData == 'nonDigitalData':
        notificationClinic = Notification(orgid = org, sendTo = org.id, serviceOrderId = service_order.id, sent = True, service = 'Digital Lab Services', user = usr.name, event = 'ORDER SUBMITTED', details = 'You have successfully submitted the order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/manageReportDigitalLab/'+str(service_order.id))
        notificationLab1 = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Digital Lab Services', user = usr.name, event = 'ORDER RECEIVED', details = 'You have recieved a new order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/lab_orders/5')
        notificationLab2 = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Digital Lab Services', user = usr.name, event = 'PICKUP REQUEST', details = 'You are requested to pick the order (Non-digital Data) for the order ID:' + str(service_order.order_id) + ', from '+str(org.address), date = datetime.now(), hyperLink = '/lab_orders/5')
        notificationClinic.save()
        notificationLab1.save()
        notificationLab2.save()
    service_log.save()
    service_order.save()
    lineItem = Prosthetic.objects.filter(repid = service_order.id)
    lineItem2 = Suricalguide.objects.filter(repid = service_order.id)
    if lineItem:
        for i in lineItem:
            i.reforgid = service_order.referTo
            i.save()
    if lineItem2:
        for j in lineItem2:
            j.reforgid = service_order.referTo
            j.save()
    my_total = org.topUpAvailable
    org.topUpAvailable = my_total - service_order.ref_price
    org.save()
    referOrgEmail = Organisation.objects.get(id=service_order.reforgid).email
    if service_order.refstudy == 'Radiological Report' or service_order.refstudy == 'Image Analysis Report' or service_order.refstudy == 'Implant Planning Report':
        # Send Mail code
        orderId = str(service_order.order_id)
        clinicName = org.orgname
        serviceName = service_order.refstudy
        details = EmailNotification.objects.get(eventCode = 'DRET-0009')
        connection = mail.get_connection()
        connection.open()
        from1 = 'info.dentread@gmail.com'
        subject1 = 'Order ' + str(orderId) + ' submitted successfully'
        subject2 = 'Order ' +str(orderId)+ ' received from ' + str(clinicName)
        message = "Dear, \n"+ str(usr.name) + '\n' + details.clinicSide%(orderId, serviceName) + '\nThank You \nDentread'
        message2 = 'Dear, \nAdmin '+'\n '+ details.adminSide%(serviceName, orderId, clinicName)
        email1 = org.email
        # email1 = 'souravmahato7643@gmail.com'
        email2 = 'support@dentread.com'
        clinicSideEmail = mail.EmailMessage(subject1, message, from1, [email1], connection = connection)
        adminSideEmail = mail.EmailMessage(subject2, message2, from1, [email2], connection = connection)
        try:
            connection.send_messages([clinicSideEmail, adminSideEmail])
            connection.close()
        except Exception as e:
            message = e
        eventLog = EventLog(eventCode = 'DRET-0009', event = 'New Order Submission' , log = 'A new Order hasbeen created from : ' + str(org.orgname), orgId = org.id, userId = usr.id, time = datetime.now())
        try:
            eventLog.save()
        except Exception as ex:
            eventMessage = ex
        
    if service_order.refstudy == 'Implant Surgical Guide' or service_order.refstudy == 'Digital Lab Services':
        # Send Mail code
        orderId = str(service_order.order_id)
        clinicName = org.orgname
        serviceName = service_order.refstudy
        details = EmailNotification.objects.get(eventCode = 'DRET-0009')
        connection = mail.get_connection()
        connection.open()
        from1 = 'info.dentread@gmail.com'
        subject1 = 'Order ' + str(orderId) + ' submitted successfully'
        subject2 = 'Order ' +str(orderId)+ ' received from ' + str(clinicName)
        subject3 = 'Pick-up Request For ' +str(service_order.order_id)
        message1 = "Dear, \n"+ str(usr.name) + '\n' + details.clinicSide%(orderId, serviceName) + '\nThank You \nDentread'
        message2 = 'Dear, \nAdmin '+'\n '+ details.adminSide%(serviceName, orderId, clinicName)
        message3 = 'Dear, \nLab Admin \nYou are requested to pick the order (Non-digital Data) for the order ID:' + str(service_order.order_id) + ', from '+str(org.address)
        email1 = org.email
        email2 = referOrgEmail
        clinicSideEmail = mail.EmailMessage(subject1, message1, from1, [email1], connection = connection)
        adminSideEmail = mail.EmailMessage(subject2, message2, from1, [email2], connection = connection)
        emailForPickup = ''
        if service_order.preferredData == 'nonDigitalData':
            emailForPickup = mail.EmailMessage(subject3, message3, from1, [email2], connection = connection)
        try:
            if service_order.preferredData == 'nonDigitalData':
                connection.send_messages([clinicSideEmail, adminSideEmail, emailForPickup])
            else:
                connection.send_messages([clinicSideEmail, adminSideEmail])
            connection.close()
        except Exception as e:
            message = e
        eventLog = EventLog(eventCode = 'DRET-0009', event = 'New Order Submission' , log = 'A new Order hasbeen created from : ' + str(org.orgname), orgId = org.id, userId = usr.id, time = datetime.now())
        try:
            eventLog.save()
        except Exception as ex:
            eventMessage = ex
    if service_order.refstudy == 'Digital Lab Services' and service_order.preferredData == 'nonDigitalData' and service_order.requestForShipment == 'Yes':
        return redirect('/createShipmentOrder/'+str(service_order.id))
    return redirect('/patientdetails/'+str(patient.id))

def payUsingWallet(request, id1, id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = id1)
    mycat = Maincat.objects.get(id=id2)
    patient = Patient.objects.get(id=service_order.pid)
    domain = Organisation.objects.get(orgtype="Domain Owner")
    if service_order.refstudy != 'Digital Lab Services' and service_order.refstudy != 'Implant Surgical Guide':
        service_order.reforgid = domain.id
    else:
        service_order.reforgid = service_order.referTo
    service_order.paymentStatus = 'Paid Using Wallet'
    service_order.status = 'Pending'
    service_order.save()
    service_log = ServiceLog(orgid = org, patient=patient.name, repid = service_order.id,sodrid = service_order.order_id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy,log = "CREATE SERVICE ORDER", message = 'Created a service order')
    
    if service_order.refstudy == 'Radiological Report':
        notificationClinic = Notification(orgid = org, sendTo = org.id, serviceOrderId = service_order.id, sent = True, service = 'Radiological Report', user = usr.name, event = 'ORDER SUBMITTED', details = 'You have successfully submitted the order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/manageReport/'+str(service_order.id))
        notificationLab = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Radiological Report', user = usr.name, event = 'ORDER RECEIVED', details = 'You have recieved a new order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/index_dent/1')
        notificationLab.save()
        notificationClinic.save()
    if service_order.refstudy == 'Image Analysis Report':
        notificationClinic = Notification(orgid = org, sendTo = org.id, serviceOrderId = service_order.id, sent = True, service = 'Image Analysis Report', user = usr.name, event = 'ORDER SUBMITTED', details = 'You have successfully submitted the order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/manageReportImage/'+str(service_order.id))
        notificationLab = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Image Analysis Report', user = usr.name, event = 'ORDER RECEIVED', details = 'You have recieved a new order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/image_Orders/2')
        notificationLab.save()
        notificationClinic.save()
    if service_order.refstudy == 'Implant Planning Report':
        notificationClinic = Notification(orgid = org, sendTo = org.id, serviceOrderId = service_order.id, sent = True, service = 'Implant Planning Report', user = usr.name, event = 'ORDER SUBMITTED', details = 'You have successfully submitted the order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/manageReportPlanning/'+str(service_order.id))
        notificationLab = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Implant Planning Report', user = usr.name, event = 'ORDER RECEIVED', details = 'You have recieved a new order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/planning_Orders/3')
        notificationLab.save()
        notificationClinic.save()
    if service_order.refstudy == 'Implant Surgical Guide':
        notificationClinic = Notification(orgid = org, sendTo = org.id, serviceOrderId = service_order.id, sent = True, service = 'Implant Surgical Guide', user = usr.name, event = 'ORDER SUBMITTED', details = 'You have successfully submitted the order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/manageReportGuide/'+str(service_order.id))
        notificationLab = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Implant Surgical Guide', user = usr.name, event = 'ORDER RECEIVED', details = 'You have recieved a new order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/guide_orders/4')
        notificationLab.save()
        notificationClinic.save()
    if service_order.refstudy == 'Digital Lab Services' and service_order.preferredData == 'digitalData':
        notificationClinic = Notification(orgid = org, sendTo = org.id, serviceOrderId = service_order.id, sent = True, service = 'Digital Lab Services', user = usr.name, event = 'ORDER SUBMITTED', details = 'You have successfully submitted the order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/manageReportDigitalLab/'+str(service_order.id))
        notificationLab = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Digital Lab Services', user = usr.name, event = 'ORDER RECEIVED', details = 'You have recieved a new order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/lab_orders/5')
        notificationLab.save()
        notificationClinic.save()
    if service_order.refstudy == 'Digital Lab Services' and service_order.preferredData == 'nonDigitalData':
        notificationClinic = Notification(orgid = org, sendTo = org.id, serviceOrderId = service_order.id, sent = True, service = 'Digital Lab Services', user = usr.name, event = 'ORDER SUBMITTED', details = 'You have successfully submitted the order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/manageReportDigitalLab/'+str(service_order.id))
        notificationLab1 = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Digital Lab Services', user = usr.name, event = 'ORDER RECEIVED', details = 'You have recieved a new order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/lab_orders/5')
        notificationLab2 = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Digital Lab Services', user = usr.name, event = 'PICKUP REQUEST', details = 'You are requested to pick the order (Non-digital Data) for the order ID:' + str(service_order.order_id) + ', from '+str(org.address), date = datetime.now(), hyperLink = '/lab_orders/5')
        notificationClinic.save()
        notificationLab1.save()
        notificationLab2.save()
    service_log.save()
    service_order.save()
    lineItem = Prosthetic.objects.filter(repid = service_order.id)
    lineItem2 = Suricalguide.objects.filter(repid = service_order.id)
    if lineItem:
        for i in lineItem:
            i.reforgid = service_order.referTo
            i.save()
    if lineItem2:
        for j in lineItem2:
            j.reforgid = service_order.referTo
            j.save()
    referOrgEmail = Organisation.objects.get(id=service_order.reforgid).email
    if service_order.refstudy == 'Radiological Report' or service_order.refstudy == 'Image Analysis Report' or service_order.refstudy == 'Implant Planning Report':
        # Send Mail code
        orderId = str(service_order.order_id)
        clinicName = org.orgname
        serviceName = service_order.refstudy
        details = EmailNotification.objects.get(eventCode = 'DRET-0009')
        connection = mail.get_connection()
        connection.open()
        from1 = 'info.dentread@gmail.com'
        subject1 = 'Order ' + str(orderId) + ' submitted successfully'
        subject2 = 'Order ' +str(orderId)+ ' received from ' + str(clinicName)
        message = "Dear, \n"+ str(usr.name) + '\n' + details.clinicSide%(orderId, serviceName) + '\nThank You \nDentread'
        message2 = 'Dear, \nAdmin '+'\n '+ details.adminSide%(serviceName, orderId, clinicName)
        email1 = org.email
        # email1 = 'souravmahato7643@gmail.com'
        email2 = 'support@dentread.com'
        clinicSideEmail = mail.EmailMessage(subject1, message, from1, [email1], connection = connection)
        adminSideEmail = mail.EmailMessage(subject2, message2, from1, [email2], connection = connection)
        try:
            connection.send_messages([clinicSideEmail, adminSideEmail])
            connection.close()
        except Exception as e:
            message = e
        eventLog = EventLog(eventCode = 'DRET-0009', event = 'New Order Submission' , log = 'A new Order hasbeen created from : ' + str(org.orgname), orgId = org.id, userId = usr.id, time = datetime.now())
        try:
            eventLog.save()
        except Exception as ex:
            eventMessage = ex
        
    if service_order.refstudy == 'Implant Surgical Guide' or service_order.refstudy == 'Digital Lab Services':
        # Send Mail code
        orderId = str(service_order.order_id)
        clinicName = org.orgname
        serviceName = service_order.refstudy
        details = EmailNotification.objects.get(eventCode = 'DRET-0009')
        connection = mail.get_connection()
        connection.open()
        from1 = 'info.dentread@gmail.com'
        subject1 = 'Order ' + str(orderId) + ' submitted successfully'
        subject2 = 'Order ' +str(orderId)+ ' received from ' + str(clinicName)
        subject3 = 'Pick-up Request For ' +str(service_order.order_id)
        message1 = "Dear, \n"+ str(usr.name) + '\n' + details.clinicSide%(orderId, serviceName) + '\nThank You \nDentread'
        message2 = 'Dear, \nAdmin '+'\n '+ details.adminSide%(serviceName, orderId, clinicName)
        message3 = 'Dear, \nLab Admin \nYou are requested to pick the order (Non-digital Data) for the order ID:' + str(service_order.order_id) + ', from '+str(org.address)
        email1 = org.email
        email2 = referOrgEmail
        clinicSideEmail = mail.EmailMessage(subject1, message1, from1, [email1], connection = connection)
        adminSideEmail = mail.EmailMessage(subject2, message2, from1, [email2], connection = connection)
        emailForPickup = ''
        if service_order.preferredData == 'nonDigitalData':
            emailForPickup = mail.EmailMessage(subject3, message3, from1, [email2], connection = connection)
        try:
            if service_order.preferredData == 'nonDigitalData':
                connection.send_messages([clinicSideEmail, adminSideEmail, emailForPickup])
            else:
                connection.send_messages([clinicSideEmail, adminSideEmail])
            connection.close()
        except Exception as e:
            message = e
        eventLog = EventLog(eventCode = 'DRET-0009', event = 'New Order Submission' , log = 'A new Order hasbeen created from : ' + str(org.orgname), orgId = org.id, userId = usr.id, time = datetime.now())
        try:
            eventLog.save()
        except Exception as ex:
            eventMessage = ex
    wallet = ClinicWalletInfo.objects.get(orgId = org)
    wallet.totalBalance = int(wallet.totalBalance) - int(service_order.ref_price)
    wallet.save()
    exp = WalletExpenses(orgId = org.id, orderId = service_order.order_id, amount = service_order.ref_price, date = datetime.today(), status = 'Debited for order Id:'+str(service_order.order_id))
    exp.save()
    if service_order.refstudy == 'Digital Lab Services' and service_order.preferredData == 'nonDigitalData' and service_order.requestForShipment == 'Yes':
        return redirect('/createShipmentOrder/'+str(service_order.id))
    return redirect('/patientdetails/'+str(patient.id))

def payUsingFreeService(request, id1, id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = id1)
    mycat = Maincat.objects.get(id = id2)
    patient = Patient.objects.get(id=service_order.pid)
    domain = Organisation.objects.get(orgtype="Domain Owner")
    if service_order.refstudy != 'Digital Lab Services' and service_order.refstudy != 'Implant Surgical Guide':
        service_order.reforgid = domain.id
    else:
        service_order.reforgid = service_order.referTo
    service_order.paymentStatus = 'Paid Using Dentread Free Credit'
    service_order.save()
    service_log = ServiceLog(orgid = org, patient=patient.name, repid = service_order.id,sodrid = service_order.order_id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy,log = "CREATE SERVICE ORDER", message = 'Created a service order')
    
    if service_order.refstudy == 'Radiological Report':
        notificationClinic = Notification(orgid = org, sendTo = org.id, serviceOrderId = service_order.id, sent = True, service = 'Radiological Report', user = usr.name, event = 'ORDER SUBMITTED', details = 'You have successfully submitted the order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/manageReport/'+str(service_order.id))
        notificationLab = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Radiological Report', user = usr.name, event = 'ORDER RECEIVED', details = 'You have recieved a new order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/index_dent/1')
        notificationLab.save()
        notificationClinic.save()
    if service_order.refstudy == 'Image Analysis Report':
        notificationClinic = Notification(orgid = org, sendTo = org.id, serviceOrderId = service_order.id, sent = True, service = 'Image Analysis Report', user = usr.name, event = 'ORDER SUBMITTED', details = 'You have successfully submitted the order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/manageReportImage/'+str(service_order.id))
        notificationLab = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Image Analysis Report', user = usr.name, event = 'ORDER RECEIVED', details = 'You have recieved a new order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/image_Orders/2')
        notificationLab.save()
        notificationClinic.save()
    if service_order.refstudy == 'Implant Planning Report':
        notificationClinic = Notification(orgid = org, sendTo = org.id, serviceOrderId = service_order.id, sent = True, service = 'Implant Planning Report', user = usr.name, event = 'ORDER SUBMITTED', details = 'You have successfully submitted the order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/manageReportPlanning/'+str(service_order.id))
        notificationLab = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Implant Planning Report', user = usr.name, event = 'ORDER RECEIVED', details = 'You have recieved a new order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/planning_Orders/3')
        notificationLab.save()
        notificationClinic.save()
    if service_order.refstudy == 'Implant Surgical Guide':
        notificationClinic = Notification(orgid = org, sendTo = org.id, serviceOrderId = service_order.id, sent = True, service = 'Implant Surgical Guide', user = usr.name, event = 'ORDER SUBMITTED', details = 'You have successfully submitted the order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/manageReportGuide/'+str(service_order.id))
        notificationLab = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Implant Surgical Guide', user = usr.name, event = 'ORDER RECEIVED', details = 'You have recieved a new order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/guide_orders/4')
        notificationLab.save()
        notificationClinic.save()
    if service_order.refstudy == 'Digital Lab Services' and service_order.preferredData == 'digitalData':
        notificationClinic = Notification(orgid = org, sendTo = org.id, serviceOrderId = service_order.id, sent = True, service = 'Digital Lab Services', user = usr.name, event = 'ORDER SUBMITTED', details = 'You have successfully submitted the order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/manageReportDigitalLab/'+str(service_order.id))
        notificationLab = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Digital Lab Services', user = usr.name, event = 'ORDER RECEIVED', details = 'You have recieved a new order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/lab_orders/5')
        notificationLab.save()
        notificationClinic.save()
    if service_order.refstudy == 'Digital Lab Services' and service_order.preferredData == 'nonDigitalData':
        notificationClinic = Notification(orgid = org, sendTo = org.id, serviceOrderId = service_order.id, sent = True, service = 'Digital Lab Services', user = usr.name, event = 'ORDER SUBMITTED', details = 'You have successfully submitted the order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/manageReportDigitalLab/'+str(service_order.id))
        notificationLab1 = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Digital Lab Services', user = usr.name, event = 'ORDER RECEIVED', details = 'You have recieved a new order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/lab_orders/5')
        notificationLab2 = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Digital Lab Services', user = usr.name, event = 'PICKUP REQUEST', details = 'You are requested to pick the order (Non-digital Data) for the order ID:' + str(service_order.order_id) + ', from '+str(org.address), date = datetime.now(), hyperLink = '/lab_orders/5')
        notificationClinic.save()
        notificationLab1.save()
        notificationLab2.save()
    service_log.save()
    service_order.save()
    lineItem = Prosthetic.objects.filter(repid = service_order.id)
    lineItem2 = Suricalguide.objects.filter(repid = service_order.id)
    if lineItem:
        for i in lineItem:
            i.reforgid = service_order.referTo
            i.save()
    if lineItem2:
        for j in lineItem2:
            j.reforgid = service_order.referTo
            j.save()
    referOrgEmail = Organisation.objects.get(id=service_order.reforgid).email
    if service_order.refstudy == 'Radiological Report' or service_order.refstudy == 'Image Analysis Report' or service_order.refstudy == 'Implant Planning Report':
        # Send Mail code
        orderId = str(service_order.order_id)
        clinicName = org.orgname
        serviceName = service_order.refstudy
        details = EmailNotification.objects.get(eventCode = 'DRET-0009')
        connection = mail.get_connection()
        connection.open()
        from1 = 'info.dentread@gmail.com'
        subject1 = 'Order ' + str(orderId) + ' submitted successfully'
        subject2 = 'Order ' +str(orderId)+ ' received from ' + str(clinicName)
        message = "Dear, \n"+ str(usr.name) + '\n' + details.clinicSide%(orderId, serviceName) + '\nThank You \nDentread'
        message2 = 'Dear, \nAdmin '+'\n '+ details.adminSide%(serviceName, orderId, clinicName)
        email1 = org.email
        # email1 = 'souravmahato7643@gmail.com'
        email2 = 'support@dentread.com'
        clinicSideEmail = mail.EmailMessage(subject1, message, from1, [email1], connection = connection)
        adminSideEmail = mail.EmailMessage(subject2, message2, from1, [email2], connection = connection)
        try:
            connection.send_messages([clinicSideEmail, adminSideEmail])
            connection.close()
        except Exception as e:
            message = e
        eventLog = EventLog(eventCode = 'DRET-0009', event = 'New Order Submission' , log = 'A new Order hasbeen created from : ' + str(org.orgname), orgId = org.id, userId = usr.id, time = datetime.now())
        try:
            eventLog.save()
        except Exception as ex:
            eventMessage = ex
        
    if service_order.refstudy == 'Implant Surgical Guide' or service_order.refstudy == 'Digital Lab Services':
        # Send Mail code
        orderId = str(service_order.order_id)
        clinicName = org.orgname
        serviceName = service_order.refstudy
        details = EmailNotification.objects.get(eventCode = 'DRET-0009')
        connection = mail.get_connection()
        connection.open()
        from1 = 'info.dentread@gmail.com'
        subject1 = 'Order ' + str(orderId) + ' submitted successfully'
        subject2 = 'Order ' +str(orderId)+ ' received from ' + str(clinicName)
        subject3 = 'Pick-up Request For ' +str(service_order.order_id)
        message1 = "Dear, \n"+ str(usr.name) + '\n' + details.clinicSide%(orderId, serviceName) + '\nThank You \nDentread'
        message2 = 'Dear, \nAdmin '+'\n '+ details.adminSide%(serviceName, orderId, clinicName)
        message3 = 'Dear, \nLab Admin \nYou are requested to pick the order (Non-digital Data) for the order ID:' + str(service_order.order_id) + ', from '+str(org.address)
        email1 = org.email
        email2 = referOrgEmail
        clinicSideEmail = mail.EmailMessage(subject1, message1, from1, [email1], connection = connection)
        adminSideEmail = mail.EmailMessage(subject2, message2, from1, [email2], connection = connection)
        emailForPickup = ''
        if service_order.preferredData == 'nonDigitalData':
            emailForPickup = mail.EmailMessage(subject3, message3, from1, [email2], connection = connection)
        try:
            if service_order.preferredData == 'nonDigitalData':
                connection.send_messages([clinicSideEmail, adminSideEmail, emailForPickup])
            else:
                connection.send_messages([clinicSideEmail, adminSideEmail])
            connection.close()
        except Exception as e:
            message = e
        eventLog = EventLog(eventCode = 'DRET-0009', event = 'New Order Submission' , log = 'A new Order hasbeen created from : ' + str(org.orgname), orgId = org.id, userId = usr.id, time = datetime.now())
        try:
            eventLog.save()
        except Exception as ex:
            eventMessage = ex
    
    MyOrder = 0
    if service_order.refstudy == 'Radiological Report' or service_order.refstudy == 'Image Analysis Report':
        if service_order.refstudy == 'Radiological Report':
            radio = RadiologycalServices.objects.filter(repid = service_order.id).count()
            MyOrder +=  radio
        elif service_order.refstudy == 'Image Analysis Report':
            radio = ImageAnalysis.objects.filter(repid = service_order.id).count()
            MyOrder +=  radio
        else:
            MyOrder = 0
        free = FreeService.objects.get(orgId = org.id)
        test = ''
        if int(free.firstMonth) <= MyOrder and int(free.firstMonth) != 0:
            free.firstMonth = int(free.firstMonth) - int(MyOrder)
        elif int(free.secondMonth) <= MyOrder and int(free.firstMonth) != 0:
            free.secondMonth = int(free.secondMonth) - int(MyOrder)
        elif int(free.thirdMonth) <= MyOrder and int(free.firstMonth) != 0:
            free.thirdMonth = int(free.thirdMonth) - int(MyOrder)
        else:
            test = 1
        free.save()
    # if service_order.refstudy == 'Digital Lab Services' and service_order.preferredData == 'nonDigitalData':
    #     return redirect('/createShipmentOrder/'+str(service_order.id))
    return redirect('/patientdetails/'+str(patient.id))


def refer_dentread(request, id1, id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)  
    service_order = ServiceOrder.objects.get(id=id1)
    patient = Patient.objects.get(id=service_order.pid)
    domain=Organisation.objects.get(orgtype="Domain Owner")
    mycat = Maincat.objects.get(id = id2)
    studies = Study.objects.filter(orgid=domain).filter(topcat=mycat.topcat)
    if mycat.topcat == "Digital Lab Services":
        return redirect('/refer_dentlab/'+str(id1)+'/'+str(id2))
    if mycat.topcat == "Implant Surgical Guide":
        return redirect('/refer_surgident/'+str(id1)+'/'+str(id2))
    if mycat.topcat == "Image Analysis Report":
        return redirect('/refer_ImageAnalysis/'+str(id1)+'/'+str(id2))
    if mycat.topcat == "Implant Planning Report":
        return redirect('/refer_ImplantPlanning/'+str(id1)+'/'+str(id2)) 
    if mycat.topcat == "Radiological Report":
        return redirect('/refer_RadiologicalService/'+str(id1)+'/'+str(id2))

    data={'usr':usr, 'org':org, 'service_order':service_order, 'patient':patient, 'studies':studies, 'mycat':mycat, 'topcat':topcat}
    return render(request, 'refer_dentread.html', data)

def refer_RadiologicalService(request, id1, id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id1)
    patient = Patient.objects.get(id=service_order.pid)
    domain = Organisation.objects.get(orgtype="Domain Owner")
    comment = Comments.objects.filter(repid=service_order.id)
    mycat = Maincat.objects.get(id = id2)
    studies = Study.objects.filter(orgid=domain).filter(topcat=mycat.topcat)
    image = RadiologycalServices.objects.filter(repid=service_order.id)
    add_image = Study.objects.filter(topcat = "Radiological Report")
    requirements = Requirements.objects.filter(topcat = 'Radiological Report')
    icon = ''
    currency = ''
    if org.country == 'IN':
        currency = 'price'
        icon = '<i class="fa-solid fa-indian-rupee-sign"></i>'
    else:
        currency = 'dollarPrice'
        icon = '<i class="fa-solid fa-dollar-sign"></i>'
    otherImage = IOSFile.objects.filter(repid = service_order.id)
    
    if request.method == "POST":
        tooth=request.POST.getlist('checks[]')
        data_type = request.POST.get('title')
        service_catagory = request.POST.get('categ')
        finding_requires = request.POST.get('finding_requires')
        price = request.POST.get('price')
        remark=request.POST.get('remark')
        notation = request.POST.get('notation-select') 
        service_order.order_id = "RR" + str(service_order.id)
        service_order.save()
        if org.orgtype == "Dental Clinic":
            radiology = RadiologycalServices(repid = service_order.id, name = patient.name, pid = patient.pid, orgid = org, tooth = tooth, data_type = data_type, service_catagory = service_catagory, finding_requires = finding_requires, price = price, remark = remark, status = "Pending", badge='badge badge-danger', service_name ='Radiological Report')
        else:
            radiology = RadiologycalServices(repid = service_order.id, name = patient.name, pid = patient.pid, orgid = org, parent_orgid=org.parent_id, tooth = tooth, data_type = data_type, service_catagory = service_catagory, finding_requires = finding_requires, price = price, remark = remark, status = "Pending", badge='badge badge-danger', service_name ='Radiological Report')
        radiology.save()
        radiology.item_id = str(service_order.order_id)  + "-" + str(radiology.id)
        radiology.sodrid = str(radiology.id)
        radiology.save()
        images = RadiologycalServices.objects.filter(repid=service_order.id)
        price = images.values('price')
        sum = price.aggregate(Sum('price'))
        total_sum = sum['price__sum']
        service_order.ref_price = total_sum
        service_order.remark = remark
        service_order.refstudy=mycat.topcat
        service_order.patient_id = patient.pid
        if service_order.tooth_notation == 'FDI':
            service_order.tooth_notation = notation
        service_order.save()
        
        otherImage = IOSFile.objects.filter(repid = service_order.id)
        data = {'usr': usr, 'org': org, 'icon': icon, 'requirements': requirements, 'otherImage': otherImage, 'currency': currency, 'service_order': service_order,'comment':comment, 'patient': patient, 'studies': studies, 'mycat': mycat,
                'topcat': topcat, 'domain': domain, 'image': image}
        return render(request, 'refer_radiologycal.html', data)
    data = {'usr':usr, 'org':org, 'service_order': service_order, 'requirements': requirements, 'otherImage': otherImage, 'icon': icon, 'currency': currency, 'patient':patient, 'studies':studies, 'mycat':mycat, 'topcat':topcat, 'domain':domain, 'image':image, 'add_image': add_image,'comment': comment}
    return render(request, 'refer_radiologycal.html', data)

def refer_ImageAnalysis(request,id1,id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id1)
    patient=Patient.objects.get(id=service_order.pid)
    domain = Organisation.objects.get(orgtype="Domain Owner")
    mycat = Maincat.objects.get(id = id2)
    studies=Study.objects.filter(orgid=domain).filter(topcat=mycat.topcat)
    image = ImageAnalysis.objects.filter(repid=service_order.id)
    add_image = Study.objects.filter(topcat = "Image Analysis Report")
    comment = Comments.objects.filter(repid=service_order.id)
    requirements = Requirements.objects.all()
    icon = ''
    currency = ''
    if org.country == 'IN':
        currency = 'price'
        icon = '<i class="fa-solid fa-indian-rupee-sign"></i>'
    else:
        currency = 'dollarPrice'
        icon = '<i class="fa-solid fa-dollar-sign"></i>'
    otherImage = IOSFile.objects.filter(repid = service_order.id)
    if request.method == "POST":
        tooth=request.POST.getlist('checks[]')
        data_type = request.POST.get('title')
        service_catagory = request.POST.get('categ')
        sub_category = request.POST.get('sub-categ')
        price = request.POST.get('price')
        remark=request.POST.get('remark')
        notation = request.POST.get('notation-select')
        
        service_order.order_id = "IA" + str(service_order.id)
        service_order.save()
        
        if org.orgtype == "Dental Clinic":
            imageAnalysis = ImageAnalysis(repid = service_order.id, pid = patient.id, name = patient.name, orgid=org, tooth = tooth, data_type = data_type, service_catagory = service_catagory, sub_category = sub_category, price = price, remark = remark, badge='badge badge-danger', service_name = 'Image Analysis Report', status ='Pending')
        else:
            imageAnalysis = ImageAnalysis(repid = service_order.id, pid = patient.id, name = patient.name, orgid =org, parent_orgid = org.parent_id, tooth = tooth, data_type = data_type, service_catagory = service_catagory, sub_category = sub_category, price = price, remark = remark, badge='badge badge-danger', service_name = 'Image Analysis Report', status ='Pending')
        imageAnalysis.save()
        imageAnalysis.item_id = str(service_order.order_id)  + "-" + str(imageAnalysis.id)
        imageAnalysis.sodrid = str(imageAnalysis.id)
        imageAnalysis.save()
        images = ImageAnalysis.objects.filter(repid=service_order.id)
        price = images.values('price')
        sum = price.aggregate(Sum('price'))
        total_sum = sum['price__sum']
        service_order.ref_price = total_sum
        service_order.remark = remark
        service_order.refstudy=mycat.topcat
        service_order.patient_id = patient.pid
        if service_order.tooth_notation == 'FDI':
            service_order.tooth_notation = notation
        service_order.save()
        otherImage = IOSFile.objects.filter(repid = service_order.id)
        data = {'usr': usr, 'org': org, 'icon': icon, 'requirements': requirements, 'otherImage': otherImage, 'currency': currency, 'service_order': service_order,'comment':comment, 'patient': patient, 'studies': studies, 'mycat': mycat,
                'topcat': topcat, 'domain': domain, 'image': image}
        return render(request, 'refer_dentread.html', data)
    data={'usr':usr, 'org':org,  'service_order':service_order, 'requirements': requirements, 'otherImage': otherImage, 'icon': icon, 'currency': currency, 'comment':comment, 'patient':patient, 'studies':studies, 'mycat':mycat, 'topcat':topcat, 'domain':domain, 'image':image, 'add_image': add_image}
    return render(request, 'refer_dentread.html', data)

def edit_Image(request,id1,id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id1)
    patient=Patient.objects.get(id=service_order.pid)
    domain=Organisation.objects.get(orgtype="Domain Owner")
    mycat = Maincat.objects.get(id = id2)
    studies=Study.objects.filter(orgid=domain).filter(topcat=mycat.topcat)
    image = ImageAnalysis.objects.filter(repid=service_order.id)
    add_image = Study.objects.filter(topcat = "Image Analysis Report")
    comment = Comments.objects.filter(repid=service_order.id)
    requirements = Requirements.objects.all()
    icon = ''
    currency = ''
    if org.country == 'IN':
        currency = 'price'
        icon = '<i class="fa-solid fa-indian-rupee-sign"></i>'
    else:
        currency = 'dollarPrice'
        icon = '<i class="fa-solid fa-dollar-sign"></i>'
    otherImage = IOSFile.objects.filter(repid = service_order.id)
    if request.method == "POST":
        tooth=request.POST.getlist('checks[]')
        data_type = request.POST.get('title')
        service_catagory = request.POST.get('categ')
        sub_category = request.POST.get('sub-categ')
        price = request.POST.get('price')
        remark=request.POST.get('remark')
        notation = request.POST.get('notation-select')
        service_order.order_id = "IA" + str(service_order.id)
        service_order.save()
        
        if org.orgtype == "Dental Clinic":
            imageAnalysis = ImageAnalysis(repid = service_order.id, pid = patient.id, name = patient.name, orgid=org, tooth = tooth, data_type = data_type, service_catagory = service_catagory, sub_category = sub_category, price = price, remark = remark, badge='badge badge-danger', service_name = 'Image Analysis Report', status ='Pending')
        else:
            imageAnalysis = ImageAnalysis(repid = service_order.id, pid = patient.id, name = patient.name, orgid =org, parent_orgid = org.parent_id, tooth = tooth, data_type = data_type, service_catagory = service_catagory, sub_category = sub_category, price = price, remark = remark, badge='badge badge-danger', service_name = 'Image Analysis Report', status ='Pending')
        imageAnalysis.save()
        imageAnalysis.item_id = str(service_order.order_id)  + "-" + str(imageAnalysis.id)
        imageAnalysis.sodrid = str(imageAnalysis.id)
        imageAnalysis.save()
        images = ImageAnalysis.objects.filter(repid=service_order.id)
        price = images.values('price')
        sum = price.aggregate(Sum('price'))
        total_sum = sum['price__sum']
        service_order.ref_price = total_sum
        service_order.remark = remark
        service_order.refstudy=mycat.topcat
        service_order.patient_id = patient.pid
        if service_order.tooth_notation == 'FDI':
            service_order.tooth_notation = notation
        service_order.save()
        otherImage = IOSFile.objects.filter(repid = service_order.id)
        data = {'usr': usr, 'org': org, 'icon': icon, 'requirements': requirements, 'otherImage': otherImage, 'currency': currency, 'service_order': service_order,'comment':comment, 'patient': patient, 'studies': studies, 'mycat': mycat,
                'topcat': topcat, 'domain': domain, 'image': image}
        return render(request, 'refer_dentread.html', data)
    data={'usr':usr, 'org':org,  'service_order':service_order, 'requirements': requirements, 'otherImage': otherImage, 'icon': icon, 'currency': currency, 'comment':comment, 'patient':patient, 'studies':studies, 'mycat':mycat, 'topcat':topcat, 'domain':domain, 'image':image, 'add_image': add_image}
    return render(request, 'refer_dentread.html', data)


def edit_Radio(request,id1,id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id1)
    patient = Patient.objects.get(id=service_order.pid)
    domain = Organisation.objects.get(orgtype="Domain Owner")
    comment = Comments.objects.filter(repid=service_order.id)
    mycat = Maincat.objects.get(id = id2)
    studies = Study.objects.filter(orgid=domain).filter(topcat=mycat.topcat)
    image = RadiologycalServices.objects.filter(repid=service_order.id)
    add_image = Study.objects.filter(topcat = "Radiological Report")
    requirements = Requirements.objects.filter(topcat = 'Radiological Report')
    icon = ''
    currency = ''
    if org.country == 'IN':
        currency = 'price'
        icon = '<i class="fa-solid fa-indian-rupee-sign"></i>'
    else:
        currency = 'dollarPrice'
        icon = '<i class="fa-solid fa-dollar-sign"></i>'
    otherImage = IOSFile.objects.filter(repid = service_order.id)
    
    if request.method == "POST":
        tooth=request.POST.getlist('checks[]')
        data_type = request.POST.get('title')
        service_catagory = request.POST.get('categ')
        finding_requires = request.POST.get('finding_requires')
        price = request.POST.get('price')
        remark=request.POST.get('remark')
        notation = request.POST.get('notation-select')
        service_order.order_id = "RR" + str(service_order.id)
        service_order.save()
        if org.orgtype == "Dental Clinic":
            radiology = RadiologycalServices(repid = service_order.id, name = patient.name, pid = patient.pid, orgid = org, tooth = tooth, data_type = data_type, service_catagory = service_catagory, finding_requires = finding_requires, price = price, remark = remark, status = "Pending", badge='badge badge-danger', service_name ='Radiological Report')
        else:
            radiology = RadiologycalServices(repid = service_order.id, name = patient.name, pid = patient.pid, orgid = org, parent_orgid=org.parent_id, tooth = tooth, data_type = data_type, service_catagory = service_catagory, finding_requires = finding_requires, price = price, remark = remark, status = "Pending", badge='badge badge-danger', service_name ='Radiological Report')
        radiology.save()
        radiology.item_id = str(service_order.order_id)  + "-" + str(radiology.id)
        radiology.sodrid = str(radiology.id)
        radiology.save()
        images = RadiologycalServices.objects.filter(repid=service_order.id)
        price = images.values('price')
        sum = price.aggregate(Sum('price'))
        total_sum = sum['price__sum']
        service_order.ref_price = total_sum
        service_order.remark = remark
        service_order.refstudy=mycat.topcat
        service_order.patient_id = patient.pid
        if service_order.tooth_notation == 'FDI':
            service_order.tooth_notation = notation
        service_order.save()
        
        otherImage = IOSFile.objects.filter(repid = service_order.id)
        data = {'usr': usr, 'org': org, 'icon': icon, 'requirements': requirements, 'otherImage': otherImage, 'currency': currency, 'service_order': service_order,'comment':comment, 'patient': patient, 'studies': studies, 'mycat': mycat,
                'topcat': topcat, 'domain': domain, 'image': image}
        return render(request, 'refer_radiologycal.html', data)
    data = {'usr':usr, 'org':org, 'service_order': service_order, 'requirements': requirements, 'otherImage': otherImage, 'icon': icon, 'currency': currency, 'patient':patient, 'studies':studies, 'mycat':mycat, 'topcat':topcat, 'domain':domain, 'image':image, 'add_image': add_image,'comment': comment}
    return render(request, 'refer_radiologycal.html', data)

def updateOrder(request, id1, id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2 
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id1)
    patient = Patient.objects.get(id=service_order.pid)
    if request.method == "POST":
        data_type = request.POST.get('title')
        service_catagory = request.POST.get('categ')
        sub_categ = request.POST.get('sub-categ')
        price = request.POST.get('price')
        remark=request.POST.get('remark')
        radio_order = RadiologycalServices.objects.get(pk=id2)
        radio_order.data_type = data_type
        radio_order.service_catagory = service_catagory
        radio_order.finding_requires = sub_categ
        radio_order.price = price
        radio_order.remark = remark
        radio_order.save()
        images = RadiologycalServices.objects.filter(repid=service_order.id)
        price = images.values('price')
        sum = price.aggregate(Sum('price'))
        total_sum = sum['price__sum']
        service_order.ref_price = total_sum
        service_order.save()
        notification = Notification(orgid = org, sendTo = radio_order.orgid_id, serviceOrderId = service_order.id, sent = True, lineItemId = radio_order.id, service = 'Radiological Report', user = usr.name, event = 'ORDER DETAILS UPDATED', details = 'Your order details has been successfully updated by Dentread for the order ID: '+str(service_order.order_id) + ' and line item ID: '+ str(radio_order.item_id), date = datetime.now(), hyperLink = '/manageReport/'+str(service_order.id))
        notification.save()
        service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy, log = "EDITED SERVICE ORDER LINE ITEM", message = 'Modified Order Line-item')
        service_log.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def updateOrderImage(request, id1, id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2 
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id1)
    patient = Patient.objects.get(id=service_order.pid)
    if request.method == "POST":
        data_type = request.POST.get('title')
        service_catagory = request.POST.get('categ')
        sub_catagory = request.POST.get('sub-categ')
        price = request.POST.get('price')
        remark=request.POST.get('remark')
        image_order = ImageAnalysis.objects.get(pk=id2)
        image_order.data_type = data_type
        image_order.service_catagory = service_catagory
        image_order.sub_category = sub_catagory
        image_order.price = price
        image_order.remark = remark
        image_order.save()
        images = ImageAnalysis.objects.filter(repid=service_order.id)
        price = images.values('price')
        sum = price.aggregate(Sum('price'))
        total_sum = sum['price__sum']
        service_order.ref_price = total_sum
        service_order.save()
        notification = Notification(orgid = org, sendTo = image_order.orgid_id, serviceOrderId = service_order.id, sent = True, lineItemId = image_order.id, service = 'Image Analysis Report', user = usr.name, event = 'ORDER DETAILS UPDATED', details = 'Your order details has been successfully updated by Dentread for the order ID: '+str(service_order.order_id) + ' and line item ID: '+ str(image_order.item_id), date = datetime.now(), hyperLink = '/manageReportImage/'+str(service_order.id))
        notification.save()
        service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy, log = "EDITED SERVICE ORDER LINE ITEM ", message = 'Modified Order Line-item')
        service_log.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def updateOrderGuide(request, id1, id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id1)
    patient = Patient.objects.get(id=service_order.pid)
    if request.method == "POST":
        data_type1 = request.POST.get('data_type1')
        data_type2 = request.POST.get('data_type2')
        guide_type = request.POST.get('guide_type')
        output_type = request.POST.get('output_type')
        planning_type = request.POST.get('planning_type')
        price = request.POST.get('price')
        remark=request.POST.get('remark')
        image_order = Suricalguide.objects.get(pk=id2)
        image_order.data_type1 = data_type1
        image_order.data_type2 = data_type2
        image_order.guide_type = guide_type
        image_order.output_type = output_type
        image_order.planning_type = planning_type
        image_order.price = price
        image_order.remark = remark
        image_order.save()
        notification = Notification(orgid = org, sendTo = image_order.orgid_id, serviceOrderId = service_order.id, sent = True, lineItemId = image_order.id, service = 'Implant Surgical Guide', user = usr.name, event = 'ORDER DETAILS UPDATED', details = 'Your order details has been successfully updated by the lab for the order ID: '+str(service_order.order_id) + ' and line item ID: '+ str(image_order.item_id), date = datetime.now(), hyperLink = '/manageReportGuide/'+str(service_order.id))
        notification.save()
        service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy, log = "EDITED SERVICE ORDER LINE ITEM ", message = 'Modified Order Line-item')
        service_log.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def updateOrderDigitalLab(request, id1, id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2 
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id1)
    patient = Patient.objects.get(id=service_order.pid)
    if request.method == "POST":
        type = request.POST.get('type')
        method = request.POST.get('method')
        material = request.POST.get('material')
        price = request.POST.get('price')
        date = request.POST.get('date')
        remark = request.POST.get('remark')
        image_order = Prosthetic.objects.get(pk=id2)
        image_order.type = type
        image_order.method = method
        image_order.material = material
        image_order.price = price
        image_order.expectedDate = date
        image_order.remark = remark
        image_order.save()
        service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy, log = "EDITED SERVICE ORDER LINE ITEM ", message = 'Modified Order Line-item')
        notification = Notification(orgid = org, sendTo = image_order.orgid_id, serviceOrderId = service_order.id, sent = True, lineItemId = image_order.id, service = 'Digital Lab Services', user = usr.name, event = 'ORDER DETAILS UPDATED', details = 'Your order details has been successfully updated by the lab for the order ID: '+str(service_order.order_id) + ' and line item ID: '+ str(image_order.item_id), date = datetime.now(), hyperLink = '/manageReportDigital/'+str(service_order.id))
        notification.save()
        service_log.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def updateOrderPlanning(request, id1, id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2 
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id1)
    patient = Patient.objects.get(id=service_order.pid)
    if request.method == "POST":
        data_type = request.POST.get('title')
        service_catagory = request.POST.get('categ')
        planning_type = request.POST.get('planning')
        price = request.POST.get('price')
        remark=request.POST.get('remark')
        
        image_order = ImplantPlanning.objects.get(pk=id2)
        image_order.data_type = data_type
        image_order.service_catagory = service_catagory
        image_order.planning_type = planning_type
        image_order.price = price
        image_order.remark = remark
        image_order.save()
        images = ImplantPlanning.objects.filter(repid=service_order.id)
        price = images.values('price')
        sum = price.aggregate(Sum('price'))
        total_sum = sum['price__sum']
        service_order.ref_price = total_sum
        service_order.save()
        notification = Notification(orgid = org, sendTo = image_order.orgid_id, serviceOrderId = service_order.id, sent = True, lineItemId = image_order.id, service = 'Implant Planning Report', user = usr.name, event = 'ORDER DETAILS UPDATED', details = 'Your order details has been successfully updated by Dentread for the order ID: '+str(service_order.order_id) + ' and line item ID: '+ str(image_order.item_id), date = datetime.now(), hyperLink = '/manageReportPlanning/'+str(service_order.id))
        notification.save()
        service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy, log = "EDITED SERVICE ORDER LINE ITEM ", message = 'Modified Order Line-item')
        service_log.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def cancelOrder(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id)
    service_order.delete()
    return redirect('/login_clinic')
def uploadedImage(request,id1,id2):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id1)
    radio = RadiologycalServices.objects.get(id=id2)
    file = IOSFile.objects.filter(repid = service_order.id).filter(sodrid = radio.id)
    data = {'file': file}
    return render(request,review_RadioOrder.html, data)

def ajaxUrl(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    if request.method == 'POST':
        id1 = request.POST.get('id1')
        id2 = request.POST.get('id2')
        service_order = ServiceOrder.objects.get(id=id1)
        radio = RadiologycalServices.objects.get(id=id2)
        file = IOSFile.objects.filter(repid = service_order.id).filter(sodrid = radio.id)
    return JsonResponse({'file': file})

def radioOrderComment(request, id1, id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    usr = Users.objects.get(username = request.user)
    org = Organisation.objects.get(id = usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = id1)
    mycat = Maincat.objects.get(id = id2)
    if request.method == 'POST':
        comment = request.POST.get('comment')
        name=usr.name
        comments = Comments(name=name,orgid = org, comment=comment, repid = service_order.id)
        comments.save()
        return redirect('/refer_RadiologicalService/'+str(service_order.id)+'/'+str(mycat.id))

def planningOrderComment(request, id1, id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    usr = Users.objects.get(username = request.user)
    org = Organisation.objects.get(id = usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = id1)
    mycat = Maincat.objects.get(id = id2)
    if request.method == 'POST':
        comment = request.POST.get('comment')
        name = usr.name
        comments = Comments(name=name,orgid = org, comment=comment, repid = service_order.id)
        comments.save()
        return redirect('/refer_ImplantPlanning/'+str(service_order.id)+'/'+str(mycat.id))


def imageOrderComment(request, id1, id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    usr = Users.objects.get(username = request.user)
    org = Organisation.objects.get(id = usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = id1)
    mycat = Maincat.objects.get(id = id2)
    if request.method == 'POST':
        comment = request.POST.get('comment')
        name=usr.name
        comments = Comments(name=name,orgid = org, comment=comment, repid = service_order.id)
        comments.save()
        return redirect('/refer_ImageAnalysis/'+str(service_order.id)+'/'+str(mycat.id))

def guideOrderComment(request, id1, id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    usr = Users.objects.get(username = request.user)
    org = Organisation.objects.get(id = usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = id1)
    mycat = Maincat.objects.get(id = id2)
    if request.method == 'POST':
        comment = request.POST.get('comment')
        name=usr.name
        comments = Comments(name=name,orgid = org, comment=comment, repid = service_order.id)
        comments.save()
        return redirect('/refer_surgident/'+str(service_order.id)+'/'+str(mycat.id))

def clinicComment(request, id):
    usr = Users.objects.get(username = request.user)
    org = Organisation.objects.get(id = usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = id)
    patient=Patient.objects.get(id=service_order.pid)
    domain=Organisation.objects.get(orgtype="Domain Owner")
    image = RadiologycalServices.objects.filter(repid=service_order.id)
    add_image = Study.objects.filter(topcat = "Radiological Report")
    patient = Patient.objects.get(id = service_order.pid)
    if request.method == 'POST':
        comment = request.POST.get('comment')
        name=usr.name
        comments = Comments(name=name,orgid = org, comment=comment, repid = service_order.id)
        comments.save()
        service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy, log = "EDITED SERVICE ORDER", message = 'Post a Comment')
        service_log.save()
        return redirect('/radiological_status/'+str(service_order.id))
    data = {'usr': usr, 'org': org, 'service_order': service_order, 'topcat': topcat, 'patient': patient, 'comments':comments, 'domain':domain, 'image':image, 'add_image': add_image}
    return render(request, 'refer_radiologycal.html', data)

def clinicCommentImage(request, id):
    usr = Users.objects.get(username = request.user)
    org = Organisation.objects.get(id = usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = id)
    patient=Patient.objects.get(id=service_order.pid)
    domain=Organisation.objects.get(orgtype="Domain Owner")
    image = ImageAnalysis.objects.filter(repid=service_order.id)
    add_image = Study.objects.filter(topcat = "Radiological Report")
    patient = Patient.objects.get(id = service_order.pid)
    if request.method == 'POST':
        comment = request.POST.get('comment')
        name=usr.name
        comments = Comments(name=name,orgid = org, comment=comment, repid = service_order.id)
        comments.save()
        service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy, log = "EDITED SERVICE ORDER", message = 'Post a Comment')
        service_log.save()
        return redirect('/imageAnalysis_status/'+str(service_order.id))
    data = {'usr': usr, 'org': org, 'service_order': service_order, 'topcat': topcat, 'patient': patient, 'comments':comments, 'domain':domain, 'image':image, 'add_image': add_image}
    return render(request, 'image_status.html', data)

def clinicSideCommment(request, id):
    usr = Users.objects.get(username = request.user)
    org = Organisation.objects.get(id = usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = id)
    patient = Patient.objects.get(id = service_order.pid)
    if request.method == 'POST':
        comment = request.POST.get('comment')
        name=usr.name
        comments = Comments(name=name,orgid = org, comment=comment, repid = service_order.id)
        comments.save()
        service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, user = usr.name, usertype = usr.department, service_name = service_order.refstudy, log = "EDITED SERVICE ORDER", message = 'Post a Comment')
        service_log.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def uploadOtherFiles(request, pk, id1, id2):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    topcat = Topcat.objects.get(id = id1)
    image = RadiologycalServices.objects.get(id = id2)
    if request.method == "POST" and 'file' in request.FILES:
        for f in request.FILES.getlist('file'):
            sfile = OtherImageFile(file=f, repid = service_order.id, topid = topcat.id, sodrid = image.id, orgid=org, size = f.size)
            sfile.save()
            html = "<html><body>It is now %s.</body></html>"
            return HttpResponse(html)
    return render(request, "refer_radiologycal.html", {'service_order':service_order, 'image': image})

from django.utils import timezone

def review_order(request, id1, id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order=ServiceOrder.objects.get(id=id1)
    patient=Patient.objects.get(id=service_order.pid)
    domain = Organisation.objects.get(orgtype="Domain Owner")
    topcat= Topcat.objects.filter(status="Active")
    mycat = Maincat.objects.get(id=id2)
    studies = Study.objects.filter(orgid=domain).filter(topcat=mycat.topcat)
    add_image = Study.objects.filter(topcat = "Image Analysis Report")
    image = ImageAnalysis.objects.filter(repid=service_order.id)
    price = image.values('price')
    sum = price.aggregate(Sum('price'))
    total_sum = sum['price__sum']
    service_order.ref_price = total_sum
    service_order.save()
    icon = ''
    currency = ''
    if org.country == 'IN':
        currency = 'price'
        icon = '<i class="fa-solid fa-indian-rupee-sign"></i>'
    else:
        currency = 'dollarPrice'
        icon = '<i class="fa-solid fa-dollar-sign"></i>'
    
    if service_order.discount == "0":
        dis = "yes"
    else:
        dis = None
    
    # Enable Payment Option
    enableButton = ''
    message = ''
    if org.paymentOption == 'payLater' and org.topUpAvailable <=  total_sum:
        enableButton = 'disabled'
        message = 'You have exceeded your Dentread credit-limit quota. Your available Balance is ₹ ' +str(org.topUpAvailable) +'. Please clear your outstanding dues to reset your credit-limit to continue using Dentread. Contact info@dentread.com to clear your dues.'
        
    elif org.paymentOption != 'payLater':
        enableButton = 'd-none'
    
    get_timezone = timezone.get_current_timezone()
    today = today = datetime.now(get_timezone)
    countOrder = image.count()
    free = FreeService.objects.filter(orgId = org.id)
    freeAvailService = ''
    if free:
        free_service = FreeService.objects.get(orgId = org.id)
        firstDate = free_service.startDate1
        secondDate = free_service.startDate2
        thirdDate = free_service.startDate3
        if free_service.firstMonth == None:
            free_service.firstMonth = 0
        if free_service.secondMonth == None:
            free_service.secondMonth = 0
        if free_service.thirdMonth == None:
            free_service.thirdMonth = 0
        
        if int(free_service.firstMonth) != 0 and countOrder <= int(free_service.firstMonth) and firstDate >= today:
            freeAvailService = 'Yes'
        elif int(free_service.secondMonth) != 0 and countOrder <= int(free_service.secondMonth) and secondDate >= today:
            freeAvailService = 'Yes'
        elif int(free_service.thirdMonth) != 0 and countOrder <= int(free_service.thirdMonth) and thirdDate >= today:
            freeAvailService = 'Yes'
        else:
            freeAvailService = 'No'
    clinicWallet = ClinicWalletInfo.objects.filter(orgId = org)
    walletPayment = ''
    if clinicWallet:
        wallet = ClinicWalletInfo.objects.get(orgId = org)
        if wallet.totalBalance <= total_sum:
            walletPayment = 'No'
        else:
            walletPayment = 'Yes'
    
    context = {'usr': usr, 'studies': studies,'message': message, 'icon': icon, 'currency': currency, 'enableButton': enableButton,'domain': domain, 'service_order': service_order,'topcat': topcat, 'image': image, 'patient': patient, 'org': org, 'dis': dis, 'total_sum':total_sum,'mycat': mycat, 'freeAvailService': freeAvailService, 'walletPayment': walletPayment}
    return render(request, "review_refer.html", context)

def review_RadioOrder(request, id1, id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    domain = Organisation.objects.get(orgtype = "Domain Owner")
    service_order = ServiceOrder.objects.get(id=id1)
    patient = Patient.objects.get(id=service_order.pid)
    topcat = Topcat.objects.filter(status = "Active")
    mycat = topcat.get(id=id2)
    image = RadiologycalServices.objects.filter(repid=service_order.id)
    price = image.values('price')
    sum = price.aggregate(Sum('price'))
    total_sum = sum['price__sum']
    service_order.ref_price = total_sum
    service_order.save()
    if service_order.discount == "0":
        dis = "yes"
    else:
        dis = None
    
    # Price Symbol
    icon = ''
    currency = ''
    if org.country == 'IN':
        currency = 'price'
        icon = '<i class="fa-solid fa-indian-rupee-sign"></i>'
    else:
        currency = 'dollarPrice'
        icon = '<i class="fa-solid fa-dollar-sign"></i>'
    # Enable Payment Option
    enableButton = ''
    message = ''
    if org.paymentOption == 'payLater' and org.topUpAvailable <=  total_sum:
        enableButton = 'disabled'
        message = 'You have exceeded your Dentread credit-limit quota. Your available Balance is ₹ ' +str(org.topUpAvailable) +'. Please clear your outstanding dues to reset your credit-limit to continue using Dentread. Contact info@dentread.com to clear your dues.'
        
    elif org.paymentOption != 'payLater':
        enableButton = 'd-none'
    
    get_timezone = timezone.get_current_timezone()
    today = today = datetime.now(get_timezone)
    countOrder = image.count()
    free = FreeService.objects.filter(orgId = org.id)
    freeAvailService = ''
    countFreeService = 0
    if free:
        free_service = FreeService.objects.get(orgId = org.id)
        firstDate = free_service.startDate1
        secondDate = free_service.startDate2
        thirdDate = free_service.startDate3
        if free_service.firstMonth == None:
            free_service.firstMonth = 0
        if free_service.secondMonth == None:
            free_service.secondMonth = 0
        if free_service.thirdMonth == None:
            free_service.thirdMonth = 0
        
        if int(free_service.firstMonth) != 0 and countOrder <= int(free_service.firstMonth) and firstDate >= today:
            freeAvailService = 'Yes'
            countFreeService = int(free_service.firstMonth)
        elif int(free_service.secondMonth) != 0 and countOrder <= int(free_service.secondMonth) and secondDate >= today:
            freeAvailService = 'Yes'
        elif int(free_service.thirdMonth) != 0 and countOrder <= int(free_service.thirdMonth) and thirdDate >= today:
            freeAvailService = 'Yes'
        else:
            freeAvailService = 'No'
    clinicWallet = ClinicWalletInfo.objects.filter(orgId = org)
    walletPayment = ''
    if clinicWallet:
        wallet = ClinicWalletInfo.objects.get(orgId = org)
        if wallet.totalBalance <= total_sum:
            walletPayment = 'No'
        else:
            walletPayment = 'Yes'
    
    context = {'mycat': mycat,'usr': usr, 'message': message, 'icon': icon,'enableButton': enableButton, 'currency': currency, 'service_order': service_order,'domain': domain, 'org': org, 'image': image, 'patient': patient, 'dis': dis, 'total_sum':total_sum,'mycat':mycat,'topcat': topcat, 'freeAvailService': freeAvailService, 'walletPayment': walletPayment}
    return render(request, "review_RadioOrder.html", context)


def review_PlanningOrder(request, id1, id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id1)
    patient = Patient.objects.get(id=service_order.pid)
    domain = Organisation.objects.get(orgtype="Domain Owner")
    topcat = Topcat.objects.filter(status="Active")
    mycat = topcat.get(id=id2)
    studies = Study.objects.filter(orgid=domain).filter(topcat=mycat.topcat)
    add_image = Study.objects.filter(topcat = "Implant Planning Report")
    image = ImplantPlanning.objects.filter(repid=service_order.id)
    price = image.values('price')
    sum = price.aggregate(Sum('price'))
    total_sum = sum['price__sum']
    service_order.ref_price = total_sum
    service_order.save()
    icon = ''
    currency = ''
    if org.country == 'IN':
        currency = 'price'
        icon = '<i class="fa-solid fa-indian-rupee-sign"></i>'
    else:
        currency = 'dollarPrice'
        icon = '<i class="fa-solid fa-dollar-sign"></i>'
    
    
    if service_order.discount == "0":
        dis = "yes"
    else:
        dis = None
    
    # Enable Payment Option
    enableButton = ''
    message = ''
    if org.paymentOption == 'payLater' and org.topUpAvailable <=  total_sum:
        enableButton = 'disabled'
        message = 'You have exceeded your Dentread credit-limit quota. Your available Balance is ₹ ' +str(org.topUpAvailable) +'. Please clear your outstanding dues to reset your credit-limit to continue using Dentread. Contact info@dentread.com to clear your dues.'
        
    elif org.paymentOption != 'payLater':
        enableButton = 'd-none'
    
    clinicWallet = ClinicWalletInfo.objects.filter(orgId = org)
    walletPayment = ''
    if clinicWallet:
        wallet = ClinicWalletInfo.objects.get(orgId = org)
        if wallet.totalBalance <= total_sum:
            walletPayment = 'No'
        else:
            walletPayment = 'Yes'
    
    context = {'walletPayment': walletPayment, 'usr':usr,'studies': studies, 'message': message, 'icon': icon, 'currency': currency, 'enableButton': enableButton, 'add_image':add_image, 'topcat': topcat, 'service_order': service_order, 'image': image, 'patient': patient, 'org': org, 'dis': dis, 'total_sum':total_sum,'mycat':mycat}
    return render(request, "review_ImplantPlanning.html", context)

def review_GuideOrder(request, id1, id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order=ServiceOrder.objects.get(id=id1)
    patient=Patient.objects.get(id=service_order.pid)
    domain = Organisation.objects.get(orgtype="Domain Owner")
    topcat = Topcat.objects.filter(status = "Active")
    mycat = topcat.get(id=id2)
    image = Suricalguide.objects.filter(repid=service_order.id)
    price = image.values('price')
    sum = price.aggregate(Sum('price'))
    total_sum = sum['price__sum']
    service_order.ref_price = total_sum
    service_order.save()
    icon = ''
    currency = ''
    if org.country == 'IN':
        currency = 'price'
        icon = '<i class="fa-solid fa-indian-rupee-sign"></i>'
    else:
        currency = 'dollarPrice'
        icon = '<i class="fa-solid fa-dollar-sign"></i>'
    
    if service_order.discount == "0":
        dis = "yes"
    else:
        dis = None
    
    #Enable Payment Option
    enableButton = ''
    message = ''
    if org.paymentOption == 'payLater' and org.topUpAvailable <=  total_sum:
        enableButton = 'disabled'
        message = 'You have exceeded your Dentread credit-limit quota. Your available Balance is ₹ ' +str(org.topUpAvailable) +'. Please clear your outstanding dues to reset your credit-limit to continue using Dentread. Contact info@dentread.com to clear your dues.'
        
    elif org.paymentOption != 'payLater':
        enableButton = 'd-none'
    
    
    clinicWallet = ClinicWalletInfo.objects.filter(orgId = org)
    walletPayment = ''
    if clinicWallet:
        wallet = ClinicWalletInfo.objects.get(orgId = org)
        if wallet.totalBalance <= total_sum:
            walletPayment = 'No'
        else:
            walletPayment = 'Yes'
  
    refer_id = Organisation.objects.get(id=service_order.referTo).orgname
    context = {'walletPayment': walletPayment, 'service_order': service_order, 'message': message, 'icon': icon, 'currency': currency, 'enableButton': enableButton, 'image': image, 'refer_id':refer_id, 'patient': patient,'topcat': topcat,'mycat': mycat, 'org': org, 'dis': dis, 'total_sum':total_sum,'mycat':mycat, 'usr': usr}
    return render(request, "review_Guide.html", context)

def checkForReview(request, id1, id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    usr = Users.objects.get(username = request.user)
    org = Organisation.objects.get(id = usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = id1)
    mycat = Topcat.objects.get(id = id2)
    prosthetic = Prosthetic.objects.filter(repid=service_order.id)
    iosFile = IOSFile.objects.filter(repid=service_order.id) 
    # countLineItem = prosthetic.count()
    
    actualFile = iosFile.count()
    if actualFile < 1 and service_order.preferredData == 'digitalData':
        messages.error(request, 'Please upload the related files first')
        return redirect('/refer_dentlab/'+str(service_order.id)+'/'+str(mycat.id))
    else:
        return redirect('/reviewLabOrder/'+str(service_order.id)+'/'+str(mycat.id))
    
def reviewLabOrder(request, id1, id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id1)
    patient = Patient.objects.get(id=service_order.pid)
    domain = Organisation.objects.get(orgtype="Domain Owner")
    topcat = Topcat.objects.filter(status = "Active")
    mycat = topcat.get(id=id2)
    footNotes = AddOnLabServices.objects.filter(orgid = service_order.referTo)
    studies = Study.objects.filter(orgid=domain).filter(topcat=mycat.topcat)
    image = Prosthetic.objects.filter(repid=service_order.id)
    
    if service_order.discount == "0":
        dis = "yes"
    else:
        dis = None
    
    # Price Symbol
    icon = ''
    currency = ''
    if org.country == 'IN':
        currency = 'price'
        icon = '<i class="fa-solid fa-indian-rupee-sign"></i>'
    else:
        currency = 'dollarPrice'
        icon = '<i class="fa-solid fa-dollar-sign"></i>'
    
    # Enable Payment Option
    total_sum = service_order.ref_price
    enableButton = ''
    message = ''
    if org.paymentOption == 'payLater' and org.topUpAvailable <=  total_sum:
        enableButton = 'disabled'
        message = 'You have exceeded your Dentread credit-limit quota. Your available Balance is ₹ ' +str(org.topUpAvailable) +'. Please clear your outstanding dues to reset your credit-limit to continue using Dentread. Contact info@dentread.com to clear your dues.'
    elif org.paymentOption != 'payLater':
        enableButton = 'd-none'
    
    clinicWallet = ClinicWalletInfo.objects.filter(orgId = org)
    walletPayment = ''
    if clinicWallet:
        wallet = ClinicWalletInfo.objects.get(orgId = org)
        if wallet.totalBalance <= total_sum:
            walletPayment = 'No'
        else:
            walletPayment = 'Yes'
    
    refer_id = Organisation.objects.get(id=service_order.referTo).orgname
    reforgId = Organisation.objects.get(id = service_order.referTo)
    extraItems = ExtraLabItem.objects.filter(repid = service_order.id)
    token = ShipRocketAuth.objects.get(id = 1).token
    saved_address = PickupLocation.objects.filter(orgId = org.id)
    pickuplocation = ''
    shipment_details = ''
    try:
        shipment_details = ShipmentDetailsClinic.objects.get(repid = service_order.id)
    except Exception as e:
        print(e)
        
    shipment_form = ''   
    if shipment_details:
        shipment_form = 'True'
    else:
        shipment_form = 'False'
    if service_order.preferredData == 'digitalData':
        shipment_form = 'True'
    context = {'service_order': service_order,'reforgId': reforgId, 'image': image, 'footNotes': footNotes, 'icon': icon, 'currency': currency, 'refer_id':refer_id, 'patient': patient,'topcat': topcat,'mycat': mycat, 'org': org, 'dis': dis, 'mycat':mycat, 'usr': usr,
               'message': 'You do not have any Verified pickup location for Logistics Support, Please add a Pickup location for your Clinic'}
    if saved_address:
        pickuplocation = PickupLocation.objects.get(orgId = org.id)
    if service_order.preferredData == 'nonDigitalData' and service_order.requestForShipment == 'Yes' and not saved_address:
        return render(request, "reviewLabNew.html", context)
    context = {'walletPayment': walletPayment, 'shipment_form': shipment_form, 'pickuplocation': pickuplocation, 'service_order': service_order, 'message': message, 'shipment_details': shipment_details, 'saved_address': saved_address, 'reforgId': reforgId, 'token': token, 'studies': studies, 'enableButton': enableButton, 'extraItems': extraItems, 'image': image, 'footNotes': footNotes, 'icon': icon, 'currency': currency, 'refer_id':refer_id, 'patient': patient,'topcat': topcat,'mycat': mycat, 'org': org, 'dis': dis, 'mycat':mycat, 'usr': usr}
    return render(request, "reviewLabNew.html", context)

def saveShipmentDetails(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id)
    orgid = Organisation.objects.get(id = service_order.referTo)
    billing_customer_name = orgid.ctperson_name
    if request.method == 'POST':
        item = request.POST.get('item')
        units = request.POST.get('units')
        height = request.POST.get('height')
        breadth = request.POST.get('breadth')
        weight = request.POST.get('weight')
        length = request.POST.get('length')
        pickupId = request.POST.get('pickupId')
        billing_address = orgid.address
        billing_city = orgid.city
        billing_state = orgid.state
        billing_pincode = orgid.pincode
        billing_email = orgid.email
        bill_phone = str(orgid.contact)
        billing_phone = ''
        for i in bill_phone:
            if i !='(' and i !=')' and i != ' ' and i != '-' and i != '+':
                billing_phone += i
        billing_country = 'India'
        locationId = ''
        myPick = ''
        if pickupId:
            pickupLocation = PickupLocation.objects.get(id = pickupId)
            myPick = pickupLocation.id
            locationId = pickupLocation.id
        else:
            return render(request, "reviewLabNew.html", {'message': 'Please Add a pickup location for your clinic, if you already added the address then please wait for the Varification'})
        rqtPkupLcn = PickupLocation.objects.get(id = myPick).pickup_location
        shipment_details = ShipmentDetailsClinic(repid = service_order.id, order_id = str(service_order.id), locationId = locationId,
                                           order_date = str(datetime.today()), pickup_location = rqtPkupLcn,
                                           billing_customer_name = billing_customer_name, height = height, breadth = breadth, weight = weight, length = length,
                                           billing_address = billing_address,
                                           billing_city = billing_city, billing_state = billing_state, billing_pincode = billing_pincode, billing_country = billing_country,
                                           billing_email = str(billing_email), billing_phone = int(billing_phone),
                                           item = item, units = units, sku = str(item) + '123', shipping_is_billing = True, selling_price = str(service_order.ref_price), sub_total = str(service_order.ref_price),
                                           payment_method = 'Prepaid'
                                           )
        shpDtl = ShipmentDetailsClinic.objects.filter(repid = service_order.id)
        if shpDtl:
            for i in shpDtl:
                i.delete()
            try:
                shipment_details.save()
            except Exception as exc:
                print('exc', exc)
        else:
            try:
                shipment_details.save()
            except Exception as ex:
                print('ex', ex)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def createShipmentOrder(request, id):
    usr = Users.objects.get(username = request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id)
    shipTo = Organisation.objects.get(id = service_order.orgid_id).orgname
    shipBy = Organisation.objects.get(id = service_order.reforgid).orgname
    shpBook = ShipmentDetailsClinic.objects.get(repid = service_order.id)
    token = ShipRocketAuth.objects.get(id = 1).token
    url = "https://apiv2.shiprocket.in/v1/external/orders/create/adhoc"
    payload = json.dumps({
    "order_id": shpBook.order_id,
    "order_date": shpBook.order_date,
    "pickup_location": shpBook.pickup_location,
    "channel_id": "",
    "comment": "",
    "billing_customer_name": shpBook.pickup_location,
    "billing_last_name": "",
    "billing_address": shpBook.billing_address,
    "billing_address_2": "",
    "billing_city": shpBook.billing_city,
    "billing_pincode": shpBook.billing_pincode,
    "billing_state": shpBook.billing_state,
    "billing_country": shpBook.billing_country,
    "billing_email": shpBook.billing_email,
    "billing_phone": shpBook.billing_phone,
    "shipping_is_billing": True,
    "shipping_customer_name": "",
    "shipping_last_name": "",
    "shipping_address": "",
    "shipping_address_2": "",
    "shipping_city": "",
    "shipping_pincode": "",
    "shipping_country": "",
    "shipping_state": "",
    "shipping_email": "",
    "shipping_phone": "",
    "order_items": [
        {
        "name": shpBook.item,
        "sku": shpBook.sku,
        "units": shpBook.units,
        "selling_price": shpBook.selling_price,
        "discount": "",
        "tax": "",
        "hsn": ""
        }
    ],
    "payment_method": "Prepaid",
    "shipping_charges": 0,
    "giftwrap_charges": 0,
    "transaction_charges": 0,
    "total_discount": 0,
    "sub_total": shpBook.sub_total,
    "length": shpBook.length,
    "breadth": shpBook.breadth,
    "height": shpBook.height,
    "weight": shpBook.weight
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer '+str(token)
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    
    try:  
        data = response.json()
        repid = service_order.id
        order_id = data["order_id"]
        shipment_id = data["shipment_id"]
        status = data["status"]
        status_code = data["status_code"]
        onboarding_completed_now = data["onboarding_completed_now"]
        awb_code = data["awb_code"]
        courier_company_id = data["courier_company_id"]
        courier_name = data["courier_name"]
        shpMnt = ShipmentOrderDetails(repid = repid, shipTo = shipTo, shipBy = shipBy, orgId = org.id, order_id = int(order_id), shipment_id = int(shipment_id), status = str(status), status_code = str(status_code), onboarding_completed_now = str(onboarding_completed_now), awb_code = str(awb_code), courier_company_id = str(courier_company_id), courier_name = str(courier_name))
        shpMnt.save()
        service_order.shipment_id = data["shipment_id"]
        service_order.shp_order_id = data["order_id"]
        service_order.shipTo = shipTo
        service_order.shipBy = shipBy
        service_order.ship_status = data["status"]
        service_order.save()
        print('Response Code', response.status_code)
    except Exception as ex:
        print(ex)
    if response.status_code != 200 and service_order.paymentStatus == 'Unpaid':
        context = {'usr': usr, 'org': org, 'topcat': topcat, 'service_order': service_order, 'code': response.status_code}
        return render(request, 'Alerts/payLaterShipment.html', context)
    if response.status_code != 200 and service_order.paymentStatus == 'Paid':
        context = {'usr': usr, 'org': org, 'topcat': topcat, 'service_order': service_order, 'code': response.status_code}
        return render(request, 'Alerts/PayNowShipment.html', context)
    return redirect('/requestForAWB/'+str(service_order.id))
    
def requestForAWB(request, id):
    usr = Users.objects.get(username = request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id)
    shpMnt = ShipmentOrderDetails.objects.get(repid = service_order.id)
    token = ShipRocketAuth.objects.get(id = 1).token
    url = "https://apiv2.shiprocket.in/v1/external/courier/assign/awb"
    payload = json.dumps({
    "shipment_id": shpMnt.shipment_id,
    "courier_id": ""
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer '+str(token)
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    if response.status_code == 200:
        data = response.json()
        shpMnt.awb_assign_status = data["awb_assign_status"]
        shpMnt.awb_code = data['response']['data']['awb_code']
        shpMnt.courier_name = data['response']['courier_name']
        service_order.awb_code = data['response']['data']['awb_code']
        service_order.courier_name = data['response']['courier_name']
        service_order.save()
        shpMnt.save()
    if response.status_code != 200 and service_order.paymentStatus == 'Unpaid':
        context = {'usr': usr, 'org': org, 'topcat': topcat, 'service_order': service_order, 'code': response.status_code}
        return render(request, 'Alerts/payLaterShipment.html', context)
    if response.status_code != 200 and service_order.paymentStatus == 'Paid':
        context = {'usr': usr, 'org': org, 'topcat': topcat, 'service_order': service_order, 'code': response.status_code}
        return render(request, 'Alerts/PayNowShipment.html', context)
    return redirect('/generatePickUp/'+str(service_order.id))

def generatePickUp(request, id):
    usr = Users.objects.get(username = request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id)
    patient = Patient.objects.get(id = service_order.pid)
    shpMnt = ShipmentOrderDetails.objects.get(repid = service_order.id)
    token = ShipRocketAuth.objects.get(id = 1).token
    url = "https://apiv2.shiprocket.in/v1/external/courier/generate/pickup"
    payload = json.dumps({
    "shipment_id": shpMnt.shipment_id,
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer '+str(token)
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        shpMnt.pickup_status = data["pickup_status"]
        shpMnt.shpDescription = data['response']['data']
        shpMnt.ship_date = datetime.today()
        shpMnt.pickup_scheduled_date = data['response']['pickup_scheduled_date']
        service_order.shpDescription = data['response']['data']
        service_order.ship_date = datetime.today()
        service_order.pickup_scheduled_date = data['response']['pickup_scheduled_date']
        shpMnt.save()
        service_order.save()
    my_context_data = {
        'order_id': str(shpMnt.order_id),
        'shipment_id': str(shpMnt.shipment_id),
        'courier_name': str(shpMnt.courier_name), 
    }
    if response.status_code != 200 and service_order.paymentStatus == 'Unpaid':
        context = {'usr': usr, 'org': org, 'topcat': topcat, 'service_order': service_order, 'code': response.status_code}
        return render(request, 'Alerts/payLaterShipment.html', context)
    if response.status_code != 200 and service_order.paymentStatus == 'Paid':
        context = {'usr': usr, 'org': org, 'topcat': topcat, 'service_order': service_order, 'code': response.status_code}
        return render(request, 'Alerts/PayNowShipment.html', context)
    if response.status_code == 200 and service_order.paymentStatus == 'Unpaid':
        context = {'usr': usr, 'org': org, 'topcat': topcat, 'service_order': service_order, 'code': response.status_code}
        return render(request, 'Alerts/payLaterShipment.html', context)
    if response.status_code == 200 and service_order.paymentStatus == 'Paid':
        context = {'usr': usr, 'org': org, 'topcat': topcat, 'service_order': service_order, 'code': response.status_code}
        return render(request, 'Alerts/PayNowShipment.html', context)


def pickUpRequest(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id)
    shp = ShipmentOrderDetails.objects.get(repid = service_order.id)
    token = ShipRocketAuth.objects.get(id = 1).token
    shipment_id = ''
    if shp:
        shipment_id = shp.shipment_id
        try:
            url = "https://apiv2.shiprocket.in/v1/external/courier/assign/awb"
            payload = json.dumps({
            "shipment_id": shipment_id,
            "courier_id": "1"
            })
            headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer '+str(token)
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            data = response.json()
            awb_code = data["awb_code"]
            courier_name = data["courier_name"]
            if awb_code:
                shpdtl = ShipmentOrderDetails.objects.get(id = service_order.id)
                shpdtl.awb_code = awb_code
                shpdtl.courier_name = courier_name
                shpdtl.save()
        except Exception as ex:
            print(ex)
    myId = ShipmentOrderDetails.objects.get(id = service_order.id)
    if myId:
        awb_code = myId.awb_code
        if awb_code:
            try:
                url = "https://apiv2.shiprocket.in/v1/external/courier/generate/pickup"
                payload = json.dumps({
                "shipment_id": [
                    myId.shipment_id
                ]
                })
                headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer '+str(token)
                }
                response = requests.request("POST", url, headers=headers, data=payload)
                print(response.text)
            except Exception as e:
                print(e)
        
    
    return JsonResponse({"status": "You Submitted The Order Successfully"})
def updateUnit(request, pk, unit, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id)

    lineItem = Prosthetic.objects.get(id=pk)
    pricePerUnit = lineItem.price/lineItem.unit
    lineItem.unit = unit
    lineItem.price = pricePerUnit * unit
    lineItem.extraPrice = pricePerUnit * unit
    lineItem.save()

    allLineItems = Prosthetic.objects.filter(repid = service_order.id)
    price = allLineItems.values('price')
    sum = price.aggregate(Sum('price'))
    total_sum = sum['price__sum']
    
    service_order.ref_price = total_sum
    service_order.lineOrderPrice = total_sum
    service_order.save()
    return JsonResponse({"updatedPrice": lineItem.price})


def edit_Surgident(request,id1,id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order=ServiceOrder.objects.get(id=id1)
    patient=Patient.objects.get(id=service_order.pid)
    domain=Organisation.objects.get(orgtype="Domain Owner")
    all_lab = Organisation.objects.filter(orgtype = 'Dental Lab').filter(Q(offered_service = "All") | Q(offered_service = "Implant Surgical Guide"))
    mycat = Maincat.objects.get(id = id2)
    otherImage = IOSFile.objects.filter(repid = service_order.id)
    studies = Study.objects.filter(orgid=domain).filter(topcat=mycat.topcat)
    prosthetic = Suricalguide.objects.filter(repid=service_order.id)
    comment = Comments.objects.filter(repid = service_order.id)
    icon = ''
    currency = ''
    if org.country == 'IN':
        currency = 'price'
        icon = '<i class="fa-solid fa-indian-rupee-sign"></i>'
    else:
        currency = 'dollarPrice'
        icon = '<i class="fa-solid fa-dollar-sign"></i>'
    
    imageUpperJaw = IOSFile.objects.filter(repid = id1).filter(site = 'Upper-Jaw') 
    imageLowerJaw = IOSFile.objects.filter(repid = id1).filter(site = 'Lower-Jaw') 
    imageLeftBite = IOSFile.objects.filter(repid = id1).filter(site = 'Left-Bite') 
    imageRightBite = IOSFile.objects.filter(repid = id1).filter(site = 'Right-Bite') 
    
    if request.method == "POST":
        tooth = request.POST.getlist('checks[]')
        data_type1 = request.POST.get('data_type1')
        data_type2 = request.POST.get('data_type2')
        output_type = request.POST.get('output_type')
        guide_type = request.POST.get('guide_type')
        planning_type = request.POST.get('planning_type')
        price = request.POST.get('price')
        remark=request.POST.get('remark')
        referto_id = domain.id
        notation = request.POST.get('notation-select')
        service_order.order_id = "SG" + str(service_order.id)
        service_order.save()
        if org.orgtype == "Dental Clinic":
            prosthetic1=Suricalguide(repid = service_order.id, orgid_id =org.id, preferredData = 'digitalData', reforgid = referto_id, tooth = tooth, data_type1 = data_type1, data_type2 = data_type2, output_type = output_type, guide_type = guide_type,planning_type = planning_type, price = price, remark = remark, badge='badge badge-secondary', service_name = 'Implant Surgical Guide', status ='Submit Order', name = usr.name)
        else:
            prosthetic1=Suricalguide(repid = service_order.id, orgid_id = org.id, preferredData = 'digitalData', reforgid = referto_id, parent_orgid = org.parent_id, tooth = tooth, data_type1 = data_type1, data_type2 = data_type2, output_type = output_type, guide_type = guide_type,planning_type = planning_type, price = price, remark = remark, badge='badge badge-secondary', service_name = 'Implant Surgical Guide', status ='Submit Order', name = usr.name)
        prosthetic1.save()
        prosthetic1.item_id = str(service_order.order_id)  + "-" + str(prosthetic1.id)
        prosthetic1.sodrid = str(prosthetic1.id)
        prosthetic1.save()
        prosthetics = Suricalguide.objects.filter(repid=service_order.id)
        price = prosthetics.values('price')
        sum = price.aggregate(Sum('price'))
        total_sum = sum['price__sum']
        service_order.ref_price = total_sum
        service_order.remark = remark
        service_order.refstudy=mycat.topcat
        service_order.referTo = domain.id
        service_order.patient_id = patient.pid
        if service_order.tooth_notation == 'FDI':
            service_order.tooth_notation = notation
        service_order.save()

        data = {'usr': usr,'all_lab': all_lab, 'icon': icon, 'currency': currency,  'org': org,'comment': comment, 'imageUpperJaw': imageUpperJaw, 'imageLowerJaw': imageLowerJaw, 'imageLeftBite': imageLeftBite, 'imageRightBite': imageRightBite, 'service_order': service_order,'prosthetic1':prosthetic1 , 'patient': patient, 'studies': studies, 'mycat': mycat,
                'topcat': topcat, 'domain': domain, 'prosthetic': prosthetic}
        return render(request, 'surgi_order.html', data)

    data={'usr':usr, 'org':org,'all_lab': all_lab,  'icon': icon, 'currency': currency, 'imageUpperJaw': imageUpperJaw, 'imageLowerJaw': imageLowerJaw, 'imageLeftBite': imageLeftBite, 'imageRightBite': imageRightBite, 'comment': comment, 'service_order':service_order, 'patient':patient, 'studies':studies, 'mycat':mycat, 'topcat':topcat, 'domain':domain, 'prosthetic':prosthetic}
    return render(request, 'surgi_order.html', data)



def edit_Planning(request,id1,id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order=ServiceOrder.objects.get(id=id1)
    patient=Patient.objects.get(id=service_order.pid)
    domain=Organisation.objects.get(orgtype="Domain Owner")
    mycat = Maincat.objects.get(id = id2)
    otherImage = IOSFile.objects.filter(repid = service_order.id)
    studies = Study.objects.filter(orgid=domain).filter(topcat=mycat.topcat)
    image = ImplantPlanning.objects.filter(repid=service_order.id)
    add_image = Study.objects.filter(topcat = "Implant Planning Report")
    comment = Comments.objects.filter(repid = service_order.id)
    icon = ''
    currency = ''
    if org.country == 'IN':
        currency = 'price'
        icon = '<i class="fa-solid fa-indian-rupee-sign"></i>'
    else:
        currency = 'dollarPrice'
        icon = '<i class="fa-solid fa-dollar-sign"></i>'
    
    if request.method == "POST":
        tooth=request.POST.getlist('checks[]')
        data_type = request.POST.get('title')
        service_catagory = request.POST.get('categ')
        planning_type = request.POST.get('finding_requires')
        price = request.POST.get('price')
        remark=request.POST.get('remark')
        notation = request.POST.get('notation-select')
        
        service_order.order_id = "IP" + str(service_order.id)
        service_order.save()
        if org.orgtype == "Dental Clinic":
            implantPlanning = ImplantPlanning(repid = service_order.id, pid = patient.pid, name = patient.name, orgid_id =org.id, tooth = tooth, data_type = data_type, service_catagory = service_catagory, planning_type = planning_type, price = price, remark = remark, badge='badge badge-danger', service_name = 'Implant Planning Report', status ='Pending')
        else:
            implantPlanning = ImplantPlanning(repid = service_order.id, pid = patient.pid, name = patient.name, orgid_id =org.id, parent_orgid = org.parent_id, tooth = tooth, data_type = data_type, service_catagory = service_catagory, planning_type = planning_type, price = price, remark = remark, badge='badge badge-danger', service_name = 'Implant Planning Report', status ='Pending')
        implantPlanning.save()
        implantPlanning.item_id = str(service_order.order_id)  + "-" + str(implantPlanning.id)
        implantPlanning.sodrid = str(implantPlanning.id)
        implantPlanning.save()
        image = ImplantPlanning.objects.filter(repid=service_order.id)
        price = image.values('price')
        sum = price.aggregate(Sum('price'))
        total_sum = sum['price__sum']
        service_order.ref_price = total_sum
        service_order.remark = remark
        service_order.refstudy = mycat.topcat
        service_order.patient_id = patient.pid
        if service_order.tooth_notation == 'FDI':
            service_order.tooth_notation = notation
        service_order.save()
        otherImage = IOSFile.objects.filter(repid = service_order.id)
        data = {'usr': usr, 'comment': comment, 'otherImage': otherImage, 'icon': icon, 'currency': currency, 'org': org, 'service_order': service_order, 'patient': patient, 'studies': studies, 'mycat': mycat, 'topcat': topcat, 'domain': domain, 'image': image}        
        return render(request, 'refer_planning.html', data)
    
    data={'usr':usr, 'org':org, 'comment': comment, 'otherImage': otherImage, 'icon': icon, 'currency': currency, 'service_order':service_order, 'patient':patient, 'studies':studies, 'mycat':mycat, 'topcat':topcat, 'domain':domain, 'image':image, 'add_image': add_image}
    return render(request, 'refer_planning.html', data)

def refer_ImplantPlanning(request,id1,id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order=ServiceOrder.objects.get(id=id1)
    patient=Patient.objects.get(id=service_order.pid)
    domain=Organisation.objects.get(orgtype="Domain Owner")
    mycat = Maincat.objects.get(id = id2)
    otherImage = IOSFile.objects.filter(repid = service_order.id)
    studies = Study.objects.filter(orgid=domain).filter(topcat=mycat.topcat)
    image = ImplantPlanning.objects.filter(repid=service_order.id)
    add_image = Study.objects.filter(topcat = "Implant Planning Report")
    comment = Comments.objects.filter(repid = service_order.id)
    icon = ''
    currency = ''
    if org.country == 'IN':
        currency = 'price'
        icon = '<i class="fa-solid fa-indian-rupee-sign"></i>'
    else:
        currency = 'dollarPrice'
        icon = '<i class="fa-solid fa-dollar-sign"></i>'
    
    if request.method == "POST":
        tooth=request.POST.getlist('checks[]')
        data_type = request.POST.get('title')
        service_catagory = request.POST.get('categ')
        planning_type = request.POST.get('scan')
        price = request.POST.get('price')
        remark=request.POST.get('remark')
        notation = request.POST.get('notation-select')
        
        service_order.order_id = "IP" + str(service_order.id)
        service_order.save()
        if org.orgtype == "Dental Clinic":
            implantPlanning = ImplantPlanning(repid = service_order.id, pid = patient.pid, name = patient.name, orgid_id =org.id, tooth = tooth, data_type = data_type, service_catagory = service_catagory, planning_type = planning_type, price = price, remark = remark, badge='badge badge-danger', service_name = 'Implant Planning Report', status ='Pending')
        else:
            implantPlanning = ImplantPlanning(repid = service_order.id, pid = patient.pid, name = patient.name, orgid_id =org.id, parent_orgid = org.parent_id, tooth = tooth, data_type = data_type, service_catagory = service_catagory, planning_type = planning_type, price = price, remark = remark, badge='badge badge-danger', service_name = 'Implant Planning Report', status ='Pending')
        implantPlanning.save()
        implantPlanning.item_id = str(service_order.order_id)  + "-" + str(implantPlanning.id)
        implantPlanning.sodrid = str(implantPlanning.id)
        implantPlanning.save()
        image = ImplantPlanning.objects.filter(repid=service_order.id)
        price = image.values('price')
        sum = price.aggregate(Sum('price'))
        total_sum = sum['price__sum']
        service_order.ref_price = total_sum
        service_order.remark = remark
        service_order.refstudy = mycat.topcat
        service_order.patient_id = patient.pid
        if service_order.tooth_notation == 'FDI':
            service_order.tooth_notation = notation
        service_order.save()
        otherImage = IOSFile.objects.filter(repid = service_order.id)
        data = {'usr': usr, 'comment': comment, 'otherImage': otherImage, 'icon': icon, 'currency': currency, 'org': org, 'service_order': service_order, 'patient': patient, 'studies': studies, 'mycat': mycat, 'topcat': topcat, 'domain': domain, 'image': image}        
        return render(request, 'refer_planning.html', data)
    
    data={'usr':usr, 'org':org, 'comment': comment, 'otherImage': otherImage, 'icon': icon, 'currency': currency, 'service_order':service_order, 'patient':patient, 'studies':studies, 'mycat':mycat, 'topcat':topcat, 'domain':domain, 'image':image, 'add_image': add_image}
    return render(request, 'refer_planning.html', data)


def refer_dentlab(request, id1, id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order=ServiceOrder.objects.get(id=id1)
    imageUpperJaw = IOSFile.objects.filter(repid = id1).filter(site = 'Upper-Jaw') 
    imageLowerJaw = IOSFile.objects.filter(repid = id1).filter(site = 'Lower-Jaw') 
    imageLeftBite = IOSFile.objects.filter(repid = id1).filter(site = 'Left-Bite') 
    imageRightBite = IOSFile.objects.filter(repid = id1).filter(site = 'Right-Bite') 
    patient=Patient.objects.get(id=service_order.pid)
    all_lab = Organisation.objects.filter(orgtype = 'Dental Lab').filter(Q(offered_service = "All") | Q(offered_service = "Digital Lab Services"))
    mycat = topcat.get(id=id2)
    domain = Organisation.objects.get(orgtype="Domain Owner")
    studies = Study.objects.filter(orgid=domain).filter(topcat=mycat.topcat)
    labItem = LabItem.objects.all()
    shade = Shade.objects.all()
    allShade = shade
    prosthetic = Prosthetic.objects.filter(repid=service_order.id)
    comment = Comments.objects.filter(repid = service_order.id)
    icon = ''
    currency = ''
    if org.country == 'IN':
        currency = 'price'
        icon = '<i class="fa-solid fa-indian-rupee-sign"></i>'
    else:
        currency = 'dollarPrice'
        icon = '<i class="fa-solid fa-dollar-sign"></i>'
    footNotes = AddOnLabServices.objects.filter(orgid = service_order.referTo)                 
    notes = Notes.objects.filter(orgid = service_order.referTo)
    extraItems = ExtraLabItem.objects.filter(repid = service_order.id)
    if request.method == "POST":
        tooth=request.POST.getlist('checks[]') 
        order = request.POST.get('orderSelection')
        expectedDate = request.POST.get('date')
        remark = request.POST.get('remark')
        designCheck = request.POST.get('designCheck')
        referto_id = request.POST.get('organisationid')
        shade = request.POST.get('shade')
        shadeType = request.POST.get('shadeType')
        fabrication = request.POST.get('fabrication')
        notation = request.POST.get('notation-select')
        orderId = LabOrderItem.objects.get(id = order)
        item = orderId.item
        price = orderId.price
        pricePerUnit = price
        unit = 1
        if item == 'Crown and Bridges' or item == 'Implant Specific Section' or item == 'Removable Prosthesis':
            unit = len(tooth[0].split(','))
            price = price*unit
        material = orderId.material
        itemId = orderId.itemId
        materialId = orderId.materialId
        type = orderId.type
        method = orderId.method
        submethod = orderId.submethod
        application = orderId.application
        sub_material = orderId.sub_material
        sub_materialId = orderId.sub_materialId
        warranty = orderId.warranty
        service_order.order_id = "DL" + str(service_order.id)
        if service_order.tooth_notation == 'FDI':
            service_order.tooth_notation = notation
        service_order.save()
        if org.orgtype == "Dental Clinic":
            prosthetic1=Prosthetic(repid=service_order.id, orgid_id =org.id, fabrication = fabrication, sub_material = sub_material, sub_materialId = sub_materialId, shade = shade, unit = unit, shadeType = shadeType, pid = patient.pid, itemId = itemId.id, materialId = materialId.id, designCheck = designCheck, price=price, extraPrice = price, expectedDate = expectedDate, item = item, material=material, type=type, method=method, submethod = submethod, application = application, warranty = warranty, pricePerUnit= pricePerUnit, tooth=tooth, remark=remark, badge='badge badge-secondary', service_name = 'Digital Lab Services', status ='Submit Order', name = usr.name )
        else:
            prosthetic1=Prosthetic(repid=service_order.id, orgid_id =org.id, fabrication = fabrication, shade = shade,  unit = unit, shadeType = shadeType, pid = patient.pid, itemId = itemId.id, materialId = materialId.id, pricePerUnit = pricePerUnit, designCheck = designCheck, price=price, extraPrice = price,  expectedDate = expectedDate, item = item, material=material, type=type, method=method, submethod = submethod, application = application, warranty = warranty, tooth=tooth, remark=remark, badge='badge badge-secondary', service_name = 'Digital Lab Services', status ='Submit Order', name = usr.name, parent_orgid = org.parent_id)
        prosthetic1.save()
        prosthetic1.item_id = str(service_order.order_id)  + "-" + str(prosthetic1.id)
        prosthetic1.sodrid = str(prosthetic1.id)
        prosthetic1.save()
        prosthetics = Prosthetic.objects.filter(repid = service_order.id)
        price = prosthetics.values('price')
        sum = price.aggregate(Sum('price'))
        total_sum = sum['price__sum']
        service_order.ref_price = total_sum
        service_order.lineOrderPrice = total_sum
        service_order.remark = remark
        service_order.refstudy = mycat.topcat
        service_order.referTo = referto_id
        service_order.patient_id = patient.pid
        service_order.save()
        footNotes = AddOnLabServices.objects.filter(orgid = service_order.referTo)
        notes = Notes.objects.filter(orgid = service_order.referTo)
        extraItems = ExtraLabItem.objects.filter(repid = service_order.id)
        data = {'usr': usr, 'labItem': labItem, 'shade': allShade, 'footNotes': footNotes, 'notes': notes, 'extraItems': extraItems, 'imageUpperJaw': imageUpperJaw, 'imageLowerJaw': imageLowerJaw, 'imageLeftBite': imageLeftBite, 'imageRightBite': imageRightBite, 'comment': comment,'icon': icon, 'currency': currency, 'org': org, 'service_order': service_order,'prosthetic1': prosthetic1, 'patient': patient, 'studies': studies, 'mycat': mycat,
                'topcat': topcat, 'all_lab': all_lab, 'prosthetic': prosthetic}
        return render(request, 'lab_order_new.html', data)

    data={'usr':usr, 'labItem': labItem, 'shade': shade, 'footNotes': footNotes, 'notes': notes, 'extraItems': extraItems, 'imageUpperJaw': imageUpperJaw, 'imageLowerJaw': imageLowerJaw,'imageLeftBite': imageLeftBite,'imageRightBite': imageRightBite, 'org':org,'comment': comment,'icon': icon, 'currency': currency, 'service_order':service_order,'patient':patient, 'studies':studies, 'mycat':mycat, 'topcat':topcat, 'all_lab':all_lab, 'prosthetic':prosthetic}
    return render(request, 'lab_order_new.html', data)

def addExtraItems(request, id1, id2, id3, units, requestFor): 
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    usr = Users.objects.get(username = request.user)
    org = Organisation.objects.get(id = usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id1)
    totalPrice = service_order.ref_price
    lineItem = Prosthetic.objects.get(id=id2)
    addOnItem = AddOnLabServices.objects.get(id=id3) #works
    addOnService = addOnItem.addOnService #works
    addOnprice = addOnItem.price*units #works
    unitPrice = addOnItem.price #works
    extraItem = ExtraLabItem.objects.filter(repid=service_order.id).filter(lineItemId = lineItem.id).filter(itemId = id3)

    if extraItem: 
        new_id = 0 
        for i in extraItem:
            new_id = i.id
        extraItemId = ExtraLabItem.objects.get(id = new_id)
        if requestFor == 'del':
            extraItemId.delete()
        else: 
            extraItemId.addOnunit = units
            extraItemId.addOnprice = extraItemId.unitPrice * units
            extraItemId.save()
    else:
        extraLabItem = ExtraLabItem(repid=service_order.id, itemId = id3, lineItemId = lineItem, lineItemIdNumber= lineItem.id, orgid = org, addOnService = addOnService, addOnprice = addOnprice, addOnunit = units, unitPrice = unitPrice)  
        extraLabItem.save()

    extra_price = ExtraLabItem.objects.filter(repid=service_order.id)
    addOnprice = extra_price.values('addOnprice')
    sum = addOnprice.aggregate(Sum('addOnprice'))
    total_price = sum['addOnprice__sum']
    if total_price == None:
        total_price = 0
    service_order.ref_price = service_order.lineOrderPrice + total_price
    service_order.save()

    line_item_extra_price = ExtraLabItem.objects.filter(repid=service_order.id).filter(lineItemId = lineItem.id)
    line_item_addOnprice = line_item_extra_price.values('addOnprice')
    line_item_sum = line_item_addOnprice.aggregate(Sum('addOnprice'))
    line_item_total_price = line_item_sum['addOnprice__sum']
    if line_item_total_price == None:
        line_item_total_price = 0
    lineItem.price = lineItem.extraPrice + line_item_total_price
    lineItem.save()

    return JsonResponse({"totalPrice": service_order.ref_price, "lineItemTotalPrice": lineItem.price})

def editDentlab(request, id1, id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order=ServiceOrder.objects.get(id=id1)
    patient=Patient.objects.get(id=service_order.pid)
    imageUpperJaw = IOSFile.objects.filter(repid = id1).filter(site = 'Upper-Jaw') 
    imageLowerJaw = IOSFile.objects.filter(repid = id1).filter(site = 'Lower-Jaw') 
    imageLeftBite = IOSFile.objects.filter(repid = id1).filter(site = 'Left-Bite') 
    imageRightBite = IOSFile.objects.filter(repid = id1).filter(site = 'Right-Bite') 
    all_lab = Organisation.objects.filter(orgtype = 'Dental Lab').filter(Q(offered_service = "All") | Q(offered_service = "Digital Lab Services"))
    mycat = topcat.get(id=id2)
    domain = Organisation.objects.get(orgtype="Domain Owner")
    studies = Study.objects.filter(orgid=domain).filter(topcat=mycat.topcat)
    labItem = LabItem.objects.all()
    shade = Shade.objects.all()
    allShade = shade
    prosthetic = Prosthetic.objects.filter(repid=service_order.id)
    comment = Comments.objects.filter(repid = service_order.id)
    icon = ''
    currency = ''
    if org.country == 'IN':
        currency = 'price'
        icon = '<i class="fa-solid fa-indian-rupee-sign"></i>'
    else:
        currency = 'dollarPrice'
        icon = '<i class="fa-solid fa-dollar-sign"></i>'
    footNotes = AddOnLabServices.objects.filter(orgid = service_order.referTo)
    notes = Notes.objects.filter(orgid = service_order.referTo)
    extraItems = ExtraLabItem.objects.filter(repid = service_order.id)
    
    if request.method == "POST":
        tooth=request.POST.getlist('checks[]') 
        order = request.POST.get('orderSelection')
        expectedDate = request.POST.get('date')
        remark = request.POST.get('remark')
        designCheck = request.POST.get('designCheck')
        referto_id = request.POST.get('organisationid')
        shade = request.POST.get('shade')
        shadeType = request.POST.get('shadeType')
        fabrication = request.POST.get('fabrication')
        notation = request.POST.get('notation-select')
        orderId = LabOrderItem.objects.get(id = order)
        item = orderId.item
        price = orderId.price
        pricePerUnit = price
        unit = 1
        if item == 'Crown and Bridges':
            unit = len(tooth[0].split(','))
            price = price*unit
        material = orderId.material
        itemId = orderId.itemId
        materialId = orderId.materialId
        type = orderId.type
        method = orderId.method
        submethod = orderId.submethod
        application = orderId.application
        sub_material = orderId.sub_material
        sub_materialId = orderId.sub_materialId
        warranty = orderId.warranty
        service_order.order_id = "DL" + str(service_order.id)
        if service_order.tooth_notation == 'FDI':
            service_order.tooth_notation = notation
        service_order.save()
        if org.orgtype == "Dental Clinic":
            prosthetic1=Prosthetic(repid=service_order.id, orgid_id =org.id, sub_material=sub_material, sub_materialId=sub_materialId, fabrication = fabrication, shade = shade, unit = unit, shadeType = shadeType, pid = patient.pid, itemId = itemId.id, materialId = materialId.id, designCheck = designCheck, price=price, extraPrice = price, expectedDate = expectedDate, item = item, material=material, type=type, method=method, submethod = submethod, application = application, warranty = warranty, pricePerUnit= pricePerUnit, tooth=tooth, remark=remark, badge='badge badge-secondary', service_name = 'Digital Lab Services', status ='Submit Order', name = usr.name )
        else:
            prosthetic1=Prosthetic(repid=service_order.id, orgid_id =org.id, fabrication = fabrication, shade = shade,  unit = unit, shadeType = shadeType, pid = patient.pid, itemId = itemId.id, materialId = materialId.id, pricePerUnit = pricePerUnit, designCheck = designCheck, price=price, extraPrice = price,  expectedDate = expectedDate, item = item, material=material, type=type, method=method, submethod = submethod, application = application, warranty = warranty, tooth=tooth, remark=remark, badge='badge badge-secondary', service_name = 'Digital Lab Services', status ='Submit Order', name = usr.name, parent_orgid = org.parent_id)
        prosthetic1.save()
        prosthetic1.item_id = str(service_order.order_id)  + "-" + str(prosthetic1.id)
        prosthetic1.sodrid = str(prosthetic1.id)
        prosthetic1.save()
        prosthetics = Prosthetic.objects.filter(repid = service_order.id)
        price = prosthetics.values('price')
        sum = price.aggregate(Sum('price'))
        total_sum = sum['price__sum']
        service_order.ref_price = total_sum
        service_order.lineOrderPrice = total_sum
        service_order.remark = remark
        service_order.refstudy = mycat.topcat
        service_order.referTo = referto_id
        service_order.patient_id = patient.pid
        service_order.save()
        footNotes = AddOnLabServices.objects.filter(orgid = service_order.referTo)
        notes = Notes.objects.filter(orgid = service_order.referTo)
        extraItems = ExtraLabItem.objects.filter(repid = service_order.id)
        data = {'usr': usr, 'labItem': labItem, 'shade': allShade, 'footNotes': footNotes, 'notes': notes, 'extraItems': extraItems, 'comment': comment,'icon': icon, 'currency': currency, 'org': org, 'service_order': service_order,'prosthetic1': prosthetic1, 'patient': patient, 'studies': studies, 'mycat': mycat,
                'topcat': topcat, 'all_lab': all_lab, 'prosthetic': prosthetic}
        return render(request, 'lab_order_new.html', data)

  
    data={'usr':usr, 'labItem': labItem, 'shade': shade, 'org':org, 'footNotes': footNotes, 'extraItems': extraItems, 'notes': notes, 'imageUpperJaw': imageUpperJaw, 'imageLowerJaw': imageLowerJaw,'imageLeftBite': imageLeftBite,'imageRightBite': imageRightBite, 'comment': comment,'icon': icon, 'currency': currency, 'service_order':service_order,'patient':patient, 'studies':studies, 'mycat':mycat, 'topcat':topcat, 'all_lab':all_lab, 'prosthetic':prosthetic}
    return render(request, 'lab_order_new.html', data)

def editLineOrderItem(request, id1, id2, id3):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    context['id3'] = id3
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id1)
    mycat = topcat.get(id=id2)
    lineItem = Prosthetic.objects.get(id=id3)
    if request.method == 'POST':
        lineItem.tooth = request.POST.get('selectedRegion-edit')
        lineItem.designCheck = request.POST.get('designCheck-edit')
        lineItem.shade = request.POST.get('selectedShadeType-edit')
        lineItem.shadeType = request.POST.get('shadeCode-edit')
        lineItem.remark = request.POST.get('clinicalNotes-edit')
        lineItem.fabrication = request.POST.get('selectFabrication-edit')
        lineItem.expectedDate = request.POST.get('expectedDate-edit')
        lineItem.save()
        return redirect('/refer_dentlab/'+str(service_order.id)+'/'+str(mycat.id))

def editRadioOrderItem(request, id1, id2, id3):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    context['id3'] = id3
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id1)
    mycat = Maincat.objects.get(id=id2)
    lineItem = RadiologycalServices.objects.get(id=id3)
    if request.method == 'POST':
        lineItem.tooth = request.POST.get('tooth')
        lineItem.data_type = request.POST.get('data_type')
        lineItem.service_catagory = request.POST.get('service_catagory')
        lineItem.finding_requires = request.POST.get('finding_requires')
        lineItem.remark = request.POST.get('remark')
        lineItem.price = request.POST.get('price')
        lineItem.save()
        return redirect('/refer_RadiologicalService/'+str(service_order.id)+'/'+str(mycat.id))

def editSurgiOrderItem(request, id1, id2, id3):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    context['id3'] = id3
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id1)
    mycat = Maincat.objects.get(id=id2)
    lineItem = Suricalguide.objects.get(id=id3)
    if request.method == 'POST':
        lineItem.tooth = request.POST.get('checks[]')
        lineItem.data_type1 = request.POST.get('data_type')
        lineItem.data_type2 = request.POST.get('data_type2')
        lineItem.output_type = request.POST.get('output_type')
        lineItem.guide_type = request.POST.get('guide_type')
        lineItem.planning_type = request.POST.get('planning_type')
        lineItem.remark = request.POST.get('remark')
        lineItem.price = request.POST.get('price')
        lineItem.save()
        return redirect('/refer_surgident/'+str(service_order.id)+'/'+str(mycat.id))

def editImageOrderItem(request, id1, id2, id3):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    context['id3'] = id3
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id1)
    mycat = Maincat.objects.get(id=id2)
    lineItem = ImageAnalysis.objects.get(id=id3)
    if request.method == 'POST':
        lineItem.tooth = request.POST.get('tooth')
        lineItem.data_type = request.POST.get('data_type')
        lineItem.service_catagory = request.POST.get('service_catagory')
        lineItem.sub_category = request.POST.get('finding_requires')
        lineItem.remark = request.POST.get('remark')
        lineItem.price = request.POST.get('price')
        lineItem.save()
        return redirect('/refer_ImageAnalysis/'+str(service_order.id)+'/'+str(mycat.id))

def editPlanningOrderItem(request, id1, id2, id3):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    context['id3'] = id3
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id1)
    mycat = Maincat.objects.get(id=id2)
    lineItem = ImplantPlanning.objects.get(id=id3)
    if request.method == 'POST':
        lineItem.tooth = request.POST.get('tooth')
        lineItem.data_type = request.POST.get('data_type')
        lineItem.service_catagory = request.POST.get('service_catagory')
        lineItem.planning_type = request.POST.get('finding_requires')
        lineItem.remark = request.POST.get('remark')
        lineItem.price = request.POST.get('price')
        lineItem.save()
        return redirect('/refer_ImplantPlanning/'+str(service_order.id)+'/'+str(mycat.id))

def updatePreferredData(request, id, data):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = id)
    service_order.preferredData = data
    service_order.save()
    iosfile = IOSFile.objects.filter(repid = service_order.id)
    if service_order.preferredData == 'nonDigitalData':
        if iosfile:
            for i in iosfile:
                deleteFile = IOSFile.objects.get(id=i.id)
                deleteFile.delete()
    return JsonResponse({'PreferredData': service_order.preferredData})

def updatePickupReq(request, id, data):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = id)
    if data == 'true':
        service_order.requestForShipment = 'Yes'
        service_order.save()
    else:
        service_order.requestForShipment = 'No'
        service_order.save()
    return JsonResponse({'requestForShipment': service_order.requestForShipment})

def labOrderComment(request, id1, id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    usr = Users.objects.get(username = request.user)
    org = Organisation.objects.get(id = usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = id1)
    patient=Patient.objects.get(id=service_order.pid)
    domain=Organisation.objects.get(orgtype="Domain Owner")
    mycat = topcat.get(id = id2)
    studies = Study.objects.filter(orgid=domain).filter(topcat=mycat.topcat)
    image = Prosthetic.objects.filter(repid=service_order.id)
    add_image = Study.objects.filter(topcat = "Implant Surgical Guide")
    patient = Patient.objects.get(id = service_order.pid)
    if request.method == 'POST':
        comment = request.POST.get('comment')
        name = usr.name
        comments = Comments(name=name,orgid = org, comment=comment, repid = service_order.id)
        comments.save()
        return redirect('/refer_dentlab/'+str(service_order.id)+'/'+str(mycat.id))
    data = {'usr': usr, 'org': org, 'service_order': service_order, 'studies':studies, 'mycat':mycat, 'topcat': topcat, 'patient': patient, 'comments':comments, 'domain':domain, 'image':image, 'add_image': add_image}
    return render(request, 'lab_order.html', data)

def labOrderCommentClinic(request, id):
    usr = Users.objects.get(username = request.user)
    org = Organisation.objects.get(id = usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = id)
    patient = Patient.objects.get(id = service_order.pid)
    if request.method == 'POST':
        comment = request.POST.get('comment')
        name = usr.name
        comments = Comments(name=name, orgid = org, comment=comment, repid = service_order.id)
        comments.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def refer_surgident(request, id1, id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order=ServiceOrder.objects.get(id=id1)
    patient=Patient.objects.get(id=service_order.pid)
    domain = Organisation.objects.get(orgtype = "Domain Owner")
    all_lab = Organisation.objects.filter(orgtype = 'Dental Lab').filter(Q(offered_service = "All") | Q(offered_service = "Implant Surgical Guide"))
    mycat = Maincat.objects.get(id = id2)
    otherImage = IOSFile.objects.filter(repid = service_order.id)
    studies = Study.objects.filter(orgid=domain).filter(topcat=mycat.topcat)
    prosthetic = Suricalguide.objects.filter(repid=service_order.id)
    comment = Comments.objects.filter(repid = service_order.id)
    icon = ''
    currency = ''
    if org.country == 'IN':
        currency = 'price'
        icon = '<i class="fa-solid fa-indian-rupee-sign"></i>'
    else:
        currency = 'dollarPrice'
        icon = '<i class="fa-solid fa-dollar-sign"></i>'
    
    imageUpperJaw = IOSFile.objects.filter(repid = id1).filter(site = 'Upper-Jaw') 
    imageLowerJaw = IOSFile.objects.filter(repid = id1).filter(site = 'Lower-Jaw') 
    imageLeftBite = IOSFile.objects.filter(repid = id1).filter(site = 'Left-Bite') 
    imageRightBite = IOSFile.objects.filter(repid = id1).filter(site = 'Right-Bite') 
    
    if request.method == "POST":
        tooth = request.POST.getlist('checks[]')
        data_type1 = request.POST.get('data_type1')
        data_type2 = request.POST.get('data_type2')
        output_type = request.POST.get('output_type')
        guide_type = request.POST.get('guide_type')
        planning_type = request.POST.get('planning_type')
        price = request.POST.get('price')
        remark=request.POST.get('remark')
        referto_id = domain.id
        notation = request.POST.get('notation-select')
        service_order.order_id = "SG" + str(service_order.id)
        service_order.save()
        if org.orgtype == "Dental Clinic":
            prosthetic1=Suricalguide(repid = service_order.id, orgid_id =org.id, preferredData = 'digitalData', reforgid = referto_id, tooth = tooth, data_type1 = data_type1, data_type2 = data_type2, output_type = output_type, guide_type = guide_type,planning_type = planning_type, price = price, remark = remark, badge='badge badge-secondary', service_name = 'Implant Surgical Guide', status ='Submit Order', name = usr.name)
        else:
            prosthetic1=Suricalguide(repid = service_order.id, orgid_id = org.id, preferredData = 'digitalData', reforgid = referto_id, parent_orgid = org.parent_id, tooth = tooth, data_type1 = data_type1, data_type2 = data_type2, output_type = output_type, guide_type = guide_type,planning_type = planning_type, price = price, remark = remark, badge='badge badge-secondary', service_name = 'Implant Surgical Guide', status ='Submit Order', name = usr.name)
        prosthetic1.save()
        prosthetic1.item_id = str(service_order.order_id)  + "-" + str(prosthetic1.id)
        prosthetic1.sodrid = str(prosthetic1.id)
        prosthetic1.save()
        prosthetics = Suricalguide.objects.filter(repid=service_order.id)
        price = prosthetics.values('price')
        sum = price.aggregate(Sum('price'))
        total_sum = sum['price__sum']
        service_order.ref_price = total_sum
        service_order.remark = remark
        service_order.refstudy=mycat.topcat
        service_order.referTo = domain.id
        service_order.patient_id = patient.pid
        if service_order.tooth_notation == 'FDI':
            service_order.tooth_notation = notation
        service_order.save()

        data = {'usr': usr,'all_lab': all_lab, 'icon': icon, 'currency': currency,  'org': org,'comment': comment, 'imageUpperJaw': imageUpperJaw, 'imageLowerJaw': imageLowerJaw, 'imageLeftBite': imageLeftBite, 'imageRightBite': imageRightBite, 'service_order': service_order,'prosthetic1':prosthetic1 , 'patient': patient, 'studies': studies, 'mycat': mycat,
                'topcat': topcat, 'domain': domain, 'prosthetic': prosthetic}
        return render(request, 'surgi_order.html', data)

    data={'usr':usr, 'org':org,'all_lab': all_lab,  'icon': icon, 'currency': currency, 'imageUpperJaw': imageUpperJaw, 'imageLowerJaw': imageLowerJaw, 'imageLeftBite': imageLeftBite, 'imageRightBite': imageRightBite, 'comment': comment, 'service_order':service_order, 'patient':patient, 'studies':studies, 'mycat':mycat, 'topcat':topcat, 'domain':domain, 'prosthetic':prosthetic}
    return render(request, 'surgi_order.html', data)

def uploadguide_data(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id)
    patient=Patient.objects.get(id=service_order.pid)
    data={'usr':usr, 'org':org, 'service_order':service_order, 'patient':patient, 'topcat': topcat}
    return render(request, 'uploadguide_data.html', data)

def delete_pros(request, id):
    pros=Prosthetic.objects.get(id=id)
    pros.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def deleteOrder(request, id):
    order = ServiceOrder.objects.get(id=id)
    order.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def delete_ImageAnalysisId(request, id):
    img=ImageAnalysis.objects.get(id=id)
    img.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def delete_ImplantPlanningId(request, id):
    img = ImplantPlanning.objects.get(id=id)
    img.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def delete_RadiologicalId(request, id):
    img=RadiologycalServices.objects.get(id=id)
    img.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
def delete_GuideId(request, id):
    img = Suricalguide.objects.get(id=id)
    img.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def downloadios(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    rep = ServiceOrder.objects.filter(Q(orgid=org) | Q(repby=usr.name))
    service_order = ServiceOrder.objects.get(id=id)
    ios=IOSFile.objects.filter(repid=id)
    patient=Patient.objects.get(id=service_order.pid)
    data={'usr':usr, 'org':org, 'service_order':service_order, 'ios':ios, 'patient':patient, 'rep':rep}
    return render(request, 'downloadios.html', data)


def downloadOtherImage(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id)
    other_images = OtherImageFile.objects.filter(repid=id)
    patient = Patient.objects.get(id=service_order.pid)
    context = {'usr':usr, 'org':org, 'service_order':service_order, 'other_images':other_images, 'patient':patient}
    return render(request, 'download_other.html', context)


def patientdetails_dent(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    patients = Patient.objects.filter(Q(orgid=org) | Q(refpt_orgid=org.id))
    patient = patients.get(id=id)
    study = Study.objects.filter(orgid=org)
    invoices = Dent_Invoice.objects.filter(orgid=org).filter(pid=patient.pid)
    allinvoice = invoices.filter(pid=patient.pid)
    for i in allinvoice:
        i.stud=study.get(id=i.study).title
    service_orders = ServiceOrder.objects.filter(Q(orgid=org)| Q(refpt_orgid=org.id))
    service_order = service_orders.filter(pid=patient.pid)
    return render(request, 'PatientDetails_dent.html',
                  {'patient': patient, 'study': study, 'allinvoice': allinvoice, 'service_order': service_order,
                   'page': 'Patient Detail', 'usr':usr, 'org':org})

def addinventory(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    patients = Patient.objects.filter(orgid=org)
    patient = patients.get(id=id)
    item = Items.objects.all
    invt = Inventory.objects.filter(pid=patient.pid)
    return render(request, 'Addinventory.html',
                  {'patient': patient, 'item': item, 'invt': invt, 'usr': usr, 'page': 'Add Inventory'})


def patientdetail(request):
    pid = request.session['pid']
    patient = Patient.objects.get(pid=pid)
    study = Study.objects.all
    allinvoice = Invoice.objects.filter(pid=pid)
    service_order = ServiceOrder.objects.filter(pid=pid)

    return render(request, 'PatientDetails.html',
                  {'patient': patient, 'study': study, 'allinvoice': allinvoice, 'service_order': service_order})


def service_ordering(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id)
    try:
        service_order.sgn=Users.objects.get(id=service_order.signby).name
        service_order.edu = Users.objects.get(id=service_order.signby).edu
        service_order.spec = Users.objects.get(id=service_order.signby).spec
    except Exception as e:
        service_order.sgn=service_order.signby
    if service_order.reforgid is not None:
        hide="readonly"
        dis="disabled"
        hden="hidden"
        show=""
        myid="n"
    else:
        hide=""
        dis =""
        hden=""
        show="hidden"
        myid = "text"
    if service_order.repby=="":
        msg="Report is not assigned , Please assign service_order from 'Reporting Management' ."
        return render(request, 'infomsg.html', {'msg':msg})
    if service_order.status == "Pending":
        service_order.status = "In Process"
        service_order.badge = "badge badge-warning"
        service_order.save()

    file = FeedFile.objects.filter(repid=service_order.id)
    techs = Users.objects.filter(usertype="Internal").filter(department="Technician")
    rep=Users.objects.filter(orgid=org).filter(department="Radiologist")
    return render(request, 'Createservice_order.html',
                  {'service_order': service_order, 'file': file, 'usr': usr, 'techs': techs, 'page': 'Create Report', 'rep':rep, 'hide':hide, 'dis':dis, 'hden':hden, 'show':show, 'myid':myid})

def service_ordering_radio(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_orders = ServiceOrder.objects.filter(orgid=org)
    service_order = service_orders.get(id=id)
    service_order.study=Study.objects.get(id=service_order.study).title
    files=FeedFile.objects.filter(orgid=org)
    if service_order.status == "Pending":
        service_order.status = "In Process"
        service_order.badge = "badge badge-warning"
        service_order.save()

    file = files.filter(repid=service_order.repid)

    return render(request, 'Createservice_order_radio.html',
                  {'service_order': service_order, 'file': file, 'usr': usr,  'page': 'Create Report', 'org':org})

def service_ordering_dent(request, id1, id2, id3):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    radio = Users.objects.filter(orgid=org).filter(department="Radiologist")
    service_order = ServiceOrder.objects.get(id=id1)
    include = ['Radiological Report', 'Image Analysis Report', 'Implant Planning Report', 'Implant Surgical Guide']
    topcat = Topcat.objects.filter(topcat__in = include)
    mycat = topcat.get(id=id2)
    radio_order = RadiologycalServices.objects.get(id=id3)
    try:
        radio_order.sgn = Users.objects.get(id=radio_order.signby).name
        radio_order.edu = Users.objects.get(id=radio_order.signby).edu
        radio_order.spec = Users.objects.get(id=radio_order.signby).spec
    except Exception as e:
        radio_order.sgn = radio_order.signby
    if radio_order.status == "Pending":
        radio_order.status = "In Process"
        radio_order.badge = "badge badge-warning"
        radio_order.save()
        notification = Notification(orgid = org, sendTo = radio_order.orgid_id, serviceOrderId = service_order.id, sent = True, lineItemId = radio_order.id, service = 'Radiological Report', user = usr.name, event = 'ORDER STATUS', details = 'Your order for Radiological Report for the order ID: '+str(service_order.order_id) + ' and the line item id '+str(radio_order.item_id)+' ,status has been changed to '+ str(radio_order.status), date = datetime.now(), hyperLink = '/manageReport/'+str(service_order.id))
        notification.save()
    file = ''
    try:
        file = FeedFile.objects.filter(repid=service_order.id).filter(sodrid = radio_order.id)
    except FileNotFoundError:
        print('File Not Found')
    
    for i in file:
        a = str(i.file)
        i.fileName = a.split('/')[-1]
    techs = Users.objects.filter(usertype="Internal").filter(department="Technician")
    return render(request, 'Createservice_order_dent.html', {'radio_order': radio_order,'mycat': mycat, 'service_order': service_order, 'file': file, 'usr': usr, 'techs': techs, 'page': 'Create Report','mycat': mycat,'topcat': topcat, 'radio':radio})


def service_ordering_image(request, id1, id2, id3):
    context = {}
    context['id1']= id1
    context['id2']= id2
    context['id3']= id3
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    radio=Users.objects.filter(orgid=org).filter(department="Radiologist")
    service_order = ServiceOrder.objects.get(id=id1)
    patient = Patient.objects.get(id = service_order.pid)
    include = ['Radiological Report', 'Image Analysis Report', 'Implant Planning Report', 'Implant Surgical Guide']
    topcat = Topcat.objects.filter(topcat__in = include)
    mycat = topcat.get(id=id2)
    image_order = ImageAnalysis.objects.get(id=id3)
    try:
        image_order.sgn = Users.objects.get(id=image_order.signby).name
        image_order.edu = Users.objects.get(id=image_order.signby).edu
        image_order.spec = Users.objects.get(id=image_order.signby).spec
    except Exception as e:
        image_order.sgn = image_order.signby
    if image_order.status == "Pending":
        image_order.status = "In Process"
        image_order.badge = "badge badge-warning"
        image_order.save()
        notification = Notification(orgid = org, sendTo = image_order.orgid_id, serviceOrderId = service_order.id, sent = True, lineItemId = image_order.id, service = 'Image Analysis Report', user = usr.name, event = 'ORDER STATUS', details = 'Your order for Image Analysis Report for the order ID: '+str(service_order.order_id) + ' and the line item id '+str(image_order.item_id)+' ,status has been changed to '+ str(image_order.status), date = datetime.now(), hyperLink = '/manageReportImage/'+str(service_order.id))
        notification.save()
    
    file = ''
    try:
        file = FeedFile.objects.filter(repid=service_order.id).filter(sodrid = image_order.id)
    except FileNotFoundError:
        print('File Not Found')
    
    for i in file:
        a = str(i.file)
        i.fileName = a.split('/')[-1]
    techno = Users.objects.filter(orgid=org).filter(department="Technician")
    return render(request, 'Admin_Orders/reporting_image.html', {'service_order': service_order, 'patient': patient, 'file': file,'image_order':image_order, 'usr': usr,'page': 'Create Report','mycat': mycat, 'topcat': topcat, 'radio':radio, 'techno': techno})
    

def createGuideReport(request, id1, id2, id3):
    context = {}
    context['id1']= id1
    context['id2']= id2
    context['id3']= id3
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    radio=Users.objects.filter(orgid=org).filter(department="Radiologist")
    service_order = ServiceOrder.objects.get(id=id1)
    patient = Patient.objects.get(id=service_order.pid)
    include = ['Implant Surgical Guide', 'Digital Lab Services']
    topcat = Topcat.objects.filter(topcat__in = include)
    mycat = topcat.get(id=id2)
    image_order = Suricalguide.objects.get(id=id3)
    try:
        image_order.sgn = Users.objects.get(id=image_order.signby).name
        image_order.edu = Users.objects.get(id=image_order.signby).edu
        image_order.spec = Users.objects.get(id=image_order.signby).spec
    except Exception as e:
        image_order.sgn = image_order.signby
    if image_order.status == "Pending":
        image_order.status = "In Process"
        image_order.badge = "badge badge-warning"
        image_order.save()

    file = FeedFile.objects.filter(repid=service_order.id).filter(sodrid = image_order.id)
    techno = Users.objects.filter(orgid=org).filter(department="Technician")
    context = {'service_order': service_order,'patient': patient, 'topcat': topcat, 'file': file,'image_order':image_order, 'usr': usr, 'org': org, 'page': 'Create Report','mycat': mycat, 'radio':radio, 'techno': techno}
    return render(request, 'LabOrder/createGuideReport.html', context)
                

def service_ordering_planning(request, id1, id2, id3):
    context = {}
    context['id1']= id1
    context['id2']= id2
    context['id3']= id3
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    radio = Users.objects.filter(orgid=org).filter(department = "Radiologist")
    service_order = ServiceOrder.objects.get(id=id1)
    mycat = topcat.get(id=id2)
    image_order = ImplantPlanning.objects.get(id=id3)
    try:
        image_order.sgn = Users.objects.get(id=image_order.signby).name
        image_order.edu = Users.objects.get(id=image_order.signby).edu
        image_order.spec = Users.objects.get(id=image_order.signby).spec
    except Exception as e:
        image_order.sgn = image_order.signby
    if image_order.status == "Pending":
        image_order.status = "In Process"
        image_order.badge = "badge badge-warning"
        image_order.save()
        notification = Notification(orgid = org, sendTo = image_order.orgid_id, serviceOrderId = service_order.id, sent = True, lineItemId = image_order.id, service = 'Implant Planning Report', user = usr.name, event = 'ORDER STATUS', details = 'Your order for Implant Planning Report for the order ID: '+str(service_order.order_id) + ' and the line item id '+str(image_order.item_id)+' ,status has been changed to '+ str(image_order.status), date = datetime.now(), hyperLink = '/manageReportPlanning/'+str(service_order.id))
        notification.save()

    file = ''
    try:
        file = FeedFile.objects.filter(repid=service_order.id).filter(sodrid = image_order.id)
    except FileNotFoundError:
        print('File Not Found')
    
    for i in file:
        a = str(i.file)
        i.fileName = a.split('/')[-1]
    techno = Users.objects.filter(orgid=org).filter(department="Technician")
    return render(request, 'Admin_Orders/reporting_planning.html',
                  {'service_order': service_order,'org':org, 'file': file,'image_order':image_order, 'usr': usr,'page': 'Create Report','mycat': mycat, 'radio':radio, 'techno': techno})
    

def case_Details(request, id1, id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id1)
    include = ['Radiological Report', 'Image Analysis Report', 'Implant Planning Report', 'Implant Surgical Guide']    
    topcat = Topcat.objects.filter(topcat__in = include)
    mycat = topcat.get(id=id2)
    domain=Organisation.objects.get(orgtype="Domain Owner")
    studies = Study.objects.filter(orgid=domain).filter(topcat=mycat.topcat) 
    file = FeedFile.objects.filter(repid=service_order.id)
    log = ServiceLog.objects.filter(repid=service_order.id)
    patient = Patient.objects.get(id=service_order.pid)
    comment = Comments.objects.filter(repid = service_order.id)
    image_order = ImageAnalysis.objects.filter(repid=service_order.id)
    for i in image_order:
        if i.upload:
            i.down = ""
        else:
            i.down = "disabled"
    
    icon = ''
    currency = ''
    if org.country == 'IN':
        currency = 'price'
        icon = '<i class="fa-solid fa-indian-rupee-sign"></i>'
    else:
        currency = 'dollarPrice'
        icon = '<i class="fa-solid fa-dollar-sign"></i>'
    
    data={'usr':usr, 'org':org,'log': log, 'icon': icon, 'currency': currency, 'service_order':service_order,'studies':studies, 'patient':patient, 'mycat':mycat, 'topcat': topcat, 'image_order': image_order, 'file':file, 'comment': comment}
    return render(request, 'Admin_Orders/case_details.html', data)


def case_DetailsGuide(request, id1, id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id1)
    
    include = ['Implant Surgical Guide', 'Digital Lab Services']
    include2 = ["Digital Lab Services"]
    page = ''
    if org.orgtype == 'Domain Owner':
        topcat = Topcat.objects.filter(status = 'Active').exclude(topcat__in = include2)
        page = 'LabOrder/CaseDetailsGuideSecond.html'
    else:
        topcat = Topcat.objects.filter(topcat__in = include)
        page = 'LabOrder/CaseDetailsGuide.html'
    mycat = topcat.get(id=id2)
    
    domain = Organisation.objects.get(orgtype="Domain Owner")
    studies = Study.objects.filter(orgid=domain).filter(topcat=mycat.topcat) 
    file = FeedFile.objects.filter(repid=service_order.id)
    log = ServiceLog.objects.filter(repid=service_order.id)
    patient = Patient.objects.get(id=service_order.pid)
    comment = Comments.objects.filter(repid = service_order.id)
    image_order = Suricalguide.objects.filter(repid=service_order.id)
    for i in image_order:
        if i.upload:
            i.down = ""
        else:
            i.down = "disabled"
    
    icon = ''
    currency = ''
    if org.country == 'IN':
        currency = 'price'
        icon = '<i class="fa-solid fa-indian-rupee-sign"></i>'
    else:
        currency = 'dollarPrice'
        icon = '<i class="fa-solid fa-dollar-sign"></i>'
    
    for i in image_order:
        if i.status != 'Submit Order':
            service_order.status = 'In Process'
            service_order.badge = 'badge badge-warning'
            service_order.save()
            break
    lineOrderNumber = 0
    totalLineItem = image_order.count()
    for i in image_order:
        if i.status == 'Order Completed':
            lineOrderNumber +=1
    if lineOrderNumber == totalLineItem:
        service_order.status = 'Completed'
        service_order.badge = 'badge badge-success'
        service_order.save()
    
    data={'usr':usr, 'org': org,'log': log,  'icon': icon, 'currency': currency, 'service_order':service_order,'studies':studies, 'patient':patient, 'mycat':mycat, 'topcat': topcat, 'image_order': image_order, 'file':file, 'comment': comment}
    return render(request, page, data)

def case_DetailsLab(request, id1, id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id1)
    
    include = ['Implant Surgical Guide', 'Digital Lab Services']
    topcat = Topcat.objects.filter(topcat__in = include)
    mycat = topcat.get(id=id2)
    
    domain = Organisation.objects.get(orgtype="Domain Owner")
    studies = Study.objects.filter(orgid=domain).filter(topcat=mycat.topcat) 
    file = FeedFile.objects.filter(repid=service_order.id)
    log = ServiceLog.objects.filter(repid=service_order.id)
    patient = Patient.objects.get(id=service_order.pid)
    comment = Comments.objects.filter(repid = service_order.id)

    extraItems = ExtraLabItem.objects.filter(repid = service_order.id)
       
    image_order = Prosthetic.objects.filter(repid=service_order.id)
    
    icon = ''
    currency = ''
    if org.country == 'IN':
        currency = 'price'
        icon = '<i class="fa-solid fa-indian-rupee-sign"></i>'
    else:
        currency = 'dollarPrice'
        icon = '<i class="fa-solid fa-dollar-sign"></i>'
    
    data={'usr':usr, 'org': org,'log': log,  'icon': icon, 'currency': currency, 'service_order':service_order,'studies':studies, 'extraItems': extraItems, 'patient':patient, 'mycat':mycat, 'topcat': topcat, 'image_order': image_order, 'file':file, 'comment': comment}
    return render(request, 'LabOrder/CaseDetailsLab.html', data)

def radiological_Details(request, id1, id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id = usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = id1)
    include= ['Radiological Report', 'Image Analysis Report', 'Implant Planning Report', 'Implant Surgical Guide']    
    topcat = Topcat.objects.filter(topcat__in = include)
    mycat = topcat.get(id = id2)
    domain=Organisation.objects.get(orgtype="Domain Owner")
    studies = Study.objects.filter(orgid=domain).filter(topcat=mycat.topcat)  
    file = FeedFile.objects.filter(repid=service_order.id)
    patient = Patient.objects.get(id=service_order.pid)
    comment = Comments.objects.filter(repid = service_order.id)
    log = ServiceLog.objects.filter(repid=service_order.id)
    radio_order = RadiologycalServices.objects.filter(repid=service_order.id)
    
    for i in radio_order:
        if service_order.upload:
            i.down = ""
        else:
            i.down = "disabled"
        
    
    icon = ''
    currency = ''
    if org.country == 'IN':
        currency = 'price'
        icon = '<i class="fa-solid fa-indian-rupee-sign"></i>'
    else:
        currency = 'dollarPrice'
        icon = '<i class="fa-solid fa-dollar-sign"></i>'
        
    data = {'usr':usr, 'org':org,'log': log, 'icon': icon, 'currency': currency, 'service_order':service_order, 'patient':patient,'mycat': mycat, 'topcat': topcat,'studies': studies, 'radio_order':radio_order, 'file':file, 'comment': comment}
    return render(request, 'Admin_Orders/case_details_radio.html', data)

def adminComment(request, id1, id2):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id1)
    mycat = topcat.get(id=id2)
    file = FeedFile.objects.filter(repid=service_order.id)
    patient = Patient.objects.get(id=service_order.pid)
    radio_order = RadiologycalServices.objects.filter(repid=service_order.id)
    comment = Comments.objects.filter(repid = service_order.id)
    if request.method == 'POST':
        comment = request.POST.get('comment')
        name=usr.name
        comments=Comments(orgid = org, name=name, comment=comment, repid=service_order.id)
        comments.save()
        service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy, log = "EDITED SERVICE ORDER", message = 'Post a Comment')
        service_log.save()
        notification = Notification(orgid = org, sendTo = service_order.orgid_id, serviceOrderId = service_order.id, sent = True, service = 'Radiological Report', user = usr.name, event = 'COMMENT', details = 'A new comment added by Dentread for the order ID: '+str(service_order.order_id) + ' .Please check the comment.', date = datetime.now(), hyperLink = '/radiological_status/'+str(service_order.id))
        notification.save()
        return redirect('/radiological_Details/'+str(service_order.id)+'/'+str(mycat.id))
    data = {'page': 'status','comment': comment, 'file':file,'mycat': mycat, 'usr': usr, 'org': org, 'topcat': topcat, 'radio_order': radio_order, 'patient': patient,
            'service_order': service_order}
    return render(request, 'Admin_Orders/case_details_radio.html', data)

def adminCommentImage(request, id1, id2):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id1)
    mycat = topcat.get(id=id2)
    file = FeedFile.objects.filter(repid=service_order.id)
    patient = Patient.objects.get(id=service_order.pid)
    radio_order = ImageAnalysis.objects.filter(repid=service_order.id)
    comment = Comments.objects.filter(repid = service_order.id)
    if request.method == 'POST':
        comment = request.POST.get('comment')
        name=usr.name
        comments=Comments(orgid = org, name=name, comment=comment, repid=service_order.id)
        comments.save()
        service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy, log = "EDITED SERVICE ORDER", message = 'Post a Comment')
        service_log.save()
        notification = Notification(orgid = org, sendTo = service_order.orgid_id, serviceOrderId = service_order.id, sent = True, service = 'Image Analysis Report', user = usr.name, event = 'COMMENT', details = 'A new comment added by Dentread for the order ID: '+str(service_order.order_id) + ' .Please check the comment.', date = datetime.now(), hyperLink = '/imageAnalysis_status/'+str(service_order.id))
        notification.save()
        return redirect('/case_Details/'+str(service_order.id)+'/'+str(mycat.id))
    data = {'page': 'status', 'file':file, 'comment': comment, 'mycat': mycat, 'usr': usr, 'org': org, 'topcat': topcat, 'radio_order': radio_order, 'patient': patient,
            'service_order': service_order}
    return render(request, 'Admin_Orders/case_details.html', data)

def adminCommentGuide(request, id1, id2):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id1)
    mycat = topcat.get(id=id2)
    file = FeedFile.objects.filter(repid=service_order.id)
    patient = Patient.objects.get(id=service_order.pid)
    radio_order = Suricalguide.objects.filter(repid=service_order.id)
    comment = Comments.objects.filter(repid = service_order.id)
    if request.method == 'POST':
        comment = request.POST.get('comment')
        name=usr.name
        comments=Comments(orgid = org, name=name, comment=comment, repid=service_order.id)
        comments.save()
        service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy, log = "EDITED SERVICE ORDER", message = 'Post a Comment')
        notification = Notification(orgid = org, sendTo = service_order.orgid_id, serviceOrderId = service_order.id, sent = True, service = 'Implant Surgical Guide', user = usr.name, event = 'COMMENT', details = 'A new comment added by the Lab '+ str(org.orgname) + ' for the order ID: '+str(service_order.order_id) , date = datetime.now(), hyperLink = '/guideStatus/'+str(service_order.id))
        service_log.save()
        notification.save()
        return redirect('/case_DetailsGuide/'+str(service_order.id)+'/'+str(mycat.id))
    data = {'page': 'status', 'file':file, 'comment': comment, 'mycat': mycat, 'usr': usr, 'org': org, 'topcat': topcat, 'radio_order': radio_order, 'patient': patient,
            'service_order': service_order}
    return render(request, 'LabOrder/CaseDetailsGuide.html', data)

def adminCommentLab(request, id1, id2):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id1)
    mycat = topcat.get(id=id2)
    file = FeedFile.objects.filter(repid=service_order.id)
    patient = Patient.objects.get(id=service_order.pid)
    radio_order = Prosthetic.objects.filter(repid=service_order.id)
    comment = Comments.objects.filter(repid = service_order.id)
    if request.method == 'POST':
        comment = request.POST.get('comment')
        name=usr.name
        comments=Comments(orgid = org, name=name, comment=comment, repid=service_order.id)
        comments.save()
        service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy, log = "EDITED SERVICE ORDER", message = 'Post a Comment')
        notification = Notification(orgid = org, sendTo = service_order.orgid_id, serviceOrderId = service_order.id, sent = True, service = 'Digital Lab Services', user = usr.name, event = 'COMMENT', details = 'A new comment added by the Lab '+ str(org.orgname) + ' for the order ID: '+str(service_order.order_id) , date = datetime.now(), hyperLink = '/DigitalLabStatus/'+str(service_order.id))
        service_log.save()
        notification.save()
        return redirect('/case_DetailsLab/'+str(service_order.id)+'/'+str(mycat.id))
    data = {'page': 'status', 'file':file, 'comment': comment, 'mycat': mycat, 'usr': usr, 'org': org, 'topcat': topcat, 'radio_order': radio_order, 'patient': patient,
            'service_order': service_order}
    return render(request, 'LabOrder/CaseDetailsLab.html', data)

def adminCommentPlanning(request, id1, id2):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id1)
    mycat = topcat.get(id=id2)
    file = FeedFile.objects.filter(repid=service_order.id)
    patient = Patient.objects.get(id=service_order.pid)
    radio_order = ImplantPlanning.objects.filter(repid=service_order.id)
    comment = Comments.objects.filter(repid = service_order.id)
    if request.method == 'POST':
        comment = request.POST.get('comment')
        name=usr.name
        comments=Comments(orgid = org, name=name, comment=comment, repid=service_order.id)
        comments.save()
        service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy, log = "EDITED SERVICE ORDER", message = 'Post a Comment')
        service_log.save()
        notification = Notification(orgid = org, sendTo = service_order.orgid_id, serviceOrderId = service_order.id, sent = True, service = 'Implant Planning Report', user = usr.name, event = 'COMMENT', details = 'A new comment added by Dentread for the order ID: '+str(service_order.order_id) + ' .Please check the comment.', date = datetime.now(), hyperLink = '/implantPlanning_status/'+str(service_order.id))
        notification.save()
        return redirect('/case_DetailsPlanning/'+str(service_order.id)+'/'+str(mycat.id))
    data = {'page': 'status','comment': comment, 'file':file,'mycat': mycat, 'usr': usr, 'org': org, 'topcat': topcat, 'radio_order': radio_order, 'patient': patient,
            'service_order': service_order}
    return render(request, 'Admin_Orders/case_DetailsPlanning.html', data)


def case_DetailsPlanning(request, id1, id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order=ServiceOrder.objects.get(id=id1)
    include = ['Radiological Report', 'Image Analysis Report', 'Implant Planning Report', 'Implant Surgical Guide']    
    topcat = Topcat.objects.filter(topcat__in = include)
    mycat = topcat.get(id=id2)
    domain = Organisation.objects.get(orgtype="Domain Owner")
    studies = Study.objects.filter(orgid = domain).filter(topcat = mycat.topcat)
    file = FeedFile.objects.filter(repid = service_order.id)
    patient = Patient.objects.get(id = service_order.pid)
    comment = Comments.objects.filter(repid = service_order.id)
    image_order = ImplantPlanning.objects.filter(repid = service_order.id)
    log = ServiceLog.objects.filter(repid = service_order.id)
    for i in image_order:
        if i.upload:
            i.down = ""
        else:
            i.down = "disabled"
    
    icon = ''
    currency = ''
    if org.country == 'IN':
        currency = 'price'
        icon = '<i class="fa-solid fa-indian-rupee-sign"></i>'
    else:
        currency = 'dollarPrice'
        icon = '<i class="fa-solid fa-dollar-sign"></i>'
    
    data={'usr':usr,'log': log, 'org':org,  'icon': icon, 'currency': currency, 'service_order':service_order, 'studies':studies, 'patient':patient, 'mycat':mycat, 'topcat': topcat, 'image_order': image_order, 'file':file, 'comment': comment}
    return render(request, 'Admin_Orders/case_DetailsPlanning.html', data)

def remark(request, id):
    if request.method == "POST":
        remark = request.POST.get('remark')
        service_order = ServiceOrder.objects.get(id=id)
        service_order.remark = remark
        service_order.save()
        return redirect('/index')


def upload(request, id):
    service_order = ServiceOrder.objects.get(id=id)
    if str(service_order.locate) != "DMDGZB" or str(service_order.locate) != "DMDGGN" or str(service_order.locate) != "DMDDEL" or str(
            service_order.locate) != "DMDNDA":
        try:
            refpt = Refpt.objects.get(pid=service_order.pid)
            dcmfile = Dcmfile.objects.filter(Q(refptid=refpt.refptid) | Q(repid=service_order.repid))
            file = FeedFile.objects.filter(Q(repid=service_order.repid) | Q(repid=service_order.repid))
            return render(request, 'Upload_files.html', {'service_order': service_order, 'file': file, 'dcmfile': dcmfile})
        except Refpt.DoesNotExist:
            print("no")

    file = FeedFile.objects.filter(repid=service_order.repid)
    dcmfile = Dcmfile.objects.filter(repid=service_order.repid)

    return render(request, 'Upload_files.html', {'service_order': service_order, 'file': file, 'dcmfile': dcmfile})


def createservice_order(request):
    service_order = ServiceOrder.objects.get(id=2)
    return render(request, 'CreateServiceOrder.html', {'service_order': service_order})


import calendar


def business(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    invoices = Invoice.objects.filter(orgid=org)
    today = date.today()

    scan = invoices.count()


    sales = invoices
    sales_cash = sales.filter(mode='Cash')
    sales_card = sales.filter(mode='Card')
    sales_online = sales.filter(mode='Online')

    amount_cash = sales_cash.aggregate(Sum('payable'))
    total_cash = amount_cash['payable__sum']

    amount_card = sales_card.aggregate(Sum('payable'))
    total_card = amount_card['payable__sum']

    amount_online = sales_online.aggregate(Sum('payable'))
    total_online = amount_online['payable__sum']

    amount = sales.aggregate(Sum('payable'))
    total = amount['payable__sum']
    if total == None:
        total = 0
    pat = Patient.objects.filter(orgid=org)
    pt = pat.count()

    rdoc = Refdoctor.objects.filter(orgid=org).count()
    pdservice_order = ServiceOrder.objects.filter(orgid=org).filter(repby='')
    radio = Users.objects.filter(orgid=org).filter(department="Radiologist")

    crmonth = datetime.today().month
    cryear = datetime.today().year
    stdate = datetime.today().replace(day=1)
    last_6month = stdate + relativedelta(months=-6)

    invoice = invoices.filter(date__gte=last_6month)


    saledel = invoices.annotate(month=ExtractMonth('date'), year=ExtractYear('date')).values('month', 'year') \
        .annotate(payable=Sum('payable')).values('month', 'payable', 'year')


    delmonth = []
    delyear = []

    delamount = []

    delcramount = []

    today = date.today()

    crdel = invoice.filter(date__month=today.month)
    crdelsale = crdel.annotate(month=ExtractMonth('date')).values('month').annotate(payable=Sum('payable')).values(
        'payable')


    for s in crdelsale:
        delcramount.append(s['payable'])

    for s in saledel:
        delmonth.append(calendar.month_name[s['month']])
        delyear.append(s['year'])
        delamount.append(s['payable'])




    data = { 'delyear': delyear,
            'total_cash': total_cash,
            'total_card': total_card, 'total_online': total_online,
            'scan': scan, 'delcramount': delcramount, 'total': total, 'pt': pt,'rdoc': rdoc, 'pdservice_order': pdservice_order, 'radio': radio,
            'delmonth': delmonth, 'delamount': delamount,'usr':usr, 'org':org}

    return render(request, 'Business.html', data)


def business_yesterday(request):
    today = date.today()
    yesterday = today + timedelta(days=-1)
    scn = Invoice.objects.filter(location__icontains='DMD')
    scan = scn.filter(date=yesterday).count()

    sl = Invoice.objects.filter(location__icontains='DMD')
    sales = sl.filter(date=yesterday)
    sales_cash = sales.filter(mode='Cash')
    sales_card = sales.filter(mode='Card')
    sales_online = sales.filter(mode='Online')

    amount_cash = sales_cash.aggregate(Sum('payable'))
    total_cash = amount_cash['payable__sum']

    amount_card = sales_card.aggregate(Sum('payable'))
    total_card = amount_card['payable__sum']

    amount_online = sales_online.aggregate(Sum('payable'))
    total_online = amount_online['payable__sum']

    amount = sales.aggregate(Sum('payable'))
    total = amount['payable__sum']
    if total == None:
        total = 0

    pat = Patient.objects.filter(locate__icontains='DMD')
    pt = pat.filter(rdate=yesterday).count()
    rdoc = Refdoctor.objects.filter(rdate=yesterday).count()
    pdservice_order = ServiceOrder.objects.filter(repby='')
    radio = Users.objects.filter(department="Radiologist")

    crmonth = datetime.today().month
    cryear = datetime.today().year
    stdate = datetime.today().replace(day=1)
    last_6month = stdate + relativedelta(months=-6)

    invoice = Invoice.objects.filter(date__gte=last_6month)

    dmddel = invoice.filter(location="DMDDEL")
    saledel = dmddel.annotate(month=ExtractMonth('date'), year=ExtractYear('date')).values('month', 'year') \
        .annotate(payable=Sum('payable')).values('month', 'payable', 'year')

    dmdggn = invoice.filter(location="DMDGGN")
    saleggn = dmdggn.annotate(month=ExtractMonth('date'), year=ExtractYear('date')).values('month', 'year') \
        .annotate(payable=Sum('payable')).values('month', 'payable', 'year')

    dmdgzb = invoice.filter(location="DMDGZB")
    salegzb = dmdgzb.annotate(month=ExtractMonth('date'), year=ExtractYear('date')).values('month', 'year') \
        .annotate(payable=Sum('payable')).values('month', 'payable', 'year')
    dmdnda = invoice.filter(location="DMDNDA")
    salenda = dmdnda.annotate(month=ExtractMonth('date'), year=ExtractYear('date')).values('month', 'year') \
        .annotate(payable=Sum('payable')).values('month', 'payable', 'year')

    dmdtele = invoice.filter(~Q(location="DMDGZB")).filter(~Q(location="DMDGGN")).filter(~Q(location="DMDDEL")).filter(
        ~Q(location="DMDNDA"))
    saletele = dmdtele.annotate(month=ExtractMonth('date'), year=ExtractYear('date')).values('month', 'year') \
        .annotate(payable=Sum('payable')).values('month', 'payable', 'year')

    saleall = invoice.annotate(month=ExtractMonth('date')).values('month').annotate(payable=Sum('payable')).values(
        'month', 'payable')

    gzbmonth = []
    gzbyear = []
    ggnmonth = []
    ggnyear = []
    delmonth = []
    delyear = []
    ndamonth = []
    ndayear = []

    telemonth = []
    teleamount = []

    allmonth = []
    allamount = []

    ggnamount = []
    gzbamount = []
    delamount = []
    ndaamount = []

    gzbcrmonth = []
    gzbcramount = []
    ggncramount = []
    delcramount = []
    ndacramount = []

    today = date.today()
    crgzb = dmdgzb.filter(date__month=today.month)
    crgzbsale = crgzb.annotate(month=ExtractMonth('date')).values('month').annotate(payable=Sum('payable')).values(
        'month', 'payable')
    crggn = dmdggn.filter(date__month=today.month)
    crggnsale = crggn.annotate(month=ExtractMonth('date')).values('month').annotate(payable=Sum('payable')).values(
        'payable')
    crdel = dmddel.filter(date__month=today.month)
    crdelsale = crdel.annotate(month=ExtractMonth('date')).values('month').annotate(payable=Sum('payable')).values(
        'payable')
    crnda = dmdnda.filter(date__month=today.month)
    crndasale = crnda.annotate(month=ExtractMonth('date')).values('month').annotate(payable=Sum('payable')).values(
        'payable')

    dsccramount = []
    paradisecramount = []
    brtcramount = []
    telecrmonth = []

    crdmddsc = invoice.filter(location="DSC").filter(date__month=today.month)
    crdscsale = crdmddsc.annotate(month=ExtractMonth('date')).values('month').annotate(payable=Sum('payable')).values(
        'month', 'payable')

    crdmdparadise = invoice.filter(location="Paradise").filter(date__month=today.month)
    crparadisesale = crdmdparadise.annotate(month=ExtractMonth('date')).values('month').annotate(
        payable=Sum('payable')).values('payable')

    crdmdbrt = invoice.filter(location="BRTXRAY").filter(date__month=today.month)
    crbrtsale = crdmdbrt.annotate(month=ExtractMonth('date')).values('month').annotate(payable=Sum('payable')).values(
        'payable')

    for s in crdscsale:
        telecrmonth.append(calendar.month_name[s['month']])
        dsccramount.append(s['payable'])

    for s in crparadisesale:
        paradisecramount.append(s['payable'])
    for s in crbrtsale:
        brtcramount.append(s['payable'])

    for s in crgzbsale:
        gzbcrmonth.append(calendar.month_name[s['month']])
        gzbcramount.append(s['payable'])
    for s in crggnsale:
        ggncramount.append(s['payable'])
    for s in crdelsale:
        delcramount.append(s['payable'])
    for s in crndasale:
        ndacramount.append(s['payable'])

    for s in saledel:
        delmonth.append(calendar.month_name[s['month']])
        delyear.append(s['year'])
        delamount.append(s['payable'])
    for s in salegzb:
        gzbmonth.append(calendar.month_name[s['month']])
        gzbyear.append(s['year'])
        gzbamount.append(s['payable'])
    for s in saleggn:
        ggnmonth.append(calendar.month_name[s['month']])
        ggnyear.append(s['year'])
        ggnamount.append(s['payable'])
    for s in salenda:
        ndamonth.append(calendar.month_name[s['month']])
        ndayear.append(s['year'])
        ndaamount.append(s['payable'])

    for s in saletele:
        telemonth.append(calendar.month_name[s['month']])
        teleamount.append(s['payable'])

    for s in saleall:
        allmonth.append(calendar.month_name[s['month']])
        allamount.append(s['payable'])

    gzb = invoice.filter(location="DMDGZB")
    gzbcrm = gzb.filter(date__month=today.month)
    gzbopg = gzbcrm.filter(study__icontains="Panaromic").count()
    gzbcbct = gzbcrm.filter(study__icontains="CBCT").count()
    gzbtot = gzbcrm.count()
    gzbother = gzbtot - gzbcbct - gzbopg

    ggn = invoice.filter(location="DMDGGN")
    ggncrm = ggn.filter(date__month=today.month)
    ggnopg = ggncrm.filter(study__icontains="Panaromic").count()
    ggncbct = ggncrm.filter(study__icontains="CBCT").count()
    ggntot = ggncrm.count()
    ggnother = ggntot - ggncbct - ggnopg

    delh = invoice.filter(location="DMDDEL")
    delhcrm = delh.filter(date__month=today.month)
    delhopg = delhcrm.filter(study__icontains="Panaromic").count()
    delhcbct = delhcrm.filter(study__icontains="Panaromic").count()
    delhtot = delhcrm.count()
    delhother = delhtot - delhopg - delhcbct

    nda = invoice.filter(location="DMDNDA")
    ndacrm = nda.filter(date__month=today.month)
    ndaopg = ndacrm.filter(study__icontains="Panaromic").count()
    ndacbct = ndacrm.filter(study__icontains="CBCT").count()
    ndatot = ndacrm.count()
    ndaother = ndatot - ndacbct - ndaopg

    invent_sm = Inventory.objects.filter(Q(pid__icontains="DMDGZB")).filter(date__month=today.month).aggregate(
        Sum('price'))
    gzbinv = invent_sm['price__sum']
    if gzbinv is None:
        gzbinv = 0
    invent_del = Inventory.objects.filter(Q(pid__icontains="DMDDEL")).filter(date__month=today.month).aggregate(
        Sum('price'))
    delinv = invent_del['price__sum']
    if delinv is None:
        delinv = 0
    invent_ggn = Inventory.objects.filter(Q(pid__icontains="DMDGGN")).filter(date__month=today.month).aggregate(
        Sum('price'))
    ggninv = invent_ggn['price__sum']
    if ggninv is None:
        ggninv = 0
    invent_nda = Inventory.objects.filter(Q(pid__icontains="DMDNDA")).filter(date__month=today.month).aggregate(
        Sum('price'))
    ndainv = invent_nda['price__sum']
    if ndainv is None:
        ndainv = 0

    data = {'dsccramount': dsccramount, 'paradisecramount': paradisecramount, 'brtcramount': brtcramount,
            'telecrmonth': telecrmonth, 'allmonth': allmonth, 'allamount': allamount, 'telemonth': telemonth,
            'teleamount': teleamount, 'gzbyear': gzbyear, 'delyear': delyear, 'ggnyear': ggnyear, 'ndayear': ndayear,
            'total_cash': total_cash,
            'total_card': total_card, 'total_online': total_online, 'gzbtot': gzbtot, 'gzbother': gzbother,
            'ggntot': ggntot, 'ndatot': ndatot,
            'ggnother': ggnother, 'delhtot': delhtot, 'delhother': delhother, 'ndaother': ndaother, 'gzbcbct': gzbcbct,
            'ndacbct': ndacbct, 'ggncbct': ggncbct,
            'delhcbct': delhcbct, 'gzbopg': gzbopg, 'ggnopg': ggnopg, 'ndaopg': ndaopg, 'delhopg': delhopg,
            'scan': scan, 'gzbcrmonth': gzbcrmonth,
            'gzbcramount': gzbcramount, 'ggncramount': ggncramount, 'ndacramount': ndacramount,
            'delcramount': delcramount, 'total': total, 'pt': pt,
            'rdoc': rdoc, 'pdservice_order': pdservice_order, 'radio': radio, 'ggnmonth': ggnmonth, 'gzbmonth': gzbmonth,
            'delmonth': delmonth, 'ndamonth': ndamonth,
            'delamount': delamount, 'ggnamount': ggnamount, 'ndaamount': ndaamount, 'gzbamount': gzbamount,
            'gzbinv': gzbinv, 'ggninv': ggninv, 'delinv': delinv, 'ndainv': ndainv}

    return render(request, 'Business.html', data)


def business_thisweek(request):
    tdate = datetime.today()
    start_week = tdate - timedelta(tdate.weekday())
    end_week = start_week + timedelta(7)
    scn = Invoice.objects.filter(location__icontains='DMD')
    scan = scn.filter(date__range=[start_week, end_week]).count()

    sl = Invoice.objects.filter(location__icontains='DMD')
    sales = sl.filter(date__range=[start_week, end_week])
    sales_cash = sales.filter(mode='Cash')
    sales_card = sales.filter(mode='Card')
    sales_online = sales.filter(mode='Online')

    amount_cash = sales_cash.aggregate(Sum('payable'))
    total_cash = amount_cash['payable__sum']

    amount_card = sales_card.aggregate(Sum('payable'))
    total_card = amount_card['payable__sum']

    amount_online = sales_online.aggregate(Sum('payable'))
    total_online = amount_online['payable__sum']

    amount = sales.aggregate(Sum('payable'))
    total = amount['payable__sum']
    if total == None:
        total = 0
    pat = Patient.objects.filter(locate__icontains='DMD')
    pt = pat.filter(rdate__range=[start_week, end_week]).count()
    rdoc = Refdoctor.objects.filter(rdate__range=[start_week, end_week]).count()
    pdservice_order = ServiceOrder.objects.filter(repby='')
    radio = Users.objects.filter(department="Radiologist")

    crmonth = datetime.today().month
    cryear = datetime.today().year
    stdate = datetime.today().replace(day=1)
    last_6month = stdate + relativedelta(months=-6)

    invoice = Invoice.objects.filter(date__gte=last_6month)

    dmddel = invoice.filter(location="DMDDEL")
    saledel = dmddel.annotate(month=ExtractMonth('date'), year=ExtractYear('date')).values('month', 'year') \
        .annotate(payable=Sum('payable')).values('month', 'payable', 'year')

    dmdggn = invoice.filter(location="DMDGGN")
    saleggn = dmdggn.annotate(month=ExtractMonth('date'), year=ExtractYear('date')).values('month', 'year') \
        .annotate(payable=Sum('payable')).values('month', 'payable', 'year')

    dmdgzb = invoice.filter(location="DMDGZB")
    salegzb = dmdgzb.annotate(month=ExtractMonth('date'), year=ExtractYear('date')).values('month', 'year') \
        .annotate(payable=Sum('payable')).values('month', 'payable', 'year')
    dmdnda = invoice.filter(location="DMDNDA")
    salenda = dmdnda.annotate(month=ExtractMonth('date'), year=ExtractYear('date')).values('month', 'year') \
        .annotate(payable=Sum('payable')).values('month', 'payable', 'year')

    dmdtele = invoice.filter(~Q(location="DMDGZB")).filter(~Q(location="DMDGGN")).filter(~Q(location="DMDDEL")).filter(
        ~Q(location="DMDNDA"))
    saletele = dmdtele.annotate(month=ExtractMonth('date'), year=ExtractYear('date')).values('month', 'year') \
        .annotate(payable=Sum('payable')).values('month', 'payable', 'year')

    saleall = invoice.annotate(month=ExtractMonth('date')).values('month').annotate(payable=Sum('payable')).values(
        'month', 'payable')

    gzbmonth = []
    gzbyear = []
    ggnmonth = []
    ggnyear = []
    delmonth = []
    delyear = []
    ndamonth = []
    ndayear = []

    telemonth = []
    teleamount = []

    allmonth = []
    allamount = []

    ggnamount = []
    gzbamount = []
    delamount = []
    ndaamount = []

    gzbcrmonth = []
    gzbcramount = []
    ggncramount = []
    delcramount = []
    ndacramount = []

    today = date.today()
    crgzb = dmdgzb.filter(date__month=today.month)
    crgzbsale = crgzb.annotate(month=ExtractMonth('date')).values('month').annotate(payable=Sum('payable')).values(
        'month', 'payable')
    crggn = dmdggn.filter(date__month=today.month)
    crggnsale = crggn.annotate(month=ExtractMonth('date')).values('month').annotate(payable=Sum('payable')).values(
        'payable')
    crdel = dmddel.filter(date__month=today.month)
    crdelsale = crdel.annotate(month=ExtractMonth('date')).values('month').annotate(payable=Sum('payable')).values(
        'payable')
    crnda = dmdnda.filter(date__month=today.month)
    crndasale = crnda.annotate(month=ExtractMonth('date')).values('month').annotate(payable=Sum('payable')).values(
        'payable')

    dsccramount = []
    paradisecramount = []
    brtcramount = []
    telecrmonth = []

    crdmddsc = invoice.filter(location="DSC").filter(date__month=today.month)
    crdscsale = crdmddsc.annotate(month=ExtractMonth('date')).values('month').annotate(payable=Sum('payable')).values(
        'month', 'payable')

    crdmdparadise = invoice.filter(location="Paradise").filter(date__month=today.month)
    crparadisesale = crdmdparadise.annotate(month=ExtractMonth('date')).values('month').annotate(
        payable=Sum('payable')).values('payable')

    crdmdbrt = invoice.filter(location="BRTXRAY").filter(date__month=today.month)
    crbrtsale = crdmdbrt.annotate(month=ExtractMonth('date')).values('month').annotate(payable=Sum('payable')).values(
        'payable')

    for s in crdscsale:
        telecrmonth.append(calendar.month_name[s['month']])
        dsccramount.append(s['payable'])

    for s in crparadisesale:
        paradisecramount.append(s['payable'])
    for s in crbrtsale:
        brtcramount.append(s['payable'])

    for s in crgzbsale:
        gzbcrmonth.append(calendar.month_name[s['month']])
        gzbcramount.append(s['payable'])
    for s in crggnsale:
        ggncramount.append(s['payable'])
    for s in crdelsale:
        delcramount.append(s['payable'])
    for s in crndasale:
        ndacramount.append(s['payable'])

    for s in saledel:
        delmonth.append(calendar.month_name[s['month']])
        delyear.append(s['year'])
        delamount.append(s['payable'])
    for s in salegzb:
        gzbmonth.append(calendar.month_name[s['month']])
        gzbyear.append(s['year'])
        gzbamount.append(s['payable'])
    for s in saleggn:
        ggnmonth.append(calendar.month_name[s['month']])
        ggnyear.append(s['year'])
        ggnamount.append(s['payable'])
    for s in salenda:
        ndamonth.append(calendar.month_name[s['month']])
        ndayear.append(s['year'])
        ndaamount.append(s['payable'])

    for s in saletele:
        telemonth.append(calendar.month_name[s['month']])
        teleamount.append(s['payable'])

    for s in saleall:
        allmonth.append(calendar.month_name[s['month']])
        allamount.append(s['payable'])

    gzb = invoice.filter(location="DMDGZB")
    gzbcrm = gzb.filter(date__month=today.month)
    gzbopg = gzbcrm.filter(study__icontains="Panaromic").count()
    gzbcbct = gzbcrm.filter(study__icontains="CBCT").count()
    gzbtot = gzbcrm.count()
    gzbother = gzbtot - gzbcbct - gzbopg

    ggn = invoice.filter(location="DMDGGN")
    ggncrm = ggn.filter(date__month=today.month)
    ggnopg = ggncrm.filter(study__icontains="Panaromic").count()
    ggncbct = ggncrm.filter(study__icontains="CBCT").count()
    ggntot = ggncrm.count()
    ggnother = ggntot - ggncbct - ggnopg

    delh = invoice.filter(location="DMDDEL")
    delhcrm = delh.filter(date__month=today.month)
    delhopg = delhcrm.filter(study__icontains="Panaromic").count()
    delhcbct = delhcrm.filter(study__icontains="Panaromic").count()
    delhtot = delhcrm.count()
    delhother = delhtot - delhopg - delhcbct

    nda = invoice.filter(location="DMDNDA")
    ndacrm = nda.filter(date__month=today.month)
    ndaopg = ndacrm.filter(study__icontains="Panaromic").count()
    ndacbct = ndacrm.filter(study__icontains="CBCT").count()
    ndatot = ndacrm.count()
    ndaother = ndatot - ndacbct - ndaopg

    invent_sm = Inventory.objects.filter(Q(pid__icontains="DMDGZB")).filter(date__month=today.month).aggregate(
        Sum('price'))
    gzbinv = invent_sm['price__sum']
    if gzbinv is None:
        gzbinv = 0
    invent_del = Inventory.objects.filter(Q(pid__icontains="DMDDEL")).filter(date__month=today.month).aggregate(
        Sum('price'))
    delinv = invent_del['price__sum']
    if delinv is None:
        delinv = 0
    invent_ggn = Inventory.objects.filter(Q(pid__icontains="DMDGGN")).filter(date__month=today.month).aggregate(
        Sum('price'))
    ggninv = invent_ggn['price__sum']
    if ggninv is None:
        ggninv = 0
    invent_nda = Inventory.objects.filter(Q(pid__icontains="DMDNDA")).filter(date__month=today.month).aggregate(
        Sum('price'))
    ndainv = invent_nda['price__sum']
    if ndainv is None:
        ndainv = 0

    data = {'dsccramount': dsccramount, 'paradisecramount': paradisecramount, 'brtcramount': brtcramount,
            'telecrmonth': telecrmonth, 'allmonth': allmonth, 'allamount': allamount, 'telemonth': telemonth,
            'teleamount': teleamount, 'gzbyear': gzbyear, 'delyear': delyear, 'ggnyear': ggnyear, 'ndayear': ndayear,
            'total_cash': total_cash,
            'total_card': total_card, 'total_online': total_online, 'gzbtot': gzbtot, 'gzbother': gzbother,
            'ggntot': ggntot, 'ndatot': ndatot,
            'ggnother': ggnother, 'delhtot': delhtot, 'delhother': delhother, 'ndaother': ndaother, 'gzbcbct': gzbcbct,
            'ndacbct': ndacbct, 'ggncbct': ggncbct,
            'delhcbct': delhcbct, 'gzbopg': gzbopg, 'ggnopg': ggnopg, 'ndaopg': ndaopg, 'delhopg': delhopg,
            'scan': scan, 'gzbcrmonth': gzbcrmonth,
            'gzbcramount': gzbcramount, 'ggncramount': ggncramount, 'ndacramount': ndacramount,
            'delcramount': delcramount, 'total': total, 'pt': pt,
            'rdoc': rdoc, 'pdservice_order': pdservice_order, 'radio': radio, 'ggnmonth': ggnmonth, 'gzbmonth': gzbmonth,
            'delmonth': delmonth, 'ndamonth': ndamonth,
            'delamount': delamount, 'ggnamount': ggnamount, 'ndaamount': ndaamount, 'gzbamount': gzbamount,
            'gzbinv': gzbinv, 'ggninv': ggninv, 'delinv': delinv, 'ndainv': ndainv}

    return render(request, 'Business.html', data)


def createcompany(request):
    return render(request, 'CreateCompany.html')


def cust_summary(request):
    invoice = Invoice.objects.all()
    return render(request, 'cust_summary.html', {'invoice': invoice})


def add_inv_item(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    patients = Patient.objects.filter(orgid=org)
    inventories = Inventory.objects.filter(orgid=org)
    if request.method == "POST":
        item = request.POST.get('item')
        price = request.POST.get('price')
        qty = request.POST.get('qty')
        remark = request.POST.get('remark')
        pid = request.POST.get('pid')
        invent = Inventory(pid=pid, item=item, qty=qty, remark=remark, price=price, orgid=org)
        invent.save()
        request.session['pid'] = pid
        return redirect('/add_inv_item')
    else:
        pid = request.session['pid']
        patient = patients.get(pid=pid)
        invt = inventories.filter(pid=pid)
        item = Items.objects.all
        return render(request, 'Addinventory.html', {'patient': patient, 'item': item, 'invt': invt})


import urllib.request
import urllib.parse


def sendSMS(apikey, numbers, sender, message):
    data = urllib.parse.urlencode({'apikey': apikey, 'numbers': numbers,
                                   'message': message, 'sender': sender})
    data = data.encode('utf-8')
    request = urllib.request.Request("https://api.textlocal.in/send/?")
    f = urllib.request.urlopen(request, data)
    fr = f.read()
    return (fr)


def addinvoice(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)

    patients = Patient.objects.filter(orgid=org)

    service_orders = ServiceOrder.objects.filter(orgid=org)

    invoices = Invoice.objects.filter(orgid=org)

    study = Study.objects.filter(orgid=org)
    connection1 = get_connection(email_backend='django.core.mail.backends.smtp.EmailBackend',
                                 host='smtpout.secureserver.net',
                                 port=25,
                                 username='info@dentread.com',
                                 password='Amit@7002',
                                 use_tls=False)


    if request.method == "POST" and 'prescription' in request.FILES:
        pid = request.POST.get('pid')
        doc = request.FILES
        prescription = doc['prescription']
        date = request.POST.get('date')

        age = request.POST.get('age')
        name = request.POST.get('name')
        location = request.POST.get('location')
        study = request.POST.get('study')
        studydes = request.POST.get('studydes')
        price = request.POST.get('price')
        discount = request.POST.get('discount')
        payable = request.POST.get('payable')
        paid = request.POST.get('paid')
        balance = request.POST.get('balance')
        remark = request.POST.get('remark')
        mode = request.POST.get('mode')
        sgst = request.POST.get('sgst')
        cgst = request.POST.get('cgst')
        igst = request.POST.get('igst')

        centre = str(location)
        checkid = Invoice.objects.filter(location=centre)

        try:
            max_invid = checkid.aggregate(Max('invid'))['invid__max']
            new_invid = checkid.get(invid=max_invid)
            myinvid = new_invid.invid + 1
        except Invoice.DoesNotExist:
            myinvid = 1
        patient = patients.get(pid=pid)
        refdoc = Refdoctor.objects.get(docid=patient.docid).name
        docemail = Refdoctor.objects.get(docid=patient.docid).email
        refclinic = Refdoctor.objects.get(docid=patient.docid).clinic
        invoice = Invoice(date=date, pid=pid, location=location, cgst=cgst, igst=igst, name=name, sgst=sgst,
                          mode=mode, balance=balance,
                          paid=paid, payable=payable, discount=discount, price=price, studydes=studydes,
                          study=study, invid=myinvid, refdoc=refdoc, refclinic=refclinic, orgid=org)
        invoice.save()

        service_order = ServiceOrder(date=date, pid=pid, remark=remark, signurl="1", study=studydes, docemail=docemail,
                        prescription=prescription, portal="No", age=age, locate=location, repid=myinvid,
                        status='Pending', name=name, badge='badge badge-danger', orgid=org)
        service_order.save()
        subject = "Patient" + patient.name+" registered for "+invoice.study
        from1=org.email

        message = "Dear Doctor, \n\nYour Patient "+patient.name+" has successfully restered for "+invoice.study+" on date "+invoice.date+"\n\nThanks\n"+org.orgname
        email1 = docemail
        try:
            mail = EmailMultiAlternatives(subject, message, from1, [email1, org.email],
                                          connection=connection1)
            mail.send()
        except Exception as e:
            print(e)

        request.session['pid'] = pid

        return redirect('/addinvoice')

    elif request.method == "POST":

        date = request.POST.get('date')
        pid = request.POST.get('pid')

        name = request.POST.get('name')
        age = request.POST.get('age')
        location = request.POST.get('location')
        study = request.POST.get('study')
        studydes = request.POST.get('studydes')
        price = request.POST.get('price')
        discount = request.POST.get('discount')
        payable = request.POST.get('payable')
        paid = request.POST.get('paid')
        balance = request.POST.get('balance')
        mode = request.POST.get('mode')
        sgst = request.POST.get('sgst')
        cgst = request.POST.get('cgst')
        igst = request.POST.get('igst')
        remark = request.POST.get('remark')

        centre = str(location)
        checkid = Invoice.objects.filter(location=centre)

        try:
            max_invid = checkid.aggregate(Max('invid'))['invid__max']
            new_invid = checkid.get(invid=max_invid)
            myinvid = new_invid.invid + 1
        except Invoice.DoesNotExist:
            myinvid = 1
        patient = patients.get(pid=pid)
        refdoctor = Refdoctor.objects.filter(docid=patient.docid).first()
        if refdoctor:
            refdoc = refdoctor.name
            refclinic = refdoctor.clinic
            docemail = refdoctor.email
        else:
            referdoctor = Users.objects.get(id=patient.docid)
            refdoc = referdoctor.name
            refclinic = Organisation.objects.get(id=referdoctor.orgid_id).orgname
            docemail = referdoctor.email

        invoice = Invoice(date=date, pid=pid, location=location, cgst=cgst, igst=igst, name=name, sgst=sgst,
                          mode=mode, balance=balance,
                          paid=paid, payable=payable, discount=discount, price=price, studydes=studydes,
                          study=study, invid=myinvid, refdoc=refdoc, refclinic=refclinic, orgid=org)
        invoice.save()

        service_order = ServiceOrder(date=date, pid=pid, remark=remark, study=studydes, signurl="1", docemail=docemail, portal="No",
                        repid=myinvid, age=age, locate=location, status='Pending', name=name,
                        badge='badge badge-danger', orgid=org)
        service_order.save()
        subject = "Patient " + patient.name + " registered for " + invoice.study
        from1 = org.email

        message = "Dear Doctor, \n\nYour Patient " + patient.name + " has successfully restered for " + invoice.study + " on date " + invoice.date + "\n\nThanks\n" + org.orgname
        email1 = docemail
        try:
            mail = EmailMultiAlternatives(subject, message, from1, [email1, org.email],
                                          connection=connection1)
            mail.send()
        except Exception as e:
            print(e)

        request.session['pid'] = pid
        return redirect('/addinvoice')
    else:
        pid = request.session['pid']
        service_order = service_orders.filter(pid=pid)
        patient = patients.get(pid=pid)
        allinvoice = invoices.filter(pid=pid)
        return render(request, 'PatientDetails.html',
                      {'patient': patient, 'study': study, 'allinvoice': allinvoice, 'service_order': service_order, 'usr': usr})


def addpatient(request):
    if request.method == "POST":

        rdate = request.POST.get('rdate')

        locate = request.POST.get('locate')
        regby = request.user
        pid = request.POST.get('pid')
        name = request.POST.get('name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        address_1 = request.POST.get('address_1')
        address_2 = request.POST.get('address_2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        medih = request.POST.get('medih')
        refdoctor = request.POST.get('refdoctor')
        docid = request.POST.get('docid')
        centre = str(locate)
        if centre == "DMDGZB":
            checkid = Patient.objects.filter(locate="DMDGZB")
        elif centre == "DMDDEL":
            checkid = Patient.objects.filter(locate="DMDDEL")
        elif centre == "DMDGGN":
            checkid = Patient.objects.filter(locate="DMDGGN")
        elif centre == "DMDNDA":
            checkid = Patient.objects.filter(locate="DMDNDA")
        elif centre == "DSC":
            checkid = Patient.objects.filter(locate="DSC")
        elif centre == "BRTXRAY":
            checkid = Patient.objects.filter(locate="BRTXRAY")
        elif centre == "Radhika Saini":
            checkid = Patient.objects.filter(locate="Radhika Saini")

        try:

            max_pid = checkid.aggregate(Max('pid'))['pid__max']
            new_pid = checkid.get(pid=max_pid)
            myid = new_pid.pid + 1
        except Patient.DoesNotExist:
            myid = 1

        p = str(myid)
        pid = locate + '-' + p

        if Patient.objects.filter(contact=contact).exists():
            checkpt = Patient.objects.filter(contact=contact)
            if checkpt.filter(name=name).exists():
                return render(request, 'exist.html')
            else:
                patient = Patient(rdate=rdate, pid=myid, locate=locate, regby=regby, contact=contact, name=name, age=age, gender=gender, email=email, address_1=address_1, address_2=address_2, city=city, state=state, zip_code=zip_code, medih=medih, refdoctor=refdoctor, docid=docid)
                patient.save()
                request.session['pid'] = pid
                request.session['gender'] = gender
                return redirect('/addinvoice')
        else:
            patient = Patient(rdate=rdate, pid=myid, locate=locate, regby=regby, contact=contact, name=name, age=age, gender=gender, email=email, address_1=address_1, address_2=address_2, city=city, state=state, zip_code=zip_code, medih=medih, refdoctor=refdoctor, docid=docid)
            patient.save()
            request.session['pid'] = pid
            request.session['gender'] = gender
            return redirect('/addinvoice')


def addservice_order(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id)
    patients = Patient.objects.filter(orgid=org)

    if request.method == "POST":

        repsdate = request.POST.get('repsdate')
        text = request.POST.get('text')
        repby = request.POST.get('repby')
        status = request.POST.get('status')
        remark = request.POST.get('remark')
        signby = request.POST.get('signby')
        badge = request.POST.get('badge')
        signurl = request.POST.get('signurl')
        processby = request.POST.get('processby')


        service_order = ServiceOrder.objects.get(id=id)
        service_order.text = text
        service_order.repby = repby
        service_order.status = status
        service_order.remark = remark
        service_order.badge = badge
        service_order.signurl = signurl
        service_order.signby = signby
        service_order.processby = processby

        service_order.save()
        patient = Patient.objects.get(id=service_order.pid)
        if str(status) == "Completed":
            try:
                refpts = Refpt.objects.filter(orgid=patient.refpt_orgid)
                refpt = refpts.get(pid=patient.pid)
                refpt.status = "Completed"
                refpt.btnstatus = "btn btn-primary btn-sm"
                refpt.save()
            except Refpt.DoesNotExist:

                return redirect('/index')
        else:

            return redirect('/index')
    return redirect('/index')

def addservice_order_radio(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_orders = ServiceOrder.objects.filter(orgid=org)


    if request.method == "POST":
        pid = request.POST.get('pid')
        repsdate = request.POST.get('repsdate')
        text = request.POST.get('text')
        repby = request.POST.get('repby')
        status = request.POST.get('status')
        remark = request.POST.get('remark')
        signby = request.POST.get('signby')
        badge = request.POST.get('badge')
        signurl = request.POST.get('signurl')
        processby = request.POST.get('processby')

        service_order = service_orders.get(id=id)
        service_order.text = text
        service_order.repby = repby
        service_order.status = status
        service_order.remark = remark
        service_order.badge = badge
        service_order.signurl = signurl
        service_order.signby = signby
        service_order.processby = processby

        service_order.save()

        return redirect('/index_radio')

    return redirect('/index_radio')

def adminUpdates(request, id1, id2):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id1)
    mycat = topcat.get(id=id2)
    file = FeedFile.objects.filter(repid=service_order.id)
    patient = Patient.objects.get(id=service_order.pid)
    radio_order = RadiologycalServices.objects.filter(repid=service_order.id)
    comment = Comments.objects.filter(repid = service_order.id)
    if request.method == "POST":
        status = request.POST.get('status-select')
        shipped_by = request.POST.get('shipped-by')
        tracking_id = request.POST.get('tracking')
        badge = request.POST.get('badge')
        service_order.status = status
        service_order.shipped_by = shipped_by
        service_order.tracking_id = tracking_id
        service_order.badge = badge
        service_order.save()
        service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy, log = "EDITED SERVICE ORDER LINE ITEM ", message = 'Changed Status To', status = service_order.status)
        service_log.save()
        return redirect('/radiological_Details/'+str(service_order.id)+'/'+str(mycat.id))
    data = {'usr':usr,'comment': comment, 'org':org, 'service_order':service_order, 'patient': patient, 'topcat': topcat, 'radio_order':radio_order,'mycat':mycat, 'file':file}
    
    return render(request, 'Admin_Orders/case_details_radio.html', data)

def adminUpdatesImage(request, id1, id2):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id1)
    mycat = topcat.get(id=id2)
    file = FeedFile.objects.filter(repid=service_order.id)
    patient = Patient.objects.get(id=service_order.pid)
    radio_order = ImageAnalysis.objects.filter(repid=service_order.id)
    comment = Comments.objects.filter(repid = service_order.id)
    if request.method == "POST":
        status = request.POST.get('status-select')
        shipped_by = request.POST.get('shipped-by')
        tracking_id = request.POST.get('tracking')
        badge = request.POST.get('badge')
        service_order.status = status
        service_order.shipped_by = shipped_by
        service_order.tracking_id = tracking_id
        service_order.badge = badge
        service_order.save()
        service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy, log = "EDITED SERVICE ORDER LINE ITEM ", message = 'Changed Status To', status = service_order.status)
        service_log.save()
        return redirect('/case_Details/'+str(service_order.id)+'/'+str(mycat.id))
    data = {'usr':usr, 'org':org,'comment': comment, 'service_order':service_order, 'patient': patient, 'topcat': topcat, 'radio_order':radio_order,'mycat':mycat, 'file':file}
    
    return render(request, 'Admin_Orders/case_details.html', data)

def adminUpdatesGuide(request, id1, id2):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id1)
    mycat = topcat.get(id=id2)
    file = FeedFile.objects.filter(repid=service_order.id)
    patient = Patient.objects.get(id=service_order.pid)
    radio_order = Suricalguide.objects.filter(repid=service_order.id)
    comment = Comments.objects.filter(repid = service_order.id)
    if request.method == "POST":
        status = request.POST.get('status-select')
        shipped_by = request.POST.get('shipped-by')
        tracking_id = request.POST.get('tracking')
        badge = request.POST.get('badge')
        service_order.status = status
        service_order.shipped_by = shipped_by
        service_order.tracking_id = tracking_id
        service_order.badge = badge
        service_order.save()
        service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy, log = "EDITED SERVICE ORDER LINE ITEM ", message = 'Changed Status To', status = service_order.status)
        service_log.save()
        return redirect('/case_DetailsGuide/'+str(service_order.id)+'/'+str(mycat.id))
    data = {'usr':usr, 'org':org,'comment': comment, 'service_order':service_order, 'patient': patient, 'topcat': topcat, 'radio_order':radio_order,'mycat':mycat, 'file':file}
    
    return render(request, 'LabOrder/CaseDetailsGuide.html', data)

def adminUpdatesPlanning(request, id1, id2):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id1)
    mycat = topcat.get(id=id2)
    file = FeedFile.objects.filter(repid=service_order.id)
    patient = Patient.objects.get(id=service_order.pid)
    radio_order = ImplantPlanning.objects.filter(repid=service_order.id)
    comment = Comments.objects.filter(repid = service_order.id)
    if request.method == "POST":
        status = request.POST.get('status-select')
        shipped_by = request.POST.get('shipped-by')
        tracking_id = request.POST.get('tracking')
        badge = request.POST.get('badge')
        service_order.status = status
        service_order.shipped_by = shipped_by
        service_order.tracking_id = tracking_id
        service_order.badge = badge
        service_order.save()
        service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy, log = "EDITED SERVICE ORDER LINE ITEM ", message = 'Changed Status To', status = service_order.status)
        service_log.save()
        return redirect('/case_DetailsPlanning/'+str(service_order.id)+'/'+str(mycat.id))
    data = {'usr':usr, 'org':org,'comment': comment, 'service_order':service_order, 'patient': patient, 'topcat': topcat, 'radio_order':radio_order,'mycat':mycat, 'file':file} 
    return render(request, 'Admin_Orders/case_DetailsPlanning.html', data)


def addservice_order_dent(request, id1, id2, id3):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    context['id3'] = id3
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    rep = ServiceOrder.objects.filter(reforgid=org.id).filter(refstudy='Radiological Report')
    users = Users.objects.filter(orgid=org)
    service_order = ServiceOrder.objects.get(id=id1)
    mycat = topcat.get(id=id2)
    radio_item = RadiologycalServices.objects.get(id=id3)
    radio_order = RadiologycalServices.objects.filter(repid=service_order.id)
    radio = users.filter(department__icontains="Radiologist")

    if request.method == "POST":
        repsdate = request.POST.get('repsdate')
        text = request.POST.get('text')
        repby = request.POST.get('repby')
        status = request.POST.get('status')
        remark = request.POST.get('remark')
        signby = request.POST.get('repby')
        signby = request.POST.get('signby')
        badge = request.POST.get('badge')
        signurl = request.POST.get('signurl')
        if str(status) == "Completed" and signby == "Select Signature" or signby == "":
            msg = "Signature is not updated , Please update signature first"
            return render(request, 'infomsg.html', {'msg': msg})

        else:
            radio_item.text = text
            radio_item.repby = repby
            radio_item.status = status
            radio_item.remark = remark
            radio_item.badge = badge
            radio_item.signurl = signurl
            radio_item.repby = repby
            radio_item.signby = signby
            radio_item.save()
            patient = Patient.objects.get(id=service_order.pid)
            service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department, service_name = service_order.refstudy, log = "CREATE REPORT FOR ORDER LINE ITEM ", message = 'Create Report For', line_item = radio_item.item_id)
            service_log.save()
            if radio_item.status == 'Completed':
                notification = Notification(orgid = org, sendTo = radio_item.orgid_id, serviceOrderId = service_order.id, sent = True, lineItemId = radio_item.id, service = 'Radiological Report', user = usr.name, event = 'ORDER STATUS', details = 'Your order has been Completed for Radiological Report for the order ID: '+str(service_order.order_id) + ' and the line item id '+str(radio_item.item_id), date = datetime.now(), hyperLink = '/manageReport/'+str(service_order.id))
                notification.save()
                # Send Mail code
                attachfiles = FeedFile.objects.filter(repid = service_order.id).filter(sodrid = radio_item.id)
                refClinicEmail = Organisation.objects.get(id = service_order.orgid_id).email
                details = EmailNotification.objects.get(eventCode = 'DRET-0016')
                connection = mail.get_connection()
                connection.open()
                from1 = 'info.dentread@gmail.com'
                order_id = str(service_order.order_id)
                service_name = str(service_order.refstudy)
                subject = details.subject%(order_id)
                message = "Dear \nUser, "+ details.clinicSide%(service_name, order_id) +'\nThank You \nDentread'
                email1 = refClinicEmail
                mymailExicute = mail.EmailMessage(subject, message, from1, [email1], connection=connection)
                # if attachfiles:
                #     for f in attachfiles:
                #         attachment = str(f.file.file.name)
                #         mymailExicute.attach_file(attachment)
                try:
                    mymailExicute.send()
                    connection.close()
                except Exception as e:
                    message = e

            return redirect('/radiological_Details/'+str(service_order.id)+'/'+str(mycat.id))
    return redirect('/radiological_Details/'+str(service_order.id)+'/'+str(mycat.id))



def addservice_order_image(request, id1, id2, id3):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    context['id3'] = id3
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    rep = ServiceOrder.objects.filter(reforgid=org.id).filter(refstudy='Image Analysis Report')
    users = Users.objects.filter(orgid=org)
    service_order = ServiceOrder.objects.get(id=id1)
    mycat = topcat.get(id=id2)
    image_item = ImageAnalysis.objects.get(id=id3)
    radio = users.filter(department__icontains="Radiologist")
    techno= users.filter(department="Technician")

    if request.method == "POST":
        # repsdate = request.POST.get('repsdate')
        repby = request.POST.get('created_by')
        signby = request.POST.get('reviewed_by')
        status = request.POST.get('status')
        remark = request.POST.get('remark')
        badge = request.POST.get('badge')
        if str(status) == "Completed" and signby == "None" or signby == "":
            msg = "Radiologist's Review Pending"
            return render(request, 'infomsg.html', {'msg': msg})

        else:
            image_item.repsdate = datetime.now()
            image_item.repby = repby
            image_item.status = status
            image_item.remark = remark
            image_item.badge = badge
            image_item.signby = signby
            image_item.save()
            patient = Patient.objects.get(id=service_order.pid)
            service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department, service_name = service_order.refstudy, log = "CREATE REPORT FOR ORDER LINE ITEM ", message = 'Create Report For', line_item = image_item.item_id)
            service_log.save()
            if image_item.status == 'Completed':
                notification = Notification(orgid = org, sendTo = image_item.orgid_id, serviceOrderId = service_order.id, sent = True, lineItemId = image_item.id, service = 'Image Analysis Report', user = usr.name, event = 'ORDER STATUS', details = 'Your order has been Completed for Image Analysis Report for the order ID: '+str(service_order.order_id) + ' and the line item id '+str(image_item.item_id), date = datetime.now(), hyperLink = '/manageReportImage/'+str(service_order.id))
                notification.save()
                # Send Mail code
                attachfiles = FeedFile.objects.filter(repid = service_order.id).filter(sodrid = image_item.id)
                refClinicEmail = Organisation.objects.get(id = service_order.orgid_id).email
                details = EmailNotification.objects.get(eventCode = 'DRET-0016')
                connection = mail.get_connection()
                connection.open()
                from1 = 'info.dentread@gmail.com'
                order_id = str(service_order.order_id)
                service_name = str(service_order.refstudy)
                subject = details.subject%(order_id)
                message = "Dear \nUser, "+ details.clinicSide%(service_name, order_id) +'\nThank You \nDentread'
                email1 = refClinicEmail
                mymailExicute = mail.EmailMessage(subject, message, from1, [email1], connection=connection)
                # if attachfiles:
                #     for f in attachfiles:
                #         attachment = str(f.file.file.name)
                #         mymailExicute.attach_file(attachment)
                try:
                    mymailExicute.send()
                    connection.close()
                except Exception as e:
                    message = e
            return redirect('/case_Details/'+str(service_order.id)+'/'+str(mycat.id)) 
    return redirect('/case_Details/'+str(service_order.id)+'/'+str(mycat.id))                              

def addservice_order_planning(request, id1, id2, id3):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    context['id3'] = id3
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    rep = ServiceOrder.objects.filter(reforgid=org.id).filter(refstudy='Implant Planning Report')
    users = Users.objects.filter(orgid=org)
    
    service_order = ServiceOrder.objects.get(id=id1)
    mycat = topcat.get(id=id2)
    image_order = ImplantPlanning.objects.get(id=id3)

    radio = users.filter(department__icontains="Radiologist")
    techno= users.filter(department="Technician")
    if request.method == "POST":
        repby = request.POST.get('created_by')
        signby = request.POST.get('reviewed_by')
        
        status = request.POST.get('status')
        remark = request.POST.get('remark')
        badge = request.POST.get('badge')
        if str(status) == "Completed" and signby == "None" or signby == "":
            msg = "Radiologist's Review Pending"
            return render(request, 'infomsg.html', {'msg': msg})

        else:
            image_order.repsdate = datetime.now()
            
            image_order.repby = repby
            image_order.status = status
            image_order.remark = remark
            image_order.badge = badge
            image_order.signby = signby
            image_order.save()
            patient = Patient.objects.get(id = service_order.pid)
            service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department, service_name = service_order.refstudy, log = "CREATE REPORT FOR ORDER LINE ITEM ", message = 'Create Report For', line_item = image_order.item_id)
            service_log.save()
            if image_order.status == 'Completed':
                notification = Notification(orgid = org, sendTo = image_order.orgid_id, serviceOrderId = service_order.id, sent = True, lineItemId = image_order.id, service = 'Implant Planning Report', user = usr.name, event = 'ORDER STATUS', details = 'Your order has been Completed for Implant Planning Report for the order ID: '+str(service_order.order_id) + ' and the line item id '+str(image_order.item_id), date = datetime.now(), hyperLink = '/manageReportPlanning/'+str(service_order.id))
                notification.save()
                
                # Send Mail code
                attachfiles = FeedFile.objects.filter(repid = service_order.id).filter(sodrid = image_order.id)
                refClinicEmail = Organisation.objects.get(id = service_order.orgid_id).email
                details = EmailNotification.objects.get(eventCode = 'DRET-0016')
                connection = mail.get_connection()
                connection.open()
                from1 = 'info.dentread@gmail.com'
                order_id = str(service_order.order_id)
                service_name = str(service_order.refstudy)
                subject = details.subject%(order_id)
                message = "Dear \nUser, "+ details.clinicSide%(service_name, order_id) +'\nThank You \nDentread'
                email1 = refClinicEmail
                mymailExicute = mail.EmailMessage(subject, message, from1, [email1], connection=connection)
                # if attachfiles:
                #     for f in attachfiles:
                #         attachment = str(f.file.file.name)
                #         mymailExicute.attach_file(attachment)
                try:
                    mymailExicute.send()
                    connection.close()
                except Exception as e:
                    message = e
            return redirect('/case_DetailsPlanning/'+str(service_order.id)+'/'+str(mycat.id))                            
    return redirect('/case_DetailsPlanning/'+str(service_order.id)+'/'+str(mycat.id))


def updateservice_orders(request, id1, id2):
    if request.method == "POST":
        text = request.POST.get('text')
        service_order = ServiceOrder.objects.get(id=id1)
        radio_order = RadiologycalServices.objects.get(id=id2)
        radio_order.text = text
        radio_order.save()
        return JsonResponse({'status': 'save'})


def updateservice_order(request):
    if request.method == "POST":
        id = request.POST.get('id')
        text = request.POST.get('text')
        service_order = ServiceOrder.objects.get(id=id)
        service_order.text = text
        service_order.save()
        return JsonResponse({'status': 'Save'})

def add_patient(request,id):
    usr = Users.objects.get(username=request.user)
    gotUserId = usr.id
    org = Organisation.objects.get(id=usr.orgid_id)
    gotOrgId = org.id
    doctors = Refdoctor.objects.filter(orgid=org)
    topcat = Topcat.objects.get(id=id)
    topcat1 = Topcat.objects.filter(status="Active")
    if request.method == "POST":
        rdate = request.POST.get('rdate')
        locate = request.POST.get('locate')
        regby = usr.name
        name = request.POST.get('name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        address_1 = request.POST.get('address')
        zip_code = request.POST.get('pincode')
        refdoctor = request.POST.get('refdoctor')
        docid = request.POST.get('docid')
        optservice = request.POST.get('optservice')
        service = Maincat.objects.get(id=optservice)
        orderpage = "/refer_dentread"
        if org.orgtype=="Dental Clinic":
            refdoctor = Users.objects.filter(orgid=org).get(department="Admin").name
            docid = Users.objects.filter(orgid=org).get(department="Admin").id
        patient = Patient(orgid=org, locate=locate, regby=regby, name=name,age=age, gender=gender, email=email, contact=contact, address_1 = address_1, zip_code = zip_code, refdoctor=refdoctor, docid=docid)
        service_order = ServiceOrder(pid=patient.id, orgid=org, locate=locate, age=age, name=name, gender=gender, status="Pending", badge='badge badge-danger')
        try:
            patient.save()
        except Exception as e:
            message=e
            return HttpResponse(request, 'HttpResponse/myResponse.html', {'message': message})
        if patient:
            try:
                service_order.pid=patient.id
                service_order.patient_id = patient.pid
                service_order.save()
                service_order.order_id = str(service_order.id)
                service_order.repid = str(service_order.id)
                service_order.save()
                patient.pid ="DR"+str(org.id)+"-"+str(patient.id)
                patient.save()
            except Exception as e:
                patient.delete()
                service_order.delete()
                message = e
                return HttpResponse(request, 'HttpResponse/myResponse.html', {'message': message})
            # Send Mail code
            patient_name = str(patient.name)
            clinic_name = str(org.orgname)
            patient_id = str(patient.pid)
            details = EmailNotification.objects.get(eventCode = 'DRET-0006')
            connection = mail.get_connection()
            connection.open()
            from1 = 'info.dentread@gmail.com'
            subject = details.subject%(patient_name, clinic_name)
            message = 'Dear '+ str(patient_name) + '\n' + details.clinicSide%(clinic_name, patient_id, clinic_name) +'\nThank You \nDentread'
            email1 = email
            mymailExicute = mail.EmailMessage(subject, message, from1, [email1], connection=connection)
            try:
                mymailExicute.send()
                connection.close()
            except Exception as exc:
                messageExc = exc
            eventLog = EventLog(eventCode = 'DRET-0006', event = subject , log = 'A new Patient Registered to dentread, name ' + str(patient.name), orgId = gotOrgId, userId = gotUserId)
            try:
                eventLog.save()
            except Exception as ex:
                eventMessage = ex
                return HttpResponse(request, 'HttpResponse/myResponse.html', {'eventMessage': eventMessage, 'messageExc': messageExc, 'message': message})
        return redirect(orderpage+'/'+str(service_order.id)+'/'+str(service.id))
    if request.method == "POST" and 'prescription' in request.FILES:
        doc = request.FILES
        prescription = doc['prescription']
        rdate = request.POST.get('rdate')
        locate = request.POST.get('locate')
        regby = usr.name
        name = request.POST.get('name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        address_1 = request.POST.get('address')
        refdoctor = request.POST.get('refdoctor')
        zip_code = request.POST.get('pincode')
        docid = request.POST.get('docid')
        optservice = request.POST.get('optservice')
        service = Maincat.objects.get(id=optservice)
        patient = Patient(orgid=org, locate=locate, regby=regby, name=name,age=age, gender=gender, email=email, contact=contact, address_1=address_1,zip_code = zip_code, refdoctor=refdoctor, docid=docid)
        service_order=ServiceOrder(pid=patient.id,orgid=org,locate=locate,age=age, name=name,status="Pending", remark=remark, badge='badge badge-danger', prescription=prescription)
        try:
            patient.save()
        except Exception as e:
            message=e
            return render(request, 'Patient/CreatePatientFirst.html', {'doctors': doctors, 'org': org, 'usr': usr, 'page': 'Add Patient', 'topcat1':topcat1, 'topcat': topcat})
        if patient:
            try:
                service_order.pid = patient.id
                service_order.patient_id = patient.pid
                service_order.save()
                service_order.order_id = str(service_order.id)
                service_order.repid = str(service_order.id)
                service_order.save()
                patient.pid="DR"+str(org.id)+"-"+str(patient.id)
                patient.save()
            except Exception as e:
                patient.delete()
                service_order.delete()
                message = e
            # Send Mail code
            patient_name = str(patient.name)
            clinic_name = str(org.orgname)
            patient_id = str(patient.pid)
            details = EmailNotification.objects.get(eventCode = 'DRET-0006')
            connection = mail.get_connection()
            connection.open()
            from1 = 'info.dentread@gmail.com'
            subject = details.subject%(patient_name, clinic_name)
            message = 'Dear '+ str(patient_name) + '\n' + details.clinicSide%(clinic_name, patient_id, clinic_name) +'\nThank You \nDentread'
            email1 = email
            mymailExicute = mail.EmailMessage(subject, message, from1, [email1], connection=connection)
            try:
                mymailExicute.send()
                connection.close()
            except Exception as exc:
                messageExc = exc
            eventLog = EventLog(eventCode = 'DRET-0006', event = subject , log = 'A new Patient Registered to dentread, name ' + str(patient.name), orgId = gotOrgId, userId = gotUserId)
            try:
                eventLog.save()
            except Exception as ex:
                eventMessage = ex
                return HttpResponse(request, 'HttpResponse/myResponse.html', {'eventMessage': eventMessage, 'messageExc': messageExc, 'message': message})                          
        return redirect(orderpage+'/'+str(service_order.id)+'/'+str(service.id))

    return render(request, 'Patient/CreatePatientFirst.html', {'doctors': doctors, 'org': org, 'usr': usr, 'page': 'Add Patient', 'topcat1':topcat1, 'topcat': topcat})

def refer_services(request, pk, id2):    
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    patient = Patient.objects.get(id = pk)
    topcat = Topcat.objects.filter(status = 'Active')
    mycat = Maincat.objects.get(id = id2)
    orderpage = "/refer_dentread"
    if org.orgtype == "Dental Clinic":
        service_order = ServiceOrder(orgid=org, locate=patient.locate, age=patient.age, name=patient.name, gender=patient.gender, status="Pending", badge='badge badge-danger')
    else:
        service_order = ServiceOrder(orgid=org, parent_orgid=org.parent_id, locate=patient.locate, age=patient.age, name=patient.name, gender=patient.gender, status="Pending", badge='badge badge-danger')
    service_order.order_id = str(service_order.id)
    if patient:
        try:
            service_order.pid = patient.id
            service_order.patient_id = patient.pid
            service_order.save()
            service_order.order_id = str(service_order.id)
            service_order.repid = str(service_order.id)
            service_order.save()
        except Exception as e:
            service_order.delete()
            message = e
    data = {'usr':usr, 'org': org, 'patient': patient}
    return redirect(orderpage+'/'+str(service_order.id)+'/'+str(mycat.id))

def refer_service(request, pk, id2):    
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    patient = Patient.objects.get(id = pk)
    topcat = Topcat.objects.get(id = id2)
    orderpage = "/refer_dentread"
    if org.orgtype == "Dental Clinic":
        service_order = ServiceOrder(orgid=org, locate=patient.locate, age=patient.age, name=patient.name, gender=patient.gender, status="Pending", badge='badge badge-danger')
    else:
        service_order = ServiceOrder(orgid=org, parent_orgid=org.parent_id, locate=patient.locate, age=patient.age, name=patient.name, gender=patient.gender, status="Pending", badge='badge badge-danger')
    if patient:
        try:
            service_order.pid = patient.id
            service_order.patient_id = patient.pid
            service_order.save()
            service_order.order_id = str(service_order.id)
            service_order.repid = str(service_order.id)
            service_order.save()
        except Exception as e:
            service_order.delete()
            message = e
    data = {'usr':usr, 'org': org, 'patient': patient, 'topcat': topcat}
    return redirect(orderpage+'/'+str(service_order.id)+'/'+str(topcat.id))


def add_new_patient(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    doctors = Refdoctor.objects.filter(orgid=org)
    studies=Study.objects.filter(orgid=org)
    if request.method == "POST":
        rdate = request.POST.get('rdate')
        locate = request.POST.get('locate')
        regby = usr.name
        name = request.POST.get('name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        address_1 = request.POST.get('address_1')
        refdoctor = request.POST.get('refdoctor')
        docid = request.POST.get('docid')
        study=request.POST.get('study')
        price = request.POST.get('price')
        discount = request.POST.get('discount')
        payable = request.POST.get('payable')
        paid = request.POST.get('paid')
        balance = request.POST.get('balance')
        remark = request.POST.get('remark')
        mode = request.POST.get('mode')
        if org.orgtype=="Dental Clinic":
            refdoctor=Users.objects.filter(orgid=org).get(department="Admin").name
            docid=Users.objects.filter(orgid=org).get(department="Admin").id
        patient=Patient(orgid=org, locate=locate,regby=regby,name=name,age=age, gender=gender,email=email,contact=contact,address_1=address_1,refdoctor=refdoctor,docid=docid)
        service_order=ServiceOrder(pid=patient.id,orgid=org,locate=locate,age=age, name=name, study=study,status="Pending",price=price,discount=discount,payable=payable,
                      paid=paid, balance=balance, remark=remark, mode=mode, badge='badge badge-danger',)
        try:
            patient.save()
        except Exception as e:
            message=e
            return render(request, 'CreatePatient.html',
                          {'doctors': doctors, 'org': org, 'usr': usr, 'page': 'Add Patient', 'studies': studies, 'message':message})
        if patient:
            try:
                service_order.pid=patient.id
                service_order.save()
                service_order.repid = str(service_order.id)
                service_order.order_id = str(service_order.id)
                service_order.save()
                patient.pid="DR"+str(org.id)+"-"+str(patient.id)
                
                patient.save()
            except Exception as e:
                patient.delete()
                service_order.delete()
                message = e
                return render(request, 'CreatePatient.html',
                              {'doctors': doctors, 'org': org, 'usr': usr, 'page': 'Add Patient', 'studies': studies, 'message': message})
        return redirect('/showpatients')
    if request.method == "POST" and 'prescription' in request.FILES:
        doc = request.FILES
        prescription = doc['prescription']
        rdate = request.POST.get('rdate')
        locate = request.POST.get('locate')
        regby = usr.name
        name = request.POST.get('name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        address_1 = request.POST.get('address_1')
        refdoctor = request.POST.get('refdoctor')
        docid = request.POST.get('docid')
        study=request.POST.get('study')
        price = request.POST.get('price')
        discount = request.POST.get('discount')
        payable = request.POST.get('payable')
        paid = request.POST.get('paid')
        balance = request.POST.get('balance')
        remark = request.POST.get('remark')
        mode = request.POST.get('mode')
        patient=Patient(orgid=org, locate=locate,regby=regby,name=name,age=age, gender=gender,email=email,contact=contact,address_1=address_1,refdoctor=refdoctor,docid=docid)
        service_order=ServiceOrder(pid=patient.id,orgid=org,locate=locate,age=age, name=name, study=study,status="Pending",price=price,discount=discount,payable=payable,
                      paid=paid, balance=balance, remark=remark, mode=mode, badge='badge badge-danger', prescription=prescription)
        try:
            patient.save()
        except Exception as e:
            message=e
            return render(request, 'CreatePatient.html',
                          {'doctors': doctors, 'org': org, 'usr': usr, 'page': 'Add Patient', 'studies': studies, 'message':message})
        if patient:
            try:
                service_order.pid = patient.id
                service_order.save()
                service_order.repid = str(service_order.id)
                service_order.order_id = str(service_order.id)
                service_order.save()
                patient.pid="DR"+str(org.id)+"-"+str(patient.id)
                patient.save()
            except Exception as e:
                patient.delete()
                service_order.delete()
                message = e
                return render(request, 'CreatePatient.html',
                              {'doctors': doctors, 'org': org, 'usr': usr, 'page': 'Add Patient', 'studies': studies,
                               'message': message})
        return redirect('/showpatients')

    return render(request, 'CreatePatient.html', {'doctors': doctors, 'org': org, 'usr': usr, 'page': 'Add Patient', 'studies':studies})


def add_patient_only(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    doctors = Refdoctor.objects.filter(orgid=org)
    studies=Study.objects.filter(orgid=org)
    topcat = Topcat.objects.filter(status = 'Active')
    if request.method == "POST":
        rdate = request.POST.get('rdate')
        locate = request.POST.get('locate')
        regby = usr.name
        name = request.POST.get('name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        address_1 = request.POST.get('address')
        refdoctor = request.POST.get('refdoctor')
        docid = request.POST.get('docid')
        if org.orgtype=="Dental Clinic Branch":
            refdoctor=Users.objects.filter(orgid=org.parent_id).get(department="Admin").name
            docid=Users.objects.filter(orgid=org.parent_id).get(department="Admin").id
        else:
            refdoctor=Users.objects.filter(orgid=org).get(department="Admin").name
            docid=Users.objects.filter(orgid=org).get(department="Admin").id
        if org.orgtype=="Dental Clinic Branch":   
            patient=Patient(orgid=org, locate=locate,regby=regby,name=name,age=age, gender=gender,email=email,contact=contact,address_1=address_1,refdoctor=refdoctor,docid=docid, parent_orgid = org.parent_id)
        else:
            patient=Patient(orgid=org, locate=locate,regby=regby,name=name,age=age, gender=gender,email=email,contact=contact,address_1=address_1,refdoctor=refdoctor,docid=docid, parent_orgid = org.id)
        try:
            patient.save()
        except Exception as e:
            message=e
            return render(request, 'Patient/CreatePatientSecond.html',{'doctors': doctors, 'org': org, 'usr': usr, 'page': 'Add Patient', 'studies': studies, 'message':message, 'topcat': topcat})
        if patient:
            try:
                patient.pid="DR"+str(org.id)+"-"+str(patient.id)
                patient.save()
            except Exception as e:
                patient.delete()
                message = e
                return render(request, 'Patient/CreatePatientSecond.html',
                              {'doctors': doctors, 'org': org, 'usr': usr, 'page': 'Add Patient', 'studies': studies, 'message': message, 'topcat': topcat})
        return redirect('/showpatients')
    if request.method == "POST" and 'prescription' in request.FILES:
        doc = request.FILES
        prescription = doc['prescription']
        rdate = request.POST.get('rdate')
        locate = request.POST.get('locate')
        regby = usr.name
        name = request.POST.get('name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        address_1 = request.POST.get('address')
        refdoctor = request.POST.get('refdoctor')
        docid = request.POST.get('docid')
        if org.orgtype=="Dental Clinic Branch":   
            patient=Patient(orgid=org, locate=locate,regby=regby,name=name,age=age, gender=gender,email=email,contact=contact,address_1=address_1,refdoctor=refdoctor,docid=docid, parent_orgid = org.parent_id)
        else:
            patient=Patient(orgid=org, locate=locate,regby=regby,name=name,age=age, gender=gender,email=email,contact=contact,address_1=address_1,refdoctor=refdoctor,docid=docid, parent_orgid = org.id)
        try:
            patient.save()
        except Exception as e:
            message=e
            return render(request, 'Patient/CreatePatientSecond.html',
                          {'doctors': doctors, 'org': org, 'usr': usr, 'page': 'Add Patient', 'studies': studies, 'message':message, 'topcat': topcat})
        if patient:
            try:
                patient.pid="DR"+str(org.id)+"-"+str(patient.id)
                patient.save()
            except Exception as e:
                patient.delete()
                message = e
                return render(request, 'Patient/CreatePatientSecond.html', {'doctors': doctors, 'org': org, 'usr': usr, 'page': 'Add Patient', 'studies': studies,
                               'message': message, 'topcat': topcat})
        return redirect('/showpatients')

    return render(request, 'Patient/CreatePatientSecond.html', {'doctors': doctors, 'org': org, 'usr': usr, 'page': 'Add Patient', 'studies':studies, 'topcat': topcat})



def search_patient(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    patient = Patient.objects.all()

    if request.method == "POST":
        search = request.POST.get('search')
        patient = Patient.objects.filter(
            Q(name__icontains=search) | Q(rdate__icontains=search) | Q(locate__icontains=search))
        page = "All Patients"
        data = {'usr': usr, 'patient': patient, 'page': page}
        return render(request, "all_patients.html", data)
    page = "All Patients"
    data = {'usr': usr, 'patient': patient, 'page': page, 'org':org, 'topcat':topcat}
    return render(request, "all_patients.html", data)


def showpatients(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    if org.orgtype == "Dental Lab" or org.orgtype == "Dental Lab Branch":
        include = ['Implant Surgical Guide', 'Digital Lab Services']
        topcat = Topcat.objects.filter(topcat__in = include)
    else:
        topcat = Topcat.objects.filter(status = 'Active')
    branch = Organisation.objects.filter(parent_id = org.id)
    if org.orgtype == "Dental Clinic":
        patient = Patient.objects.filter(orgid = org)
    else:
        patient = Patient.objects.filter(Q(orgid=org) | Q(reforgid=org.id))
    usr = Users.objects.get(username=request.user)
    
    if request.method == "POST":
        search = request.POST.get('search')
        users = request.POST.get('users')
        if search:
            if org.orgtype == "Dental Clinic":
                patient = Patient.objects.filter(Q(orgid = org.id)| Q(parent_orgid=org.id)).filter(Q(name__icontains=search) | Q(rdate__icontains=search) | Q(locate__icontains=search))     
            else:
                patient = Patient.objects.filter(Q(orgid=org) | Q(reforgid=org.id)).filter(Q(name__icontains=search) | Q(rdate__icontains=search) | Q(locate__icontains=search))
        if users:
            patient = Patient.objects.filter(Q(orgid=users) | Q(parent_orgid = users))
        page = "All Patients"
        data = {'usr': usr, 'org': org, 'patient': patient, 'topcat': topcat, 'page': page, 'branch': branch}
        return render(request, "AllPatients.html", data)
    page = "All Patients"
    data = {'usr': usr, 'patient': patient, 'page': page, 'org':org, 'topcat':topcat, 'branch': branch}
    return render(request, "AllPatients.html", data)


def showpatients_dent(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)

    patient = Patient.objects.filter(Q(orgid=org) | Q(refpt_orgid=org.id))

    usr = Users.objects.get(username=request.user)

    page = "All Patients"
    data = {'usr': usr, 'patient': patient, 'page': page, 'org':org}
    return render(request, "AllPatients_dent.html", data)


def patient_search(request):
    if request.method == "POST":
        search = request.POST.get('search')
        patient = Patient.objects.filter(
            Q(name__icontains=search) | Q(rdate__icontains=search) | Q(locate__icontains=search))
        return render(request, "AllPatients.html", {'patient': patient})


def allusers(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    users = Users.objects.filter(orgid=org)
    branch = Organisation.objects.filter(parent_id = org.id)
    if org.orgtype == "Dental Lab" or org.orgtype == "Dental Lab Branch":
        include = ['Implant Surgical Guide', 'Digital Lab Services']
        topcat = Topcat.objects.filter(topcat__in = include)
    elif org.orgtype == "Domain Owner":
        exclude = ['Digital Lab Services']
        topcat = Topcat.objects.filter(status = 'Active').exclude(topcat__in = exclude)
    else:
        topcat = Topcat.objects.filter(status = 'Active')
    if request.method == "POST":
        search = request.POST.get('users')
        users = Users.objects.filter(orgid = search)
        return render(request, "AllUsers.html", {'users': users, 'usr': usr, 'org': org, 'page': 'All Users','branch': branch, 'topcat':topcat})
    return render(request, "AllUsers.html", {'users': users, 'usr': usr, 'org': org, 'page': 'All Users','branch': branch, 'topcat':topcat})


def allusers_dent(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    users = Users.objects.filter(orgid=org)
    if org.orgtype == "Dental Lab" or org.orgtype == "Dental Lab Branch":
        include = ['Implant Surgical Guide', 'Digital Lab Services']
        topcat = Topcat.objects.filter(topcat__in = include)
    elif org.orgtype == "Domain Owner":
        exclude = ['Digital Lab Services']
        topcat = Topcat.objects.filter(status = 'Active').exclude(topcat__in = exclude)
    else:
        topcat = Topcat.objects.filter(status = 'Active')
    return render(request, "AllUsers_dent.html", {'users': users, 'usr': usr, 'org': org, 'page': 'All Users', 'topcat':topcat})


def allusers_clinic(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    users = Users.objects.filter(orgid=org)
    if org.orgtype == "Dental Lab" or org.orgtype == "Dental Lab Branch":
        include = ['Implant Surgical Guide', 'Digital Lab Services']
        topcat = Topcat.objects.filter(topcat__in = include)
    elif org.orgtype == "Domain Owner":
        exclude = ['Digital Lab Services']
        topcat = Topcat.objects.filter(status = 'Active').exclude(topcat__in = exclude)
    else:
        topcat = Topcat.objects.filter(status = 'Active')
    return render(request, "AllUsers_clinic.html", {'users': users, 'usr': usr, 'org': org, 'page': 'All Users', 'topcat':topcat})


def showdoctors(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    doctor = Refdoctor.objects.filter(orgid=org)

    return render(request, "AllDoctors.html", {'doctor': doctor, 'usr': usr, 'page': 'All Doctors'})

def allinvites(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    partner = Partners.objects.filter(Q(req_sender=org.id) | Q (req_receiver=org.id))
    if partner:
        for i in partner:
            i.sender=Organisation.objects.get(id=i.req_sender).orgname
            i.receiver=Organisation.objects.get(id=i.req_receiver).orgname
            if str(i.req_receiver) == str(org.id):
                hide=""
            else:
                hide ="hidden"
    else:
        hide=""

    return render(request, "AllPartners.html", {'partner': partner, 'usr': usr, 'org' :org, 'page': 'All Invites', 'hide':hide})


def allexpenses(request):
    expense = Expenses.objects.all()
    return render(request, "allexpenses.html", {'expense': expense})


def doctor_detail(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    doctor = Refdoctor.objects.get(id=id)
    return render(request, "DoctorDetail.html", {'doctor': doctor, 'usr': usr, 'org': org, 'page': 'Doctor Detail'})


def showstudies(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    study = Study.objects.filter(orgid=org)
    return render(request, "AllStudies.html", {'study': study, 'org': org, 'usr': usr, 'page': 'All Studies'})


def showstudies_dent(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    study = Study.objects.filter(orgid=org)
    mycat = ['Radiological Report', 'Image Analysis Report', 'Implant Planning Report', 'Implant Surgical Guide']
    topcat = Topcat.objects.filter(topcat__in = mycat)
    return render(request, "AllStudies_dent.html", {'study': study,'topcat': topcat, 'org': org, 'usr': usr, 'page': 'All Studies'})

def myMail(request):
    usr = Users.objects.get(username=request.user)
    name = usr.name
    details = EmailNotification.objects.get(eventCode = 'DRET-0001')
    connection = mail.get_connection()
    connection.open()
    from1 = 'info.dentread@gmail.com'
    subject = str(details.subject)
    message = "Dear, \n"+ name + '\n' +details.clinicSide + '\nThank You \nDentread'
    message2 = 'A new Organisation Registered to dentread'
    email1 = "souravmahato7643@gmail.com"
    email2 = 'info.dentread@gmail.com'
    mymailExicute = mail.EmailMessage(subject, message, from1, [email1], connection=connection)
    mymailExicute2 = mail.EmailMessage(subject, message2, from1, [email2], connection=connection)
    try:
        mymailExicute.send()
        mymailExicute2.send()
        connection.close()
    except Exception as e:
        message = e
    return HttpResponse("Sent Successfully")

def sendmail(request, id):
    usr=Users.objects.get(username=request.user)
    org=Organisation.objects.get(id=usr.orgid_id)
    rep = ServiceOrder.objects.filter(orgid=org)
    users = Users.objects.filter(orgid=org)

    radio = users.filter(department__icontains="Radiologist")
    service_order=ServiceOrder.objects.get(id=id)
    try:
        service_order.sgn=Users.objects.get(id=service_order.signby).name
        service_order.edu = Users.objects.get(id=service_order.signby).edu
        service_order.spec = Users.objects.get(id=service_order.signby).spec
    except Exception as e:
        service_order.sgn=service_order.signby
    patient = Patient.objects.get(id=service_order.pid)
    doctor = Refdoctor.objects.get(id=patient.docid)
    connection1 = get_connection(email_backend='django.core.mail.backends.smtp.EmailBackend',
                                 host='smtpout.secureserver.net',
                                 port=25,
                                 username='info@dentread.com',
                                 password='Amit@7002',
                                 use_tls=False)
    from1= "info@dentread.com"

    if request.method == "POST":

        data = request.POST.get('data')
        recipient = request.POST.get('recipient')
        recdata = str(recipient)
        if recdata == "Doctor":
            email1 = doctor.email
            email2 = ""
            mailstatus = "Mail sent to Doctor"

        if recdata == "Patient":
            email1 = patient.email
            email2 = ""
            mailstatus = "Mail sent to Patient"

        if recdata == "Doctor & Patient":
            email1 = doctor.email
            email2 = patient.email
            mailstatus = "Mail sent to Doctor & Patient"

        maindata = str(data)
        if maindata == "Report":
            brand='dentread/assets/img/brand/mainlogo.png'
            logo = org.logo
            sgn=service_order.signurl

            repby=Users.objects.get(id=service_order.signby)

            template_path = 'MainPDF.html'
            context = {'patient': patient, 'service_order': service_order,  'sgn': sgn, 'logo': logo, 'brand':brand}
            response = HttpResponse(content_type='application/pdf')
            # response['Content-Disposition'] = 'attachment; filename="service_order.pdf"'

            response['Content-Disposition'] = 'filename="ServiceOrder.pdf"'

            # find the template and render it.
            template = get_template(template_path)
            html = template.render(context)
            result_file = open("ServiceOrder.pdf", "w+b")
            pdf = pisa.CreatePDF(html, dest=result_file, link_callback=link_callback)
            result_file.close()
            subject ="Report of Patient_"+service_order.name

            html_template = 'mailmsg.html'

            html_message = render_to_string(html_template)
            message = strip_tags(html_message)

            try:
                mail = EmailMultiAlternatives(subject, message, from1, [email1, email2,  from1],
                                              connection=connection1)

                with open("ServiceOrder.pdf", "rb") as pdf:
                    mail.attach('ServiceOrder.pdf', pdf.read(), 'application/pdf')
                    mail.send()

                service_order.repsdate = datetime.now()
                service_order.status = "Sent"
                service_order.badge = "badge badge-info"
                service_order.mailstatus = mailstatus
                service_order.save()
                return render(request, 'Dashboard.html',
                              {'usr': usr, 'org': org, 'rep': rep, 'page': 'Reporting Dash', 'radio': radio,
                               'message': 'Mail sent Successfully'})
            except Exception as e:
                return render(request, 'Dashboard.html',
                              {'usr': usr, 'org': org, 'rep': rep, 'page': 'Reporting Dash', 'radio': radio, 'message':e})

        if maindata == "Images":
            service_order = ServiceOrder.objects.get(id=id)

            attachfiles = FeedFile.objects.filter(repid=service_order.id)
            subject =  "Images of Patient_"+patient.name

            html_template = 'mailmsg.html'
            html_message = render_to_string(html_template)
            message = strip_tags(html_message)
            try:
                mail = EmailMultiAlternatives(subject, message, from1, [email1, email2,  from1],
                                              connection=connection1)
                if attachfiles:
                    for f in attachfiles:
                        attachment = str(f.file.file.name)
                        mail.attach_file(attachment)
                mail.send()
                return render(request, 'Dashboard.html',
                              {'usr': usr, 'org': org, 'rep': rep, 'page': 'Reporting Dash', 'radio': radio,
                               'message': 'Mail sent Successfully'})
            except Exception as e:
                return render(request, 'Dashboard.html',
                              {'usr': usr, 'org': org, 'rep': rep, 'page': 'Reporting Dash', 'radio': radio,
                               'message': e})
        if maindata == "Report & Images":
            service_order = ServiceOrder.objects.get(id=id)
            attachfiles = FeedFile.objects.filter(repid=service_order.id)

            logo = org.logo
            sgn = service_order.signurl
            template_path = 'MainPDF.html'
            context = {'patient': patient, 'service_order': service_order, 'sgn': sgn, 'logo': logo}
            response = HttpResponse(content_type='application/pdf')
            # response['Content-Disposition'] = 'attachment; filename="service_order.pdf"'

            response['Content-Disposition'] = 'filename="ServiceOrder.pdf"'

            # find the template and render it.
            template = get_template(template_path)
            html = template.render(context)
            result_file = open("ServiceOrder.pdf", "w+b")
            pdf = pisa.CreatePDF(html, dest=result_file, link_callback=link_callback)
            result_file.close()

            subject = "Report & Images of Patient-" + patient.name

            html_template = 'mailmsg.html'
            html_message = render_to_string(html_template)
            message = strip_tags(html_message)
            try:
                mail = EmailMultiAlternatives(subject, message, from1, [email1, email2, from1],
                                              connection=connection1)
                with open("ServiceOrder.pdf", "rb") as pdf:
                    mail.attach('ServiceOrder.pdf', pdf.read(), 'application/pdf')
                if attachfiles:
                    for f in attachfiles:
                        attachment = str(f.file.file.name)
                        mail.attach_file(attachment)
                mail.send()
                service_order.repsdate = datetime.now()
                service_order.status = "Sent"
                service_order.badge = "badge badge-info"
                service_order.mailstatus = mailstatus
                service_order.save()
                return render(request, 'Dashboard.html',
                              {'usr': usr, 'org': org, 'rep': rep, 'page': 'Reporting Dash', 'radio': radio,
                               'message': 'Mail sent Successfully'})
            except Exception as e:
                return render(request, 'Dashboard.html',
                              {'usr': usr, 'org': org, 'rep': rep, 'page': 'Reporting Dash', 'radio': radio,
                               'message': e})
        else:
            return redirect("/index")

    else:

        return render(request, "sendmail.html",
                      {'service_order': service_order,  'patient': patient,  'usr':usr, 'org':org,
                       'page':'Sendmail'})

def checkCreatePdf(request, id1, id2):
    usr=Users.objects.get(username=request.user)
    org=Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id1)
    line_item = RadiologycalServices.objects.get(id=id2)
    template_path = 'MainPDF_radio.html'
    context = { 'service_order': service_order,'line_item': line_item}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="Report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)
    result_file = open("ServiceOrder.pdf", "w+b")
    pdf = pisa.CreatePDF(html, dest=result_file)
    result_file.close()
    print('pdf', pdf)
    print('result_file', result_file)
    return render(request,'testhtml.html', {'pdf': pdf})

def sendmail_radio(request, id1, id2, id3):
    context={}
    context['id1'] = id1
    context['id2'] = id2
    context['id3'] = id3
    usr=Users.objects.get(username=request.user)
    org=Organisation.objects.get(id=usr.orgid_id)
    users = Users.objects.filter(orgid=org)
    radio = users.filter(department__icontains="Radiologist")
    service_orders = ServiceOrder.objects.filter(orgid=org)
    service_order = ServiceOrder.objects.get(id=id1)
    mycat = topcat.get(id= id2)
    line_item = RadiologycalServices.objects.get(id=id3)
    rep = ServiceOrder.objects.filter(orgid=org)
    patient = Patient.objects.filter(id=service_order.pid)
    files = FeedFile.objects.filter(orgid=org)
    
    connection1 = mail.get_connection()
    connection1.open()
    from1 = 'info.dentread@gmail.com'

    if request.method == "POST":
        data = request.POST.get('data')
        input_email = request.POST.get('email')
        mailstatus = "Mail sent to Doctor"
        maindata = str(data)
        if maindata == "Report":
            attachfiles = FeedFile.objects.filter(repid = service_order.repid).filter(sodrid = line_item.sodrid)
            logo = "static/logo/DentreadlogoV3cloud30May.png"
            template_path = 'MainPDF_radio.html'
            context = { 'service_order': service_order,'line_item': line_item, 'logo': logo}
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'filename="Report.pdf"'

            # find the template and render it.
            template = get_template(template_path)
            html = template.render(context)
            result_file = open("ServiceOrder.pdf", "w+b")
            pdf = pisa.CreatePDF(html, dest=result_file)
            result_file.close()
            subject = "Report of Patient -" + service_order.name

            html_template = 'mailmsg.html'

            html_message = render_to_string(html_template)
            message = strip_tags(html_message)

            try:
                myEmail = EmailMultiAlternatives(subject, message, from1, [input_email, from1], connection=connection1)
                myEmail.send()
                line_item.repsdate = datetime.now()
                line_item.badge = "badge badge-info"
                line_item.mailstatus = mailstatus
                line_item.save()
                messages.success(request, 'Mail Sent Successfully')
                return redirect('/radiological_Details/'+str(service_order.id)+'/'+str(mycat.id))
            except Exception as e:
                context = {'usr': usr, 'org': org, 'rep': rep, 'page': 'Reporting Dash','line_item': line_item,'mycat': mycat, 'radio': radio, 'message':e}
                return redirect('/radiological_Details/'+str(service_order.id)+'/'+str(mycat.id))
        if maindata == "Images":
            attachfiles = FeedFile.objects.filter(repid = service_order.repid).filter(sodrid = line_item.sodrid)
            subject = "Images of Patient- " + service_order.name

            html_template = 'mailmsg.html'
            html_message = render_to_string(html_template)
            message = strip_tags(html_message)
            try:
                myEmail = EmailMultiAlternatives(subject, message, from1, [input_email,  from1],
                                              connection=connection1)
                if attachfiles:
                    for f in attachfiles:
                        attachment = str(f.file.file.name)
                        myEmail.attach_file(attachment)
                myEmail.send()
                messages.success(request, 'Mail Sent Successfully')
                return redirect('/radiological_Details/'+str(service_order.id)+'/'+str(mycat.id))
            except Exception as e:
                return render(request, 'domain_dashboard.html', {'usr': usr, 'org': org, 'rep': rep, 'page': 'Reporting Dash','mycat': mycat, 'radio': radio,'line_item':line_item, 'message': e})
        if maindata == "Report & Images":
            attachfiles = FeedFile.objects.filter(repid = service_order.repid).filter(sodrid = line_item.sodrid)

            logo = "static/logo/DentreadlogoV3cloud30May.png"
            template_path = 'MainPDF_radio.html'
            context = { 'service_order': service_order, 'logo': logo}
            response = HttpResponse(content_type='application/pdf')
            # response['Content-Disposition'] = 'attachment; filename="service_order.pdf"'

            response['Content-Disposition'] = 'filename="Report.pdf"'

            # find the template and render it.
            template = get_template(template_path)
            html = template.render(context)
            result_file = open("Report.pdf", "w+b")
            pdf = pisa.CreatePDF(html, dest=result_file)
            result_file.close()

            subject = "Report & Images of Patient-" + service_order.name

            html_template = 'mailmsg.html'
            html_message = render_to_string(html_template)
            message = strip_tags(html_message)
            try:
                myEmail = EmailMultiAlternatives(subject, message, from1, [input_email,   from1], connection=connection1)
                if attachfiles:
                    for f in attachfiles:
                        attachment = str(f.file.file.name)
                        myEmail.attach_file(attachment)
                myEmail.send()
                line_item.repsdate = datetime.now()
                line_item.badge = "badge badge-info"
                line_item.mailstatus = mailstatus
                line_item.save()
                messages.success(request, 'Mail Sent Successfully')
            except Exception as e:
                return render(request, 'domain_dashboard.html',
                              {'usr': usr, 'line_item':line_item, 'org': org,'mycat': mycat, 'rep': rep, 'page': 'Reporting Dash', 'radio': radio, 'line_item': line_item,
                               'message': e})
        else:
            messages.success(request, 'Your given data is not sufficient to sent a email')
            return redirect('/radiological_Details/'+str(service_order.id)+'/'+str(mycat.id))

    else:
        return render(request, "Admin_Orders/case_details_radio.html",
                      {'service_order': service_order, 'line_item': line_item, 'mycat': mycat,
                       'page':'case_details_radio'})


def sendmail_image(request, id1, id2, id3):
    context={}
    context['id1'] = id1
    context['id2'] = id2
    context['id3'] = id3
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    users = Users.objects.filter(orgid=org)
    radio = users.filter(department__icontains="Radiologist")
    service_orders = ServiceOrder.objects.filter(orgid=org)
    service_order = ServiceOrder.objects.get(id=id1)
    mycat = topcat.get(id= id2)
    line_item = ImageAnalysis.objects.get(id=id3)
    rep = ServiceOrder.objects.filter(orgid=org)
    patient = Patient.objects.filter(id=service_order.pid)

    files = FeedFile.objects.filter(orgid=org)


    connection1 = get_connection(email_backend='django.core.mail.backends.smtp.EmailBackend',
                                 host='smtp.gmail.com',
                                 port=587,
                                 username='info.dentread@gmail.com',
                                 password='vcgnsotfrcxaetwd',
                                 use_tls=False)

    from1="info.dentread@gmail.com"

    if request.method == "POST":

        data = request.POST.get('data')
        input_email = request.POST.get('email')

        mailstatus = "Mail sent to Doctor"



        maindata = str(data)
        if maindata == "Images":

            attachfiles = FeedFile.objects.filter(repid = service_order.repid).filter(sodrid = line_item.sodrid)
            subject = "Images of Patient- " + service_order.name

            html_template = 'mailmsg.html'
            html_message = render_to_string(html_template)
            message = strip_tags(html_message)
            try:
                mail = EmailMultiAlternatives(subject, message, from1, [input_email,  from1],
                                              connection=connection1)
                if attachfiles:
                    for f in attachfiles:
                        attachment = str(f.file.file.name)
                        mail.attach_file(attachment)
                mail.send()
                context = {'usr': usr, 'org': org, 'rep': rep, 'page': 'Reporting Dash', 'radio': radio,'line_item':line_item,'mycat': mycat,
                               'message': 'Mail sent Successfully'}
                return render(request, 'domain_dashboard.html', context)
            except Exception as e:
                return render(request, 'domain_dashboard.html',
                              {'usr': usr, 'org': org, 'rep': rep, 'page': 'Reporting Dash','mycat': mycat, 'radio': radio,'line_item':line_item,
                               'message': e})
        
        else:
            return redirect("/image_Orders/"+str(mycat.id))

    else:

        return render(request, "Admin_Orders/case_details.html",
                      {'service_order': service_order, 'line_item': line_item, 'mycat': mycat,'topcat':topcat, 'page':'case_details'})

def sendmail_planning(request, id1, id2, id3):
    context={}
    context['id1'] = id1
    context['id2'] = id2
    context['id3'] = id3
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    users = Users.objects.filter(orgid=org)
    radio = users.filter(department__icontains="Radiologist")
    service_orders = ServiceOrder.objects.filter(orgid=org)
    service_order = ServiceOrder.objects.get(id=id1)
    mycat = topcat.get(id= id2)
    line_item = ImplantPlanning.objects.get(id=id3)
    rep = ServiceOrder.objects.filter(orgid=org)
    patient = Patient.objects.filter(id=service_order.pid)

    files = FeedFile.objects.filter(orgid=org)


    connection1 = get_connection(email_backend='django.core.mail.backends.smtp.EmailBackend',
                                 host='smtp.gmail.com',
                                 port=587,
                                 username='info.dentread@gmail.com',
                                 password='vcgnsotfrcxaetwd',
                                 use_tls=False)

    from1="info.dentread@gmail.com"

    if request.method == "POST":

        data = request.POST.get('data')
        input_email = request.POST.get('email')
        # email1 = service_order.docemail
        # email2 = usr.email

        mailstatus = "Mail sent to Doctor"



        maindata = str(data)
        if maindata == "Images":

            attachfiles = FeedFile.objects.filter(repid = service_order.repid).filter(sodrid = line_item.sodrid)
            subject = "Images of Patient- " + service_order.name

            html_template = 'mailmsg.html'
            html_message = render_to_string(html_template)
            message = strip_tags(html_message)
            try:
                mail = EmailMultiAlternatives(subject, message, from1, [input_email,  from1],
                                              connection=connection1)
                if attachfiles:
                    for f in attachfiles:
                        attachment = str(f.file.file.name)
                        mail.attach_file(attachment)
                mail.send()
                context = {'usr': usr, 'org': org, 'rep': rep, 'page': 'Reporting Dash', 'radio': radio,'line_item':line_item,'mycat': mycat,
                               'message': 'Mail sent Successfully'}
                return render(request, 'domain_dashboard.html', context)
            except Exception as e:
                return render(request, 'domain_dashboard.html',
                              {'usr': usr, 'org': org, 'rep': rep, 'page': 'Reporting Dash','mycat': mycat, 'radio': radio,'line_item':line_item,
                               'message': e})
        
        else:
            return redirect("/planning_Orders/"+str(mycat.id))

    else:

        return render(request, "Admin_Orders/case_DetailsPlanning.html",
                      {'service_order': service_order, 'line_item': line_item, 'mycat': mycat,'topcat':topcat, 'page':'case_details'})
                       








def sendmail_clinic(request, id1, id2):
    context={}
    context['id1'] = id1
    context['id2'] = id2
    usr=Users.objects.get(username=request.user)
    org=Organisation.objects.get(id=usr.orgid_id)
    users = Users.objects.filter(orgid=org)
    radio = users.filter(department__icontains="Radiologist")
    service_orders=ServiceOrder.objects.filter(orgid=org)
    service_order = ServiceOrder.objects.get(id=id1)
    line_item = RadiologycalServices.objects.get(id=id2)
    rep = ServiceOrder.objects.filter(orgid=org)
    patient = Patient.objects.filter(id=service_order.pid)

    files = FeedFile.objects.filter(orgid=org)


    # connection1 = get_connection(email_backend='django.core.mail.backends.smtp.EmailBackend',
    #                              host='smtpout.secureserver.net',
    #                              port=25,
    #                              username='info@dentread.com',
    #                              password='Amit@7002',
    #                              use_tls=False)
    connection1 = get_connection(email_backend='django.core.mail.backends.smtp.EmailBackend',
                                 host='smtp.gmail.com',
                                 port=587,
                                 username='info.dentread@gmail.com',
                                 password='vcgnsotfrcxaetwd',
                                 use_tls=True
                                 )
    from1="souravmahato7643@gmail.com"

    if request.method == "POST":

        data = request.POST.get('data')
        input_email = request.POST.get('email')

        mailstatus = "Mail Sent"



        maindata = str(data)
        if maindata == "Report":
            attachfiles = FeedFile.objects.filter(repid = service_order.repid).filter(sodrid = line_item.sodrid)
            logo = "static/logo/DentreadlogoV3cloud30May.png"

            template_path = 'MainPDF_radio.html'
            context = { 'service_order': service_order,'org': org, 'line_item': line_item, 'patient':patient,'logo': logo}
            response = HttpResponse(content_type='application/pdf')

            response['Content-Disposition'] = 'filename="Report.pdf"'

            # find the template and render it.
            template = get_template(template_path)
            html = template.render(context)
            result_file = open("Report.pdf", "w+b")
            pdf = pisa.CreatePDF(html, dest=result_file)
            result_file.close()
            subject = "Report of Patient -" + service_order.name

            html_template = 'mailmsg.html'

            html_message = render_to_string(html_template)
            message = strip_tags(html_message)

            try:
                mail = EmailMultiAlternatives(subject, message, from1, [input_email,  from1],
                                              connection=connection1)

                with open("Report.pdf", "rb") as pdf:
                    mail.attach('Report.pdf', pdf.read(), 'application/pdf')
        
                    mail.send()

                line_item.repsdate = datetime.now()
                line_item.badge = "badge badge-info"
                line_item.mailstatus = mailstatus
                line_item.save()
                context = {'usr': usr, 'org': org,'line_item': line_item,'patient':patient,'service_order':service_order,'page': 'Reporting Dash', 'radio': radio,'message': 'Mail sent Successfully'}
                return redirect("/manageReport/"+str(service_order.id))
            except Exception as e:
                context = {'usr': usr, 'org': org,'page': 'Reporting Dash','patient':patient,'line_item': line_item,'radio': radio, 'message':e}
                return redirect("/manageReport/"+str(service_order.id))

        if maindata == "Images":

            attachfiles = FeedFile.objects.filter(repid = service_order.repid).filter(sodrid = line_item.sodrid)
            subject = "Images of Patient- " + service_order.name

            html_template = 'mailmsg.html'
            html_message = render_to_string(html_template)
            message = strip_tags(html_message)
            try:
                mail = EmailMultiAlternatives(subject, message, from1, [input_email,  from1], connection=connection1)
                if attachfiles:
                    for f in attachfiles:
                        attachment = str(f.file.file.name)
                        mail.attach_file(attachment)
                mail.send()
                context = {'usr': usr, 'org': org, 'page': 'Reporting Dash','patient':patient, 'radio': radio,'line_item':line_item,
                               'message': 'Mail sent Successfully'}
                return redirect("/manageReport/"+str(service_order.id))
            except Exception as e:
                redirect("/manageReport/"+str(service_order.id))
        if maindata == "Report & Images":
            attachfiles = FeedFile.objects.filter(repid = service_order.repid).filter(sodrid = line_item.sodrid)

            logo = "static/logo/DMD Logo.png"
            template_path = 'MainPDF_radio.html'
            context = { 'service_order': service_order, 'patient':patient, 'line_item':line_item, 'logo': logo}
            response = HttpResponse(content_type='application/pdf')

            response['Content-Disposition'] = 'filename="Report.pdf"'

            # find the template and render it.
            template = get_template(template_path)
            html = template.render(context)
            result_file = open("Report.pdf", "w+b")
            pdf = pisa.CreatePDF(html, dest=result_file)
            result_file.close()

            subject = "Report & Images of Patient-" + service_order.name

            html_template = 'mailmsg.html'
            html_message = render_to_string(html_template)
            message = strip_tags(html_message)
            try:
                mail = EmailMultiAlternatives(subject, message, from1, [input_email,   from1],
                                              connection=connection1)
                with open("ServiceOrder.pdf", "rb") as pdf:
                    mail.attach('Report.pdf', pdf.read(), 'application/pdf')
                if attachfiles:
                    for f in attachfiles:
                        attachment = str(f.file.file.name)
                        mail.attach_file(attachment)
                mail.send()
                line_item.repsdate = datetime.now()
                line_item.badge = "badge badge-info"
                line_item.mailstatus = mailstatus
                line_item.save()

                return redirect("/manageReport/"+str(service_order.id))
            except Exception as e:

                return redirect("/manageReport/"+str(service_order.id))
        else:
            return redirect("/manageReport/"+str(service_order.id))

    else:

        return redirect("/manageReport/"+str(service_order.id))


def sendmail_ImageService(request, id1, id2):
    context={}
    context['id1'] = id1
    context['id2'] = id2
    usr=Users.objects.get(username=request.user)
    org=Organisation.objects.get(id=usr.orgid_id)
    users = Users.objects.filter(orgid=org)
    radio = users.filter(department__icontains="Radiologist")
    service_orders = ServiceOrder.objects.filter(orgid=org)
    service_order = ServiceOrder.objects.get(id=id1)
    line_item = ImageAnalysis.objects.get(id=id2)
    rep = ServiceOrder.objects.filter(orgid=org)
    patient = Patient.objects.get(id=service_order.pid)

    files = FeedFile.objects.filter(orgid=org)
    connection1 = get_connection(email_backend='django.core.mail.backends.smtp.EmailBackend',
                                 host='smtp.gmail.com',
                                 port=587,
                                 username='info.dentread@gmail.com',
                                 password='vcgnsotfrcxaetwd',
                                 use_tls=False)

    from1="info.dentread@gmail.com"
    if request.method == "POST":
        data = request.POST.get('data')
        input_email = request.POST.get('email')
        mailstatus = "Mail Sent"
        maindata = str(data)
        if maindata == "Images":

            attachfiles = FeedFile.objects.filter(repid = service_order.repid).filter(sodrid = line_item.sodrid)
            subject = "Images of Patient- " + service_order.name

            html_template = 'mailmsg.html'
            html_message = render_to_string(html_template)
            message = strip_tags(html_message)
            try:
                mail = EmailMultiAlternatives(subject, message, from1, [input_email,  from1],
                                              connection=connection1)
                if attachfiles:
                    for f in attachfiles:
                        attachment = str(f.file.file.name)
                        mail.attach_file(attachment)
                mail.send()
                context = {'usr': usr, 'org': org, 'page': 'Reporting Dash','patient':patient, 'radio': radio,'line_item':line_item,
                               'message': 'Mail sent Successfully'}
                service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department, file = f.name, service_name = service_order.refstudy, log = "REPORT SHARE FOR ORDER LINE ITEM", message = 'Report Share For', line_item = line_item.item_id, email = input_email)
                service_log.save()
                return redirect("/manageReportImage/"+str(service_order.id))
            except Exception as e:
                redirect("/manageReportImage/"+str(service_order.id))
        
        else:
            return redirect("/manageReportImage/"+str(service_order.id))

    else:

        return redirect("/manageReportImage/"+str(service_order.id))

def sendmail_ImplantPlanning(request, id1, id2):
    context={}
    context['id1'] = id1
    context['id2'] = id2
    usr=Users.objects.get(username=request.user)
    org=Organisation.objects.get(id=usr.orgid_id)
    users = Users.objects.filter(orgid=org)
    radio = users.filter(department__icontains="Radiologist")
    service_orders = ServiceOrder.objects.filter(orgid=org)
    service_order = ServiceOrder.objects.get(id=id1)
    line_item = ImplantPlanning.objects.get(id=id2)
    rep = ServiceOrder.objects.filter(orgid=org)
    patient = Patient.objects.get(id=service_order.pid)
    # ptnt = Patient.objects.get(id=service_order.pid)

    files = FeedFile.objects.filter(orgid=org)


    connection1 = get_connection(email_backend='django.core.mail.backends.smtp.EmailBackend',
                                 host='smtp.gmail.com',
                                 port=587,
                                 username='info.dentread@gmail.com',
                                 password='vcgnsotfrcxaetwd',
                                 use_tls=False)

    from1="info@dentread.com"

    if request.method == "POST":

        data = request.POST.get('data')
        input_email = request.POST.get('email')

        mailstatus = "Mail Sent"



        maindata = str(data)
        if maindata == "Images":

            attachfiles = FeedFile.objects.filter(repid = service_order.repid).filter(sodrid = line_item.sodrid)
            subject = "Images of Patient- " + service_order.name

            html_template = 'mailmsg.html'
            html_message = render_to_string(html_template)
            message = strip_tags(html_message)
            try:
                mail = EmailMultiAlternatives(subject, message, from1, [input_email,  from1],
                                              connection=connection1)
                if attachfiles:
                    for f in attachfiles:
                        attachment = str(f.file.file.name)
                        mail.attach_file(attachment)
                mail.send()
                service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department, file = f.name, service_name = service_order.refstudy, log = "REPORT SHARE FOR ORDER LINE ITEM", message = 'Report Share For', line_item = line_item.item_id, email = input_email)
                service_log.save()
                context = {'usr': usr, 'org': org, 'page': 'Reporting Dash','patient':patient, 'radio': radio,'line_item':line_item,
                               'message': 'Mail sent Successfully'}
                return redirect("/manageReportPlanning/"+str(service_order.id))
            except Exception as e:
                redirect("/manageReportPlanning/"+str(service_order.id))
        
        else:
            return redirect("/manageReportPlanning/"+str(service_order.id))

    else:

        return redirect("/manageReportPlanning/"+str(service_order.id))
    

def addfiles(request, pk, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=pk)
    radio_order = RadiologycalServices.objects.get(id=id)
    patient = Patient.objects.get(id = service_order.pid)
    if request.method == "POST" and 'file' in request.FILES:
        for f in request.FILES.getlist('file'):
            singlefile = FeedFile(file=f, fileName = f.name, size = f.size, repid=service_order.id, sodrid = radio_order.sodrid, orgid=org)
            singlefile.save()
            service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department, file = f.name, service_name = service_order.refstudy, log = "CREATE REPORT FOR ORDER LINE ITEM ", message = 'Create Report and Upload a File For', line_item = radio_order.item_id)
            service_log.save()
            html = "<html><body>It is now %s.</body></html>"
        return HttpResponse(html)
    data = {'service_order': service_order, 'radio_order': radio_order}
    return render(request, 'Createservice_order_dent.html', data)

def addfilesGuideAgain(request, pk, id1, id2):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=pk)
    image_order = Suricalguide.objects.get(id=id1)
    patient = Patient.objects.get(id = service_order.pid)
    feedFile = FeedFile.objects.get(id=id2)
    if request.method == "POST" and 'file' in request.FILES:
        for f in request.FILES.getlist('file'):
            feedFile.file=f
            feedFile.fileName = f.name
            feedFile.size = f.size
            feedFile.upload= 'Uploaded'
            feedFile.fileStatus = 'Re-uploaded'
            feedFile.fileComment = ''
            feedFile.date = datetime.now()
            feedFile.save()
            image_order.GuideUpload ='Uploaded'
            image_order.GuideUploadDate = datetime.now()
            image_order.save()
            service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department, file = f.name, service_name = service_order.refstudy, log = "SURGICAL GUIDE UPLOADED AGAIN", message = 'Surgical Guide File Upload Again', line_item = image_order.item_id)
            service_log.save()
            notification = Notification(orgid = org, sendTo = service_order.orgid_id, serviceOrderId = service_order.id, sent = True, service = 'Implant Surgical Guide', user = usr.name, event = 'PLAN RE-UPLOADED', details = 'The Lab has Re-uploaded the plan for the order ID: '+ str(service_order.order_id) + ' and the line item ID: '+str(image_order.item_id) + '. Please review the plan.', date = datetime.now(), hyperLink = '/lineOrderDetails/'+str(service_order.id)+'/'+str(image_order.id))
            notification.save()
            html = "<html><body>It is now %s.</body></html>"
            return HttpResponse(html)
    data = {'service_order': service_order, 'image_order': image_order}
    return render(request, 'LabOrder/lineOrderDetailsLab.html', data)



def addfilesGuide(request, pk, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=pk)
    image_order = Suricalguide.objects.get(id=id)
    patient = Patient.objects.get(id = service_order.pid)
    if request.method == "POST" and 'file' in request.FILES:
        for f in request.FILES.getlist('file'):
            singlefile = FeedFile(file=f, fileName= f.name, repid = service_order.id, sodrid = image_order.sodrid, orgid = org, upload= 'Uploaded')
            singlefile.save()
            image_order.GuideUpload ='Uploaded'
            image_order.GuideUploadDate = datetime.now()
            image_order.status = 'Share Plan'
            image_order.save()
            service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department, file = f.name, service_name = service_order.refstudy, log = "CREATE REPORT FOR ORDER LINE ITEM ", message = 'Create Report and Upload a File For', line_item = image_order.item_id)
            service_log.save()
            notification = Notification(orgid = org, sendTo = service_order.orgid_id, serviceOrderId = service_order.id, sent = True, service = 'Implant Surgical Guide', user = usr.name, event = 'PLAN UPLOADED', details = 'The Lab has uploaded the plan for the order ID: '+ str(service_order.order_id) + ' and the line item ID: '+str(image_order.item_id) + '. Please review the plan.', date = datetime.now(), hyperLink = '/lineOrderDetails/'+str(service_order.id)+'/'+str(image_order.id))
            notification.save()
            html = "<html><body>It is now %s.</body></html>"
            return HttpResponse(html)
    data = {'service_order': service_order, 'image_order': image_order}
    return render(request, 'LabOrder/lineOrderDetailsLab.html', data)

def addfilesGuideDigital(request, pk, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=pk)
    image_order = Prosthetic.objects.get(id=id)
    patient = Patient.objects.get(id = service_order.pid)
    designFile = FeedFile.objects.filter(repid = service_order.id).filter(sodrid = image_order.sodrid)
    
    if request.method == "POST" and 'file' in request.FILES:
        for f in request.FILES.getlist('file'):
            singlefile = FeedFile(file=f, fileName= f.name, size = f.size, repid=service_order.id, sodrid = image_order.sodrid, orgid=org, upload= 'Uploaded')
            singlefile.save()
            html = "<html><body>It is now %s.</body></html>"
            image_order.GuideUpload='Uploaded'
            image_order.GuideUploadDate = datetime.now()
            image_order.status = 'Share Design'
            image_order.save()
            if designFile.count() == 1:
                service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department, file = f.name, service_name = service_order.refstudy, log = "UPLOAD DESIGN FOR ORDER LINE ITEM", message = 'Create Report and Upload a File For', line_item = image_order.item_id)
                notification = Notification(orgid = org, sendTo = service_order.orgid_id, serviceOrderId = service_order.id, sent = True, service = 'Digital Lab Services', user = usr.name, event = 'DESIGN UPLOADED', details = 'The Lab has uploaded the design for the order ID: '+ str(service_order.order_id) + ' and the line item ID: '+str(image_order.item_id) + '. Please review the design.', date = datetime.now(), hyperLink = '/lineOrderDetailsDigital/'+str(service_order.id)+'/'+str(image_order.id))
                notification.save()
                service_log.save()
            # Send Mail code
            attachfiles = FeedFile.objects.filter(repid = service_order.id).filter(sodrid = image_order.sodrid)
            refClinicEmail = Organisation.objects.get(id = service_order.orgid_id).email
            connection = mail.get_connection()
            connection.open()
            details = EmailNotification.objects.get(eventCode = 'DRET-0021')
            from1 = 'info.dentread@gmail.com'
            labName = str(org.orgname)
            orderId = str(service_order.order_id)
            firstId = str(service_order.id)
            secId = str(image_order.id)
            subject = details.subject%(labName, orderId)
            message = "Dear User, \n" + details.clinicSide%(labName, orderId, firstId, secId) +"\nThank You \nDentread"
            email1 = refClinicEmail
            mymailExicute = mail.EmailMessage(subject, message, from1, [email1], connection=connection)
            if attachfiles:
                for f in attachfiles:
                    attachment = str(f.file.file.name)
                    mymailExicute.attach_file(attachment)
            try:
                mymailExicute.send()
                connection.close()
            except Exception as e:
                message = e
            return HttpResponse(html)
    data = {'service_order': service_order, 'image_order': image_order}
    return render(request, 'LabOrder/lineOrderDetailsDigitalLab.html', data)


def addfilesGuideDigitalAgain(request, id1, id2):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id1)
    image_order = Prosthetic.objects.get(id=id2)
    patient = Patient.objects.get(id = service_order.pid)
    if request.method == "POST" and 'file' in request.FILES:
        if image_order.designStatus == 'Reject':
            feedFile = FeedFile.objects.filter(sodrid = image_order.id)
            feedFile.delete()
        for f in request.FILES.getlist('file'):
            singlefile = FeedFile(file=f, fileName=f.name, size=f.size, repid=service_order.id, sodrid=image_order.sodrid, orgid=org, upload= 'Uploaded')
            singlefile.save()
            html = "<html><body>It is now %s.</body></html>"
            image_order.designStatus = 'Re-uploaded'
            image_order.designComment = ''
            image_order.GuideUpload='Uploaded'
            image_order.GuideUploadDate = datetime.now()
            image_order.save()
            service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department, file = f.name, service_name = service_order.refstudy, log = "DESIGN UPLOADED AGAIN", message = 'Surgical Guide File Upload Again', line_item = image_order.item_id)
            notification = Notification(orgid = org, sendTo = service_order.orgid_id, serviceOrderId = service_order.id, sent = True, service = 'Digital Lab Services', user = usr.name, event = 'DESIGN RE-UPLOADED', details = 'The Lab has Re-uploaded the design for the order ID: '+ str(service_order.order_id) + ' and the line item ID: '+str(image_order.item_id) + '. Please review the design.', date = datetime.now(), hyperLink = '/lineOrderDetailsDigital/'+str(service_order.id)+'/'+str(image_order.id))
            notification.save()
            service_log.save()
            # Send Mail code
            attachfiles = FeedFile.objects.filter(repid = service_order.id).filter(sodrid = image_order.sodrid)
            refClinicEmail = Organisation.objects.get(id = service_order.orgid_id).email
            connection = mail.get_connection()
            connection.open()
            from1 = 'info.dentread@gmail.com'
            subject = 'Design Re-Shared by the '+str(org.orgname)
            message = "Dear User, \nThe Design has been re-shared by " +str(org.orgname)+ " for the order ID: "+ str(service_order.order_id) + "and the line item ID: " +str(image_order.item_id) + ". To review and approve/reject the design, Visit  https://cloud.dentread.com/lineOrderDetailsDigital/"+str(service_order.id)+'/'+str(image_order.id)+" \nThank You \nDentread"
            email1 = refClinicEmail
            mymailExicute = mail.EmailMessage(subject, message, from1, [email1], connection=connection)
            if attachfiles:
                for f in attachfiles:
                    attachment = str(f.file.file.name)
                    mymailExicute.attach_file(attachment)
            try:
                mymailExicute.send()
                connection.close()
            except Exception as e:
                message = e
            return HttpResponse(html)
    data = {'service_order': service_order, 'image_order': image_order}
    return render(request, 'LabOrder/lineOrderDetailsDigitalLab.html', data)



def addfilesImage(request, pk, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=pk)
    image_order = ImageAnalysis.objects.get(id=id)
    patient = Patient.objects.get(id = service_order.pid)
    if request.method == "POST" and 'file' in request.FILES:
        for f in request.FILES.getlist('file'):
            singlefile = FeedFile(file=f, repid=service_order.id, sodrid = image_order.sodrid, orgid=org)
            singlefile.save()
            service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department, file = f.name, service_name = service_order.refstudy, log = "CREATE REPORT FOR ORDER LINE ITEM ", message = 'Create Report and Upload a File For', line_item = image_order.item_id)
            service_log.save()
            html = "<html><body>It is now %s.</body></html>"
        return HttpResponse(html)
    data = {'service_order': service_order, 'image_order': image_order}
    return render(request, 'Createservice_order_dent.html', data)    

def addfilesPlanning(request, pk, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=pk)
    image_order = ImplantPlanning.objects.get(id=id)
    patient = Patient.objects.get(id=service_order.pid)
    if request.method == "POST" and 'file' in request.FILES:
        for f in request.FILES.getlist('file'):
            singlefile = FeedFile(file=f, repid=service_order.id, sodrid = image_order.sodrid, orgid=org)
            singlefile.save()
            service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department, file = f.name, service_name = service_order.refstudy, log = "CREATE REPORT FOR ORDER LINE ITEM ", message = 'Create Report and Upload a File For', line_item = image_order.item_id)
            service_log.save()
            html = "<html><body>It is now %s.</body></html>"
        return HttpResponse(html)
    data = {'service_order': service_order, 'image_order': image_order}
    return render(request, 'Createservice_order_dent.html', data)


def edit_patient(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    pt=Patient.objects.get(id=id)
    doctors = Refdoctor.objects.filter(orgid=org)
    if request.method == "POST":

        locate = request.POST.get('locate')
        name = request.POST.get('name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        address_1 = request.POST.get('address_1')

        refdoctor = request.POST.get('refdoctor')
        docid = request.POST.get('docid')

        patient = Patient.objects.get(id=id)
        patient.name = name
        patient.gender = gender
        patient.refdoctor = refdoctor
        patient.email = email
        patient.address_1 = address_1
        patient.age = age
        patient.contact = contact
        patient.docid = docid
        patient.locate = locate
        patient.save()

        service_order = ServiceOrder.objects.filter(pid=patient.id)
        for r in service_order:
            r.age = age
            r.name = name
            r.locate = locate
            r.save()

        return redirect('/showpatients')
    else:
        pt = Patient.objects.get(id=id)

        return render(request, "EditPatient.html",
                      {'pt': pt, 'doctors': doctors, 'usr': usr, 'page': 'Edit Patient', 'org':org})

def edit_patient_dent(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    patients = Patient.objects.filter(orgid=org)
    doctor = Refdoctor.objects.filter(orgid=org)
    if request.method == "POST":
        rdate = request.POST.get('rdate')

        locate = request.POST.get('locate')
        regby = request.POST.get('regby')

        name = request.POST.get('name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        address_1 = request.POST.get('address_1')
        address_2 = request.POST.get('address_2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        medih = request.POST.get('medih')
        refdoctor = request.POST.get('refdoctor')
        docid = request.POST.get('docid')

        patient = Patient.objects.get(id=id)
        patient.name = name
        patient.gender = gender
        patient.rdate = rdate
        patient.refdoctor = refdoctor
        patient.email = email
        patient.zip_code = zip_code
        patient.state = state
        patient.city = city
        patient.address_1 = address_1
        patient.address_2 = address_2
        patient.age = age
        patient.contact = contact
        patient.medih = medih
        patient.docid = docid
        patient.regby = regby
        patient.locate = locate
        patient.save()

        invoice = Invoice.objects.filter(pid=patient.pid)
        for i in invoice:
            i.name = name
            i.location = locate
            i.refdoc = refdoctor
            i.save()
        service_order = ServiceOrder.objects.filter(pid=patient.pid)
        for r in service_order:
            r.age = age
            r.name = name
            r.locate = locate
            r.save()

        return redirect('/showpatients_dent')
    else:
        patient = patients.get(id=id)

        return render(request, "EditPatient_dent.html",
                      {'patient': patient, 'doctor': doctor, 'usr': usr, 'page': 'Edit Patient'})


def edit_invoice(request, id):
    service_order = ServiceOrder.objects.get(id=id)
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    studies = Study.objects.filter(orgid=org)
    patient=Patient.objects.get(id=service_order.pid)
    if request.method == "POST" and 'prescription' in request.FILES:
        doc = request.FILES
        prescription = doc['prescription']
        date = request.POST.get('date')
        study = request.POST.get('study')
        price = request.POST.get('price')
        discount = request.POST.get('discount')
        payable = request.POST.get('payable')
        paid = request.POST.get('paid')
        remark=request.POST.get('remark')
        balance = request.POST.get('balance')
        mode = request.POST.get('mode')

        service_order = ServiceOrder.objects.get(id=id)
        service_order.study = study
        service_order.discount = discount
        service_order.paid = paid
        service_order.date = paid
        service_order.mode = mode
        service_order.remark=remark
        service_order.date = date
        service_order.price = price
        service_order.payable = payable
        service_order.balance = balance
        service_order.prescription = prescription
        service_order.save()
        return redirect('/patientdetails/'+service_order.pid)

    if request.method == "POST":
        date = request.POST.get('date')
        study = request.POST.get('study')
        price = request.POST.get('price')
        discount = request.POST.get('discount')
        payable = request.POST.get('payable')
        paid = request.POST.get('paid')
        remark = request.POST.get('remark')
        balance = request.POST.get('balance')
        mode = request.POST.get('mode')

        service_order = ServiceOrder.objects.get(id=id)
        service_order.study = study
        service_order.discount = discount
        service_order.paid = paid
        service_order.date = paid
        service_order.mode = mode
        service_order.remark = remark
        service_order.date = date
        service_order.price = price
        service_order.payable = payable
        service_order.balance = balance
        service_order.save()
        return redirect('/patientdetails/'+service_order.pid)

    return render(request, "EditInvoice.html",
                  { 'studies': studies, 'service_order': service_order,'patient':patient,
                   'page': 'Edit Details', 'usr': usr})

def add_invest(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    studies=Study.objects.filter(orgid=org)
    patient=Patient.objects.get(id=id)
    if request.method == "POST" and 'prescription' in request.FILES:
        doc = request.FILES
        prescription = doc['prescription']
        study = request.POST.get('study')
        price = request.POST.get('price')
        discount = request.POST.get('discount')
        payable = request.POST.get('payable')
        paid = request.POST.get('paid')
        remark=request.POST.get('remark')
        balance = request.POST.get('balance')
        mode = request.POST.get('mode')

        service_order = ServiceOrder(pid=patient.id, orgid=org, locate=patient.locate, age=patient.age, name=patient.name, study=study,
                        status="Pending", price=price, discount=discount, payable=payable,
                        paid=paid, balance=balance, remark=remark, mode=mode, badge='badge badge-danger', prescription=prescription)
        service_order.save()
        return redirect('/patientdetails/'+str(patient.id))

    if request.method == "POST":
        study = request.POST.get('study')
        price = request.POST.get('price')
        discount = request.POST.get('discount')
        payable = request.POST.get('payable')
        paid = request.POST.get('paid')
        remark = request.POST.get('remark')
        balance = request.POST.get('balance')
        mode = request.POST.get('mode')

        service_order = ServiceOrder(pid=patient.id, orgid=org, locate=patient.locate, age=patient.age, name=patient.name,
                        study=study,
                        status="Pending", price=price, discount=discount, payable=payable,
                        paid=paid, balance=balance, remark=remark, mode=mode, badge='badge badge-danger')
        service_order.save()
        return redirect('/patientdetails/' + str(patient.id))
    data={'usr':usr, 'org':org, 'patient':patient, 'studies':studies}

    return render(request, 'add_invest.html', data)




def edit_invoice_dent(request, id):
    invoice = Invoice.objects.get(id=id)

    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    patients = Patient.objects.filter(orgid=org)
    patient = patients.get(pid=invoice.pid)
    study = Study.objects.filter(orgid=org)

    service_orders = ServiceOrder.objects.filter(orgid=org)
    service_order = service_orders.filter(pid=invoice.pid)

    invoices = Invoice.objects.filter(orgid=org)
    allinvoice = invoices.filter(pid=invoice.pid)

    if request.method == "POST" and 'prescription' in request.FILES:
        doc = request.FILES
        prescription = doc['prescription']

        date = request.POST.get('date')
        pid = request.POST.get('pid')
        study = request.POST.get('study')
        studydes = request.POST.get('studydes')
        price = request.POST.get('price')
        discount = request.POST.get('discount')
        payable = request.POST.get('payable')
        paid = request.POST.get('paid')
        balance = request.POST.get('balance')
        mode = request.POST.get('mode')
        sgst = request.POST.get('sgst')
        cgst = request.POST.get('cgst')
        igst = request.POST.get('igst')

        invoice = Invoice.objects.get(id=id)

        invoice.study = study
        invoice.studydes = studydes
        invoice.discount = discount

        invoice.sgst = sgst
        invoice.igst = igst
        invoice.cgst = cgst
        invoice.paid = paid
        invoice.date = paid
        invoice.mode = mode
        invoice.date = date

        invoice.price = price
        invoice.payable = payable
        invoice.balance = balance
        invoice.save()

        service_order = service_orders.get(repid=invoice.invid)
        service_order.date = date
        service_order.prescription = prescription

        service_order.study = studydes

        service_order.save()

        request.session['pid'] = pid

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    if request.method == "POST":
        date = request.POST.get('date')
        pid = request.POST.get('pid')
        study = request.POST.get('study')
        studydes = request.POST.get('studydes')
        price = request.POST.get('price')
        discount = request.POST.get('discount')
        payable = request.POST.get('payable')
        paid = request.POST.get('paid')
        balance = request.POST.get('balance')
        mode = request.POST.get('mode')
        sgst = request.POST.get('sgst')
        cgst = request.POST.get('cgst')
        igst = request.POST.get('igst')

        invoice = Invoice.objects.get(id=id)
        invoice.study = study
        invoice.studydes = studydes
        invoice.discount = discount
        invoice.sgst = sgst
        invoice.igst = igst
        invoice.cgst = cgst
        invoice.paid = paid
        invoice.date = paid
        invoice.mode = mode
        invoice.date = date
        invoice.price = price
        invoice.payable = payable
        invoice.balance = balance
        invoice.save()

        service_order = service_orders.get(repid=invoice.invid)
        service_order.date = date
        service_order.study = studydes
        service_order.save()

        request.session['pid'] = pid

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, "EditInvoice_dent.html",
                  {'invoice': invoice, 'patient': patient, 'study': study, 'service_order': service_order, 'allinvoice': allinvoice,
                   'page': 'Edit Invoice', 'usr': usr, 'org':org})

def edit_doctor(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    doctors = Refdoctor.objects.filter(orgid=org)
    if request.method == "POST":


        name = request.POST.get('name')

        gender = request.POST.get('gender')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        address_1 = request.POST.get('address_1')
        address_2 = request.POST.get('address_2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')

        clinic = request.POST.get('clinic')
        clcontact = request.POST.get('clcontact')

        doctor = Refdoctor.objects.get(id=id)

        doctor.name = name
        doctor.contact = contact

        doctor.gender = gender
        doctor.email = email
        doctor.address_1 = address_1
        doctor.address_2 = address_2
        doctor.city = city
        doctor.state = state
        doctor.zip_code = zip_code

        doctor.clinic = clinic

        doctor.clcontact = clcontact
        doctor.save()

        return redirect('/showdoctors')
    else:
        doctor = doctors.get(id=id)

        return render(request, "EditDoctor.html", {'doctor': doctor, 'org': org, 'usr': usr, 'page': 'Edit Doctor'})


def edit_study(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    topcat=Topcat.objects.filter(status="Active")
    if request.method == "POST":
        topcat = request.POST.get('topcat')

        title = request.POST.get('title')
        maincat = request.POST.get('maincat')
        subcat = request.POST.get('subcat')
        price = request.POST.get('price')
        study = Study.objects.get(id=id)

        study.title = title
        study.topcat = topcat
        study.maincat = maincat
        study.subcat = subcat
        study.price = price
        study.save()

        return redirect('/showstudies')
    else:
        studies = Study.objects.filter(orgid=org)
        study = studies.get(id=id)
        return render(request, "EditStudy.html", {'study': study, 'usr':usr, 'org':org, 'page':'Edit Study', 'topcat':topcat})

def edit_study_dent(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    topcat=Topcat.objects.filter(status="Active")
    if request.method == "POST":
        topcat = request.POST.get('topcat')

        title = request.POST.get('title')
        maincat = request.POST.get('maincat')
        subcat = request.POST.get('subcat')
        price = request.POST.get('price')
        dollarPrice = request.POST.get('dollarPrice')
        study = Study.objects.get(id=id)

        study.title = title
        study.topcat = topcat
        study.maincat = maincat
        study.subcat = subcat
        study.price = price
        study.dollarPrice = dollarPrice
        study.save()

        return redirect('/showstudies_dent')
    else:
        studies = Study.objects.filter(orgid=org)
        study = studies.get(id=id)
        return render(request, "EditStudy_dent.html", {'study': study, 'usr':usr, 'org':org, 'page':'Edit Study', 'topcat':topcat})


def edit_module(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    if request.method == "POST":

        code = request.POST.get('code')
        head = request.POST.get('head')
        pack = request.POST.get('pack')

        module = Modules.objects.get(id=id)

        module.head = head
        module.code = code
        module.pack = pack
        module.save()

        return redirect('/allmodules')
    else:
        module = Modules.objects.get(id=id)
        return render(request, 'editmodule.html', {'usr': usr, 'org': org, 'page': 'All Modules', 'module': module})


def edit_pack(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    if request.method == "POST":
        code = request.POST.get('code')
        head = request.POST.get('head')
        pack = request.POST.get('pack')
        price = request.POST.get('price')
        type = request.POST.get('type')
        applied = request.POST.get('applied')
        packs = Pack.objects.get(id=id)

        packs.head = head
        packs.code = code
        packs.pack = pack
        packs.price = price
        packs.type = type
        packs.applied = applied
        packs.save()

        return redirect('/allpacks')
    else:
        packs = Pack.objects.get(id=id)
        module = Modules.objects.all()
        return render(request, 'editpack.html',
                      {'usr': usr, 'org': org, 'page': 'Add Module', 'module': module, 'packs': packs})


def delete_patient(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    patient = Patient.objects.get(id=id)

    service_orders = ServiceOrder.objects.filter(pid=id)

    for r in service_orders:
        if r.prescription:
            if os.path.isfile(r.prescription.path):
                os.remove(r.prescription.path)
        r.delete()

    patient.delete()

    return redirect('/showpatients')

def delete_patient_dent(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    invoices = Invoice.objects.filter(orgid=org)
    service_orders = ServiceOrder.objects.filter(orgid=org)

    patient = Patient.objects.get(id=id)
    invoice = invoices.filter(pid=patient.pid)
    service_order = service_orders.filter(pid=patient.pid)
    files = FeedFile.objects.filter(pid=patient.pid)

    for r in service_order:
        if r.prescription:
            if os.path.isfile(r.prescription.path):
                os.remove(r.prescription.path)
        r.delete()
    for r in files:
        if r.file:
            if os.path.isfile(r.file.path):
                os.remove(r.file.path)
        r.delete()
    patient.delete()
    invoice.delete()
    return redirect('/showpatients_dent')

def delete_user(request, id):
    user = Users.objects.get(id=id)
    u = User.objects.filter(username=user.username).first()
    if u:
        u.delete()
    user.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def delete_invoice(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    invoices = Invoice.objects.filter(orgid=org)
    service_orders = ServiceOrder.objects.filter(orgid=org)

    invoice = invoices.get(id=id)

    pid = invoice.pid

    invoice.delete()

    service_order = service_orders.get(repid=invoice.invid)
    service_order.prescription.delete(save=True)
    service_order.delete()
    files = FeedFile.objects.filter(repid=service_order.repid)

    for r in files:
        if r.file:
            if os.path.isfile(r.file.path):
                os.remove(r.file.path)
        r.delete()
    request.session['pid'] = pid

    return redirect('/addinvoice')


def delete_doctor(request, id):
    doctor = Refdoctor.objects.get(id=id)

    doctor.delete()
    return redirect('/showdoctors')


def delete_study(request, id):
    study = Study.objects.get(id=id)

    study.delete()
    return redirect('/showstudies')


def delete_module(request, id):
    module = Modules.objects.get(id=id)

    module.delete()
    return redirect('/allmodules')


def delete_pack(request, id):
    pack = Pack.objects.get(id=id)

    pack.delete()
    return redirect('/allpacks')


def file_delete(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    fl = FeedFile.objects.get(id=id)
    files = fl.file.path
    # os.remove(files)
    fl.delete()

    return redirect(request.META.get('HTTP_REFERER'))

def ios_delete(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    fl = IOSFile.objects.get(id=id)
    files = fl.file.path
    os.remove(files)
    fl.delete()
    return redirect(request.META.get('HTTP_REFERER'))

def feedFile_delete(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    fl = FeedFile.objects.get(id=id)
    files = fl.file.path
    os.remove(files)
    fl.delete()
    return redirect(request.META.get('HTTP_REFERER'))

def service_order_delete(request, id):
    re = ServiceOrder.objects.get(id=id)
    re.delete()

    return redirect('/index')


def dcmfile_delete(request, id):
    fl = Dcmfile.objects.get(id=id)
    fl.file.delete(save=True)

    fl.delete()

    return redirect(request.META['HTTP_REFERER'])


def invoice_print(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    if org.logo:
        logo=org.logo.url
    else:
        logo=""
    service_order = ServiceOrder.objects.get(id=id)
    patient=Patient.objects.get(id=service_order.pid)
    if service_order.discount == "0":
        dis = "yes"
    else:
        dis = None
    return render(request, "InvoicePrint.html", {'logo':logo,'invoice': service_order, 'patient': patient, 'centre': org, 'dis': dis})


def service_order_print(request, pk, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    if org.logo:
        logo=org.logo
    else:
        logo=""
    service_order = ServiceOrder.objects.get(id=pk)
    line_item = RadiologycalServices.objects.get(id=id)
    try:
        line_item.sgn=Users.objects.get(id=line_item.signby).name
        line_item.edu=Users.objects.get(id=line_item.signby).edu
        line_item.spec=Users.objects.get(id=line_item.signby).spec
    except Exception as e:
        line_item.sgn=service_order.signby

    patient=Patient.objects.get(id=service_order.pid)
    
    if service_order.discount == "0":
        dis = "yes"
    else:
        dis = None
    return render(request, "patientservice_order.html", {'logo':logo,'service_order': service_order,'line_item': line_item, 'patient': patient, 'centre': org, 'dis': dis})

def viewRadiologyReport(request, pk, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    if org.logo:
        logo=org.logo
    else:
        logo=""
    service_order = ServiceOrder.objects.get(id=pk)
    line_item = RadiologycalServices.objects.get(id=id)
    try:
        line_item.sgn=Users.objects.get(id=line_item.signby).name
        line_item.edu=Users.objects.get(id=line_item.signby).edu
        line_item.spec=Users.objects.get(id=line_item.signby).spec
    except Exception as e:
        line_item.sgn=service_order.signby

    patient=Patient.objects.get(id=service_order.pid)
    
    if service_order.discount == "0":
        dis = "yes"
    else:
        dis = None
    return render(request, "viewRadiologicalReportOrder.html", {'logo':logo,'service_order': service_order,'line_item': line_item, 'patient': patient, 'centre': org, 'dis': dis})


def pdfReport(request, id1, id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    usr=Users.objects.get(username=request.user)
    org=Organisation.objects.get(id=usr.orgid_id)
    if org.logo:
        logo = org.logo
    else:
        logo=""
    service_order = ServiceOrder.objects.get(id=id1)
    line_item = RadiologycalServices.objects.get(id=id2)
    try:
        line_item.sgn=Users.objects.get(id=line_item.signby).name
        line_item.edu=Users.objects.get(id=line_item.signby).edu
        line_item.spec=Users.objects.get(id=line_item.signby).spec
    except Exception as e:
        line_item.sgn=service_order.signby

    patient=Patient.objects.get(id=service_order.pid)
    patient = Patient.objects.get(id=service_order.pid)
    service_log = ServiceLog(orgid = org, patient=patient.name, repid = service_order.id,sodrid = service_order.order_id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy,log = "REPORT DOWNLOADED FOR ORDER LINE ITEM", message ='Report Downloaded', line_item = line_item.item_id)
    service_log.save()
    template_path = 'MainPDF_radio.html'
    context = { 'service_order': service_order,'line_item': line_item, 'patient':patient,'logo': logo, 'centre': org,}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(html, dest=response)
       
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

def download_report_radio(request, pk, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=pk)
    line_item = RadiologycalServices.objects.get(id=id)
    patient = Patient.objects.get(id=service_order.pid)
    service_log = ServiceLog(orgid = org, patient=patient.name, repid = service_order.id,sodrid = service_order.order_id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy,log = "REPORT DOWNLOADED FOR ORDER LINE ITEM", message ='Report Downloaded', line_item = line_item.item_id)
    service_log.save() 
    cfile = FeedFile.objects.filter(repid = service_order.id).filter(sodrid = line_item.id)
    for i in cfile:
        url = i.file.url
        # main = '/' + url
        # return redirect(main)
        return redirect(url)

def download_report_image(request, pk, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=pk)
    line_item = ImageAnalysis.objects.get(id=id)
    patient = Patient.objects.get(id=service_order.pid)
    service_log = ServiceLog(orgid = org, patient=patient.name, repid = service_order.id,sodrid = service_order.order_id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy,log = "REPORT DOWNLOADED FOR ORDER LINE ITEM", message ='Report Downloaded', line_item = line_item.item_id)
    service_log.save()  
    cfile = FeedFile.objects.filter(repid = service_order.id).filter(sodrid = line_item.id)
    for i in cfile:
        url = i.file.url
        # main = '/' + url
        # return redirect(main)
        return redirect(url)

def download_report_planning(request, pk, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=pk)
    line_item = ImplantPlanning.objects.get(id=id)
    patient = Patient.objects.get(id=service_order.pid)
    service_log = ServiceLog(orgid = org, patient=patient.name, repid = service_order.id,sodrid = service_order.order_id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy,log = "REPORT DOWNLOADED FOR ORDER LINE ITEM", message ='Report Downloaded', line_item = line_item.item_id)
    service_log.save()
    cfile = FeedFile.objects.filter(repid = service_order.id).filter(sodrid = line_item.id)
    for i in cfile:
        url = i.file.url
        # main = '/' + url
        # return redirect(main)
        return redirect(url)

def downloadStlLab(request, pk, id1, id2):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=pk)
    line_item = Suricalguide.objects.get(id=id1)
    patient = Patient.objects.get(id=service_order.pid)
    service_log = ServiceLog(orgid = org, patient=patient.name, repid = service_order.id,sodrid = service_order.order_id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy,log = "DOWNLOADED STL FILE FOR ORDER LINE ITEM", message ='Stl File Downloaded', line_item = line_item.item_id)
    service_log.save()
    cfile = IOSFile.objects.get(id=id2)
    url = cfile.file.url
    return redirect(url)


def downloadStlDigitalLab(request, pk, id1, id2):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=pk)
    line_item = Prosthetic.objects.get(id=id1)
    patient = Patient.objects.get(id=service_order.pid)
    iosFile = IOSFile.objects.filter(repid = service_order.id).filter(sodrid = line_item.id).filter(download = 'downloaded')
    cfile = IOSFile.objects.get(id=id2)
    cfile.download = 'Downloaded'
    cfile.save()
    url = cfile.file.url
    # main = '/' + url
    # return redirect(main)
    return redirect(url)


def label_print(request, id):
    service_order = ServiceOrder.objects.get(id=id)
    patient = Patient.objects.get(pid=service_order.pid)

    return render(request, "LabelPrint.html", {'patient': patient, 'service_order': service_order})


def add_user(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    if org.orgtype == "Dental Lab":
        include = ['Implant Surgical Guide', 'Digital Lab Services']
        topcat = Topcat.objects.filter(topcat__in = include)
    else:
        topcat = Topcat.objects.filter(status = 'Active')
    if request.method == "POST" and 'propic' in request.FILES:
        doc = request.FILES
        pic = doc['propic']
        name = request.POST.get('name')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        username = request.POST.get('username')
        password = request.POST.get('password')
        department = request.POST.get('department')
        status = request.POST.get('status')
        newuser = Users(name=name, email=email, contact=contact, username=username, password=password, orgid=org, department=department, propic=pic, status=status)
        checkuser = User.objects.filter(username=username).first()
        if checkuser:
            context = {'message': 'User already exists', 'class': 'danger', 'page': 'Add User', 'org': org}
            return render(request, 'CreateUser.html', context)
        else:
            user = User.objects.create_user(username, email, password)
            user.save()
            newuser.save()
            
            # Send Mail code
            user_name = str(newuser.name)
            clinic_name = str(org.orgname)
            user_id = str(newuser.username)
            user_password = str(newuser.password)
            details = EmailNotification.objects.get(eventCode = 'DRET-0008')
            connection = mail.get_connection()
            connection.open()
            from1 = 'info.dentread@gmail.com'
            subject = details.subject%(user_name, clinic_name)
            message = 'Dear '+str(user_name)+ '\n' + details.clinicSide%(clinic_name, user_id, user_password) + '\nThank You \nDentread'
            email1 = email
            email2 = 'info@dentread.com'
            mymailExicute = mail.EmailMessage(subject, message, from1, [email1], connection=connection)
            try:
                mymailExicute.send()
                connection.close()
            except Exception as e:
                message = e
            eventLog = EventLog(eventCode = 'DRET-0008', event = subject , log = 'A new User Registered to dentread, named : ' + str(org.orgname) + 'Form '+(org.orgname), orgId = org.id, userId = usr.id, time = datetime.now())
            try:
                eventLog.save()
            except Exception as ex:
                eventMessage = ex
            return redirect('/allusers')
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        username = request.POST.get('username')
        password = request.POST.get('password')
        department = request.POST.get('department')
        status = request.POST.get('status')
        newuser = Users(name=name, email=email, contact=contact,
                        username=username, password=password, orgid=org, department=department,
                        status=status)
        checkuser = User.objects.filter(username=username).first()
        if checkuser:
            context = {'message': 'User already exists', 'class': 'danger', 'page': 'Add User', 'org': org}
            return render(request, 'CreateUser.html', context)
        else:
            user = User.objects.create_user(username, email, password)
            user.save()
            newuser.save()
            # Send Mail code
            user_name = str(newuser.name)
            clinic_name = str(org.orgname)
            user_id = str(newuser.username)
            user_password = str(newuser.password)
            details = EmailNotification.objects.get(eventCode = 'DRET-0008')
            connection = mail.get_connection()
            connection.open()
            from1 = 'info.dentread@gmail.com'
            subject = details.subject%(user_name, clinic_name)
            message = message = 'Dear '+str(user_name)+ '\n' + details.clinicSide%(clinic_name, user_id, user_password) + '\nThank You \nDentread'
            email1 = email
            email2 = 'info@dentread.com'
            mymailExicute = mail.EmailMessage(subject, message, from1, [email1], connection=connection)
            try:
                mymailExicute.send()
                connection.close()
            except Exception as e:
                message = e
            eventLog = EventLog(eventCode = 'DRET-0008', event = subject , log = 'A new User Registered to dentread, named : ' + str(org.orgname) + 'Form '+(org.orgname), orgId = org.id, userId = usr.id, time = datetime.now())
            try:
                eventLog.save()
            except Exception as ex:
                eventMessage = ex
            return redirect('/allusers')
    context = { 'page': 'Add User', 'org': org,'topcat': topcat, 'usr':usr}
    return render(request, 'CreateUser.html', context)


def add_user_dent(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    if request.method == "POST" and 'propic' in request.FILES:
        doc = request.FILES
        pic = doc['propic']
        name = request.POST.get('name')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        username = request.POST.get('username')
        password = request.POST.get('password')
        department = request.POST.get('department')
        status = request.POST.get('status')
        newuser = Users(name=name, email=email, contact=contact,
                        username=username, password=password, orgid=org, department=department, propic=pic,
                        status=status)
        checkuser = User.objects.filter(username=username).first()
        if checkuser:
            context = {'message': 'User already exists', 'class': 'danger', 'page': 'Add User', 'org': org}
            return render(request, 'CreateUser_dent.html', context)
        else:
            user = User.objects.create_user(username, email, password)
            user.save()
            newuser.save()
            return redirect('/allusers_dent')
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        username = request.POST.get('username')
        password = request.POST.get('password')
        department = request.POST.get('department')
        status = request.POST.get('status')
        newuser = Users(name=name, email=email, contact=contact,
                        username=username, password=password, orgid=org, department=department,
                        status=status)
        checkuser = User.objects.filter(username=username).first()
        if checkuser:
            context = {'message': 'User already exists', 'class': 'danger', 'page': 'Add User', 'org': org}
            return render(request, 'CreateUser_dent.html', context)
        else:
            user = User.objects.create_user(username, email, password)
            user.save()
            newuser.save()
            return redirect('/allusers_dent')



def edit_user(request, id):
    usr = Users.objects.get(username=request.user)
    edit_user = Users.objects.get(id=id)
    org = Organisation.objects.get(id=usr.orgid_id)
    if request.method == "POST" and 'propic' in request.FILES:
        doc = request.FILES
        pic = doc['propic']
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        department = request.POST.get('department')
        status = request.POST.get('status')

        edit_user.name = name
        edit_user.propic = pic
        edit_user.contact = contact
        edit_user.email = email
        edit_user.department = department
        edit_user.status = status
        edit_user.save()
        return redirect('/mainSettings')
    if request.method == "POST" and 'sign' in request.FILES:
        doc = request.FILES
        sgn = doc['sign']
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        department = request.POST.get('department')
        status = request.POST.get('status')

        edit_user.name = name
        edit_user.sign = sgn
        edit_user.contact = contact
        edit_user.email = email
        edit_user.department = department
        edit_user.status = status
        edit_user.save()
        return redirect('/mainSettings')
    if request.method == "POST":
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        department = request.POST.get('department')
        status = request.POST.get('status')
        edit_user.name = name
        edit_user.contact = contact
        edit_user.email = email
        edit_user.department = department
        edit_user.status = status
        edit_user.save()
        return redirect('/mainSettings')
    return render(request, 'edituser.html', {'usr': usr, 'org': org,'edit_user': edit_user, 'page': 'Edit User'})

def edit_user_dent(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    edit_user=Users.objects.get(id=id)
    if request.method == "POST" and 'propic' in request.FILES:
        doc = request.FILES
        pic = doc['propic']
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        edu = request.POST.get('edu')
        spec = request.POST.get('spec')
        email = request.POST.get('email')
        department = request.POST.get('department')
        status = request.POST.get('status')

        edit_user.name = name
        edit_user.propic = pic
        edit_user.contact = contact
        edit_user.email = email
        edit_user.department = department
        edit_user.status = status
        edit_user.edu=edu
        edit_user.spec=spec
        edit_user.save()
        return redirect('/allusers_dent')
    if request.method == "POST" and 'sign' in request.FILES:
        doc = request.FILES
        sgn = doc['sign']
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        department = request.POST.get('department')
        status = request.POST.get('status')
        edu = request.POST.get('edu')
        spec = request.POST.get('spec')

        edit_user.name = name
        edit_user.sign = sgn
        edit_user.contact = contact
        edit_user.email = email
        edit_user.department = department
        edit_user.status = status
        edit_user.edu = edu
        edit_user.spec = spec
        edit_user.save()
        return redirect('/allusers_dent')
    if request.method == "POST":
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        department = request.POST.get('department')
        status = request.POST.get('status')
        edu = request.POST.get('edu')
        spec = request.POST.get('spec')
        edit_user.name = name
        edit_user.contact = contact
        edit_user.email = email
        edit_user.department = department
        edit_user.status = status
        edit_user.edu = edu
        edit_user.spec = spec
        edit_user.save()
        return redirect('/allusers_dent')
    return render(request, 'edituser_dent.html', {'usr': usr, 'org': org, 'page': 'Edit User', 'edit_user':edit_user})


def edit_user_clinic(request, id):
    usr = Users.objects.get(id=id)
    org = Organisation.objects.get(id=usr.orgid_id)
    if request.method == "POST" and 'propic' in request.FILES:
        doc = request.FILES
        pic = doc['propic']
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        department = request.POST.get('department')
        status = request.POST.get('status')

        usr.name = name
        usr.propic = pic
        usr.contact = contact
        usr.email = email
        usr.department = department
        usr.status = status
        usr.save()
        return redirect('/allusers_clinic')

    if request.method == "POST":
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        department = request.POST.get('department')
        status = request.POST.get('status')
        usr.name = name
        usr.contact = contact
        usr.email = email
        usr.department = department
        usr.status = status
        usr.save()
        return redirect('/allusers_clinic')
    return render(request, 'edituser_clinic.html', {'usr': usr, 'org': org, 'page': 'Edit User'})


def add_org(request):
    if request.method == "POST":
        orgname = request.POST.get('orgname')
        orgtype = request.POST.get('orgtype')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        gstin = request.POST.get('gstin')
        address = request.POST.get('address')
        status = request.POST.get('status')

        neworg = Organisation(orgname=orgname, orgtype=orgtype, email=email, contact=contact, address=address,
                              status=status, gstin=gstin)
        neworg.save()
        return redirect('/allorg')


def saveitem(request):
    if request.method == "POST":
        item = request.POST.get('item')
        price = request.POST.get('price')
        detail = request.POST.get('detail')

        newitem = Items(item=item, price=price, detail=detail)
        newitem.save()
        return redirect('/allitems')


def allitems(request):
    item = Items.objects.all
    return render(request, "Allitems.html", {'item': item})


def allorg(request):
    org = Organisation.objects.all
    return render(request, "Allorganisation.html", {'org': org})


def delete_org(request, id):
    org = Organisation.objects.get(id=id)
    org.delete()
    return redirect('/all_imaging')


def delete_expense(request, id):
    exp = Expenses.objects.get(id=id)
    exp.delete()
    return redirect('/allexpenses')


def delete_item(request, id):
    item = Items.objects.get(id=id)
    item.delete()
    return redirect('/allitems')


def delete_inv_item(request, id):
    invt = Inventory.objects.get(id=id)
    pid = invt.pid
    invt.delete()
    request.session['pid'] = pid

    return redirect('/add_inv_item')


def assign(request, id):
    if request.method == "POST":
        repby = request.POST.get('repby')

        service_order = ServiceOrder.objects.get(id=id)
        service_order.repby = repby
        service_order.save()

        return redirect('/todo')


def main_pdf(request, id):
    service_order = ServiceOrder.objects.get(id=id)
    invoice = Invoice.objects.get(invid=service_order.repid)
    patient = Patient.objects.get(pid=service_order.pid)
    sgn = Sign.objects.get(sid=service_order.signurl)
    if str(invoice.location) == "DMDGZB" or str(invoice.location) == "DMDGGN" or str(
            invoice.location) == "DMDDEL" or str(invoice.location) == "DMDNDA":
        logo = "static/logo/DMD Logo.png"
    else:
        logo = ""
    return render(request, "MainPDF.html",
                  {'service_order': service_order, 'invoice': invoice, 'patient': patient, 'sgn': sgn, 'logo': logo})


def cstlogin(request):
    return render(request, "cstlogin.html")


def cstloginhandle(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        usr = Users.objects.get(username=username)
        usrtype = str(usr.usertype)
        user = authenticate(username=username, password=password)
        if usrtype == "External":
            if user is not None:
                login(request, user)
                messages.success(request, "You have Successfully logged in")
                return redirect('/cstdashboard')
            else:
                messages.error(request, "Invalid Credentials")
                return redirect('/cstlogin')
        else:
            return redirect('/cstlogin')
    return render(request, "cstlogin.html")


def cstdashboard(request):
    user = request.user
    usr = Users.objects.get(username=user)
    refpt = Refpt.objects.filter(centre=usr.organisation)
    usr = Users.objects.get(username=request.user)
    refrgpt = Patient.objects.filter(locate=usr.organisation)
    service_order = ServiceOrder.objects.filter(locate=usr.organisation)

    return render(request, "cstdashboard.html", {'refpt': refpt, 'refrgpt': refrgpt, 'service_order': service_order})


def allcstpatient(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    refpt = Refpt.objects.filter(orgid=org)
    dcmfiles = Dcmfile.objects.filter(orgid=org)
    cfiles = ClinicFile.objects.filter(orgid=org)
    for i in refpt:
        i.reforg = Organisation.objects.get(id=i.ref_centre).orgname
        stud = Study.objects.get(id=i.study)
        i.stud = stud.title + "-" + stud.maincat
        dcm = dcmfiles.filter(refptid=i.refptid).first()
        if dcm:
            i.dcm = dcm
        else:
            print("no")
        i.files = cfiles.filter(refptid=i.refptid)

    return render(request, 'allcstpatient.html', {'refpt': refpt, 'page': 'All Patients', 'org': org, 'usr':usr})


def referpt(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    centers = Organisation.objects.filter(orgtype="Domain Owner")
    dentorg = Organisation.objects.get(orgtype="Domain Owner")
    studies = Study.objects.filter(orgid=dentorg)
    if request.method == "POST":
        name = request.POST.get('name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        study = request.POST.get('study')
        ref_centre = request.POST.get('ref_centre')
        remark = request.POST.get('remark')
        hardcopy = request.POST.get('hardcopy')

        regby = request.user
        checkid = Refpt.objects.filter(orgid=usr.orgid_id)

        try:
            max_refptid = checkid.aggregate(Max('refptid'))['refptid__max']
            new_refptid = checkid.get(refptid=max_refptid)
            myid = new_refptid.refptid + 1
        except Refpt.DoesNotExist:
            myid = 1

        reftpt = Refpt(regby=regby, contact=contact, name=name, age=age, refptid=myid,
                       gender=gender, orgid=org, email=email, remark=remark, study=study, ref_centre=ref_centre,
                       status='Under Review', btnstatus='btn btn-primary btn-sm disabled', hardcopy=hardcopy)
        reftpt.save()

        request.session['refptid'] = myid

        return redirect('/uploaddcm')

    return render(request, "referpt.html", {'usr': usr, 'org': org, 'centers': centers, 'studies': studies})

def addreferpt_radio(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)

    studyowner=Organisation.objects.get(orgtype='Domain Owner')
    studies = Study.objects.filter(orgid=studyowner)

    centres=Organisation.objects.filter(regby_email=usr.email)
    if request.method == "POST" and 'prescription' in request.FILES:
        doc = request.FILES
        prescription = doc['prescription']
        name = request.POST.get('name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        study = request.POST.get('study')
        price = request.POST.get('price')
        ref_centre = request.POST.get('ref_centre')
        remark = request.POST.get('remark')
        if str(price)=="":
            price =0

        regby = request.user
        checkid = ServiceOrder.objects.filter(orgid=usr.orgid_id)

        try:
            max_pid = checkid.aggregate(Max('pid'))['pid__max']
            new_pid = checkid.get(pid=max_pid)
            myid = new_pid.pid + 1
        except ServiceOrder.DoesNotExist:
            myid = 1
        docemail = Organisation.objects.get(id=ref_centre).email

        service_order = ServiceOrder(reg_by=regby, pt_contact=contact, name=name, age=age, refptid=myid, pid=myid, repid=myid,
                        locate=org.orgname,
                        gender=gender, study=study, orgid=org, pt_email=email, remark=remark, status="Pending",
                        docemail=docemail, refpt_orgid=ref_centre, price=price, repby=usr.name, prescription=prescription)

        service_order.save()

        request.session['repid'] = myid
        return redirect('/uploaddcm_radio')
    if request.method == "POST":
        name = request.POST.get('name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        study = request.POST.get('study')
        price = request.POST.get('price')
        ref_centre = request.POST.get('ref_centre')
        remark = request.POST.get('remark')
        if str(price)=="":
            price =0
        regby = request.user
        checkid = ServiceOrder.objects.filter(orgid=usr.orgid_id)

        try:
            max_pid = checkid.aggregate(Max('pid'))['pid__max']
            new_pid = checkid.get(pid=max_pid)
            myid = new_pid.pid + 1
        except ServiceOrder.DoesNotExist:
            myid = 1
        docemail=Organisation.objects.get(id=ref_centre).email

        service_order = ServiceOrder(reg_by=regby, pt_contact=contact, name=name, age=age, refptid=myid, pid=myid, repid=myid,locate=org.orgname,
                       gender=gender, study=study, orgid=org, pt_email=email, remark=remark,   status="Pending",
                        docemail=docemail, refpt_orgid=ref_centre, price=price, repby=usr.name)

        service_order.save()

        request.session['repid'] = myid

        return redirect('/uploaddcm_radio')

    return render(request, "addreferpt_radio.html", {'usr': usr, 'org': org, 'studies': studies, 'page':'Dashboard', 'centres':centres})

def allrefpt(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    refpt = Refpt.objects.filter(ref_centre=org.id)
    for i in refpt:
        stud = Study.objects.get(id=i.study)
        i.stud = stud.title + "-" + stud.maincat
        dcm = Dcmfile.objects.filter(orgid=i.orgid)

    return render(request, "All_ref-patients.html", {'refpt': refpt})


def allrefpt_dent(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    refpt = Refpt.objects.filter(ref_centre=org.id)

    for i in refpt:
        cfiles = ClinicFile.objects.filter(orgid=i.orgid)
        stud = Study.objects.get(id=i.study)
        i.stud = stud.title + "-" + stud.maincat
        i.files = cfiles.filter(refptid=i.refptid)
        dcm = Dcmfile.objects.filter(orgid=i.orgid)
        i.refclinic=Organisation.objects.get(id=i.orgid_id).orgname

    return render(request, "All_ref-patients_dent.html", {'refpt': refpt, 'usr': usr, 'org': org})


def reftopt(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    refpts = Refpt.objects.filter(ref_centre=org.id)

    refpt = refpts.get(id=id)

    rdate = date.today()
    regby = request.user
    contact = refpt.contact
    name = refpt.name
    age = refpt.age
    gender = refpt.gender
    email = refpt.email
    reffor = refpt.study
    remark = refpt.remark

    refclinic = Organisation.objects.get(id=refpt.orgid_id)
    refdoc = Users.objects.filter(orgid=refclinic).get(usertype="Admin")

    checkid = Patient.objects.filter(orgid=usr.orgid_id)
    try:

        max_pid = checkid.aggregate(Max('pid'))['pid__max']
        new_pid = checkid.get(pid=max_pid)
        myid = new_pid.pid + 1
    except Patient.DoesNotExist:
        myid = 1

    if refpt.status != "Registered":
        patient = Patient(rdate=rdate, pid=myid, locate=org.orgname, regby=regby, contact=contact, name=name, age=age,
                          gender=gender, email=email,
                          refdoctor=refdoc.name, docid=refdoc.id, reffor=reffor, refptid=refpt.refptid,
                          refpt_orgid=refpt.orgid_id, orgid=org)
        patient.save()
        refpt.status = "Registered"
        refpt.pid = myid
        refpt.save()

        pid = myid
        request.session['pid'] = pid

        return redirect('/addinvoice')
    else:
        return render(request, 'exist.html')




def reftopt_dent(request, id):
    connection1 = get_connection(email_backend='django.core.mail.backends.smtp.EmailBackend',
                                 host='smtpout.secureserver.net',
                                 port=25,
                                 username='info@dentread.com',
                                 password='Amit@7002',
                                 use_tls=False)
    subject = "Patient registered successfully"
    from1 = "info@dentread.com"
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_orders = ServiceOrder.objects.filter(orgid=org)
    patients = Patient.objects.filter(orgid=org)
    invoices = Invoice.objects.filter(orgid=org)

    study = Study.objects.filter(orgid=org)

    refpt = Refpt.objects.filter(ref_centre=org.id)

    for i in refpt:
        cfiles = ClinicFile.objects.filter(orgid=i.orgid)
        stud = Study.objects.get(id=i.study)
        i.stud = stud.title + "-" + stud.maincat
        i.files = cfiles.filter(refptid=i.refptid)
        dcm = Dcmfile.objects.filter(orgid=i.orgid)

    refp = refpt.get(id=id)
    if refp.pid =="":
        stud = study.get(id=refp.study)

        rdate = date.today()
        regby = request.user
        contact = refp.contact
        name = refp.name
        age = refp.age
        gender = refp.gender
        email = refp.email
        reffor = refp.study
        remark = refp.remark

        refclinic = Organisation.objects.get(id=refp.orgid_id)
        refdoc = Users.objects.filter(orgid=refclinic).get(usertype="Admin")

        checkid = Patient.objects.filter(orgid=usr.orgid_id)
        try:

            max_pid = checkid.aggregate(Max('pid'))['pid__max']
            new_pid = checkid.get(pid=max_pid)
            myid = new_pid.pid + 1
        except Patient.DoesNotExist:
            myid = 1

        if refp.status != "Registered":
            patient = Patient(rdate=rdate, pid=myid, locate=org.orgname, regby=regby, contact=contact, name=name, age=age,
                              gender=gender, email=email,
                              refdoctor=refdoc.name, docid=refdoc.id, reffor=reffor, refptid=refp.refptid,
                              refpt_orgid=refp.orgid_id, orgid=org)
            patient.save()

            try:
                max_invid = invoices.aggregate(Max('invid'))['invid__max']
                new_invid = invoices.get(invid=max_invid)
                myinvid = new_invid.invid + 1
            except Invoice.DoesNotExist:
                myinvid = 1

            price = stud.price
            paid = 0
            balance = price - paid
            discount = 0
            payable = price - discount
            studydes = stud.title + stud.maincat
            location = org.orgname
            invoice = Invoice(date=rdate, pid=patient.pid, location=location, name=name,
                              mode="Invoiced", balance=balance, study=stud.title,
                              paid=paid, payable=payable, discount=discount, price=price, studydes=studydes,
                              invid=myinvid, refdoc=refdoc.name, refclinic=refclinic.orgname, orgid=org,
                              refpt_orgid=refp.orgid_id, refptid=refp.refptid)

            service_order = ServiceOrder(date=rdate, pid=patient.pid, remark=remark, signurl="1", study=studydes, docemail=refdoc.email,
                            portal="No", age=age, locate=location, repid=myinvid,
                            status='Pending', name=name, badge='badge badge-danger', orgid=org,
                            refpt_orgid=refp.orgid_id, refptid=refp.refptid)

            try:
                invoice.save()
            except Exception as e:
                patient.delete()
                message = e
                return render(request, "All_ref-patients_dent.html", {'refpt': refpt, 'message': message})

            try:
                service_order.save()
                refp.status = "Registered"
                refp.pid = myid
                refp.save()
                email1 = refdoc.email
                message = "Dear User,\nPatient " + refp.name + " registered successfully fo r" + studydes + "\nWe will notify you once Report will complete.\nThank You \nDentread"
                mail = EmailMessage(subject, message, from1, [email1], connection=connection1)
                mail.send()
            except Exception as e:
                patient.delete()
                invoice.delete()
                service_order.delete()
                refp.status = "Under Review"
                refp.pid=""
                refp.save()
                message = e

                return render(request, "All_ref-patients_dent.html", {'refpt': refpt, 'message': message})

            return redirect('/showpatients_dent')
        else:

            return render(request, 'exist_dent.html', {'usr':usr,'org':org})
    else:
        patient=Patient.objects.filter(orgid_id=refp.orgid_id).get(pid=refp.pid)
        service_order=ServiceOrder.objects.filter(orgid_id=refp.orgid_id).filter(refpt_orgid=org.id).get(pid=refp.pid)
        stud=Study.objects.get(id=refp.study)
        patient.refptid=refp.refptid
        patient.refpt_orgid=org.id
        service_order.refptid=refp.refptid
        service_order.save()
        patient.save()
        dent_invoice=Dent_Invoice(pid=patient.pid, orgid=org, name=patient.name,study=refp.study, price=stud.price, invid=service_order.repid,refptid=refp.refptid, refpt_orgid=refp.orgid_id )
        dent_invoice.save()
        refp.status="Registered"
        refp.save()

        return redirect('/allrefpt_dent')


def refptservice_order(request, id):
    refpt = Refpt.objects.get(id=id)
    usr = Users.objects.get(username=refpt.regby)
    service_order = ServiceOrder.objects.get(pid=refpt.pid)
    file = FeedFile.objects.filter(repid=service_order.repid)

    dcm = Dcmfile.objects.filter(Q(refptid=refpt.refptid) | Q(repid=service_order.repid))
    return render(request, "refptservice_order.html", {'service_order': service_order, 'file': file, 'dcm': dcm})


def cstptservice_order(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    ref_patients = Refpt.objects.filter(orgid=org)
    ref_patient = ref_patients.get(pid=id)
    patients = Patient.objects.filter(refpt_orgid=ref_patient.orgid_id)
    patient = patients.filter(pid=ref_patient.pid).get(refptid=ref_patient.refptid)
    service_orders = ServiceOrder.objects.filter(orgid_id=patient.orgid_id)
    service_order = service_orders.get(pid=patient.pid)

    file = FeedFile.objects.filter(orgid_id=patient.orgid_id).filter(repid=service_order.repid)

    dcm = Dcmfile.objects.filter(orgid_id=patient.orgid_id)

    return render(request, "refptservice_order.html", {'service_order': service_order, 'file': file, 'dcm': dcm})


def uploaddcm(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    refpts = Refpt.objects.filter(orgid=org)
    myid = request.session['refptid']
    refpt = refpts.get(refptid=myid)
    return render(request, "uploaddcm.html", {'refpt': refpt})

def uploaddcm_radio(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_orders = ServiceOrder.objects.filter(orgid=org)
    myid = request.session['repid']
    service_order = service_orders.get(repid=myid)
    return render(request, "uploaddcm_radio.html", {'service_order': service_order})



def adddcmfiles(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    refpts = Refpt.objects.filter(orgid=org)
    refpt = refpts.get(refptid=id)
    if request.method == "POST" and 'file' in request.FILES:

        for f in request.FILES.getlist('file'):
            singlefile = Dcmfile(file=f, refptid=id, orgid=org)
            size  = f.size
            singlefile.save()

            refpt.upload = "uploaded"
            refpt.save()

            html = "<html><body>It is now %s.</body></html>"
            return HttpResponse(html)
    return render(request, "uploaddcm.html", {'refpt': refpt})

def adddcmfiles_radio(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_orders = ServiceOrder.objects.filter(orgid=org)
    service_order = service_orders.get(repid=id)
    if request.method == "POST" and 'file' in request.FILES:

        for f in request.FILES.getlist('file'):
            singlefile = Dcmfile(file=f, repid=id, orgid=org)
            singlefile.save()

            html = "<html><body>It is now %s.</body></html>"
            return HttpResponse(html)
    return render(request, "uploaddcm_radio.html", {'service_order': service_order})

def addclinicfiles(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    refpts = Refpt.objects.filter(orgid=org)
    refpt = refpts.get(refptid=id)
    if request.method == "POST" and 'file' in request.FILES:

        for f in request.FILES.getlist('file'):
            sfile = ClinicFile(file=f, refptid=id, orgid=org)
            sfile.save()

            html = "<html><body>It is now %s.</body></html>"
            return HttpResponse(html)
    return render(request, "uploaddcm.html", {'refpt': refpt})



def adddcmpt(request, id):
    if request.method == "POST" and 'file' in request.FILES:
        repid = id

        for f in request.FILES.getlist('file'):
            singlefile = Dcmfile(file=f, repid=repid)
            singlefile.save()

            html = "<html><body>It is now %s.</body></html>"
            return HttpResponse(html)


def files(request, id):
    usr=Users.objects.get(username=request.user)
    org=Organisation.objects.get(id=usr.orgid_id)

    feedfile = FeedFile.objects.filter(repid=id)
    for i in feedfile:
        url = i.file.url
        main = '/' + url
        return redirect(main)
    return redirect(main)

def filess(request, id):
    usr=Users.objects.get(username=request.user)
    org=Organisation.objects.get(id=usr.orgid_id)

    feedfile = IOSFile.objects.filter(repid=id)
    for i in feedfile:
        url = i.file.url
        main = '/' + url
        return redirect(main)
    return redirect(main)



def download(request, id):
    usr=Users.objects.get(username=request.user)
    org=Organisation.objects.get(id=usr.orgid_id)
    refpt=Refpt.objects.filter(Q(ref_centre=org.id) | Q(orgid=org)).get(id=id)
    dcmfile = Dcmfile.objects.filter(orgid=refpt.orgid).filter(refptid=refpt.refptid)
    for i in dcmfile:
        url = i.file.url
        main = '/' + url
        return redirect(main)
    return redirect(main)

def download_imaging(request, id):
    usr=Users.objects.get(username=request.user)
    org=Organisation.objects.get(id=usr.orgid_id)
    service_order=ServiceOrder.objects.get(id=id)
    dcmfile = Dcmfile.objects.filter(repid=service_order.id)
    for i in dcmfile:
        url = i.file.url
        main = '/' + url
        return redirect(main)
    return redirect(main)


def download_file(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    clinicfiles = ClinicFile.objects.filter(orgid=org)
    cfile = clinicfiles.filter(refptid=id)
    for i in cfile:
        url = i.file.url
        main = '/' + url
        return redirect(main)
    return redirect(main)


def download_file_radio(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    dcmfiles = Dcmfile.objects.filter(orgid=org)
    cfile = dcmfiles.filter(repid=id)
    for i in cfile:
        url = i.file.url
        main = '/' + url
        return redirect(main)
    return redirect(main)


def download_file_dent(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    refpt = Refpt.objects.filter(ref_centre=org.id).get(refptid=id)
    cfile = ClinicFile.objects.filter(orgid=refpt.orgid_id).filter(refptid=refpt.refptid)
    for i in cfile:
        url = i.file.url
        main = '/' + url
        return redirect(main)
    return redirect(main)


def allinvoices(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    if request.method == "POST":
        fd = request.POST.get('fromdate')
        td = request.POST.get('todate')

        inv = Invoice.objects.filter(orgid=org)

        invoice = inv.filter(date__range=[fd, td])

        amount = invoice.aggregate(Sum('payable'))
        total = amount['payable__sum']

        cs = invoice.filter(mode="Cash")
        csh = cs.aggregate(Sum('payable'))
        cash = csh['payable__sum']

        cd = invoice.filter(mode="Card")
        crd = cd.aggregate(Sum('payable'))
        card = crd['payable__sum']

        on = invoice.filter(mode="Online")
        onl = on.aggregate(Sum('payable'))
        online = onl['payable__sum']

        return render(request, 'allinvoices.html',
                      {'invoice': invoice, 'total': total, 'cash': cash, 'card': card, 'online': online, 'org': org,
                       'usr': usr})

    else:

        return render(request, 'allinvoices.html', {'org': org, 'usr': usr, 'page': 'All Invoices'})

def self(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        contact= request.POST.get('contact')
        age = request.POST.get('age')
        gender=request.POST.get('gender')

        self=Self(name=name, age=age, contact=contact, gender=gender, email=email)
        self.save()
        token=self.id
        name=self.name

        return render(request, 'selfreg.html', {'usr':usr, 'org':org, 'token':token, 'name':name})

    return render(request, 'self.html', {'usr':usr, 'org':org})








def invoices(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_orders = ServiceOrder.objects.filter(orgid=org)


    today=datetime.today()
    check1="checked"
    td_service_orders=ServiceOrder.objects.filter(orgid=org).filter(date=today)
    amount = td_service_orders.aggregate(Sum('ref_price'))
    total = amount['ref_price__sum']
    if total is None:
        total=0

    cs = td_service_orders.filter(mode="Cash").aggregate(Sum('ref_price'))
    cash = cs['ref_price__sum']
    if cash is None:
        cash=0

    cd = td_service_orders.filter(mode="Card").aggregate(Sum('ref_price'))
    card = cd['ref_price__sum']
    if card is None:
        card=0

    on = td_service_orders.filter(mode="Online").aggregate(Sum('ref_price'))
    online = on['ref_price__sum']
    if online is None:
        online=0

    if request.method == "POST":
        check1=""
        check2=""
        check3=""
        dat=request.POST.get('dat')
        fd = request.POST.get('fromdate')
        td = request.POST.get('todate')
        if dat=="Today":
            data=today
            nd_service_orders = service_orders.filter(Q(date=data))
            check1="checked"
        if dat=="Yesterday":
            data=today + timedelta(days=-1)
            nd_service_orders = service_orders.filter(Q(date=data))
            check2 = "checked"
        if dat=="Thisweek":
            data=today - timedelta(weeks=1)
            nd_service_orders = service_orders.filter(Q(date__gte=data))
            check3 = "checked"
        if dat=="":
            data=None

        if data is None:
            nd_service_orders = service_orders.filter(date__range=[fd, td])


        amount = nd_service_orders.aggregate(Sum('payable'))
        total = amount['payable__sum']
        if total is None:
            total = 0

        cs = nd_service_orders.filter(mode="Cash").aggregate(Sum('payable'))
        cash = cs['payable__sum']
        if cash is None:
            cash = 0

        cd = nd_service_orders.filter(mode="Card").aggregate(Sum('payable'))
        card = cd['payable__sum']
        if card is None:
            card = 0

        on = nd_service_orders.filter(mode="Online").aggregate(Sum('payable'))
        online = on['payable__sum']
        if online is None:
            online = 0


        return render(request, 'cstbusinesss.html', {'service_orders': nd_service_orders, 'total':total, 'cash':cash, 'card':card, 'online':online, 'usr':usr, 'org':org,
                                                     'check1':check1, 'check2':check2, 'check3':check3, 'page':'My Invoices'})

    return render(request, 'cstbusinesss.html', {'service_orders': td_service_orders, 'total':total, 'cash':cash, 'card':card, 'online':online, 'usr':usr, 'org':org,
                                                 'check1':check1, 'page':'My Invoices'})

def ref_invoices(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_orders = ServiceOrder.objects.filter(orgid=org).exclude(reforgid__isnull=True)
    today=datetime.today()
    check1="checked"
    td_service_orders=service_orders.filter(orgid=org).filter(date=today)
    for i in td_service_orders:
        i.referto=Organisation.objects.get(id=i.reforgid).orgname

    amount = td_service_orders.aggregate(Sum('ref_price'))
    total = amount['ref_price__sum']
    if total is None:
        total=0

    cs = td_service_orders.filter(mode="Cash").aggregate(Sum('payable'))
    cash = cs['payable__sum']
    if cash is None:
        cash=0

    cd = td_service_orders.filter(mode="Card").aggregate(Sum('payable'))
    card = cd['payable__sum']
    if card is None:
        card=0

    on = td_service_orders.filter(mode="Online").aggregate(Sum('payable'))
    online = on['payable__sum']
    if online is None:
        online=0

    if request.method == "POST":
        check1=""
        check2=""
        check3=""
        dat=request.POST.get('dat')
        fd = request.POST.get('fromdate')
        td = request.POST.get('todate')
        if dat=="Today":
            data=today
            check1="checked"
            nd_service_orders = service_orders.filter(Q(date=data))
        if dat=="Yesterday":
            data=today - timedelta(days=1)
            check2 = "checked"
            nd_service_orders = service_orders.filter(Q(date=data))
        if dat=="Thisweek":
            data=today - timedelta(weeks=1)
            nd_service_orders = service_orders.filter(Q(date__gte=data))
            check3 = "checked"
        if dat=="":
            data=None

        if data is None:

            nd_service_orders = service_orders.filter(date__range=[fd, td])


        amount = nd_service_orders.aggregate(Sum('ref_price'))
        total = amount['ref_price__sum']
        if total is None:
            total = 0

        cs = nd_service_orders.filter(mode="Cash").aggregate(Sum('payable'))
        cash = cs['payable__sum']
        if cash is None:
            cash = 0

        cd = nd_service_orders.filter(mode="Card").aggregate(Sum('payable'))
        card = cd['payable__sum']
        if card is None:
            card = 0

        on = nd_service_orders.filter(mode="Online").aggregate(Sum('payable'))
        online = on['payable__sum']
        if online is None:
            online = 0

        for i in nd_service_orders:
            i.referto = Organisation.objects.get(id=i.reforgid).orgname


        return render(request, 'ref_cstbusinesss.html', {'service_orders': nd_service_orders, 'total':total, 'cash':cash, 'card':card, 'online':online, 'usr':usr, 'org':org,
                                                     'check1':check1, 'check2':check2, 'check3':check3, 'page':'Referral Invoices'})

    return render(request, 'ref_cstbusinesss.html', {'service_orders': td_service_orders, 'total':total, 'cash':cash, 'card':card, 'online':online, 'usr':usr, 'org':org,
                                                 'check1':check1, 'page':'Referral Invoices'})





def cstbusiness_dent(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    orgtype = ['Dental Clinic', 'Dental Clinic Branch']
    organisation = Organisation.objects.filter(orgtype__in = orgtype)
    today = datetime.today()
    include = ['Radiological Report', 'Image Analysis Report', 'Implant Planning Report', 'Implant Surgical Guide']
    topcat = Topcat.objects.filter(topcat__in = include)
    service_order = ServiceOrder.objects.filter(reforgid = org.id).filter(status = 'Completed')
    if request.method == "POST":
        request_org = request.POST.get('requestOrg')
        year = request.POST.get('year')
        month = request.POST.get('month')
        fd = request.POST.get('fromdate')
        td = request.POST.get('todate')
        radiology_discount = request.POST.get('radio_discount')
        imageAnalysis_discount = request.POST.get('image_discount')
        implantPlanning_discount = request.POST.get('implant_discount')
        radio_discount = ''
        if radiology_discount:
            radio_discount = int(radiology_discount)
        image_discount = ''
        if imageAnalysis_discount: 
            image_discount = int(imageAnalysis_discount)
        implant_discount = ''
        if implantPlanning_discount:
            implant_discount = int(implantPlanning_discount)

        orderbyorg = service_order.filter(orgid = request_org)
        if fd and td:
            service_orders = orderbyorg.filter(date__range=[fd, td])
        else:
            service_orders = orderbyorg.filter(date__year = year).filter(date__month = month)
                
        ids = []
        for j in service_orders:
            ids.append(j.id)
        
        radioData = RadiologycalServices.objects.filter(repid__in = ids)
        if radio_discount:
            for r_discount in radioData:
                r_discount.discount = radio_discount
                r_discount.netAmount = (r_discount.price - (r_discount.price*(radio_discount)/100))
                r_discount.save()
        else:
            for radio in radioData:
                radio.discount = 0
                radio.netAmount = radio.price
                radio.save()
        for rdo in radioData:
            rdo.orgid_id = Organisation.objects.get(id = rdo.orgid_id).orgname
            rdo.name = rdo.name.title()
        
        imageData = ImageAnalysis.objects.filter(repid__in = ids)
        if image_discount:
            for i_discount in imageData:
                i_discount.discount = image_discount
                i_discount.netAmount = (i_discount.price - (i_discount.price*image_discount/100))
                i_discount.save()
        else:
            for image in imageData:
                image.discount = 0
                image.netAmount = image.price
                image.save()
        for img in imageData:
            img.orgid_id = Organisation.objects.get(id = img.orgid_id).orgname
            img.name = img.name.title()
        
        implantData = ImplantPlanning.objects.filter(repid__in = ids)
        if implant_discount:
            for im_discount in implantData:
                im_discount.discount = implant_discount
                im_discount.netAmount = (im_discount.price - (im_discount.price*implant_discount/100))
                im_discount.save()
        else:
            for implant in implantData:
                implant.discount = 0
                implant.netAmount = image.price
                implant.save()
        for imp in implantData:
            imp.orgid_id = Organisation.objects.get(id = imp.orgid_id).orgname
            imp.name = imp.name.title()

        radio_price = radioData.aggregate(Sum('price'))
        radio_price_discount = radioData.aggregate(Sum('discount'))
        radio_total = radio_price['price__sum']
        radio_total_discount = radio_price_discount['discount__sum']
        if radio_total is None:
            radio_total = 0
        if radio_total_discount is None:
            radio_total_discount = 0
        
        image_price = imageData.aggregate(Sum('price'))
        image_price_discount = radioData.aggregate(Sum('discount'))
        image_total = image_price['price__sum']
        image_total_discount = image_price_discount['discount__sum']
        if image_total is None:
            image_total = 0
        if image_total_discount is None:
            image_total_discount = 0
        
        implant_price = implantData.aggregate(Sum('price'))
        implant_price_discount = radioData.aggregate(Sum('discount'))
        implant_total_discount = implant_price_discount['discount__sum']
        implant_total = implant_price['price__sum']
        if implant_total is None:
            implant_total = 0
        if implant_total_discount is None:
            implant_total_discount = 0
        
        total_price = (radio_total + image_total + implant_total)
        total_discount = (radio_total_discount + image_total_discount + implant_total_discount)
        total_payble = (total_price - total_discount)
        for i in service_orders:
            i.reforgid = Organisation.objects.get(id = i.reforgid).orgname
        context = {'radioData': radioData, 'imageData': imageData, 'total_payble': total_payble, 'total_price': total_price, 'total_discount': total_discount, 'request_org': request_org, 'year': year, 'month': month, 'fd': fd, 'td': td, 'implantData': implantData, 'service_order': service_orders,'organisation': organisation,'topcat': topcat, 'usr': usr, 'org': org, 'radiology_discount': radiology_discount, 'imageAnalysis_discount': imageAnalysis_discount, 'implantPlanning_discount': implantPlanning_discount, 'page': 'Referral Invoices'}           
        return render(request, 'orginvoices_all.html', context)
    context = {'organisation': organisation,'usr': usr, 'org': org, 'topcat': topcat, 'page': 'Referral Invoices'}              
    return render(request, 'orginvoices_all.html', context)

def invoiceForClinic(request):
    if request.method == "POST":
        usr = Users.objects.get(username=request.user)
        organisation = Organisation.objects.get(id=usr.orgid_id)
        service_order = ServiceOrder.objects.filter(reforgid = organisation.id).filter(status = 'Completed')
        request_org = request.POST.get('organisationId-edit')
        year = request.POST.get('year-edit')
        month = request.POST.get('month-edit')
        fd = request.POST.get('dateFrom-edit')
        td = request.POST.get('dateTo-edit')
        radiology_discount = request.POST.get('discountRadio-edit')
        imageAnalysis_discount = request.POST.get('discountImage-edit')
        implantPlanning_discount = request.POST.get('discountImplant-edit')
        org = Organisation.objects.get(id = request_org)
        radio_discount = ''
        if radiology_discount:
            radio_discount = int(radiology_discount)
        image_discount = ''
        if imageAnalysis_discount: 
            image_discount = int(imageAnalysis_discount)
        implant_discount = ''
        if implantPlanning_discount:
            implant_discount = int(implantPlanning_discount)
        orderbyorg = service_order.filter(orgid = request_org)
        if fd and td:
            service_orders = orderbyorg.filter(date__range=[fd, td])
        else:
            service_orders = orderbyorg.filter(date__year = year).filter(date__month = month)
                
        ids = []
        for j in service_orders:
            ids.append(j.id)
        
        radioData = RadiologycalServices.objects.filter(repid__in = ids)
        if radio_discount:
            for r_discount in radioData:
                r_discount.discount = radio_discount
                r_discount.netAmount = (r_discount.price - (r_discount.price*(radio_discount)/100))
                r_discount.save()
        else:
            for radio in radioData:
                radio.discount = 0
                radio.netAmount = radio.price
                radio.save()
        for rdo in radioData:
            rdo.orgid_id = Organisation.objects.get(id = rdo.orgid_id).orgname
            rdo.name = rdo.name.title()
        
        imageData = ImageAnalysis.objects.filter(repid__in = ids)
        if image_discount:
            for i_discount in imageData:
                i_discount.discount = image_discount
                i_discount.netAmount = (i_discount.price - (i_discount.price*image_discount/100))
                i_discount.save()
        else:
            for image in imageData:
                image.discount = 0
                image.netAmount = image.price
                image.save()
        for img in imageData:
            img.orgid_id = Organisation.objects.get(id = img.orgid_id).orgname
            img.name = img.name.title()
        
        implantData = ImplantPlanning.objects.filter(repid__in = ids)
        if implant_discount:
            for im_discount in implantData:
                im_discount.discount = implant_discount
                im_discount.netAmount = (im_discount.price - (im_discount.price*implant_discount/100))
                im_discount.save()
        else:
            for implant in implantData:
                implant.discount = 0
                implant.netAmount = image.price
                implant.save()
        for imp in implantData:
            imp.orgid_id = Organisation.objects.get(id = imp.orgid_id).orgname
            imp.name = imp.name.title()

        radio_price = radioData.aggregate(Sum('price'))
        radio_price_discount = radioData.aggregate(Sum('discount'))
        radioNetAmount =  radioData.aggregate(Sum('netAmount'))
        rdoNetAmt = radioNetAmount['netAmount__sum']
        radio_total = radio_price['price__sum']
        radio_total_discount = radio_price_discount['discount__sum']
        if radio_total is None:
            radio_total = 0
        if radio_total_discount is None:
            radio_total_discount = 0
        if rdoNetAmt is None:
            rdoNetAmt = 0
        
        image_price = imageData.aggregate(Sum('price'))
        image_price_discount = radioData.aggregate(Sum('discount'))
        image_total = image_price['price__sum']
        image_total_discount = image_price_discount['discount__sum']
        imageNetAmount =  imageData.aggregate(Sum('netAmount'))
        imgNetAmt = imageNetAmount['netAmount__sum']
        if image_total is None:
            image_total = 0
        if image_total_discount is None:
            image_total_discount = 0
        if imgNetAmt is None:
            imgNetAmt = 0
        
        implant_price = implantData.aggregate(Sum('price'))
        implant_price_discount = radioData.aggregate(Sum('discount'))
        implant_total_discount = implant_price_discount['discount__sum']
        implant_total = implant_price['price__sum']
        impNetAmount =  implantData.aggregate(Sum('netAmount'))
        impNetAmt = impNetAmount['netAmount__sum']
        
        if implant_total is None:
            implant_total = 0
        if implant_total_discount is None:
            implant_total_discount = 0
        if impNetAmt is None:
            impNetAmt = 0
        radio_tax_amount = 0
        image_tax_amount = 0
        implant_tax_amount = (implant_total - (implant_total-(implant_total*18/100)))
        total_tax = radio_tax_amount + image_tax_amount + implant_tax_amount
        total_price = (radio_total + image_total + implant_total) 
        taxable_amount = (total_price + total_tax)
        totalNetAmount = (rdoNetAmt + imgNetAmt + impNetAmt)
        total_discount = (total_price - totalNetAmount)
        total_payble = (total_price - total_discount)     
        for i in service_orders:
            i.reforgid = Organisation.objects.get(id = i.reforgid).orgname 
        now = datetime.now()
        today = datetime.now().strftime("%d/%m/%Y")
        due_date = (now + timedelta(days=7)).strftime("%d/%m/%Y")
        context = {'due_date': due_date, 'today': today, 'total_payble': total_payble, 'taxable_amount': taxable_amount, 'total_tax': total_tax, 'radioData': radioData, 'imageData': imageData, 'total_price': total_price, 'total_discount': total_discount, 'request_org': request_org, 'year': year, 'month': month, 'fd': fd, 'td': td, 'implantData': implantData, 'service_order': service_orders,'organisation': organisation,'topcat': topcat, 'org': org, 'radiology_discount': radiology_discount, 'imageAnalysis_discount': imageAnalysis_discount, 'implantPlanning_discount': implantPlanning_discount, 'page': 'Referral Invoices'}           
        return render(request, 'ManagePayment/adminInvoice.html', context)
    
    return render(request, 'ManagePayment/adminInvoice.html')

def editPrice(request, id, price, service):
    usr = usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service = service
    priceLast = ''
    if service == 'Overall':
        serviceOrder = ServiceOrder.objects.get(id = id)
        serviceOrder.ref_price = price
        serviceOrder.save()
        priceLast = serviceOrder.ref_price
    elif service == 'Radio':
        radio = RadiologycalServices.objects.get(id = id)
        radio.price = price
        radio.save()
        priceLast = radio.price
    elif service =='Image':
        image = ImageAnalysis.objects.get(id = id)
        image.price = price
        image.save()
        priceLast = image.price
    else:
        implant = ImplantPlanning.objects.get(id = id)
        implant.price = price
        implant.save()
        priceLast = implant.price
    return JsonResponse({"price": priceLast})

def EditPriceForImplant(request, id):
    usr = usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    implant = ImplantPlanning.objects.get(id = id)
    if request.method == "POST":
        price = request.POST.get('price')
        implant.price = price
        implant.save()
        return JsonResponse({"price": implant.price})
                   

def dent_invoices(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    patients = Patient.objects.filter(Q(orgid=org) | Q(refpt_orgid=org.id))
    invoice = Dent_Invoice.objects.filter(refpt_orgid=org.id)
    for i in invoice:
        i.stud=Study.objects.get(id=i.study).title
        i.refer=Organisation.objects.get(id=i.refpt_orgid).orgname
    amount = invoice.aggregate(Sum('price'))
    total = amount['price__sum']

    if request.method == "POST":
        fd = request.POST.get('fromdate')
        td = request.POST.get('todate')

        invoice = invoice.filter(date__range=[fd, td])


        amount = invoice.aggregate(Sum('price'))
        total = amount['price__sum']

        return render(request, 'dent_invoices.html', {'invoice': invoice, 'total':total, 'usr':usr, 'org':org})

    return render(request, 'dent_invoices.html', {'invoice': invoice, 'total':total,'usr':usr, 'org':org})

def cstbusiness_radio(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)

    service_order = ServiceOrder.objects.filter(orgid=org)
    for i in service_order:
        i.referby = Organisation.objects.get(id=i.refpt_orgid).orgname
    amount = service_order.aggregate(Sum('price'))
    total = amount['price__sum']

    if request.method == "POST":
        fd = request.POST.get('fromdate')
        td = request.POST.get('todate')

        service_order = service_order.filter(date__range=[fd, td])
        for i in service_order:
            i.referby=Organisation.objects.get(id=i.refpt_orgid).orgname

        amount = service_order.aggregate(Sum('price'))
        total = amount['price__sum']

        return render(request, 'cstbusinesss_radio.html', {'service_order': service_order, 'total':total})

    return render(request, 'cstbusinesss_radio.html', {'service_order': service_order, 'total':total})


def todo(request):
    pdservice_order = ServiceOrder.objects.filter(repby='')
    radio = Users.objects.filter(department="Radiologist")

    return render(request, 'todo.html', {'pdservice_order': pdservice_order, 'radio': radio})


def getservice_order(request):
    if request.method == "POST":
        pid = request.POST.get('ptid')
        fname = request.POST.get('fname')
        patient = Patient.objects.filter(pid__iexact=pid).first()
        if patient:
            service_order = ServiceOrder.objects.filter(pid=patient.pid).filter(status="Sent")
            file = FeedFile.objects.filter(pid=patient.pid)
            try:
                sgn = Sign.objects.get(sid=1)
            except Sign.DoesNotExist:
                sgn = ''
        else:
            return HttpResponse("Patient ID not found")

        return render(request, 'myservice_order.html', {'service_order': service_order, 'file': file, 'sgn': sgn})

    return render(request, 'getservice_order.html')


from django.core import serializers
from django.http import JsonResponse


def plsummary1(request):
    crmonth = datetime.today().month
    cryear = datetime.today().year
    checkexp = Expenses.objects.filter(month__year__gte=cryear, month__year__lte=cryear)
    dmdexpgzb = checkexp.filter(locate="DMDGZB")
    sale = dmdexpgzb.annotate(months=ExtractMonth('month')).values('months').annotate(
        amount_rent=Sum('amount', filter=Q(expensetype="Rent"))) \
        .annotate(amount_salary=Sum('amount', filter=Q(expensetype="Salary"))) \
        .annotate(amount=Sum('amount')).values('months', 'amount', 'amount_rent', 'amount_salary')
    gzbexpamount_rent = []
    gzbexpamount_salary = []

    for s in sale:
        gzbexpamount_rent.append(s['amount_rent'])
        gzbexpamount_salary.append(s['amount_salary'])
    return HttpResponse(gzbexpamount_salary)

def plsummary(request):
    crmonth = datetime.today().month
    cryear = datetime.today().year
    last_12month = datetime.today() - timedelta(days=365)

    expense = Expenses.objects.filter(month__year__gte=cryear,
                                      month__month__gte=crmonth,
                                      month__year__lte=cryear,
                                      month__month__lte=crmonth)

    try:
        exp = expense.get(expensetype="gzbsale")
        dmdgzb = Invoice.objects.filter(location="DMDGZB")
        gzbcrmonth = dmdgzb.filter(date__year__gte=cryear,
                                   date__month__gte=crmonth,
                                   date__year__lte=cryear,
                                   date__month__lte=crmonth)

        gzbsale = gzbcrmonth.aggregate(Sum('payable'))
        gzbsaleamount = gzbsale['payable__sum']
        exp.saleamount = gzbsaleamount
        exp.save()

    except Expenses.DoesNotExist:
        dmdgzb = Invoice.objects.filter(location="DMDGZB")
        gzbcrmonth = dmdgzb.filter(date__year__gte=cryear,
                                   date__month__gte=crmonth,
                                   date__year__lte=cryear,
                                   date__month__lte=crmonth)

        gzbsale = gzbcrmonth.aggregate(Sum('payable'))
        gzbsaleamount = gzbsale['payable__sum']
        exp = Expenses(month=datetime.today(), expensetype='gzbsale', remark='none', amount=0, saleamount=gzbsaleamount,
                       locate='DMDGZB')
        exp.save()

    try:
        exp = expense.get(expensetype="ggnsale")
        dmdggn = Invoice.objects.filter(location="DMDGGN")
        ggncrmonth = dmdggn.filter(date__year__gte=cryear,
                                   date__month__gte=crmonth,
                                   date__year__lte=cryear,
                                   date__month__lte=crmonth)

        ggnsale = ggncrmonth.aggregate(Sum('payable'))
        ggnsaleamount = ggnsale['payable__sum']
        exp.saleamount = ggnsaleamount
        exp.save()

    except Expenses.DoesNotExist:
        dmdggn = Invoice.objects.filter(location="DMDGGN")
        ggncrmonth = dmdggn.filter(date__year__gte=cryear,
                                   date__month__gte=crmonth,
                                   date__year__lte=cryear,
                                   date__month__lte=crmonth)

        ggnsale = ggncrmonth.aggregate(Sum('payable'))
        ggnsaleamount = ggnsale['payable__sum']
        exp = Expenses(month=datetime.today(), expensetype='ggnsale', remark='none', amount=0, saleamount=ggnsaleamount,
                       locate='DMDGGN')
        exp.save()

    try:
        exp = expense.get(expensetype="delsale")
        dmddel = Invoice.objects.filter(location="DMDDEL")
        delcrmonth = dmddel.filter(date__year__gte=cryear,
                                   date__month__gte=crmonth,
                                   date__year__lte=cryear,
                                   date__month__lte=crmonth)

        delsale = delcrmonth.aggregate(Sum('payable'))
        delsaleamount = delsale['payable__sum']
        exp.saleamount = delsaleamount
        exp.save()

    except Expenses.DoesNotExist:
        dmddel = Invoice.objects.filter(location="DMDDEL")
        delcrmonth = dmddel.filter(date__year__gte=cryear,
                                   date__month__gte=crmonth,
                                   date__year__lte=cryear,
                                   date__month__lte=crmonth)

        delsale = delcrmonth.aggregate(Sum('payable'))
        delsaleamount = delsale['payable__sum']
        exp = Expenses(month=datetime.today(), expensetype='delsale', remark='none', amount=0, saleamount=delsaleamount,
                       locate='DMDDEL')
        exp.save()
    try:
        exp = expense.get(expensetype="ndasale")
        dmdnda = Invoice.objects.filter(location="DMDNDA")
        ndacrmonth = dmdnda.filter(date__year__gte=cryear,
                                   date__month__gte=crmonth,
                                   date__year__lte=cryear,
                                   date__month__lte=crmonth)

        ndasale = ndacrmonth.aggregate(Sum('payable'))
        ndasaleamount = ndasale['payable__sum']
        exp.saleamount = ndasaleamount
        exp.save()

    except Expenses.DoesNotExist:
        dmdnda = Invoice.objects.filter(location="DMDNDA")
        ndacrmonth = dmdnda.filter(date__year__gte=cryear,
                                   date__month__gte=crmonth,
                                   date__year__lte=cryear,
                                   date__month__lte=crmonth)

        ndasale = ndacrmonth.aggregate(Sum('payable'))
        ndasaleamount = ndasale['payable__sum']
        exp = Expenses(month=datetime.today(), expensetype='ndasale', remark='none', amount=0, saleamount=ndasaleamount,
                       locate='DMDNDA')
        exp.save()

    checkexp = Expenses.objects.filter(month__gte=last_12month)

    allsaleamount = []
    allsalemonth = []
    allprofit = []
    allsaleyear = []
    allexpamount = []
    allsale = checkexp.annotate(months=ExtractMonth('month'), year=ExtractYear('month')).values('months', 'year') \
        .annotate(saleamount=Sum('saleamount')) \
        .annotate(amount=Sum('amount')) \
        .annotate(profit=(F('saleamount') - F('amount'))) \
        .values('months', 'year', 'saleamount', 'amount', 'profit')
    for s in allsale:
        allsalemonth.append(calendar.month_name[s['months']])
        allsaleyear.append(s['year'])
        allsaleamount.append(s['saleamount'])
        allexpamount.append(s['amount'])
        allprofit.append(s['profit'])
    year = [str(x) for x in allsaleyear]
    res = [i + '-' + j for i, j in zip(allsalemonth, year)]
    allsaleamount = [0 if v is None else v for v in allsaleamount]
    allexpamount = [0 if v is None else v for v in allexpamount]
    allprofit = [0 if v is None else v for v in allprofit]

    gzbexpamount = []
    gzbexpamount_rent = []
    gzbexpamount_profees = []
    gzbexpamount_salary = []
    gzbexpamount_electric = []
    gzbexpamount_mbulid = []
    gzbexpamount_mequip = []
    gzbexpamount_dep = []
    gzbexpamount_print = []
    gzbexpamount_film = []
    gzbexpamount_other = []

    gzbsaleamount = []
    gzbprofit = []

    gzbexpmonth = []
    gzbexpyear = []
    gzbmonthyear = []

    dmdexpgzb = checkexp.filter(locate="DMDGZB")
    expgzb = dmdexpgzb.annotate(months=ExtractMonth('month'), year=ExtractYear('month')).values('months', 'year') \
        .annotate(saleamount=Sum('saleamount', filter=Q(expensetype="gzbsale"))) \
        .annotate(amount_rent=Sum('amount', filter=Q(expensetype="Rent"))) \
        .annotate(amount_salary=Sum('amount', filter=Q(expensetype="Salary"))) \
        .annotate(amount_profees=Sum('amount', filter=Q(expensetype="Professional Fees"))) \
        .annotate(amount_electric=Sum('amount', filter=Q(expensetype="Electricity"))) \
        .annotate(amount_mbuild=Sum('amount', filter=Q(expensetype="Maintenance of Building"))) \
        .annotate(amount_mequip=Sum('amount', filter=Q(expensetype="Maintenance of Equipment"))) \
        .annotate(amount_dep=Sum('amount', filter=Q(expensetype="Depreciation"))) \
        .annotate(amount_print=Sum('amount', filter=Q(expensetype="Printing & Stationary"))) \
        .annotate(amount_film=Sum('amount', filter=Q(expensetype="Dry view Film"))) \
        .annotate(amount_other=Sum('amount', filter=Q(expensetype="Others"))) \
        .annotate(amount=Sum('amount')) \
        .annotate(profit=(F('saleamount') - F('amount'))) \
        .values('months', 'amount', 'amount_rent', 'amount_salary', 'amount_profees', 'amount_electric',
                'amount_mbuild',
                'amount_mequip', 'profit', 'amount_dep', 'amount_print', 'amount_film', 'amount_other', 'saleamount',
                'year')
    for s in expgzb:
        gzbexpmonth.append(calendar.month_name[s['months']])
        gzbexpamount.append(s['amount'])
        gzbexpamount_rent.append(s['amount_rent'])
        gzbexpamount_profees.append(s['amount_profees'])
        gzbexpamount_salary.append(s['amount_salary'])
        gzbexpamount_electric.append(s['amount_electric'])
        gzbexpamount_mbulid.append(s['amount_mbuild'])
        gzbexpamount_mequip.append(s['amount_mequip'])
        gzbexpamount_dep.append(s['amount_dep'])
        gzbexpamount_print.append(s['amount_print'])
        gzbexpamount_film.append(s['amount_film'])
        gzbexpamount_other.append(s['amount_other'])
        gzbsaleamount.append(s['saleamount'])
        gzbexpyear.append(s['year'])
        gzbprofit.append(s['profit'])

    year = [str(x) for x in gzbexpyear]
    gzbmonthyear = [i + '-' + j for i, j in zip(gzbexpmonth, year)]
    gzbprofit = [0 if v is None else v for v in gzbprofit]

    gzbexpamount_rent = [0 if v is None else v for v in gzbexpamount_rent]
    gzbexpamount_profees = [0 if v is None else v for v in gzbexpamount_profees]
    gzbexpamount_salary = [0 if v is None else v for v in gzbexpamount_salary]
    gzbexpamount_electric = [0 if v is None else v for v in gzbexpamount_electric]
    gzbexpamount_mbulid = [0 if v is None else v for v in gzbexpamount_mbulid]
    gzbexpamount_mequip = [0 if v is None else v for v in gzbexpamount_mequip]
    gzbexpamount_dep = [0 if v is None else v for v in gzbexpamount_dep]
    gzbexpamount_print = [0 if v is None else v for v in gzbexpamount_print]
    gzbexpamount_film = [0 if v is None else v for v in gzbexpamount_film]
    gzbexpamount_other = [0 if v is None else v for v in gzbexpamount_other]
    gzbexpamount = [0 if v is None else v for v in gzbexpamount]
    gzbsaleamount = [0 if v is None else v for v in gzbsaleamount]

    ggnexpamount = []
    ggnexpamount_rent = []
    ggnexpamount_profees = []
    ggnexpamount_salary = []
    ggnexpamount_electric = []
    ggnexpamount_mbulid = []
    ggnexpamount_mequip = []
    ggnexpamount_dep = []
    ggnexpamount_print = []
    ggnexpamount_film = []
    ggnexpamount_other = []

    ggnsaleamount = []
    ggnprofit = []

    ggnexpmonth = []
    ggnexpyear = []

    dmdexpggn = checkexp.filter(locate="DMDGGN")
    expggn = dmdexpggn.annotate(months=ExtractMonth('month'), year=ExtractYear('month')).values('months', 'year') \
        .annotate(saleamount=Sum('saleamount', filter=Q(expensetype="ggnsale"))) \
        .annotate(amount_rent=Sum('amount', filter=Q(expensetype="Rent"))) \
        .annotate(amount_salary=Sum('amount', filter=Q(expensetype="Salary"))) \
        .annotate(amount_profees=Sum('amount', filter=Q(expensetype="Professional Fees"))) \
        .annotate(amount_electric=Sum('amount', filter=Q(expensetype="Electricity"))) \
        .annotate(amount_mbuild=Sum('amount', filter=Q(expensetype="Maintenance of Building"))) \
        .annotate(amount_mequip=Sum('amount', filter=Q(expensetype="Maintenance of Equipment"))) \
        .annotate(amount_dep=Sum('amount', filter=Q(expensetype="Depreciation"))) \
        .annotate(amount_print=Sum('amount', filter=Q(expensetype="Printing & Stationary"))) \
        .annotate(amount_film=Sum('amount', filter=Q(expensetype="Dry view Film"))) \
        .annotate(amount_other=Sum('amount', filter=Q(expensetype="Others"))) \
        .annotate(amount=Sum('amount')) \
        .annotate(profit=(F('saleamount') - F('amount'))) \
        .values('months', 'amount', 'amount_rent', 'amount_salary', 'amount_profees',
                'amount_electric', 'amount_mbuild',
                'amount_mequip', 'amount_dep', 'amount_print', 'amount_film',
                'amount_other', 'saleamount', 'year', 'profit')
    for s in expggn:
        ggnexpmonth.append(calendar.month_name[s['months']])
        ggnexpamount.append(s['amount'])
        ggnexpamount_rent.append(s['amount_rent'])
        ggnexpamount_profees.append(s['amount_profees'])
        ggnexpamount_salary.append(s['amount_salary'])
        ggnexpamount_electric.append(s['amount_electric'])
        ggnexpamount_mbulid.append(s['amount_mbuild'])
        ggnexpamount_mequip.append(s['amount_mequip'])
        ggnexpamount_dep.append(s['amount_dep'])
        ggnexpamount_print.append(s['amount_print'])
        ggnexpamount_film.append(s['amount_film'])
        ggnexpamount_other.append(s['amount_other'])
        ggnsaleamount.append(s['saleamount'])
        ggnexpyear.append(s['year'])
        ggnprofit.append(s['profit'])

    year = [str(x) for x in ggnexpyear]
    ggnmonthyear = [i + '-' + j for i, j in zip(ggnexpmonth, year)]
    ggnprofit = [0 if v is None else v for v in ggnprofit]
    ggnexpamount_rent = [0 if v is None else v for v in ggnexpamount_rent]
    ggnexpamount_profees = [0 if v is None else v for v in ggnexpamount_profees]
    ggnexpamount_salary = [0 if v is None else v for v in ggnexpamount_salary]
    ggnexpamount_electric = [0 if v is None else v for v in ggnexpamount_electric]
    ggnexpamount_mbulid = [0 if v is None else v for v in ggnexpamount_mbulid]
    ggnexpamount_mequip = [0 if v is None else v for v in ggnexpamount_mequip]
    ggnexpamount_dep = [0 if v is None else v for v in ggnexpamount_dep]
    ggnexpamount_print = [0 if v is None else v for v in ggnexpamount_print]
    ggnexpamount_film = [0 if v is None else v for v in ggnexpamount_film]
    ggnexpamount_other = [0 if v is None else v for v in ggnexpamount_other]
    ggnexpamount = [0 if v is None else v for v in ggnexpamount]
    ggnsaleamount = [0 if v is None else v for v in ggnsaleamount]

    ndaexpamount = []
    ndaexpamount_rent = []
    ndaexpamount_profees = []
    ndaexpamount_salary = []
    ndaexpamount_electric = []
    ndaexpamount_mbulid = []
    ndaexpamount_mequip = []
    ndaexpamount_dep = []
    ndaexpamount_print = []
    ndaexpamount_film = []
    ndaexpamount_other = []

    ndasaleamount = []
    ndaprofit = []

    ndaexpmonth = []
    ndaexpyear = []

    dmdexpnda = checkexp.filter(locate="DMDnda")
    expnda = dmdexpnda.annotate(months=ExtractMonth('month'), year=ExtractYear('month')).values('months', 'year') \
        .annotate(saleamount=Sum('saleamount', filter=Q(expensetype="ndasale"))) \
        .annotate(amount_rent=Sum('amount', filter=Q(expensetype="Rent"))) \
        .annotate(amount_salary=Sum('amount', filter=Q(expensetype="Salary"))) \
        .annotate(amount_profees=Sum('amount', filter=Q(expensetype="Professional Fees"))) \
        .annotate(amount_electric=Sum('amount', filter=Q(expensetype="Electricity"))) \
        .annotate(amount_mbuild=Sum('amount', filter=Q(expensetype="Maintenance of Building"))) \
        .annotate(amount_mequip=Sum('amount', filter=Q(expensetype="Maintenance of Equipment"))) \
        .annotate(amount_dep=Sum('amount', filter=Q(expensetype="Depreciation"))) \
        .annotate(amount_print=Sum('amount', filter=Q(expensetype="Printing & Stationary"))) \
        .annotate(amount_film=Sum('amount', filter=Q(expensetype="Dry view Film"))) \
        .annotate(amount_other=Sum('amount', filter=Q(expensetype="Others"))) \
        .annotate(amount=Sum('amount')) \
        .annotate(profit=(F('saleamount') - F('amount'))) \
        .values('months', 'amount', 'amount_rent', 'amount_salary', 'amount_profees',
                'amount_electric', 'amount_mbuild',
                'amount_mequip', 'amount_dep', 'amount_print', 'amount_film',
                'amount_other', 'saleamount', 'year', 'profit')
    for s in expnda:
        ndaexpmonth.append(calendar.month_name[s['months']])
        ndaexpamount.append(s['amount'])
        ndaexpamount_rent.append(s['amount_rent'])
        ndaexpamount_profees.append(s['amount_profees'])
        ndaexpamount_salary.append(s['amount_salary'])
        ndaexpamount_electric.append(s['amount_electric'])
        ndaexpamount_mbulid.append(s['amount_mbuild'])
        ndaexpamount_mequip.append(s['amount_mequip'])
        ndaexpamount_dep.append(s['amount_dep'])
        ndaexpamount_print.append(s['amount_print'])
        ndaexpamount_film.append(s['amount_film'])
        ndaexpamount_other.append(s['amount_other'])
        ndasaleamount.append(s['saleamount'])
        ndaexpyear.append(s['year'])
        ndaprofit.append(s['profit'])

    year = [str(x) for x in ndaexpyear]
    ndamonthyear = [i + '-' + j for i, j in zip(ndaexpmonth, year)]
    ndaprofit = [0 if v is None else v for v in ndaprofit]
    ndaexpamount_rent = [0 if v is None else v for v in ndaexpamount_rent]
    ndaexpamount_profees = [0 if v is None else v for v in ndaexpamount_profees]
    ndaexpamount_salary = [0 if v is None else v for v in ndaexpamount_salary]
    ndaexpamount_electric = [0 if v is None else v for v in ndaexpamount_electric]
    ndaexpamount_mbulid = [0 if v is None else v for v in ndaexpamount_mbulid]
    ndaexpamount_mequip = [0 if v is None else v for v in ndaexpamount_mequip]
    ndaexpamount_dep = [0 if v is None else v for v in ndaexpamount_dep]
    ndaexpamount_print = [0 if v is None else v for v in ndaexpamount_print]
    ndaexpamount_film = [0 if v is None else v for v in ndaexpamount_film]
    ndaexpamount_other = [0 if v is None else v for v in ndaexpamount_other]
    ndaexpamount = [0 if v is None else v for v in ndaexpamount]
    ndasaleamount = [0 if v is None else v for v in ndasaleamount]

    delexpamount = []
    delexpamount_rent = []
    delexpamount_profees = []
    delexpamount_salary = []
    delexpamount_electric = []
    delexpamount_mbulid = []
    delexpamount_mequip = []
    delexpamount_dep = []
    delexpamount_print = []
    delexpamount_film = []
    delexpamount_other = []

    delsaleamount = []
    delprofit = []

    delexpmonth = []
    delexpyear = []

    dmdexpdel = checkexp.filter(locate="DMDDEL")
    expdel = dmdexpdel.annotate(months=ExtractMonth('month'), year=ExtractYear('month')).values('months', 'year') \
        .annotate(saleamount=Sum('saleamount', filter=Q(expensetype="delsale"))) \
        .annotate(amount_rent=Sum('amount', filter=Q(expensetype="Rent"))) \
        .annotate(amount_salary=Sum('amount', filter=Q(expensetype="Salary"))) \
        .annotate(amount_profees=Sum('amount', filter=Q(expensetype="Professional Fees"))) \
        .annotate(amount_electric=Sum('amount', filter=Q(expensetype="Electricity"))) \
        .annotate(amount_mbuild=Sum('amount', filter=Q(expensetype="Maintenance of Building"))) \
        .annotate(amount_mequip=Sum('amount', filter=Q(expensetype="Maintenance of Equipment"))) \
        .annotate(amount_dep=Sum('amount', filter=Q(expensetype="Depreciation"))) \
        .annotate(amount_print=Sum('amount', filter=Q(expensetype="Printing & Stationary"))) \
        .annotate(amount_film=Sum('amount', filter=Q(expensetype="Dry view Film"))) \
        .annotate(amount_other=Sum('amount', filter=Q(expensetype="Others"))) \
        .annotate(amount=Sum('amount')) \
        .annotate(profit=(F('saleamount') - F('amount'))) \
        .values('months', 'amount', 'amount_rent', 'amount_salary', 'amount_profees',
                'amount_electric', 'amount_mbuild',
                'amount_mequip', 'amount_dep', 'amount_print', 'amount_film',
                'amount_other', 'saleamount', 'year', 'profit')
    for s in expdel:
        delexpmonth.append(calendar.month_name[s['months']])
        delexpamount.append(s['amount'])
        delexpamount_rent.append(s['amount_rent'])
        delexpamount_profees.append(s['amount_profees'])
        delexpamount_salary.append(s['amount_salary'])
        delexpamount_electric.append(s['amount_electric'])
        delexpamount_mbulid.append(s['amount_mbuild'])
        delexpamount_mequip.append(s['amount_mequip'])
        delexpamount_dep.append(s['amount_dep'])
        delexpamount_print.append(s['amount_print'])
        delexpamount_film.append(s['amount_film'])
        delexpamount_other.append(s['amount_other'])
        delsaleamount.append(s['saleamount'])
        delexpyear.append(s['year'])
        delprofit.append(s['profit'])

    year = [str(x) for x in delexpyear]
    delmonthyear = [i + '-' + j for i, j in zip(delexpmonth, year)]
    delprofit = [0 if v is None else v for v in delprofit]

    delexpamount_rent = [0 if v is None else v for v in delexpamount_rent]
    delexpamount_profees = [0 if v is None else v for v in delexpamount_profees]
    delexpamount_salary = [0 if v is None else v for v in delexpamount_salary]
    delexpamount_electric = [0 if v is None else v for v in delexpamount_electric]
    delexpamount_mbulid = [0 if v is None else v for v in delexpamount_mbulid]
    delexpamount_mequip = [0 if v is None else v for v in delexpamount_mequip]
    delexpamount_dep = [0 if v is None else v for v in delexpamount_dep]
    delexpamount_print = [0 if v is None else v for v in delexpamount_print]
    delexpamount_film = [0 if v is None else v for v in delexpamount_film]
    delexpamount_other = [0 if v is None else v for v in delexpamount_other]
    delexpamount = [0 if v is None else v for v in delexpamount]
    delsaleamount = [0 if v is None else v for v in delsaleamount]

    data = {'gzbexpamount_rent': gzbexpamount_rent, 'gzbexpamount_profees': gzbexpamount_profees,
            'gzbexpamount_salary': gzbexpamount_salary,
            'gzbexpamount_print': gzbexpamount_print, 'gzbexpamount_dep': gzbexpamount_dep,
            'gzbexpamount_film': gzbexpamount_film,
            'gzbexpamount_mbulid': gzbexpamount_mbulid, 'gzbexpamount_mequip': gzbexpamount_mequip,
            'gzbexpamount_other': gzbexpamount_other,
            'gzbexpamount_electric': gzbexpamount_electric, 'gzbsaleamount': gzbsaleamount,
            'gzbexpmonth': gzbexpmonth, 'gzbexpamount': gzbexpamount, 'gzbexpyear': gzbexpyear,
            'ggnexpamount_rent': ggnexpamount_rent, 'ggnexpamount_profees': ggnexpamount_profees,
            'ggnexpamount_salary': ggnexpamount_salary,
            'ggnexpamount_print': ggnexpamount_print, 'ggnexpamount_dep': ggnexpamount_dep,
            'ggnexpamount_film': ggnexpamount_film,
            'ggnexpamount_mbulid': ggnexpamount_mbulid, 'ggnexpamount_mequip': ggnexpamount_mequip,
            'ggnexpamount_other': ggnexpamount_other,
            'ggnexpamount_electric': ggnexpamount_electric, 'ggnsaleamount': ggnsaleamount,
            'ggnexpmonth': ggnexpmonth, 'ggnexpamount': ggnexpamount, 'ggnexpyear': ggnexpyear,
            'allsalemonth': allsalemonth, 'allsaleyear': allsaleyear, 'allsaleamount': allsaleamount,
            'allexpamount': allexpamount, 'delexpamount_rent': delexpamount_rent,
            'delexpamount_profees': delexpamount_profees, 'delexpamount_salary': delexpamount_salary,
            'delexpamount_print': delexpamount_print, 'delexpamount_dep': delexpamount_dep,
            'delexpamount_film': delexpamount_film,
            'delexpamount_mbulid': delexpamount_mbulid, 'delexpamount_mequip': delexpamount_mequip,
            'delexpamount_other': delexpamount_other,
            'delexpamount_electric': delexpamount_electric, 'delsaleamount': delsaleamount,
            'delexpmonth': delexpmonth, 'delexpamount': delexpamount, 'delexpyear': delexpyear,
            'gzbmonthyear': gzbmonthyear, 'gzbprofit': gzbprofit, 'allprofit': allprofit, 'res': res,
            'ggnprofit': ggnprofit,
            'ggnmonthyear': ggnmonthyear, 'delprofit': delprofit, 'delmonthyear': delmonthyear,
            'ndaexpamount_rent': ndaexpamount_rent, 'ndaexpamount_profees': ndaexpamount_profees,
            'ndaexpamount_salary': ndaexpamount_salary,
            'ndaexpamount_print': ndaexpamount_print, 'ndaexpamount_dep': ndaexpamount_dep,
            'ndaexpamount_film': ndaexpamount_film,
            'ndaexpamount_mbulid': ndaexpamount_mbulid, 'ndaexpamount_mequip': ndaexpamount_mequip,
            'ndaexpamount_other': ndaexpamount_other,
            'ndaexpamount_electric': ndaexpamount_electric, 'ndasaleamount': ndasaleamount,
            'ndaexpmonth': ndaexpmonth, 'ndaexpamount': ndaexpamount, 'ndaexpyear': ndaexpyear,
            'ndaprofit': ndaprofit, 'ndamonthyear': ndamonthyear, }
    return render(request, 'plsummary.html', data)


def delete_dcm(request):
    dcm = Dcmfile.objects.all()
    for i in dcm:
        matchid = i.refptid
        refpt = Refpt.objects.get(refptid=matchid)
        rgdate = refpt.rdate
        expdate = rgdate + timedelta(days=2)
        today = date.today()
        if expdate <= today:
            if len(i.file) > 0:
                os.remove(i.file.path)
            i.delete()
            refpt.upload = ""
            refpt.save()
    return HttpResponse("Success")


def assign_case(request):
    if request.method == "POST":
        assign = request.POST.get('repby')
        processby = request.POST.get('processby')
        process_as = request.POST.get('process_as')
        day = request.POST.get('day')
        case = request.POST.get('case')

        list = request.POST.getlist('selection')
        for i in list:
            service_order = ServiceOrder.objects.get(id=i)
            if assign is not None:
                service_order.repby = assign
            if processby is not None:
                if process_as == "CS":
                    service_order.CS_processby = processby

                if process_as == "Ondemand":
                    service_order.ON_processby = processby
            service_order.save()

        return redirect('/index')

def refer_case(request):
    usr=Users.objects.get(username=request.user)
    org=Organisation.objects.get(id=usr.orgid_id)
    patients=Patient.objects.filter(orgid=org)
    ref_centre=Organisation.objects.get(orgtype="Domain Owner").id
    connection1 = get_connection(email_backend='django.core.mail.backends.smtp.EmailBackend',
                                 host='smtpout.secureserver.net',
                                 port=25,
                                 username='info@dentread.com',
                                 password='Amit@7002',
                                 use_tls=False)

    from1 = org.email
    if request.method == "POST":
        assign = "Dentread"
        study=request.POST.get('study')
        list = request.POST.getlist('selection')
        for i in list:
            service_order = ServiceOrder.objects.get(id=i)
            patient = patients.get(pid=service_order.pid)
            dcm = Dcmfile.objects.filter(orgid=org).filter(repid=service_order.repid).first()
            if dcm:
                if service_order.refpt_orgid is None:
                    service_order.refpt_orgid=ref_centre
                    service_order.save()

                    regby = request.user
                    checkid = Refpt.objects.filter(orgid=usr.orgid_id)

                    try:
                        max_refptid = checkid.aggregate(Max('refptid'))['refptid__max']
                        new_refptid = checkid.get(refptid=max_refptid)
                        myid = new_refptid.refptid + 1
                    except Refpt.DoesNotExist:
                         myid = 1

                    reftpt = Refpt(regby=regby, contact=service_order.pt_contact, name=service_order.name, age=patient.age, refptid=myid,
                           gender=patient.gender, orgid=org, email=patient.email, remark=service_order.remark, study=study, ref_centre=ref_centre,
                           status='Under Review', btnstatus='btn btn-primary btn-sm disabled', pid=patient.pid, upload=service_order.upload)
                    reftpt.save()

                    dcm.refptid=reftpt.refptid
                    dcm.save()
                    subject = "New Patient referred for Pre read"
                    message = "Dear Dentread,\n\nNew Patient has referred by "+org.orgname+" for pre read,\n\nKindly check your login\n\nThanks"
                    email1 = "info@dentread.com"
                    try:
                        mail = EmailMultiAlternatives(subject, message, from1, [email1],
                                                  connection=connection1)
                        mail.send()
                    except Exception as e:
                        print(e)
                else:
                    return HttpResponse(" Patient is already assigned")
            else:
                return HttpResponse("please upload DICOM data first")



        return redirect('/refer_dent')


def assign_case_dent(request,id):
    mycat = topcat.get(id=id)
    if request.method == "POST":
        assign = request.POST.get('repby')
        processby = request.POST.get('processby')
        process_as = request.POST.get('process_as')
        day = request.POST.get('day')
        case = request.POST.get('case')

        list = request.POST.getlist('selection')
        for i in list:
            service_order = ServiceOrder.objects.get(id=i)
            
            if assign is not None:
                service_order.repby = assign
                
            if processby is not None:
                if process_as == "CS":
                    service_order.CS_processby = processby

                if process_as == "Ondemand":
                    service_order.ON_processby = processby
            service_order.save()

        return redirect('/index_dent/'+str(mycat.id))

    
def assign_case_image(request, id):
    mycat = topcat.get(id=id)
    if request.method == "POST":
        assign = request.POST.get('repby')
        processby = request.POST.get('processby')
        process_as = request.POST.get('process_as')
        day = request.POST.get('day')
        case = request.POST.get('case')

        list = request.POST.getlist('selection')
        for i in list:
            service_order = ServiceOrder.objects.get(id=i)
            if assign is not None:
                service_order.repby = assign
            if processby is not None:
                if process_as == "CS":
                    service_order.CS_processby = processby

                if process_as == "Ondemand":
                    service_order.ON_processby = processby
            service_order.save()

        return redirect('/image_Orders/'+str(mycat.id))

def assignCaseGuide(request, id):
    mycat = topcat.get(id=id)
    if request.method == "POST":
        assign = request.POST.get('repby')
        processby = request.POST.get('processby')
        process_as = request.POST.get('process_as')
        day = request.POST.get('day')
        case = request.POST.get('case')

        list = request.POST.getlist('selection')
        for i in list:
            service_order = ServiceOrder.objects.get(id=i)
            if assign is not None:
                service_order.repby = assign
            if processby is not None:
                if process_as == "CS":
                    service_order.CS_processby = processby

                if process_as == "Ondemand":
                    service_order.ON_processby = processby
            service_order.save()

        return redirect('/guide_orders/'+str(mycat.id))

def assignCaseLab(request, id):
    mycat = topcat.get(id=id)
    if request.method == "POST":
        assign = request.POST.get('repby')
        processby = request.POST.get('processby')
        process_as = request.POST.get('process_as')
        day = request.POST.get('day')
        case = request.POST.get('case')

        list = request.POST.getlist('selection')
        for i in list:
            service_order = ServiceOrder.objects.get(id=i)
            sent_org = Organisation.objects.get(id=service_order.reforgid)
            if assign is not None:
                service_order.repby = assign
            if processby is not None:
                if process_as == "CS":
                    service_order.CS_processby = processby

                if process_as == "Ondemand":
                    service_order.ON_processby = processby
            service_order.save()

        return redirect('/lab_orders/'+str(mycat.id))

def assign_case_planning(request, id):
    mycat = topcat.get(id=id)
    if request.method == "POST":
        assign = request.POST.get('repby')
        processby = request.POST.get('processby')
        process_as = request.POST.get('process_as')
        day = request.POST.get('day')
        case = request.POST.get('case')

        list = request.POST.getlist('selection')
        for i in list:
            service_order = ServiceOrder.objects.get(id=i)
            if assign is not None:
                service_order.repby = assign
            if processby is not None:
                if process_as == "CS":
                    service_order.CS_processby = processby

                if process_as == "Ondemand":
                    service_order.ON_processby = processby
            service_order.save()

        return redirect('/planning_Orders/'+str(mycat.id))


def posturl(request):
    payload = {'ID': 'D121', 'LastName': 'Amit', 'FirstName': 'Kumar', 'Sex': 'Male', 'SSN': 'OPG'}
    r = requests.post('http://122.160.193.152:9000/Patient', data=json.dumps(payload))
    return HttpResponse(r)


def marksent(request, id):
    service_order = ServiceOrder.objects.get(id=id)
    service_order.mailstatus = "Marked as sent"
    service_order.status = "Sent"
    service_order.badge = "badge badge-info"
    service_order.save()
    return redirect('/index')


def appointments(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    appointment = Appointment.objects.filter(orgid=org)
    return render(request, 'appointments.html',
                  {'org': org, 'appointment': appointment, 'page': 'Appointments', 'usr': usr, 'org':org})


def add_appointment(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    appointment = Appointment.objects.filter(orgid=org)
    connection1 = get_connection(email_backend='django.core.mail.backends.smtp.EmailBackend',
                                 host='smtpout.secureserver.net',
                                 port=25,
                                 username='info@dentread.com',
                                 password='Amit@7002',
                                 use_tls=False)

    from1 = "info@dentread.com"
    if request.method == 'POST':
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        study = request.POST.get('study')
        date = request.POST.get('date')
        email = request.POST.get('email')
        time = request.POST.get('time')
        remark = request.POST.get('remark')

        subject = "Your Appointment Scheduled for "+study
        appoint = Appointment(name=name, remark=remark, contact=contact, study=study, centre=org.orgname, orgid=org,
                                  date=date, time=time,  status="Not Registered" , email=email)
        appoint.save()
        email1=str(email)
        message = "Hi "+appoint.name+",\nThanks for contacting "+org.orgname+"\n\nYour appointment is confirmed as per your request on "+appoint.date+" at "+appoint.time+". \n\nThank You "
        mail = EmailMessage(subject, message, from1, [email1], connection=connection1)
        try:
            mail.send()
            message = "Notification sent successfully."

            return render(request, 'appointments.html',
                          {'org': org, 'appointment': appointment, 'page': 'Appointments', 'usr': usr,
                           'message': message})
        except Exception as e:
            message = e
            return render(request, 'appointments.html',
                          {'org': org, 'appointment': appointment, 'page': 'Appointments', 'usr': usr,
                           'message': message})

    return render(request, 'add_appointment.html',
                  {'org': org, 'appointment': appointment, 'page': 'Appointments', 'usr': usr,
                   })




def edit_appointment(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    appoint = Appointment.objects.get(id=id)
    if request.method == 'POST':
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        study = request.POST.get('study')
        email = request.POST.get('email')

        date = request.POST.get('date')
        time = request.POST.get('time')
        remark = request.POST.get('remark')

        appoint.name = name
        appoint.contact = contact
        appoint.study = study
        appoint.email=email
        appoint.date = date
        appoint.time = time
        appoint.remark = remark
        appoint.save()

        return redirect('/appointments')
    appoint = Appointment.objects.get(id=id)

    appointment = Appointment.objects.filter(orgid=org)

    return render(request, 'appointments_edit.html',
                  {'org': org, 'appointment': appointment, 'appoint': appoint, 'page': 'Edit Appointment', 'usr': usr})

    return redirect('/appointments')


def delete_appointment(request, id):
    appoint = Appointment.objects.get(id=id)
    appoint.delete()
    return redirect('/appointments')


def delete_refpt(request, id):
    refpt = Refpt.objects.get(id=id)
    refpt.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def appoint_patient(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    appoint = Appointment.objects.get(id=id)
    if appoint.status == "Registered":
        msg="Patient is already registered"
        return render(request, 'infomsg.html', {'msg':msg})
    else:
        appoint.status = "Registered"
        appoint.save()
        doctors = Refdoctor.objects.filter(orgid=org)
        studies = Study.objects.filter(orgid=org)
        return render(request, 'appoint_patient.html',
                      {'appoint': appoint, 'doctors': doctors, 'studies': studies, 'org': org, 'usr':usr})


def addsign(request):
    if request.method == 'POST' and 'sign' in request.FILES:
        sid = request.POST.get('sid')
        doc = request.FILES
        sign = doc['sign']
        signat = Sign(sid=sid, sign=sign)
        signat.save()
        return redirect('/addsign')

    return render(request, 'addsign.html')


def self_appointment(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        study = request.POST.get('study')
        centre = request.POST.get('centre')
        date = request.POST.get('date')
        time = request.POST.get('time')
        remark = request.POST.get('remark')
        mdate = str(date)
        mtime = str(time)
        fcentre = str(centre)
        if fcentre == "DMDGZB":
            location = "https://bit.ly/307fHhD"
        elif fcentre == "DMDGGN":
            location = "https://bit.ly/3wBgYtq"
        elif fcentre == "DMDDEL":
            location = "https://bit.ly/2YAckPN"
        elif fcentre == "DMDNDA":
            location = "https://bit.ly/3nyfk8v"

        msg = "HI " + name + ", Thanks for contacting DMD IMAGING. Your appointment is confirmed as per your request on " + mdate + " at " + mtime + ". The address is " + centre + ", See location " + location
        try:

            max_id = Appointment.objects.aggregate(Max('id'))['id__max']
            new_id = Appointment.objects.get(id=max_id)
            myid = new_id.id + 1
        except Appointment.DoesNotExist:
            myid = 1

        p = str(myid)
        aptid = 'Appt' + '-' + p

        appointment = Appointment(name=name, remark=remark, contact=contact, study=study, centre=centre, date=date,
                                  time=time, aptid=aptid, status="Not Registered")
        appointment.save()
        s = sendSMS('m/jjNoDNJyg-OaNKA6wVqYOFS388dQ3jnW0yjF3Vlh', contact,
                    'DETECH', msg)
        messages.success(request, "You have register for appointment")
        return render(request, 'success.html')

    org = Organisation.objects.filter(orgname__icontains="DMD")

    return render(request, 'self_appointment.html', {'org': org})


def drprofile(request):
    user = request.user
    usr = Users.objects.get(username=user.username)
    if request.method == 'POST':
        user = request.user
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        username = request.POST.get('username')
        password = request.POST.get('password')

        usr.name = name
        usr.contact = contact
        usr.username = username
        usr.password = password
        usr.save()

        user.set_password(password)
        user.username = username
        user.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have successfully updated the profile")
            return redirect('/cstdashboard')
        else:
            messages.error(request, "Wrong Credentials")
            return redirect('/cstlogin')
    return render(request, 'docprofile.html', {'usr': usr})


def inventory(request):
    org = Organisation.objects.filter(orgname__icontains="DMD")
    if request.method == 'POST':
        fdate = request.POST.get('fdate')
        tdate = request.POST.get('tdate')
        centre = request.POST.get('centre')
        items = Items.objects.all()
        org = Organisation.objects.filter(orgname__icontains="DMD")
        total = 0
        for i in items:
            invent_ct = Inventory.objects.filter(Q(item=i.item)).filter(pid__icontains=centre).filter(
                date__range=[fdate, tdate]).aggregate(Sum('qty'))
            invent_count = invent_ct['qty__sum']
            if invent_count is None:
                invent_count = 0

            invent_sm = Inventory.objects.filter(Q(item=i.item)).filter(pid__icontains=centre).filter(
                date__range=[fdate, tdate]).aggregate(Sum('price'))
            tsum = invent_sm['price__sum']
            if tsum is None:
                tsum = 0
            i.centre = centre
            i.qty = invent_count
            i.amount = tsum
            total = total + tsum

        data = {'items': items, 'org': org, 'total': total}
        return render(request, 'inventory.html', data)
    return render(request, 'inventory.html', {'org': org})


def reg_choose_prof(request):
    page = "Register"
    data = {'page': page}
    return render(request, 'Choose_type.html', data)

def lab_services(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    patient = Patient.objects.filter(orgid = org)
    mycat=topcat.get(id=id)
    today = datetime.today()
    btnchecked='none'
    if request.method == "POST":
        check1 = ""
        check2 = ""
        check3 = ""
        query_date = request.POST.get('query_date')
        if str(query_date) == "today":
            query_date = today
            check1 = "checked"
            btnchecked='todayFunction'
            patient = patient.filter(rdate=query_date)
        if str(query_date) == "yesterday":
            query_date = today - timedelta(days=1)
            check2 = "checked"
            btnchecked='yesterdayFunction'
            patient = patient.filter(rdate=query_date)
        if str(query_date) == "thisweek":
            query_date = today - timedelta(weeks=1)
            patient = patient.filter(Q(rdate__gte = query_date))
            btnchecked='thisweekFunction'
            
        data = {'usr': usr, 'org': org, 'patient': patient, 'topcat': topcat, 'mycat':mycat, 'btnchecked': btnchecked, "check1": check1, "check2": check2, "check3": check3}
        return render(request, 'lab_services.html', data)
    
    page = "Lab Services"
    data = {'page': page, 'usr':usr, 'btnchecked':btnchecked, 'org':org, 'patient': patient, 'topcat': topcat, 'mycat': mycat}
    return render(request, 'lab_services.html', data)

def guide_services(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    patient = Patient.objects.filter(orgid = org)
    mycat=topcat.get(id=id)
    today = datetime.today()
    btnchecked='none'
    if request.method == "POST":
        check1 = ""
        check2 = ""
        check3 = ""
        query_date = request.POST.get('query_date')
        search = request.POST.get('search')
        
        if query_date:
            if str(query_date) == "today":
                query_date = today
                check1 = "checked"
                btnchecked = 'todayFunction'
                patient = patient.filter(Q(rdate__gte=query_date))
            
            if str(query_date) == "yesterday":
                query_date = today - timedelta(days=1)
                check2 = "checked"
                btnchecked = 'yesterdayFunction'
                patient = patient.filter(Q(rdate__gte=query_date))
            if str(query_date) == "thisweek":
                query_date = today - timedelta(weeks=1)
                btnchecked = 'thisweekFunction'
                patient = patient.filter(Q(rdate__gte=query_date))

        if search:
            patient = Patient.objects.filter(orgid = org).filter(Q(name__icontains=search) | Q(rdate__icontains=search) | Q(locate__icontains=search) | Q(pid__icontains=search))
            
        data = {'usr': usr, 'org': org, 'patient': patient, 'topcat': topcat, 'mycat':mycat, 'btnchecked': btnchecked, "check1": check1, "check2": check2, "check3": check3}
        return render(request, 'guide_services.html', data)
    
    page = "Guide Services"
    data = {'page': page, 'usr':usr, 'btnchecked':btnchecked, 'org':org, 'patient': patient, 'topcat': topcat, 'mycat': mycat}
    return render(request, 'guide_services.html', data)

def image_services(request, id):
    
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    patient = Patient.objects.filter(orgid=org)
    today = datetime.today()
    mycat=topcat.get(id=id)
    btnchecked='none'

    if request.method == "POST":
        check1 = ""
        check2 = ""
        check3 = ""
        query_date = request.POST.get('query_date')
        search = request.POST.get('search')
        if query_date:
            if str(query_date) == "today":
                query_date = today
                check1 = "checked"
                btnchecked='todayFunction'
                patient = patient.filter(Q(rdate__gte = query_date))
            if str(query_date) == "yesterday":
                btnchecked='yesterdayFunction'
                query_date = today - timedelta(days=1)
                check2 = "checked"
                patient = patient.filter(Q(rdate__gte = query_date))
            if str(query_date) == "thisweek":
                btnchecked='thisweekFunction'
                query_date = today - timedelta(weeks=1)
                patient = patient.filter(Q(rdate__gte = query_date))
        if search:
            patient = Patient.objects.filter(orgid = org).filter(Q(name__icontains=search) | Q(rdate__icontains=search) | Q(locate__icontains=search) | Q(pid__icontains=search))
        context = {'patient': patient, 'btnchecked': btnchecked, 'usr': usr, 'org': org,'check1': check1,'topcat': topcat, 'check2': check2, 'check3': check3, 'mycat':mycat}
        return render(request, 'image_services.html', context)   
    page = "Image Analisys Report"
    data = {'page': page, 'usr':usr, 'org':org, 'btnchecked': btnchecked, 'patient': patient, 'topcat': topcat, 'mycat':mycat}
    return render(request, 'image_services.html', data)
def branchServiceDetails(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=id)
    branch = Organisation.objects.filter(parent_id = org.id)
    get_dicomsize = Dcmfile.objects.filter(orgid = org).aggregate(Sum('size'))
    dcm =get_dicomsize['size__sum']
    if dcm is None:
        dcm = 0
    get_ios = IOSFile.objects.filter(orgid = org).aggregate(Sum('size'))
    ios = get_ios['size__sum']
    if ios is None:
        ios = 0
    get_other = OtherImageFile.objects.filter(orgid = org).aggregate(Sum('size'))
    other = get_other['size__sum']
    if other is None:
        other = 0
    final_total_size = (dcm + ios + other)
    today=datetime.today()
    btnchecked = 'todayFunction'
    if request.method == 'POST':
        check1 = ""
        check2 = ""
        check3 = ""
        query_date = request.POST.get('query_date')
        filter = request.POST.get('filter')
        get_service_order=ServiceOrder.objects.filter(orgid=filter)
        main_service_order = get_service_order.filter(date=today)
        if str(query_date)=="today":
            query_data = today
            check1 = 'checked'
        if str(query_date)=="yesterday":
            check2 = 'checked'
            btnchecked = 'yesterdayFunction'
            query_data=today - timedelta(days=1)
            main_service_order=get_service_order.filter(date=query_data)
        if str(query_date)=="thisweek":
            check3= 'checked'
            btnchecked = 'thisweekFunction'
            query_data = today - timedelta(weeks=1)
            main_service_order=get_service_order.filter(Q(date__gte=query_data))
        lab_data=main_service_order.filter(refstudy='Digital Lab Services')
        lab_pending = lab_data.filter(status='Pending').count()
        lab_inprogress = lab_data.filter(status='In Process').count()
        lab_completed = lab_data.filter(status='Completed').count()
        lab_total = lab_data.count()
        lab_context = {'lab_total': lab_total, 'lab_pending': lab_pending, 'lab_inprogress': lab_inprogress, 'lab_completed':lab_completed}
        
        radio_data = main_service_order.filter(refstudy='Radiological Report')
        radio_pending = radio_data.filter(status='Pending').count()
        radio_inprogress = radio_data.filter(status='In Process').count()
        radio_completed = radio_data.filter(status='Completed').count()
        radio_total = radio_data.count()
        radio_context = {'radio_pending': radio_pending, 'radio_inprogress': radio_inprogress, 'radio_completed': radio_completed, 'radio_total':radio_total}
        
        image_data = main_service_order.filter(refstudy='Image Analysis Report')
        image_pending = image_data.filter(status='Pending').count()
        image_inprogress = image_data.filter(status='In Process').count()
        image_completed = image_data.filter(status='Completed').count()
        image_total = image_data.count()
        image_context = {'image_pending': image_pending, 'image_inprogress': image_inprogress, 'image_completed': image_completed, 'image_total':image_total}
        
        guide_data = main_service_order.filter(refstudy='Implant Surgical Guide')
        guide_pending =guide_data.filter(status='Pending').count()
        guide_inprogress =guide_data.filter(status='In Process').count()
        guide_completed =guide_data.filter(status='Completed').count()
        guide_total =guide_data.count()
        guide_context = {'guide_pending': guide_pending, 'guide_inprogress': guide_inprogress, 'guide_completed': guide_completed, 'guide_total':guide_total}
        
        planning_data = main_service_order.filter(refstudy='Implant Planning Report')
        planning_pending = planning_data.filter(status='Pending').count()
        planning_inprogress = planning_data.filter(status='In Process').count()
        planning_completed = planning_data.filter(status='Completed').count()
        planning_total = planning_data.count()
        planning_context = {'planning_pending': planning_pending, 'planning_inprogress': planning_inprogress, 'planning_completed': planning_completed, 'planning_total': planning_total}
        
        today=datetime.today()
        appointment = Appointment.objects.all().filter(orgid=org).count()
        patient = Patient.objects.all().filter(orgid=org).count()
        business = ServiceOrder.objects.all().filter(orgid=org).aggregate(Sum('ref_price'))
        amount=business['ref_price__sum']
        data = {'usr': usr, 'branch': branch, 'message': 'You have signed in successfully', 'page': 'Dashboard', 'final_total_size': final_total_size, 'btnchecked': btnchecked, 'org':org,'topcat':topcat, 'appointment':appointment,'patient': patient, 'lab_total':lab_total,'amount': amount, 'planning_pending': planning_pending, 'planning_inprogress': planning_inprogress, 'planning_completed': planning_completed, 'planning_total': planning_total, 'lab_total': lab_total, 'lab_pending': lab_pending, 'lab_inprogress': lab_inprogress, 'lab_completed':lab_completed, 'guide_pending': guide_pending, 'guide_inprogress': guide_inprogress, 'guide_completed': guide_completed, 'guide_total':guide_total, 'image_pending': image_pending, 'image_inprogress': image_inprogress, 'image_completed': image_completed, 'image_total':image_total, 'radio_pending': radio_pending, 'radio_inprogress': radio_inprogress, 'radio_completed': radio_completed, 'radio_total':radio_total}
        return render(request, 'branchServiceDetails.html', data)

def login_clinic(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    main_org_id = org.id
    parent_id = org.id
    branch = Organisation.objects.filter(parent_id = org.id)
    get_service_order=ServiceOrder.objects.filter(orgid=org).exclude(reforgid__isnull = True)
    
    #All DicomSize
    radioSize = RadiologycalServices.objects.filter(orgid = org).aggregate(Sum('size'))
    radioDcm = radioSize['size__sum']
    if radioDcm is None:
        radioDcm = 0
    imageSize = ImageAnalysis.objects.filter(orgid = org).aggregate(Sum('size'))
    imageDcm = imageSize['size__sum']
    if imageDcm is None:
        imageDcm = 0
    planingSize = ImplantPlanning.objects.filter(orgid = org).aggregate(Sum('size'))
    planningDcm = planingSize['size__sum']
    if planningDcm is None:
        planningDcm = 0
    guideSize = Suricalguide.objects.filter(orgid = org).aggregate(Sum('size'))
    guideDcm = guideSize['size__sum']
    if guideDcm is None:
        guideDcm = 0
    get_dicomsize = Dcmfile.objects.filter(orgid = org).aggregate(Sum('size'))
    dcm = get_dicomsize['size__sum']
    if dcm is None:
        dcm = 0
    get_ios = IOSFile.objects.filter(orgid = org).aggregate(Sum('size'))
    ios = get_ios['size__sum']
    if ios is None:
        ios = 0
    get_other = OtherImageFile.objects.filter(orgid = org).aggregate(Sum('size'))
    other = get_other['size__sum']
    if other is None:
        other = 0
    
    newImageSize = ServiceOrder.objects.filter(orgid = org).aggregate(Sum('size'))
    newSize = newImageSize['size__sum']
    if newSize is None:
        newSize = 0
    newImageSize1 = ServiceOrder.objects.filter(orgid = org).aggregate(Sum('size1'))
    newSize1 = newImageSize1['size1__sum']
    if newSize1 is None:
        newSize1 = 0
    final_total_size = (dcm + ios + other + radioDcm + imageDcm + planningDcm + guideDcm + newSize + newSize1)
    today=datetime.today()
    main_service_order = get_service_order.filter(date=today)
    btnchecked = 'todayFunction'
    if request.method == 'POST':
        check1 = ""
        check2 = ""
        check3 = ""
        query_date = request.POST.get('query_date')
        filter_branch = request.POST.get('filter')
        if filter_branch != 0:
            main_org_id = filter_branch
        
        # if filter:
        get_service_order=ServiceOrder.objects.filter(orgid=main_org_id).exclude(reforgid__isnull = True)
        main_service_order = get_service_order.filter(date=today)
        if str(query_date)=="today":
            query_data = today
            check1 = 'checked'
        if str(query_date)=="yesterday":
            check2 = 'checked'
            btnchecked = 'yesterdayFunction'
            query_data=today - timedelta(days=1)
            main_service_order=get_service_order.filter(date=query_data)
        if str(query_date)=="thisweek":
            check3= 'checked'
            btnchecked = 'thisweekFunction'
            query_data = today - timedelta(weeks=1)
            main_service_order=get_service_order.filter(Q(date__gte=query_data))
        lab_data=main_service_order.filter(refstudy='Digital Lab Services')
        lab_pending = lab_data.filter(status='Pending').count()
        lab_inprogress = lab_data.filter(status='In Process').count()
        lab_completed = lab_data.filter(status='Completed').count()
        lab_total = lab_data.count()
        lab_context = {'lab_total': lab_total, 'lab_pending': lab_pending, 'lab_inprogress': lab_inprogress, 'lab_completed':lab_completed}
        
        radio_data = main_service_order.filter(refstudy='Radiological Report')
        radio_pending = radio_data.filter(status='Pending').count()
        radio_inprogress = radio_data.filter(status='In Process').count()
        radio_completed = radio_data.filter(status='Completed').count()
        radio_total = radio_data.count()
        radio_context = {'radio_pending': radio_pending, 'radio_inprogress': radio_inprogress, 'radio_completed': radio_completed, 'radio_total':radio_total}
        
        image_data = main_service_order.filter(refstudy='Image Analysis Report')
        image_pending = image_data.filter(status='Pending').count()
        image_inprogress = image_data.filter(status='In Process').count()
        image_completed = image_data.filter(status='Completed').count()
        image_total = image_data.count()
        image_context = {'image_pending': image_pending, 'image_inprogress': image_inprogress, 'image_completed': image_completed, 'image_total':image_total}
        
        guide_data = main_service_order.filter(refstudy='Implant Surgical Guide')
        guide_pending =guide_data.filter(status='Pending').count()
        guide_inprogress =guide_data.filter(status='In Process').count()
        guide_completed =guide_data.filter(status='Completed').count()
        guide_total =guide_data.count()
        guide_context = {'guide_pending': guide_pending, 'guide_inprogress': guide_inprogress, 'guide_completed': guide_completed, 'guide_total':guide_total}
        
        planning_data = main_service_order.filter(refstudy='Implant Planning Report')
        planning_pending = planning_data.filter(status='Pending').count()
        planning_inprogress = planning_data.filter(status='In Process').count()
        planning_completed = planning_data.filter(status='Completed').count()
        planning_total = planning_data.count()
        planning_context = {'planning_pending': planning_pending, 'planning_inprogress': planning_inprogress, 'planning_completed': planning_completed, 'planning_total': planning_total}
        
        today=datetime.today()
        appointment = Appointment.objects.all().filter(orgid=org).count()
        patient = Patient.objects.all().filter(orgid=org).count()
        business = ServiceOrder.objects.all().filter(orgid=org).filter(paymentStatus = 'Pay Later').aggregate(Sum('ref_price'))
        amount = business['ref_price__sum']
        notification = Notification.objects.filter(sendTo = org.id)
        data = {'usr': usr, 'branch': branch, 'main_org_id': main_org_id, 'notification': notification, 'message': 'You have signed in successfully', 'page': 'Dashboard', 'final_total_size': final_total_size, 'btnchecked': btnchecked, 'org':org,'topcat':topcat, 'appointment':appointment,'patient': patient, 'lab_total':lab_total,'amount': amount, 'planning_pending': planning_pending, 'planning_inprogress': planning_inprogress, 'planning_completed': planning_completed, 'planning_total': planning_total, 'lab_total': lab_total, 'lab_pending': lab_pending, 'lab_inprogress': lab_inprogress, 'lab_completed':lab_completed, 'guide_pending': guide_pending, 'guide_inprogress': guide_inprogress, 'guide_completed': guide_completed, 'guide_total':guide_total, 'image_pending': image_pending, 'image_inprogress': image_inprogress, 'image_completed': image_completed, 'image_total':image_total, 'radio_pending': radio_pending, 'radio_inprogress': radio_inprogress, 'radio_completed': radio_completed, 'radio_total':radio_total}
        return render(request, 'dashboard_clinic.html', data)
            
    
    
    lab_data=main_service_order.filter(refstudy='Digital Lab Services')
    lab_pending = lab_data.filter(status='Pending').count()
    lab_inprogress = lab_data.filter(status='In Process').count()
    lab_completed = lab_data.filter(status='Completed').count()
    lab_total = lab_data.count()
    lab_context = {'lab_total': lab_total, 'lab_pending': lab_pending, 'lab_inprogress': lab_inprogress, 'lab_completed':lab_completed}
    
    radio_data = main_service_order.filter(refstudy='Radiological Report')
    radio_pending = radio_data.filter(status='Pending').count()
    radio_inprogress = radio_data.filter(status='In Process').count()
    radio_completed = radio_data.filter(status='Completed').count()
    radio_total = radio_data.count()
    radio_context = {'radio_pending': radio_pending, 'radio_inprogress': radio_inprogress, 'radio_completed': radio_completed, 'radio_total':radio_total}
    
    image_data = main_service_order.filter(refstudy='Image Analysis Report')
    image_pending = image_data.filter(status='Pending').count()
    image_inprogress = image_data.filter(status='In Process').count()
    image_completed = image_data.filter(status='Completed').count()
    image_total = image_data.count()
    image_context = {'image_pending': image_pending, 'image_inprogress': image_inprogress, 'image_completed': image_completed, 'image_total':image_total}
    
    guide_data = main_service_order.filter(refstudy='Implant Surgical Guide')
    guide_pending =guide_data.filter(status='Pending').count()
    guide_inprogress =guide_data.filter(status='In Process').count()
    guide_completed =guide_data.filter(status='Completed').count()
    guide_total =guide_data.count()
    guide_context = {'guide_pending': guide_pending, 'guide_inprogress': guide_inprogress, 'guide_completed': guide_completed, 'guide_total':guide_total}
    
    planning_data= main_service_order.filter(refstudy='Implant Planning Report')
    planning_pending = planning_data.filter(status='Pending').count()
    planning_inprogress = planning_data.filter(status='In Process').count()
    planning_completed = planning_data.filter(status='Completed').count()
    planning_total = planning_data.count()
    planning_context = {'planning_pending': planning_pending, 'planning_inprogress': planning_inprogress, 'planning_completed': planning_completed, 'planning_total': planning_total}
    
    today=datetime.today()
    appointment = Appointment.objects.all().filter(orgid=org).filter(date=today).count()
    patient = Patient.objects.all().filter(orgid=org).count()
    business = ServiceOrder.objects.all().filter(orgid=org).filter(paymentStatus = 'Pay Later').aggregate(Sum('ref_price'))
    amount = business['ref_price__sum']
    notification = Notification.objects.filter(sendTo = org.id)
    data = {'usr': usr,'branch': branch,'main_org_id':main_org_id, 'notification': notification, 'message': 'You have signed in successfully', 'page': 'Dashboard','final_total_size': final_total_size, 'org':org,'topcat':topcat, 'appointment':appointment,'patient': patient,'amount': amount, 'planning_pending': planning_pending, 'planning_inprogress': planning_inprogress, 'planning_completed': planning_completed, 'planning_total': planning_total, 'lab_total': lab_total, 'lab_pending': lab_pending, 'lab_inprogress': lab_inprogress, 'lab_completed':lab_completed, 'guide_pending': guide_pending, 'guide_inprogress': guide_inprogress, 'guide_completed': guide_completed, 'guide_total':guide_total, 'image_pending': image_pending, 'image_inprogress': image_inprogress, 'image_completed': image_completed, 'image_total':image_total, 'radio_pending': radio_pending, 'radio_inprogress': radio_inprogress, 'radio_completed': radio_completed, 'radio_total':radio_total, 'btnchecked': btnchecked}
    return render(request, 'dashboard_clinic.html', data)



def radiology_services(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    patient = Patient.objects.filter(orgid = org)
    today = datetime.today()
    mycat=topcat.get(id=id)

    btnchecked='none'
    
    if request.method == "POST":
        check1 = ""
        check2 = ""
        check3 = ""
        query_date = request.POST.get('query_date')
        print(query_date)
        print(org)     
        if str(query_date) == "today":
            query_date = today
            check1 = "checked"
            btnchecked='todayFunction'
            patient = patient.filter(rdate=query_date)
        if str(query_date) == "yesterday":
            query_date = today - timedelta(days=1)
            check2 = "checked"
            btnchecked='yesterdayFunction'
            patient = patient.filter(rdate=query_date)
        if str(query_date) == "thisweek":
            query_date = today - timedelta(weeks=1)
            patient = patient.filter(Q(rdate__gte = query_date))
            btnchecked='thisweekFunction'    
        context = {'patient': patient, 'btnchecked': btnchecked, 'usr': usr,'org': org,'check1': check1,'topcat':topcat, 'check2': check2, 'check3': check3, 'mycat':mycat}
        return render(request, 'radiology_services.html', context)
       
    page = "Radiology Services"
    data = {'page': page, 'usr':usr, 'btnchecked': btnchecked, 'org':org, 'patient':patient, 'topcat':topcat, 'mycat':mycat}
    return render(request, 'radiology_services.html', data)

def implant_services(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    patient = Patient.objects.filter(orgid = org)
    today = datetime.today()
    mycat=topcat.get(id=id)
    btnchecked='none'
    if request.method == "POST":
        query_date = request.POST.get('query_date')
        if str(query_date) == "today":
            query_date = today
            check1 = "checked"
            btnchecked='todayFunction'
            patient = patient.filter(rdate=query_date)
        if str(query_date) == "yesterday":
            query_date = today - timedelta(days=1)
            check2 = "checked"
            btnchecked='yesterdayFunction'
            patient = patient.filter(rdate=query_date)
        if str(query_date) == "thisweek":
            query_date = today - timedelta(weeks=1)
            patient = patient.filter(Q(rdate__gte = query_date))
            btnchecked='thisweekFunction'
            
        data = {'usr': usr, 'org': org, 'patient': patient, 'topcat': topcat, 'mycat':mycat, 'btnchecked': btnchecked}
        return render(request, 'implant_services.html', data)
    
    page = "Implant Planning Report"
    data = {'page': page, 'usr':usr, 'org':org, 'patient':patient, 'topcat':topcat, 'mycat':mycat, 'btnchecked': btnchecked}
    return render(request, 'implant_services.html', data)

def lab_status(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order=ServiceOrder.objects.get(id=id)
    patient=Patient.objects.get(id=service_order.pid)
    pros=Prosthetic.objects.filter(repid=service_order.id)
    comment = Comments.objects.filter(repid=service_order.id)
  
    data = {'page': 'status', 'usr':usr, 'org':org,  'topcat':topcat, 'pros':pros, 'patient':patient, 'service_order':service_order, 'comment':comment}
    return render(request, 'lab_status.html', data)

def lab_post_comment(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    rept = ServiceOrder.objects.get(id=id)
    # pros=Prosthetic.objects.get(repid=rept.id)
    patient=Patient.objects.get(id=rept.pid)
    if request.method == 'POST':
        comment = request.POST.get('comment')
        name=usr.name
        comments=Comments(orgid = org, name=name, comment=comment, repid=rept.id)
        comments.save()
        return redirect('/lab_status/'+str(rept.id))
    data = {'page': 'status', 'usr': usr, 'org': org, 'topcat': topcat, 'patient': patient,'rept': rept, 'comments':comments}
    return render(request, 'lab_status.html', data)

def cancel_case(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    case=Suricalguide.objects.get(id=id)
    case.status="Canceled by Sender"
    case.save()
    return redirect(request.META['HTTP_REFERER'])


def surgi_status(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id)
    patient = Patient.objects.get(id=service_order.pid)
    pros = Suricalguide.objects.get(repid=service_order.id)
    comments = Comments.objects.filter(repid=service_order.id)
    icon = ''
    currency = ''
    if org.country == 'IN':
        currency = 'price'
        icon = '<i class="fa-solid fa-indian-rupee-sign"></i>'
    else:
        currency = 'dollarPrice'
        icon = '<i class="fa-solid fa-dollar-sign"></i>'
    data = {'page': 'status', 'usr':usr, 'org':org, 'icon': icon, 'currency': currency, 'topcat':topcat, 'pros':pros, 'patient':patient, 'service_order':service_order, 'comments':comments}
    return render(request, 'surgi_status.html', data)

def radiological_status(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id)
    patient = Patient.objects.get(id=service_order.pid)
    pros = RadiologycalServices.objects.filter(repid=service_order.id)
    comment = Comments.objects.filter(repid=service_order.id)
    log = ServiceLog.objects.filter(repid = service_order.id)
    
    icon = ''
    currency = ''
    if org.country == 'IN':
        currency = 'price'
        icon = '<i class="fa-solid fa-indian-rupee-sign"></i>'
    else:
        currency = 'dollarPrice'
        icon = '<i class="fa-solid fa-dollar-sign"></i>'
    
    data = {'page': 'status', 'usr':usr, 'org':org, 'topcat':topcat, 'icon': icon, 'pros':pros, 'patient':patient, 'service_order':service_order,'log': log, 'comment':comment}
    return render(request, 'Radiological_Service/radio_status.html', data)
    
def manageReport(request,id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id)
    patient = Patient.objects.get(id = service_order.pid)
    pros = RadiologycalServices.objects.filter(repid=service_order.id)
    for i in pros:
        if i.status == 'Report Completed':
            i.status = 'In Process'
        if i.status == 'For Review':
            i.status = 'In Process'
    
    for i in pros:
        if i.status != 'Pending':
            service_order.status = 'In Process'
            service_order.badge = 'badge badge-warning'
            service_order.save()
            break
    lineOrderNumber = 0
    totalLineItem = pros.count()
    for i in pros:
        if i.status == 'Completed':
            lineOrderNumber +=1
    if lineOrderNumber == totalLineItem:
        service_order.status = 'Completed'
        service_order.badge = 'badge badge-success'
        service_order.save()
    comments = Comments.objects.filter(repid=service_order.id)
    otherImage = OtherImageFile.objects.filter(repid = service_order.id)
    imgFile = FeedFile.objects.filter(repid = service_order.id)
    for i in imgFile:
        i.fileName = os.path.basename(i.file.url).split('/')[-1]
    data = {'page': 'status', 'usr':usr, 'org':org, 'otherImage': otherImage, 'imgFile': imgFile, 'topcat':topcat, 'pros':pros, 'patient':patient, 'service_order':service_order, 'comments':comments}
    return render(request, 'Radiological_Service/manage_report.html', data)

def manageReportImage(request,id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id)
    patient = Patient.objects.get(id=service_order.pid)
    pros = ImageAnalysis.objects.filter(repid=service_order.id)
    for i in pros:
        if i.status == 'Report Completed':
            i.status = 'In Process'
        if i.status == 'For Review':
            i.status = 'In Process'
    
    for i in pros:
        if i.status != 'Pending':
            service_order.status = 'In Process'
            service_order.badge = 'badge badge-warning'
            service_order.save()
            break
    lineOrderNumber = 0
    totalLineItem = pros.count()
    for i in pros:
        if i.status == 'Completed':
            lineOrderNumber +=1
    if lineOrderNumber == totalLineItem:
        service_order.status = 'Completed'
        service_order.badge = 'badge badge-success'
        service_order.save()
    comments = Comments.objects.filter(repid=service_order.id)
    otherImage = OtherImageFile.objects.filter(repid = service_order.id)
    imgFile = FeedFile.objects.filter(repid = service_order.id)
    for i in imgFile:
        i.fileName = os.path.basename(i.file.url).split('/')[-1]
    data = {'page': 'status', 'usr':usr, 'org':org, 'imgFile': imgFile, 'otherImage': otherImage, 'topcat':topcat, 'pros':pros, 'patient':patient, 'service_order':service_order, 'comments':comments}
    return render(request, 'ImageAnalysis/manageReportImage.html', data)

def manageReportPlanning(request,id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id)
    patient = Patient.objects.get(id=service_order.pid)
    pros = ImplantPlanning.objects.filter(repid=service_order.id)
    for i in pros:
        if i.status == 'Report Completed':
            i.status = 'In Process'
        if i.status == 'For Review':
            i.status = 'In Process'
    
    for i in pros:
        if i.status != 'Pending':
            service_order.status = 'In Process'
            service_order.badge = 'badge badge-warning'
            service_order.save()
            break
    lineOrderNumber = 0
    totalLineItem = pros.count()
    for i in pros:
        if i.status == 'Completed':
            lineOrderNumber +=1
    if lineOrderNumber == totalLineItem:
        service_order.status = 'Completed'
        service_order.badge = 'badge badge-success'
        service_order.save()
    comments = Comments.objects.filter(repid=service_order.id)
    otherImage = OtherImageFile.objects.filter(repid = service_order.id)
    imgFile = FeedFile.objects.filter(repid = service_order.id)
    for i in imgFile:
        i.fileName = os.path.basename(i.file.url).split('/')[-1]
    data = {'page': 'status', 'usr':usr, 'org':org, 'otherImage': otherImage, 'imgFile': imgFile, 'topcat':topcat, 'pros':pros, 'patient':patient, 'service_order':service_order, 'comments':comments}
    return render(request, 'Implant_Planning/manageReport_Implant.html', data)

def manageReportGuide(request,id):
    usr = Users.objects.get(username = request.user)
    org = Organisation.objects.get(id = usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = id)
    patient = Patient.objects.get(id = service_order.pid)
    pros = Suricalguide.objects.filter(repid = service_order.id)
    refer_id = Organisation.objects.get(id = service_order.reforgid).orgname
    for i in pros:
        if i.status == 'Report Completed':
            i.status = 'In Process'
        if i.status == 'For Review':
            i.status = 'In Process'
    icon = ''
    currency = ''
    if org.country == 'IN':
        currency = 'price'
        icon = '<i class="fa-solid fa-indian-rupee-sign"></i>'
    else:
        currency = 'dollarPrice'
        icon = '<i class="fa-solid fa-dollar-sign"></i>'
    for i in pros:
        if i.status != 'Submit Order':
            service_order.status = 'In Process'
            service_order.badge = 'badge badge-warning'
            service_order.save()
            break
    lineOrderNumber = 0
    totalLineItem = pros.count()
    for i in pros:
        if i.status == 'Order Completed':
            lineOrderNumber +=1
    if lineOrderNumber == totalLineItem:
        service_order.status = 'Completed'
        service_order.badge = 'badge badge-success'
        service_order.save()
    comments = Comments.objects.filter(repid=service_order.id)
    data = {'page': 'status','refer_id': refer_id, 'usr':usr,'icon': icon, 'currency': currency, 'org':org,  'topcat':topcat, 'pros':pros, 'patient':patient, 'service_order':service_order, 'comments':comments}
    return render(request, 'LabOrder/manageReportGuide.html', data)

def manageReportDigitalLabOld(request,id):
    
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id)
    patient = Patient.objects.filter(id=service_order.pid)
    pros = Prosthetic.objects.filter(repid=service_order.id)
    refer_id = Organisation.objects.get(id=service_order.reforgid).orgname
    comments = Comments.objects.filter(repid=service_order.id)
    for i in pros:
        if i.status == 'Report Completed':
            i.status = 'In Process'
        if i.status == 'For Review':
            i.status = 'In Process'
    
     # Price Symbol
    icon = ''
    currency = ''
    if org.country == 'IN':
        currency = 'price'
        icon = '<i class="fa-solid fa-indian-rupee-sign"></i>'
    else:
        currency = 'dollarPrice'
        icon = '<i class="fa-solid fa-dollar-sign"></i>'
    for i in pros:
        if i.status != 'Submit Order':
            service_order.status = 'In Process'
            service_order.badge = 'badge badge-warning'
            service_order.save()
            break
    lineOrderNumber = 0
    totalLineItem = pros.count()
    for i in pros:
        if i.status == 'Production Complete':
            lineOrderNumber +=1
    if lineOrderNumber == totalLineItem:
        service_order.status = 'Completed'
        service_order.badge = 'badge badge-success'
        service_order.save()
    data = {'page': 'status','refer_id': refer_id, 'usr':usr,'icon': icon, 'currency': currency, 'org':org,  'topcat':topcat, 'pros':pros, 'patient':patient, 'service_order':service_order, 'comments':comments}
    return render(request, 'LabOrder/manageReportDigitalLab.html', data)


def manageReportDigitalLab(request,id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id)
    patient = Patient.objects.get(id=service_order.pid)
    file = FeedFile.objects.filter(repid=service_order.id)
    log = ServiceLog.objects.filter(repid=service_order.id)
    patient = Patient.objects.get(id=service_order.pid)
    comment = Comments.objects.filter(repid = service_order.id)
    extraItems = ExtraLabItem.objects.filter(repid = service_order.id)   
    image_order = Prosthetic.objects.filter(repid=service_order.id)
    ref_org = Organisation.objects.get(id = service_order.reforgid).orgname
    data={'usr':usr, 'org': org,'log': log, 'ref_org': ref_org, 'service_order':service_order, 'extraItems': extraItems, 'patient':patient, 'topcat': topcat, 'image_order': image_order, 'file':file, 'comment': comment}
    return render(request, 'LabOrder/manageReportDigitalLabNew.html', data)


def orderDeliver(request, id1, id2):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = id1)
    lineItem = Suricalguide.objects.get(id=id2)
    if request.method == 'POST':
        orderDeliverDate = request.POST.get('date')
        orderDeliverComment = request.POST.get('comment')
        lineItem.orderDeliverDate = orderDeliverDate
        lineItem.orderDeliverComment = orderDeliverComment
        lineItem.orderDeliverConfirmationL = "True"
        lineItem.status = "Order Delivered"
        notification = Notification(orgid = org, sendTo = lineItem.orgid_id, serviceOrderId = service_order.id, sent = True, lineItemId = lineItem.id, service = 'Implant Surgical Guide', user = usr.name, event = 'ORDER DELIVERED', details = 'Your order has been successfully delivered by the lab for the order ID: '+str(service_order.order_id) + ' and line item ID: '+ str(lineItem.item_id), date = datetime.now(), hyperLink = '/lineOrderDetails/'+str(service_order.id)+'/'+str(lineItem.id))
        lineItem.save()
        notification.save()
        data={'usr':usr, 'org':org,'lineItem':lineItem, 'org': org}
        return redirect('/lineOrderDetailsLab/'+ str(service_order.id) + '/' + str(lineItem.id))
    data={'usr':usr, 'org':org,'lineItem':lineItem, 'org': org}
    return redirect('/lineOrderDetailsLab/'+ str(service_order.id) + '/' + str(lineItem.id))

def orderDeliverDigital(request, id1, id2):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = id1)
    lineItem = Prosthetic.objects.get(id=id2)
    if request.method == 'POST':
        orderDeliverDate = request.POST.get('date')
        orderDeliverComment = request.POST.get('comment')
        lineItem.orderDeliverDate = orderDeliverDate
        lineItem.orderDeliverComment = orderDeliverComment
        lineItem.orderDeliverConfirmationL = "True"
        lineItem.status = "Order Delivered"
        lineItem.save()
        notification = Notification(orgid = org, sendTo = lineItem.orgid_id, serviceOrderId = service_order.id, sent = True, lineItemId = lineItem.id, service = 'Digital Lab Services', user = usr.name, event = 'ORDER DELIVERED', details = 'Your order has been successfully delivered by the lab for the order ID: '+str(service_order.order_id) + ' and line item ID: '+ str(lineItem.item_id), date = datetime.now(), hyperLink = '/lineOrderDetailsDigital/'+str(service_order.id)+'/'+str(lineItem.id))
        notification.save()
        # Send Mail code
        clinicEmail = Organisation.objects.get(id = service_order.orgid_id).email
        clinicName = Organisation.objects.get(id = service_order.orgid_id).orgname
        connection = mail.get_connection()
        connection.open()
        subject = 'Order Delivered'
        message = 'Dear \nClinic Admin, '+ str(clinicName)+'\nYour order has been successfully delivered by the lab: '+ str(org.orgname) +' , for the order ID: '+str(service_order.order_id) + ' and line item ID: '+ str(lineItem.item_id) + '. \nThank You \nDentread'
        from1 = 'info.dentread@gmail.com'
        email1 = clinicEmail
        mymailExicute = mail.EmailMessage(subject, message, from1, [email1], connection=connection)
        try:
            mymailExicute.send()
            connection.close()
        except Exception as e:
            message = e
        return redirect('/lineOrderDetailsDigitalLab/'+ str(service_order.id) + '/' + str(lineItem.id))
    data={'usr':usr, 'org':org,'lineItem':lineItem, 'org': org}
    return redirect('/lineOrderDetailsDigitalLab/'+ str(service_order.id) + '/' + str(lineItem.id))

def orderDispatch(request, id1, id2):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = id1)
    lineItem = Suricalguide.objects.get(id=id2)
    if request.method == 'POST':
        trackingId = request.POST.get('trackingId')
        shipby = request.POST.get('courier')
        DispatchComment = request.POST.get('comment')
        DispatchDate = request.POST.get('date')
        DispatchAddress = request.POST.get('address')
        lineItem.trackingId = trackingId
        lineItem.shipby = shipby
        lineItem.DispatchComment = DispatchComment
        lineItem.DispatchAddress = DispatchAddress
        lineItem.DispatchDate = DispatchDate
        lineItem.status = "Order Dispatched"
        notification = Notification(orgid = org, sendTo = lineItem.orgid_id, serviceOrderId = service_order.id, sent = True, lineItemId = lineItem.id, service = 'Implant Surgical Guide', user = usr.name, event = 'ORDER DISPATCHED', details = 'Your order has been successfully dispatched by the lab : '+ str(org.orgname) +' for the order ID: '+str(service_order.order_id) + ' and line item ID: '+ str(lineItem.item_id), date = datetime.now(), hyperLink = '/lineOrderDetails/'+str(service_order.id)+'/'+str(lineItem.id))
        lineItem.save()
        notification.save()
        data={'usr':usr, 'org':org,'lineItem':lineItem, 'org': org}
        return redirect('/lineOrderDetailsLab/' + str(service_order.id) + '/' + str(lineItem.id))
    data={'usr':usr, 'org':org,'lineItem':lineItem, 'org': org}
    return redirect('/lineOrderDetailsLab/'+ str(service_order.id) + '/' + str(lineItem.id))


def orderDispatchDigital(request, id1, id2):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = id1)
    lineItem = Prosthetic.objects.get(id=id2)
    if request.method == 'POST':
        trackingId = request.POST.get('trackingId')
        shipby = request.POST.get('courier')
        DispatchComment = request.POST.get('comment')
        DispatchDate = request.POST.get('date')
        DispatchAddress = request.POST.get('address')
        lineItem.trackingId = trackingId
        lineItem.shipby = shipby
        lineItem.DispatchComment = DispatchComment
        lineItem.DispatchAddress = DispatchAddress
        lineItem.DispatchDate = DispatchDate
        lineItem.status = "Order Dispatched"
        notification = Notification(orgid = org, sendTo = lineItem.orgid_id, serviceOrderId = service_order.id, sent = True, lineItemId = lineItem.id, service = 'Digital Lab Services', user = usr.name, event = 'ORDER DISPATCHED', details = 'Your order has been successfully dispatched by the lab : '+ str(org.orgname) +' for the order ID: '+str(service_order.order_id) + ' and line item ID: '+ str(lineItem.item_id), date = datetime.now(), hyperLink = '/lineOrderDetailsDigital/'+str(service_order.id)+'/'+str(lineItem.id))
        lineItem.save()
        notification.save()
        # Send Mail code
        clinicEmail = Organisation.objects.get(id = service_order.orgid_id).email
        clinicName = Organisation.objects.get(id = service_order.orgid_id).orgname
        connection = mail.get_connection()
        connection.open()
        subject = 'Order Dispatched'
        message = 'Dear \nClinic Admin, '+ str(clinicName)+'\nYour order has been successfully dispatched by the lab: '+ str(org.orgname) +' , for the order ID: '+str(service_order.order_id) + ' and line item ID: '+ str(lineItem.item_id) + '. \nTracking ID: '+str(lineItem.trackingId)+'\nCourier Name: ' +str(lineItem.shipby) + '\nDispatch Date: ' +str(lineItem.DispatchDate) + '\nDispatch Address: ' +str(lineItem.DispatchAddress) + '\nThank You \nDentread'
        from1 = 'info.dentread@gmail.com'
        email1 = clinicEmail
        mymailExicute = mail.EmailMessage(subject, message, from1, [email1], connection=connection)
        try:
            mymailExicute.send()
            connection.close()
        except Exception as e:
            message = e
        data={'usr':usr, 'org':org,'lineItem':lineItem, 'org': org}
        return redirect('/lineOrderDetailsDigitalLab/' + str(service_order.id) + '/' + str(lineItem.id))
    data={'usr':usr, 'org':org,'lineItem':lineItem, 'org': org}
    return redirect('/lineOrderDetailsDigitalLab/'+ str(service_order.id) + '/' + str(lineItem.id))


def lineOrderDetailsDigital(request, id1, id2):
    context= {}
    context['id1']= id1
    context['id2']= id2 
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    topcat = Topcat.objects.filter(status="Active")
    service_order = ServiceOrder.objects.get(id=id1)
    lineItem= Prosthetic.objects.get(id=id2)
    feedFile = FeedFile.objects.filter(repid=service_order.id).filter(sodrid = lineItem.id)
    selfStlFile =  IOSFile.objects.filter(repid= service_order.id).filter(sodrid= lineItem.id).count() == 0
    if selfStlFile:
        stlFile = IOSFile.objects.filter(repid= service_order.id)
    else:     
        stlFile= IOSFile.objects.filter(repid= service_order.id).filter(sodrid = lineItem.id)
    refer_id = Organisation.objects.get(id=service_order.reforgid).orgname
    designFile = DesignFile.objects.filter(repid= service_order.id).filter(sodrid = lineItem.id)

    if lineItem.status == "Share Design":
        for i in feedFile: 
            if i.fileStatus != None: 
                lineItem.status = "Review Design"
                lineItem.save()

        if lineItem.status == 'Production Complete':
            nauty = Notification.objects.filter(serviceOrderId = service_order.id).filter(lineItemId = lineItem.id).filter(event='PRODUCTION COMPLETE')
            notification = Notification(orgid = org, sendTo = org.id, serviceOrderId = service_order.id, sent = True, lineItemId = lineItem.id, service = 'Digital Lab Services', user = usr.name, event = 'PRODUCTION COMPLETED', details = 'Your order with order ID: '+str(service_order.order_id) + ' and line item ID: '+ str(lineItem.item_id) + ' has succesfully completed', date = datetime.now(), hyperLink = '/lineOrderDetailsDigital/'+str(service_order.id)+'/'+str(lineItem.id))
            if nauty.count() == 0:
                notification.save()

    fileName = ''
    stlCheck = False
    for i in feedFile:
        fileName = i.fileName
        if fileName.endswith('.stl'):
            stlCheck = True
    data = {'usr': usr, 'org': org, 'stlCheck': stlCheck, 'designFile': designFile, 'feedFile':feedFile, 'service_order': service_order, 'lineItem': lineItem, 'stlFile': stlFile, 'refer_id': refer_id, 'topcat': topcat}
    return render(request, 'LabOrder/lineOrderDetailsDigital.html', data)

def lineOrderDetails(request, id1, id2):
    context= {}
    context['id1']= id1
    context['id2']= id2 
    usr = Users.objects.get(username=request.user)
    
    org = Organisation.objects.get(id=usr.orgid_id)
    topcat = Topcat.objects.filter(status="Active")
    service_order = ServiceOrder.objects.get(id=id1)
    lineItem = Suricalguide.objects.get(id=id2)
    feedFile = FeedFile.objects.filter(repid=service_order.id).filter(sodrid= lineItem.id)
    fileName = ''
    stlCheck = False
    if feedFile:
        for i in feedFile:
            fileName = i.fileName
            if fileName.endswith('.stl'):
                stlCheck = True
    stlFile = IOSFile.objects.filter(repid= service_order.id)
    refer_id = Organisation.objects.get(id=service_order.reforgid).orgname
    designFile = DesignFile.objects.filter(repid= service_order.id).filter(sodrid= lineItem.id)
    
    fileName2 = ''
    stlFileCheck = False
    if designFile:
        for i in designFile:
            fileName2 = i.fileName
            if fileName2.endswith('.stl'):
                stlFileCheck = True
            
    if lineItem.output_type == 'Prosthetically Driven Planning' and lineItem.status == 'Review Plan':
        for i in feedFile:
            if i.fileStatus =="Approve":
                lineItem.status = "Order Completed"
                lineItem.save()

    if lineItem.status == 'Production Complete':
        nauty = Notification.objects.filter(serviceOrderId = service_order.id).filter(lineItemId = lineItem.id).filter(event='Production Complete')
        notification = Notification(orgid = org, sendTo = org.id, serviceOrderId = service_order.id, sent = True, lineItemId = lineItem.id, service = 'Implant Surgical Guide', user = usr.name, event = 'PRODUCTION COMPLETED', details = 'Your order with order ID: '+str(service_order.order_id) + ' and line item ID: '+ str(lineItem.item_id) + ' has succesfully completed', date = datetime.now(), hyperLink = '/lineOrderDetails/'+str(service_order.id)+'/'+str(lineItem.id))
        if nauty.count() == 0:
            notification.save()
    data = {'usr': usr,'stlFileCheck': stlFileCheck, 'stlCheck': stlCheck, 'org': org, 'designFile': designFile, 'feedFile':feedFile, 'service_order': service_order, 'lineItem': lineItem, 'stlFile': stlFile, 'refer_id': refer_id, 'topcat': topcat}
    return render(request, 'LabOrder/lineOrderDetails.html', data)

def orthancdownloadGuideSecond(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    t = Timeout(read_timeout=1000, connection_timeout=1000)
    line_item = Suricalguide.objects.get(id=id)
    from orthanc_rest_client import Orthanc
    from requests.auth import HTTPBasicAuth
    auth = HTTPBasicAuth('dentread', 'dentread')
    import requests
    url = 'http://68.178.166.31:8042/patients/'+line_item.ParentStudy1+'/archive'
    return redirect(url)

def lineOrderDetailsDigitalLab(request, id1, id2):
    context= {}
    context['id1']= id1
    context['id2']= id2
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id1)
    lineItem = Prosthetic.objects.get(id=id2)
    allLineItem = Prosthetic.objects.filter(repid = id1)
    include = ['Implant Surgical Guide', 'Digital Lab Services']
    topcat = Topcat.objects.filter(topcat__in = include)
    selfStlFile =  IOSFile.objects.filter(repid= service_order.id).filter(sodrid= lineItem.id).count() == 0
    if selfStlFile:
        stlFile = IOSFile.objects.filter(repid= service_order.id)
    else:     
        stlFile= IOSFile.objects.filter(repid= service_order.id).filter(sodrid= lineItem.id)
    designFile = DesignFile.objects.filter(repid= service_order.id).filter(sodrid= lineItem.id)
    feedFile = FeedFile.objects.filter(repid=service_order.id).filter(sodrid= lineItem.id)
    refer_id = Organisation.objects.get(id=lineItem.orgid_id).orgname
    sent_org = Organisation.objects.get(id=lineItem.orgid_id).id
    lab_id= Organisation.objects.get(id=service_order.reforgid).orgname
    if lineItem.status == 'Submit Order':
        for i in stlFile: 
            if i.fileStatus != None:
                lineItem.status= 'Validate Data'
                service_order.status = 'In Process'
                service_order.badge = 'badge badge-warning'
                service_order.save()
                lineItem.save()
    overallStatus = 0
    noOfFiles = 0
    for i in stlFile:
        noOfFiles += 1
        if i.fileStatus == 'Approve':
            overallStatus += 1
    if overallStatus == noOfFiles:
        lineItem.fileStatus = 'Approved'
    else:
        lineItem.fileStatus = ''
    lineItem.save()

    numberCompleted = 0
    totalNumbers = 0
    for item in allLineItem:
        totalNumbers += 1
        if item.status == 'Order Delivered':
            numberCompleted += 1

    if totalNumbers == numberCompleted: 
        service_order.status = 'Completed'
        service_order.badge = 'badge badge-success'
        service_order.save()
    
    fileName = ''
    stlCheck = False
    for i in feedFile:
        fileName = i.fileName
        if fileName.endswith('.stl'):
            stlCheck = True
    print('stlCheck', stlCheck)
    data={'stlCheck': stlCheck,'usr': usr, 'org': org, 'designFile': designFile, 'feedFile':feedFile, 'lab_id':lab_id, 'service_order': service_order, 'lineItem': lineItem,'refer_id': refer_id, 'stlFile': stlFile, 'topcat': topcat}
    
    return render(request, 'LabOrder/lineOrderDetailsDigitalLab.html', data)

def orderPickup(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    lineItem = Prosthetic.objects.get(id = id)
    service_order = ServiceOrder.objects.get(id = lineItem.repid)
    ref_org = Organisation.objects.get(id=service_order.reforgid)
    ref_orgname = ref_org.orgname
    refOrgEmail = ref_org.email
    if request.method == 'POST':
        orderPickup = request.POST.get('orderPickup')
        orderPickupTime = request.POST.get('orderPickupTime')
        lineItem.orderPickup = orderPickup
        lineItem.orderPickupTime = orderPickupTime
        lineItem.status = 'Pickup Order'
        lineItem.save()
        notification = Notification(orgid = org, sendTo = lineItem.orgid_id, serviceOrderId = service_order.id, sent = True, service = 'Digital Lab Services', user = usr.name, event = 'ORDER PICKED-UP', details = 'Your order for the order ID: ' +str(service_order.order_id) + ' and line item ID: '+str(lineItem.item_id) + ' has been picked-up by the lab ' + str(ref_orgname)+ '.', date = datetime.now(), hyperLink = '/lineOrderDetailsDigital/'+str(service_order.id)+'/'+str(lineItem.id))
        notification.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def orderPickupAvailablity(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    lineItem = Prosthetic.objects.get(id = id)
    service_order = ServiceOrder.objects.get(id = lineItem.repid)
    ref_org = Organisation.objects.get(id=service_order.reforgid)
    ref_orgname = ref_org.orgname
    refOrgEmail = ref_org.email
    if request.method == 'POST':
        availableForCollection = request.POST.get('orderPickup')
        lineItem.availableForCollection = availableForCollection
        lineItem.save()
        notification = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Digital Lab Services', user = usr.name, event = 'PICKUP REQUEST', details = 'You are requested to pick the Re-shared Data for the order ID:' + str(service_order.order_id) + ' and line item ID: '+str(lineItem.item_id) + ', from '+str(org.address), date = datetime.now(), hyperLink = '/lineOrderDetailsDigitalLab/'+str(service_order.id)+'/'+str(lineItem.id))
        notification.save()
        # Send Mail code
        connection = mail.get_connection()
        connection.open()
        from1 = 'info.dentread@gmail.com'
        subject = 'Pickup Request'
        message = 'Dear \nLab Admin, ' +str(ref_orgname) +' \nYou are requested to pick the order (Non-digital Data) for the order ID:' + str(service_order.order_id) + ', from '+str(org.address)
        email2 = refOrgEmail
        # email2 = 'souravmahato7643@gmail.com'
        emailForPickup = mail.EmailMessage(subject, message, from1, [email2], connection = connection)   
        try:
            emailForPickup.send()
            connection.close()
        except Exception as e:
            message = e
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def fabricationComplete(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    lineItem = Prosthetic.objects.get(id = id)
    service_order = ServiceOrder.objects.get(id = lineItem.repid)
    if request.method == 'POST':
        fabricationComplete = request.POST.get('fabricationComplete')
        lineItem.fabricationComplete = fabricationComplete
        lineItem.status = 'Production Complete'
        lineItem.save()
        notification = Notification(orgid = org, sendTo = lineItem.orgid_id, serviceOrderId = service_order.id, sent = True, service = 'Digital Lab Services', user = usr.name, event = 'FABRICATION COMPLETED', details = 'The Fabrication for your order with order ID: ' +str(service_order.order_id) + ' and line item ID: '+str(lineItem.item_id) + ' has been completed by the lab.', date = datetime.now(), hyperLink = '/lineOrderDetailsDigital/'+str(service_order.id)+'/'+str(lineItem.id))
        notification.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def fabricationCompleteSurgi(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    lineItem = Suricalguide.objects.get(id = id)
    service_order = ServiceOrder.objects.get(id = lineItem.repid)
    if request.method == 'POST':
        fabricationComplete = request.POST.get('fabricationComplete')
        lineItem.fabricationComplete = fabricationComplete
        lineItem.status = 'Production Complete'
        lineItem.save()
        notification = Notification(orgid = org, sendTo = lineItem.orgid_id, serviceOrderId = service_order.id, sent = True, service = 'Implant Surgical Guide', user = usr.name, event = 'FABRICATION COMPLETED', details = 'The Fabrication for your order with order ID: ' +str(service_order.order_id) + ' and line item ID: '+str(lineItem.item_id) + ' has been completed .', date = datetime.now(), hyperLink = '/lineOrderDetails/'+str(service_order.id)+'/'+str(lineItem.id))
        notification.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def dataApprove(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    lineItem = Prosthetic.objects.get(id = id)
    service_order = ServiceOrder.objects.get(id = lineItem.repid)
    if request.method == 'POST':
        dataApprove = request.POST.get('selectBox')
        dataApproveComment = request.POST.get('comment')
        lineItem.dataApprove = dataApprove
        lineItem.dataApproveComment = dataApproveComment
        if dataApprove == 'Approve':
            lineItem.status = 'Validate Data'
        else: 
            lineItem.orderPickup = False
            lineItem.availableForCollection = False
            lineItem.status = 'Submit Order'
            notification = Notification(orgid = org, sendTo = lineItem.orgid_id, serviceOrderId = lineItem.repid, sent = True, service = 'Digital Lab Services', user = usr.name, event = 'DATA REJECTED', details = 'Your given data is not sufficient for the order ID: ' +str(service_order.order_id)+ ' and the line item ID: '+str(lineItem.item_id) + ' .Please Re-share the data.', date = datetime.now(), hyperLink = '/lineOrderDetailsDigital/'+str(service_order.id)+'/'+ str(lineItem.id))
            notification.save()
            #Send Mail code
            clinicEmail = Organisation.objects.get(id = service_order.orgid_id).email
            details = EmailNotification.objects.get(eventCode = 'DRET-0017')
            connection = mail.get_connection()
            connection.open()
            orderId = str(service_order.order_id)
            labName = str(org.orgname)
            reason = dataApproveComment
            firstId = str(service_order.id)
            secId = str(lineItem.id)
            from1 = 'info.dentread@gmail.com'
            subject = details.subject%(labName, orderId)
            message = "Dear User, \n" + details.clinicSide%(orderId, reason, firstId, secId) +" \nThank You \nDentread"
            email1 = clinicEmail
            # email1 = 'souravmahato7643@gmail.com'
            mymailExicute = mail.EmailMessage(subject, message, from1, [email1], connection=connection)
            try:
                mymailExicute.send()
                connection.close()
            except Exception as e:
                message = e  
        lineItem.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def lineOrderDetailsLab(request, id1, id2):
    context= {}
    context['id1']= id1
    context['id2']= id2
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id1)
    lineItem = Suricalguide.objects.get(id=id2)
    allLineItem = Suricalguide.objects.filter(repid=id1)
    
    include = ['Implant Surgical Guide', 'Digital Lab Services']
    include2 = ["Digital Lab Services"]
    page = ''
    if org.orgtype == 'Domain Owner':
        topcat = Topcat.objects.filter(status = 'Active').exclude(topcat__in = include2)
        page = 'LabOrder/lineOrderDetailsLabSecond.html'
    else:
        topcat = Topcat.objects.filter(topcat__in = include)
        page = 'LabOrder/lineOrderDetailsLab.html'
    stlFile = IOSFile.objects.filter(repid= service_order.id)
    designFile = DesignFile.objects.filter(repid= service_order.id).filter(sodrid= lineItem.id)
    fileName2 = ''
    stlFileCheck = False
    if designFile:
        for i in designFile:
            fileName2 = i.fileName
            if fileName2.endswith('.stl'):
                stlFileCheck = True
    feedFile = FeedFile.objects.filter(repid = service_order.id).filter(sodrid = lineItem.id)
    fileName = ''
    stlCheck = False
    if feedFile:
        for i in feedFile:
            fileName = i.fileName
            if fileName.endswith('.stl'):
                stlCheck = True
    
    if lineItem.status == 'Order Delivered' and lineItem.orderDeliverConfirmationL == 'True':
        lineItem.status = 'Order Completed'
        lineItem.save()
        
    if lineItem.output_type == 'Prosthetically Driven Planning' and lineItem.status == 'Share Plane':
        lineItem.status = 'Order Completed'
        lineItem.save()
    
    if lineItem.output_type == 'Plan + Design (.stl)' and lineItem.status == 'Share Design':
        lineItem.status = 'Order Completed'
        lineItem.save()
    countIOSFile = IOSFile.objects.filter(repid = service_order.id).count()
    countIOSFileApprove = IOSFile.objects.filter(repid = service_order.id).filter(fileStatus = 'Approve').count()
    
    if lineItem.status == 'Submit Order' and service_order.file != None and service_order.file1 != None and service_order.fileStatus == 'Approve' and service_order.fileStatus1 == 'Approve' and countIOSFile == countIOSFileApprove:
        lineItem.status = 'Validate Data'
        lineItem.save()
    elif lineItem.status == 'Submit Order' and service_order.file != None and service_order.fileStatus == 'Approve' and countIOSFile == countIOSFileApprove:
        lineItem.status = 'Validate Data'
        lineItem.save()
    elif lineItem.status == 'Submit Order' and service_order.file1 != None and service_order.fileStatus1 == 'Approve' and countIOSFile == countIOSFileApprove:
        lineItem.status = 'Validate Data'
        lineItem.save()
    else:
        lineItem.status = lineItem.status
        lineItem.save()     
    

    numberCompleted = 0
    totalNumbers = 0
    for item in allLineItem:
        totalNumbers += 1
        if item.status == 'Order Completed':
            numberCompleted += 1

    if totalNumbers == numberCompleted: 
        service_order.status = 'Completed'
        service_order.badge = 'badge badge-success'
        service_order.save()

    if lineItem.status == 'Submit Order':
        if lineItem.fileStatus != None:
            if lineItem.fileStatus1 != None:
                lineItem.status = 'Validate Data'
                
            else:
                for i in stlFile: 
                    if i.fileStatus != None:
                        lineItem.status= 'Validate Data'
            lineItem.save()
            

    if lineItem.status == "Validate Data":
        service_order.status = 'In Process'
        service_order.badge = 'badge badge-warning'
        if lineItem.fileStatus == "Approve" and lineItem.fileStatus1 == "Approve":
            for i in feedFile:
                if i.upload == 'Uploaded':
                    lineItem.status = "Share Plan"
                    lineItem.save()   
        else:
            for i in stlFile:
                if i.fileStatus == 'Approve' and lineItem.fileStatus == 'Approve':
                    for i in feedFile: 
                        if i.upload == 'Uploaded':
                            lineItem.status = 'Share Plan'
                            lineItem.save()

    refer_id = Organisation.objects.get(id=lineItem.orgid_id).orgname
    lab_id = Organisation.objects.get(id=service_order.reforgid).orgname
    data={'usr': usr, 'stlFileCheck': stlFileCheck, 'stlCheck': stlCheck,'org': org, 'designFile': designFile, 'feedFile':feedFile, 'lab_id':lab_id, 'service_order': service_order, 'lineItem': lineItem,'refer_id': refer_id, 'stlFile': stlFile, 'topcat': topcat}
    return render(request, page, data)

def imageAnalysis_status(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id)
    patient = Patient.objects.get(id=service_order.pid)
    pros = ImageAnalysis.objects.filter(repid=service_order.id)
    comment = Comments.objects.filter(repid=service_order.id)
    log = ServiceLog.objects.filter(repid = service_order.id)
    data = {'page': 'status', 'usr':usr, 'org':org,  'topcat':topcat, 'pros':pros, 'patient':patient, 'service_order':service_order,'log': log, 'comment':comment}
    return render(request, 'ImageAnalysis/image_status.html', data)

def image_post_comment(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order=ServiceOrder.objects.get(id=id)
    pros=ImageAnalysis.objects.filter(repid=service_order.id)
    patient=Patient.objects.get(id=service_order.pid)
    if request.method == 'POST':
        comment = request.POST.get('comment')
        name=usr.name
        comments=Comments(name=name, comment=comment, orgid = org, repid=service_order.id)
        comments.save()
        notification = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Image Analysis Report', user = usr.name, event = 'COMMENT', details = 'A new comment added by the Clinic '+ str(org.orgname) + ' for the order ID: '+str(service_order.order_id) , date = datetime.now(), hyperLink = '/case_Details/'+str(service_order.id)+'/2')
        notification.save()
        return redirect('/imageAnalysis_status/'+str(service_order.id))
    data = {'page': 'status', 'usr': usr, 'org': org, 'topcat': topcat, 'pros': pros, 'patient': patient,
            'service_order': service_order}
    return render(request, 'ImageAnalysis/image_status.html', data)

def implantPlanning_status(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id)
    patient = Patient.objects.get(id=service_order.pid)
    pros = ImplantPlanning.objects.filter(repid=service_order.id)
    comment = Comments.objects.filter(repid=service_order.id)
    data = {'page': 'status', 'usr':usr, 'org':org,  'topcat':topcat, 'pros': pros, 'patient':patient, 'service_order':service_order, 'comment':comment}
    return render(request, 'Implant_Planning/implant_status.html', data)

def guideStatus(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id)
    patient = Patient.objects.get(id=service_order.pid)
    pros = Suricalguide.objects.filter(repid=service_order.id)
    comment = Comments.objects.filter(repid=service_order.id)
    refer_id = Organisation.objects.get(id=service_order.reforgid).orgname
    data = {'page': 'status', 'usr':usr, 'org':org,  'topcat':topcat, 'pros': pros,'refer_id': refer_id, 'patient':patient, 'service_order':service_order, 'comment':comment}
    return render(request, 'LabOrder/GuideOrderStatus.html', data)

def DigitalLabStatus(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id)
    patient = Patient.objects.get(id=service_order.pid)
    pros = Prosthetic.objects.filter(repid=service_order.id)
    comment = Comments.objects.filter(repid=service_order.id)
    refer_id = Organisation.objects.get(id=service_order.reforgid).orgname
    iosFile = IOSFile.objects.filter(repid=service_order.repid)
    
    # Price Symbol
    icon = ''
    currency = ''
    if org.country == 'IN':
        currency = 'price'
        icon = '<i class="fa-solid fa-indian-rupee-sign"></i>'
    else:
        currency = 'dollarPrice'
        icon = '<i class="fa-solid fa-dollar-sign"></i>'
    
    data = {'page': 'status', 'usr':usr, 'org':org,'icon': icon, 'currency': currency, 'iosFile': iosFile, 'topcat':topcat, 'pros': pros,'refer_id': refer_id, 'patient':patient, 'service_order':service_order, 'comment':comment}
    return render(request, 'LabOrder/DigitalLabOrderStatus.html', data)

def implantPlanning_post_comment(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id)
    pros = ImplantPlanning.objects.filter(repid=service_order.id)
    
    patient = Patient.objects.get(id=service_order.pid)
    if request.method == 'POST':
        comment = request.POST.get('comment')
        name=usr.name
        comments=Comments(name=name, comment=comment,orgid = org, repid = service_order.id)
        comments.save()
        service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy, log = "EDITED SERVICE ORDER", message = 'Post a Comment')
        notification = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Implant Planning Report', user = usr.name, event = 'COMMENT', details = 'A new comment added by the Clinic '+ str(org.orgname) + ' for the order ID: '+str(service_order.order_id) , date = datetime.now(), hyperLink = '/case_DetailsPlanning/'+str(service_order.id)+'/3')
        service_log.save()
        notification.save()
        return redirect('/implantPlanning_status/'+str(service_order.id))
    data = {'page': 'status', 'usr': usr, 'org': org, 'topcat': topcat, 'pros': pros, 'patient': patient,'service_order': service_order}
            
    return render(request, 'Implant_Planning/implant_status.html', data)

def guidePostComment(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id)
    pros = Suricalguide.objects.filter(repid=service_order.id)
    patient = Patient.objects.get(id=service_order.pid)
    if request.method == 'POST':
        comment = request.POST.get('comment')
        name=usr.name
        comments=Comments(name=name, comment=comment,orgid = org, repid = service_order.id)
        comments.save()
        service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy, log = "EDITED SERVICE ORDER", message = 'Post a Comment')
        notification = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Implant Surgical Guide', user = usr.name, event = 'COMMENT', details = 'A new comment added by the Clinic '+ str(org.orgname) + ' for the order ID: '+str(service_order.order_id) , date = datetime.now(), hyperLink = '/case_DetailsGuide/'+str(service_order.id)+'/4')
        service_log.save()
        notification.save()
        return redirect('/guideStatus/'+str(service_order.id))
    data = {'page': 'status', 'usr': usr, 'org': org, 'topcat': topcat, 'pros': pros, 'patient': patient,'service_order': service_order}
            
    return render(request, 'LabOrder/GuideOrderStatus.html', data)

def digitalLabComment(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id)
    pros = Prosthetic.objects.filter(repid=service_order.id)
    patient = Patient.objects.get(id=service_order.pid)
    if request.method == 'POST':
        comment = request.POST.get('comment')
        name=usr.name
        comments=Comments(name=name, comment=comment,orgid = org, repid = service_order.id)
        comments.save()
        service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy, log = "EDITED SERVICE ORDER", message = 'Post a Comment')
        notification = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Digital Lab Services', user = usr.name, event = 'COMMENT', details = 'A new comment added by the Clinic '+ str(org.orgname) + ' for the order ID: '+str(service_order.order_id) , date = datetime.now(), hyperLink = '/case_DetailsLab/'+str(service_order.id)+'/5')
        service_log.save()
        notification.save()
        return redirect('/DigitalLabStatus/'+str(service_order.id))
    data = {'page': 'status', 'usr': usr, 'org': org, 'topcat': topcat, 'pros': pros, 'patient': patient,'service_order': service_order}
            
    return render(request, 'LabOrder/DigitalLabOrderStatus.html', data)

def radio_post_comment(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order=ServiceOrder.objects.get(id=id)
    pros = RadiologycalServices.objects.filter(repid=service_order.id)
    patient=Patient.objects.filter(id=service_order.pid)
    if request.method == 'POST':
        comment = request.POST.get('comment')
        name=usr.name
        comments=Comments(name=name, comment=comment,orgid=org, repid=service_order.id)
        comments.save()
        notification = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Radiological Report', user = usr.name, event = 'COMMENT', details = 'A new comment added by the Clinic '+ str(org.orgname) + ' for the order ID: '+str(service_order.order_id) , date = datetime.now(), hyperLink = '/radiological_Details/'+str(service_order.id)+'/1')
        notification.save()
        return redirect('/radiological_status/'+str(service_order.id))
    data = {'page': 'status', 'usr': usr, 'org': org, 'topcat': topcat, 'pros': pros, 'patient': patient,
            'service_order': service_order}
    return render(request, 'Radiological_Service/radio_status.html', data)

def post_comment(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order=ServiceOrder.objects.get(id=id)
    pros=Suricalguide.objects.filter(repid=service_order.id)
    patient=Patient.objects.filter(id=service_order.pid)
    if request.method == 'POST':
        comment = request.POST.get('comment')
        name=usr.name
        comments=Comments(name=name, comment=comment, repid=service_order.id)
        comments.save()
        return redirect('/surgi_status/'+str(service_order.id))
    data = {'page': 'status', 'usr': usr, 'org': org, 'topcat': topcat, 'pros': pros, 'patient': patient,
            'service_order': service_order}
    return render(request, 'surgi_status.html', data)



def downloaGuideDesign(request, pk, id1, id2):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=pk)
    line_item = Suricalguide.objects.get(id=id1)
    patient = Patient.objects.get(id=service_order.pid)
    cfile = DesignFile.objects.get(id=id2)
    url = cfile.file.url
    # main = '/' + url
    # return redirect(main)
    return redirect(url)

from .serializers import DesignFileSerializers
def viewGuideDesignAPI(request, pk, id1):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    lineItem = Suricalguide.objects.get(id = id1)
    if request.method =='GET':
        files = DesignFile.objects.filter(repid=service_order.repid).filter(sodrid = lineItem.id)
        file = DesignFileSerializers(files, many=True)
        return JsonResponse(file.data, safe=False)

def uploadGuideDesign(request, pk, id1):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    image = Suricalguide.objects.get(id = id1)
    if request.method == "POST" and 'file' in request.FILES:
        for f in request.FILES.getlist('file'):
            sfile = DesignFile(file=f, repid = service_order.id, sodrid = image.sodrid, orgid=org,fileName = f.name, size = f.size,upload = 'Uploaded' )
            sfile.save()
            image.status = 'Share Design'
            image.save()
            notification = Notification(orgid = org, sendTo = service_order.orgid_id, serviceOrderId = service_order.id, sent = True, service = 'Implant Surgical Guide', user = usr.name, event = 'DESIGN UPLOADED', details = 'The Lab has uploaded the design for the order ID: '+ str(service_order.order_id) + ' and the line item ID: '+str(image.item_id) + '. View the design.', date = datetime.now(), hyperLink = '/lineOrderDetails/'+str(service_order.id)+'/'+str(image.id))
            notification.save()
            html = "<html><body>It is now %s.</body></html>"
            return HttpResponse(html)
            
def uploadGuideDesignAgain(request, pk, id1, id2):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    lineItem = Suricalguide.objects.get(id = id1)
    designFile = DesignFile.objects.get(id=id2)
    if request.method == "POST" and 'file' in request.FILES:
        for f in request.FILES.getlist('file'):
            designFile.file = f
            designFile.fileName = f.name
            designFile.size = f.size
            designFile.upload = 'Uploaded'
            designFile.fileStatus = ''
            designFile.fileComment = ''
            designFile.date = datetime.now()
            designFile.save()
            lineItem.designUploadDate = datetime.now()
            lineItem.save()
            notification = Notification(orgid = org, sendTo = service_order.orgid_id, serviceOrderId = service_order.id, sent = True, service = 'Implant Surgical Guide', user = usr.name, event = 'DESIGN RE-UPLOADED', details = 'The Lab has re-uploaded the design for the order ID: '+ str(service_order.order_id) + ' and the line item ID: '+str(lineItem.item_id) + '. View the design.', date = datetime.now(), hyperLink = '/lineOrderDetails/'+str(service_order.id)+'/'+str(lineItem.id))
            notification.save()
            html = "<html><body>It is now %s.</body></html>"
            return HttpResponse(html)
# has context menu

def imaging_reg(request):
    if request.method == 'POST':
        orgname = request.POST.get('orgname')
        orgemail = request.POST.get('orgemail')
        address = request.POST.get('address')
        orgcontact = request.POST.get('orgcontact')
        gstin = request.POST.get('gstin')
        name = request.POST.get('name')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        username = request.POST.get('email')
        password = request.POST.get('password')
        country = request.POST.get('country')
        city = request.POST.get('cityname')
        state = request.POST.get('statename')
        pincode = request.POST.get('pincode')
        org = Organisation(orgname=orgname, email=orgemail, address=address, contact=orgcontact, gstin=gstin, country=country, state=state, pincode=pincode, city=city, 
                           orgtype="Imaging Centre")
        checkorg = Organisation.objects.filter(email=orgemail).first()
        if checkorg:
            context = {'message': 'Organisation details already exists', 'class': 'danger', 'page': 'Registration'}
            return render(request, 'imaging_reg.html', context)
        else:
            org.save()
        checkusr = Users.objects.filter(username=username).first()
        if checkusr:
            context = {'message': 'User details already exists', 'class': 'danger', 'page': 'Registration'}
            return render(request, 'Imaging_reg.html', context)
        else:
            usr = Users(name=name, email=email, contact=contact, password=password, usertype="Admin",
                        username=email, orgid=org, department="Admin", status="Active")
            usr.save()
            user = User.objects.create_user(username, email, password)
            user.save()
            org.regby_email = usr.email
            org.regby_userid = usr.id
            org.ctperson_name = usr.name
            org.save()
            usr = authenticate(username=username, password=password)
            login(request, usr)
            return redirect('/login_imaging')
    page = "Registration"
    data = {'page': page}
    return render(request, 'imaging_reg.html', data)

def clinic_reg(request):
    details = EmailNotification.objects.get(eventCode = 'DRET-0001')
    if request.method == 'POST' and  request.FILES:
        doc = request.FILES
        logo = doc['logo']
        orgname = request.POST.get('name')
        orgemail = request.POST.get('email')
        orgcontact = request.POST.get('mobile')
        name = 'Admin'
        email = request.POST.get('email')
        contact = request.POST.get('mobile')
        username = request.POST.get('email')
        password = request.POST.get('password')
        mobileVer = str(contact)
        chkContact = Users.objects.filter(contact=contact).first()
        if chkContact:
            context = {'message': 'Mobile Number Already Exists', 'class': 'danger', 'page': 'Registration'}
            return render(request, 'clinic_reg.html', context)
        org = Organisation(orgname=orgname, email=orgemail, contact = orgcontact, country='IN', orgtype="Dental Clinic", status="Active")
        checkorg = Organisation.objects.filter(email = orgemail).first()
        if checkorg:
            context = {'message': 'Organisation details already exists', 'class': 'danger', 'page': 'Registration'}
            return render(request, 'clinic_reg.html', context)
        else:
            org.save()
        checkusr = Users.objects.filter(username=username).first()
        if checkusr:
            context = {'message': 'User details already exists', 'class': 'danger', 'page': 'Registration'}
            return render(request, 'clinic_reg.html', context)
        else:
            usr = Users(name=name, email=email, contact = contact, password = password, usertype="Admin", username=email,
                        orgid=org, department="Admin", status="Active")
            usr.save()
            user = User.objects.create_user(username, email, password)
            user.save()
            org.regby_email = usr.email
            org.regby_userid = usr.id
            gotUserId = usr.id
            gotOrgId = org.id
            org.ctperson_name = usr.name
            org.org_id = str(org.id)
            org.admin = usr.id
            org.save()
            usr = authenticate(username=username, password=password)
            login(request, usr)
            
            # Send Mail code
            details = EmailNotification.objects.get(eventCode = 'DRET-0001')
            var1 = str(org.orgname)
            connection = mail.get_connection()
            connection.open()
            from1 = 'info.dentread@gmail.com'
            subject = details.subject%(var1)
            message = details.clinicSide%(var1) + '\nThank You \nDentread'
            message2 = details.adminSide%(var1)
            email1 = user.email
            email2 = 'support@dentread.com'
            mymailExicute = mail.EmailMessage(subject, message, from1, [email1], connection=connection)
            mymailExicute2 = mail.EmailMessage(subject, message2, from1, [email2], connection=connection)
            try:
                mymailExicute.send()
                mymailExicute2.send()
                connection.close()
            except Exception as e:
                message = e
            eventLog = EventLog(eventCode = 'DRET-0001', event = subject , log = 'A new Organisation Registered to dentread, named : ' + str(org.orgname), orgId = gotOrgId, userId = gotUserId, time = datetime.now())
            try:
                eventLog.save()
            except Exception as ex:
                eventMessage = ex
            return redirect('/login_clinic')
        
    if request.method == 'POST':
        orgname = request.POST.get('name')
        orgemail = request.POST.get('email')
        orgcontact = request.POST.get('mobile')
        name = 'Admin'
        email = request.POST.get('email')
        contact = request.POST.get('mobile')
        username = request.POST.get('email')
        password = request.POST.get('password')
        mobileVer = str(contact)
        chkContact = Users.objects.filter(contact=contact).first()
        if chkContact:
            context = {'message': 'Mobile Number Already Exists', 'class': 'danger', 'page': 'Registration'}
            return render(request, 'clinic_reg.html', context)
        
        org = Organisation(orgname=orgname, email=orgemail, contact = orgcontact, country ='IN', orgtype="Dental Clinic", status="Active")
        checkorg = Organisation.objects.filter(email=orgemail).first()
        if checkorg:
            context = {'message': 'Organisation details already exists', 'class': 'danger', 'page': 'Registration'}
            return render(request, 'clinic_reg.html', context)
        else:
            org.save()
        checkusr = Users.objects.filter(username=username).first()
        if checkusr:
            context = {'message': 'User details already exists', 'class': 'danger', 'page': 'Registration'}
            return render(request, 'clinic_reg.html', context)
        else:
            user = User.objects.create_user(username, email, password)
            user.save()
            usr = Users(name=name, email=email, contact=contact, password=password, usertype="Admin", username=email, user = user,
                        orgid=org, department="Admin", status="Active")
            usr.save()
            org.regby_email = usr.email
            org.regby_userid = usr.id
            gotUserId = usr.id
            gotOrgId = org.id
            org.ctperson_name = usr.name
            org.org_id = str(org.id)
            org.admin = usr.id
            org.save()
            usr = authenticate(username=username, password=password)
            login(request, usr)
            
            # Send Mail code
            details = EmailNotification.objects.get(eventCode = 'DRET-0001')
            var1 = str(org.orgname)
            connection = mail.get_connection()
            connection.open()
            from1 = 'info.dentread@gmail.com'
            subject = details.subject%(var1)
            message = details.clinicSide%(var1) + '\nThank You \nDentread'
            message2 = details.adminSide%(var1)
            email1 = user.email
            email2 = 'support@dentread.com'
            mymailExicute = mail.EmailMessage(subject, message, from1, [email1], connection=connection)
            mymailExicute2 = mail.EmailMessage(subject, message2, from1, [email2], connection=connection)
            try:
                mymailExicute.send()
                mymailExicute2.send()
                connection.close()
            except Exception as e:
                message = e
            eventLog = EventLog(eventCode = 'DRET-0001', event = subject , log = 'A new Organisation Registered to dentread, named : ' + str(org.orgname), orgId = gotOrgId, userId = gotUserId, time = datetime.now())
            try:
                eventLog.save()
            except Exception as ex:
                eventMessage = ex
            return redirect('/login_clinic')
    page = "Registration"
    data = {'page': page}
    return render(request, 'clinic_reg.html', data)


def viewStl(request, id, id1, id2, site, fileName):
    selfStlFile = IOSFile.objects.filter(repid=id).filter(sodrid = id1).count() == 0
    stlFile = ''
    if selfStlFile:
        stlFile = IOSFile.objects.filter(repid = id)
    else:
        stlFil = IOSFile.objects.filter(repid= id).filter(sodrid = id1)
    stlCheck = False
    if fileName.endswith('.stl'):
        stlCheck = True
    data = {'service_id': id, 'lineId': id1, 'itemId': id2, 'site': site, 'stlFile': stlFile, 'stlCheck': stlCheck}
    return render(request, 'viewStl.html', data)

def lab_reg(request):
    if request.method == 'POST' and  request.FILES:
        doc = request.FILES 
        customFile = doc['customFile']
        logo = doc['logo']
        orgname = request.POST.get('orgname')
        orgemail = request.POST.get('orgemail')
        address = request.POST.get('address')
        orgcontact = request.POST.get('orgcontact')
        gstin = request.POST.get('gstin')
        name = request.POST.get('name')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        username = request.POST.get('email')
        password = request.POST.get('password')
        country = request.POST.get('country')
        city = request.POST.get('cityname')
        state = request.POST.get('statename')
        pincode = request.POST.get('pincode')
        services = request.POST.get('services_offered')
        pan = request.POST.get('pan')
        cin = request.POST.get('cin')
        regNo = request.POST.get('regNo')
        bankName = request.POST.get('bankName')
        accountNumber = request.POST.get('accountNumber')
        ifscCode = request.POST.get('ifscCode')
        org = Organisation(orgname=orgname,pan=pan, cin=cin, regNo=regNo,ifscCode = ifscCode, logo=logo, bankName=bankName, accountNumber=accountNumber, customFile=customFile, email=orgemail, address = address + ', ' +str(city)+', ' + str(state)+ ', ' + str(country)+' '+'('+str(pincode)+')', offered_service = services, status = "Active", contact = orgcontact, gstin=gstin, country=country, state=state, city=city, pincode=pincode, 
                           orgtype="Dental Lab")
        checkorg = Organisation.objects.filter(email=orgemail).first()
        if checkorg:
            context = {'message': 'Organisation details already exists', 'class': 'danger', 'page': 'Registration'}
            return render(request, 'lab_reg.html', context)
        else:
            org.save()
        checkusr = Users.objects.filter(username=username).first()
        if checkusr:
            context = {'message': 'User details already exists', 'class': 'danger', 'page': 'Registration'}
            return render(request, 'lab_reg.html', context)
        else:
            usr = Users(name=name, email=email, contact=contact, password=password, usertype="Admin", username=email, orgid=org, department="Admin", status="Active")
            usr.save()
            user = User.objects.create_user(username, email, password)
            user.save()
            org.regby_email = usr.email
            org.regby_userid = usr.id
            gotUserId = usr.id
            gotOrgId = org.id
            org.ctperson_name = usr.name
            org.org_id = str(org.id)
            org.admin = usr.id
            org.save()
            usr = authenticate(username=username, password=password)
            login(request, usr)
            
            # Send Mail code
            details = EmailNotification.objects.get(eventCode = 'DRET-0001')
            var1 = str(org.orgname)
            connection = mail.get_connection()
            connection.open()
            from1 = 'info.dentread@gmail.com'
            subject = details.subject%(var1)
            message = details.clinicSide%(var1) + '\nThank You \nDentread'
            message2 = details.adminSide%(var1)
            email1 = user.email
            email2 = 'support@dentread.com'
            mymailExicute = mail.EmailMessage(subject, message, from1, [email1], connection=connection)
            mymailExicute2 = mail.EmailMessage(subject, message2, from1, [email2], connection=connection)
            try:
                mymailExicute.send()
                mymailExicute2.send()
                connection.close()
            except Exception as e:
                message = e
            eventLog = EventLog(eventCode = 'DRET-0001', event = subject , log = 'A new Organisation Registered to dentread, named : ' + str(org.orgname), orgId = gotOrgId, userId = gotUserId)
            try:
                eventLog.save()
            except Exception as ex:
                eventMessage = ex
            return redirect('/login_lab')
    page = "Registration"
    data = {'page': page}
    return render(request, 'lab_reg.html', data)


def radio_reg(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        address = request.POST.get('address')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        username = request.POST.get('email')
        dci=request.POST.get('dci')
        password = request.POST.get('password')
        country = request.POST.get('country')
        city = request.POST.get('cityname')
        state = request.POST.get('statename')
        pincode = request.POST.get('pincode')
        org = Organisation(orgname=name, email=email, address=address, contact=contact, country=country, city=city, state=state, pincode=pincode, 
                           orgtype="Radiologist")
        org.save()
        if org:
            usr = Users(name=name, email=email, contact=contact, password=password, usertype="Admin",
                        username=email,orgid=org, department="Admin", status="Active", dci=dci)
            usr.save()
        else:
            page = "Registration"
            data = {'page': page}
            return render(request, 'radio_reg.html', data)

        if usr:
            user = User.objects.create_user(username, email, password)
            user.save()
            org.ctperson_name=usr.name
            org.save()
            page = "Registration"
            data = {'page': page}
            usr = authenticate(username=username, password=password)
            login(request, usr)
            return redirect('/login_radio')
        else:
            page = "Registration"
            data = {'page': page}
            return render(request, 'radio_reg.html', data)
    page = "Registration"
    data = {'page': page, }
    return render(request, 'radio_reg.html', data)


def login_imaging(request):
    usr = Users.objects.get(username=request.user)
    org=Organisation.objects.get(id=usr.orgid_id)
    get_service_order=ServiceOrder.objects.filter(orgid=usr.orgid_id)
    today=datetime.today()
    main_service_order=get_service_order.filter(date=today)
    topcat = Topcat.objects.filter(status='Active').exclude(topcat='Digital Lab Services')
    btnchecked = 'todayFunction'    
    if request.method == 'POST':
        check1 = ""
        check2 = ""
        check3 = ""
        query_date = request.POST.get('query_date')
        if str(query_date)=="today":
            query_data = today
            check1 = 'checked'
        if str(query_date)=="yesterday":
            check2 = 'checked'
            query_data=today - timedelta(days=1)
            main_service_order=get_service_order.filter(date=query_data)
            btnchecked = 'yesterdayFunction'
        if str(query_date)=="thisweek":
            check3= 'checked'
            query_data = today - timedelta(weeks=1)
            main_service_order=get_service_order.filter(Q(date__gte=query_data))
            btnchecked = 'thisweekFunction'
        lab_data=main_service_order.filter(refstudy='Digital Lab Services')
        lab_pending = lab_data.filter(status='Pending').count()
        lab_inprogress = lab_data.filter(status='In Process').count()
        lab_completed = lab_data.filter(status='Completed').count()
        lab_total = lab_data.count()
        lab_context = {'lab_total': lab_total, 'lab_pending': lab_pending, 'lab_inprogress': lab_inprogress, 'lab_completed':lab_completed}
        
        radio_data = main_service_order.filter(refstudy='Radiological Report')
        radio_pending = radio_data.filter(status='Pending').count()
        radio_inprogress = radio_data.filter(status='In Process').count()
        radio_completed = radio_data.filter(status='Completed').count()
        radio_total = radio_data.count()
        radio_context = {'radio_pending': radio_pending, 'radio_inprogress': radio_inprogress, 'radio_completed': radio_completed, 'radio_total':radio_total}
        
        image_data = main_service_order.filter(refstudy='Image Analysis Report')
        image_pending = image_data.filter(status='Pending').count()
        image_inprogress = image_data.filter(status='In Process').count()
        image_completed = image_data.filter(status='Completed').count()
        image_total = image_data.count()
        image_context = {'image_pending': image_pending, 'image_inprogress': image_inprogress, 'image_completed': image_completed, 'image_total':image_total}
        
        guide_data = main_service_order.filter(refstudy='Implant Surgical Guide')
        guide_pending =guide_data.filter(status='Pending').count()
        guide_inprogress =guide_data.filter(status='In Process').count()
        guide_completed =guide_data.filter(status='Completed').count()
        guide_total =guide_data.count()
        guide_context = {'guide_pending': guide_pending, 'guide_inprogress': guide_inprogress, 'guide_completed': guide_completed, 'guide_total':guide_total}
        
        planning_data = main_service_order.filter(refstudy='Implant Planning Report')
        planning_pending = planning_data.filter(status='Pending').count()
        planning_inprogress = planning_data.filter(status='In Process').count()
        planning_completed = planning_data.filter(status='Completed').count()
        planning_total = planning_data.count()
        planning_context = {'planning_pending': planning_pending, 'planning_inprogress': planning_inprogress, 'planning_completed': planning_completed, 'planning_total': planning_total}
        
        today=datetime.today()
        appointment = Appointment.objects.all().filter(orgid=org).count()
        patient = Patient.objects.all().filter(orgid=org).count()
        business = ServiceOrder.objects.all().filter(orgid=org).aggregate(Sum('price'))
        amount=business['price__sum']
        data = {'usr': usr, 'message': 'You have signed in successfully', 'page': 'Dashboard', 'btnchecked': btnchecked, 'org':org,'topcat':topcat, 'appointment':appointment,'patient': patient, 'lab_total':lab_total,'amount': amount, 'planning_pending': planning_pending, 'planning_inprogress': planning_inprogress, 'planning_completed': planning_completed, 'planning_total': planning_total, 'lab_total': lab_total, 'lab_pending': lab_pending, 'lab_inprogress': lab_inprogress, 'lab_completed':lab_completed, 'guide_pending': guide_pending, 'guide_inprogress': guide_inprogress, 'guide_completed': guide_completed, 'guide_total':guide_total, 'image_pending': image_pending, 'image_inprogress': image_inprogress, 'image_completed': image_completed, 'image_total':image_total, 'radio_pending': radio_pending, 'radio_inprogress': radio_inprogress, 'radio_completed': radio_completed, 'radio_total':radio_total}
        return render(request, 'main_dashboard.html', data)
            
    
    
    lab_data=main_service_order.filter(refstudy='Digital Lab Services')
    lab_pending = lab_data.filter(status='Pending').count()
    lab_inprogress = lab_data.filter(status='In Process').count()
    lab_completed = lab_data.filter(status='Completed').count()
    lab_total = lab_data.count()
    lab_context = {'lab_total': lab_total, 'lab_pending': lab_pending, 'lab_inprogress': lab_inprogress, 'lab_completed':lab_completed}
    
    radio_data = main_service_order.filter(refstudy='Radiological Report')
    radio_pending = radio_data.filter(status='Pending').count()
    radio_inprogress = radio_data.filter(status='In Process').count()
    radio_completed = radio_data.filter(status='Completed').count()
    radio_total = radio_data.count()
    radio_context = {'radio_pending': radio_pending, 'radio_inprogress': radio_inprogress, 'radio_completed': radio_completed, 'radio_total':radio_total}
    
    image_data = main_service_order.filter(refstudy='Image Analysis Report')
    image_pending = image_data.filter(status='Pending').count()
    image_inprogress = image_data.filter(status='In Process').count()
    image_completed = image_data.filter(status='Completed').count()
    image_total = image_data.count()
    image_context = {'image_pending': image_pending, 'image_inprogress': image_inprogress, 'image_completed': image_completed, 'image_total':image_total}
    
    guide_data = main_service_order.filter(refstudy='Implant Surgical Guide')
    guide_pending =guide_data.filter(status='Pending').count()
    guide_inprogress =guide_data.filter(status='In Process').count()
    guide_completed =guide_data.filter(status='Completed').count()
    guide_total =guide_data.count()
    guide_context = {'guide_pending': guide_pending, 'guide_inprogress': guide_inprogress, 'guide_completed': guide_completed, 'guide_total':guide_total}
    
    planning_data= main_service_order.filter(refstudy='Implant Planning Report')
    planning_pending = planning_data.filter(status='Pending').count()
    planning_inprogress = planning_data.filter(status='In Process').count()
    planning_completed = planning_data.filter(status='Completed').count()
    planning_total = planning_data.count()
    planning_context = {'planning_pending': planning_pending, 'planning_inprogress': planning_inprogress, 'planning_completed': planning_completed, 'planning_total': planning_total}
    
    today=datetime.today()
    appointment = Appointment.objects.all().filter(orgid=org).filter(date=today).count()
    patient = Patient.objects.all().filter(orgid=org).count()
    business = Study.objects.all().filter(orgid=org).aggregate(Sum('price'))
    amount=business['price__sum']
    data = data = {'usr': usr, 'message': 'You have signed in successfully', 'page': 'Dashboard', 'btnchecked': btnchecked, 'org':org, 'topcat':topcat, 'appointment':appointment,'patient': patient,'amount': amount, 'planning_pending': planning_pending, 'planning_inprogress': planning_inprogress, 'planning_completed': planning_completed, 'planning_total': planning_total, 'lab_total': lab_total, 'lab_pending': lab_pending, 'lab_inprogress': lab_inprogress, 'lab_completed':lab_completed, 'guide_pending': guide_pending, 'guide_inprogress': guide_inprogress, 'guide_completed': guide_completed, 'guide_total':guide_total, 'image_pending': image_pending, 'image_inprogress': image_inprogress, 'image_completed': image_completed, 'image_total':image_total, 'radio_pending': radio_pending, 'radio_inprogress': radio_inprogress, 'radio_completed': radio_completed, 'radio_total':radio_total}
    return render(request, 'main_dashboard.html', data)


def dashboard_imaging(request):
    usr = Users.objects.get(username=request.user)
    org=Organisation.objects.get(id=usr.orgid_id)

    subs=Subscriptions.objects.filter(orgid=org).filter(status="Active").first()
    if subs:
        alert= "hidden"
    else:
        alert=""
    today=date.today()
    appointment=Appointment.objects.filter(orgid=org).filter(date=today).count()
    patient = Patient.objects.filter(orgid=org).filter(rdate=today).count()
    business=ServiceOrder.objects.filter(orgid=org).filter(date=today).aggregate(Sum('payable'))
    amount=business['payable__sum']
    
    data = {'usr': usr, 'page': 'Dashboard', 'alert':alert, 'org':org,'topcat':topcat, 'appointment':appointment, 'patient':patient, 'amount':amount}
    return render(request, 'main_dashboard.html', data)


def dashboard_clinic(request):
    usr = Users.objects.get(username=request.user)
    org=Organisation.objects.get(id=usr.orgid_id)
    data = {'usr': usr, 'page': 'Dashboard', 'org':org,'topcat':topcat}
    return render(request, 'main_dashboard.html', data)


def login_lab(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    exclude= ['Radiological Report', 'Image Analysis Report', 'Implant Planning Report', 'Digital Orthodontics']
    topcat = Topcat.objects.filter(status="Active").exclude(topcat__in = exclude)
    
    main_org_id = org.id
    parent_id = org.id
    branch = Organisation.objects.filter(parent_id = org.id)
    # get_service_order = ServiceOrder.objects.filter(reforgid = org.id)
    getLabData = Prosthetic.objects.filter(reforgid = org.id)
    
    getGuideData = Suricalguide.objects.filter(reforgid = org.id)
    get_ios = IOSFile.objects.filter(orgid = org).aggregate(Sum('size'))
    ios = get_ios['size__sum']
    if ios is None:
        ios = 0
    get_designFile = FeedFile.objects.filter(orgid = org).aggregate(Sum('size'))
    designFile = get_designFile['size__sum']
    if designFile is None:
        designFile = 0
    final_total_size = (ios + designFile)
    today = datetime.today()
    
    # Total IOSdata Count
    totalDigitalData =  ServiceOrder.objects.filter(reforgid = org.id).filter(preferredData = 'digitalData').filter(date=today).count()
    if totalDigitalData is None:
        totalDigitalData = 0
    totalNonDigitalData =  ServiceOrder.objects.filter(reforgid = org.id).filter(preferredData = 'nonDigitalData').filter(date=today).count()
    if totalNonDigitalData is None:
        totalNonDigitalData = 0
    
    #PaymentSummary
    mainTotal = ServiceOrder.objects.filter(reforgid = org.id).filter(paymentStatus__isnull = False).filter(date=today).aggregate(Sum('ref_price'))
    total = mainTotal['ref_price__sum']
    if total is None:
        total = 0
    mainPaid = ServiceOrder.objects.filter(reforgid = org.id).filter(paymentStatus = 'Paid').filter(date=today).aggregate(Sum('ref_price'))
    paid = mainPaid['ref_price__sum']
    if paid is None:
        paid = 0
    mainPosted = ServiceOrder.objects.filter(reforgid = org.id).filter(paymentStatus = 'Unpaid').filter(date=today).aggregate(Sum('ref_price'))
    posted = mainPosted['ref_price__sum']
    if posted is None:
        posted = 0
    
    # Today Data
    mainLabData = getLabData.filter(date=today)
    
    mainGuideData = getGuideData.filter(date=today)
    btnchecked = 'todayFunction'
    if request.method == 'POST':
        check1 = ""
        check2 = ""
        check3 = ""
        query_date = request.POST.get('query_date')
        filter_branch = request.POST.get('filter')
        if filter_branch != 0:
            main_org_id = filter_branch

        mainLabData = getLabData.filter(date=today)
        mainGuideData = getGuideData.filter(date=today)
        
        # Total IOSdata Count
        totalDigitalData =  ServiceOrder.objects.filter(reforgid = org.id).filter(preferredData = 'digitalData').filter(date=today).count()
        if totalDigitalData is None:
            totalDigitalData = 0
        totalNonDigitalData =  ServiceOrder.objects.filter(reforgid = org.id).filter(preferredData = 'nonDigitalData').filter(date=today).count()
        if totalNonDigitalData is None:
            totalNonDigitalData = 0
        
        #PaymentSummary
        mainTotal = ServiceOrder.objects.filter(reforgid = org.id).filter(paymentStatus__isnull = False).filter(date=today).aggregate(Sum('ref_price'))
        total = mainTotal['ref_price__sum']
        if total is None:
            total = 0
        mainPaid = ServiceOrder.objects.filter(reforgid = org.id).filter(paymentStatus = 'Paid').filter(date=today).aggregate(Sum('ref_price'))
        paid = mainPaid['ref_price__sum']
        if paid is None:
            paid = 0
        mainPosted = ServiceOrder.objects.filter(reforgid = org.id).filter(paymentStatus = 'Unpaid').filter(date=today).aggregate(Sum('ref_price'))
        posted = mainPosted['ref_price__sum']
        if posted is None:
            posted = 0
        if str(query_date)=="today":
            query_data = today
            check1 = 'checked'
        if str(query_date)=="yesterday":
            check2 = 'checked'
            btnchecked = 'yesterdayFunction'
            query_data = today - timedelta(days=1)
            mainLabData = getLabData.filter(date = query_data)
            mainGuideData = getGuideData.filter(date = query_data)
            #PaymentSummary
            mainTotal = ServiceOrder.objects.filter(reforgid = org.id).filter(paymentStatus__isnull = False).filter(date=query_data).aggregate(Sum('ref_price'))
            total = mainTotal['ref_price__sum']
            if total is None:
                total = 0
            mainPaid = ServiceOrder.objects.filter(reforgid = org.id).filter(paymentStatus = 'Paid').filter(date=query_data).aggregate(Sum('ref_price'))
            paid = mainPaid['ref_price__sum']
            if paid is None:
                paid = 0
            mainPosted = ServiceOrder.objects.filter(reforgid = org.id).filter(paymentStatus = 'Unpaid').filter(date=query_data).aggregate(Sum('ref_price'))
            posted = mainPosted['ref_price__sum']
            if posted is None:
                posted = 0
            # Total IOSdata Count
            totalDigitalData =  ServiceOrder.objects.filter(reforgid = org.id).filter(preferredData = 'digitalData').filter(date=query_data).count()
            if totalDigitalData is None:
                totalDigitalData = 0
            totalNonDigitalData =  ServiceOrder.objects.filter(reforgid = org.id).filter(preferredData = 'nonDigitalData').filter(date=query_data).count()
            if totalNonDigitalData is None:
                totalNonDigitalData = 0
        
        if str(query_date)=="thisweek":
            check3= 'checked'
            btnchecked = 'thisweekFunction'
            query_data = today - timedelta(weeks=1)
            # main_service_order = get_service_order.filter(Q(date__gte=query_data))
            mainLabData = getLabData.filter(Q(date__gte=query_data))
            mainGuideData = getGuideData.filter(Q(date__gte=query_data))
            
            # Total IOSdata Count
            totalDigitalData =  ServiceOrder.objects.filter(reforgid = org.id).filter(preferredData = 'digitalData').filter(date=query_data).count()
            if totalDigitalData is None:
                totalDigitalData = 0
            totalNonDigitalData =  ServiceOrder.objects.filter(reforgid = org.id).filter(preferredData = 'nonDigitalData').filter(date=query_data).count()
            if totalNonDigitalData is None:
                totalNonDigitalData = 0
            
            #PaymentSummary
            mainTotal = ServiceOrder.objects.filter(reforgid = org.id).filter(paymentStatus__isnull = False).filter(Q(date__gte=query_data)).aggregate(Sum('ref_price'))
            total = mainTotal['ref_price__sum']
            if total is None:
                total = 0
            mainPaid = ServiceOrder.objects.filter(reforgid = org.id).filter(paymentStatus = 'Paid').filter(Q(date__gte=query_data)).aggregate(Sum('ref_price'))
            paid = mainPaid['ref_price__sum']
            if paid is None:
                paid = 0
            mainPosted = ServiceOrder.objects.filter(reforgid = org.id).filter(paymentStatus = 'Unpaid').filter(Q(date__gte=query_data)).aggregate(Sum('ref_price'))
            posted = mainPosted['ref_price__sum']
            if posted is None:
                posted = 0
        corwnAndBridge = mainLabData.filter(item = 'Crown and Bridges')
        corwnAndBridge_pending = corwnAndBridge.filter(status='Submit Order').count()
        corwnAndBridge_inprogress = corwnAndBridge.filter(Q(status='Validate Data') | Q(status='Share Design') | Q(status='Review Design') | Q(status='Share Plan') | Q(status='Review Plan') | Q(status='Order Dispatched') | Q(status='Deliver Order')).count()
        corwnAndBridge_completed = corwnAndBridge.filter(status='Order Delivered').count()
        corwnAndBridge_onhold = corwnAndBridge.filter(status='Order Onhold').count()
        corwnAndBridge_cancelled = corwnAndBridge.filter(status='Order Cancelled').count()
        corwnAndBridge_total = corwnAndBridge.count()
        corwnAndBridge_context = {'corwnAndBridge_total': corwnAndBridge_total, 'corwnAndBridge_pending': corwnAndBridge_pending, 'corwnAndBridge_inprogress': corwnAndBridge_inprogress, 'corwnAndBridge_completed': corwnAndBridge_completed, 'corwnAndBridge_onhold': corwnAndBridge_onhold, 'corwnAndBridge_cancelled': corwnAndBridge_cancelled}
        
        
        implantCrown = mainLabData.filter(item = 'Implant Specific Section')
        implantCrown_pending = implantCrown.filter(status='Submit Order').count()
        implantCrown_inprogress = implantCrown.filter(Q(status='Validate Data') | Q(status='Share Design') | Q(status='Review Design') | Q(status='Share Plan') | Q(status='Review Plan') | Q(status='Order Dispatched') | Q(status='Deliver Order')).count()
        implantCrown_completed = implantCrown.filter(status='Order Delivered').count()
        implantCrown_onhold = implantCrown.filter(status='Order Onhold').count()
        implantCrown_cancelled = implantCrown.filter(status='Order Cancelled').count()
        implantCrown_total = implantCrown.count()
        implantCrown_context = {'implantCrown_total': implantCrown_total, 'implantCrown_cancelled': implantCrown_cancelled, 'implantCrown_onhold': implantCrown_onhold, 'implantCrown_pending': implantCrown_pending, 'implantCrown_inprogress': implantCrown_inprogress, 'implantCrown_completed': implantCrown_completed}
        
        customizedAbutment = mainLabData.filter(item = 'Removable Prosthesis')
        customizedAbutment_pending = customizedAbutment.filter(status='Submit Order').count()
        customizedAbutment_inprogress = customizedAbutment.filter(Q(status='Validate Data') | Q(status='Share Design') | Q(status='Review Design') | Q(status='Share Plan') | Q(status='Review Plan') | Q(status='Order Dispatched') | Q(status='Deliver Order')).count()
        customizedAbutment_completed = customizedAbutment.filter(status='Order Delivered').count()
        customizedAbutment_onhold = customizedAbutment.filter(status='Order Onhold').count()
        customizedAbutment_cancelled = customizedAbutment.filter(status='Order Cancelled').count()
        customizedAbutment_total = customizedAbutment.count()
        customizedAbutment_context = {'customizedAbutment_total': customizedAbutment_total, 'customizedAbutment_cancelled': customizedAbutment_cancelled, 'customizedAbutment_onhold': customizedAbutment_onhold, 'customizedAbutment_pending': customizedAbutment_pending, 'customizedAbutment_inprogress': customizedAbutment_inprogress, 'customizedAbutment_completed': customizedAbutment_completed}
        
        dentureComplete = mainLabData.filter(item = 'Precision Attachment')
        dentureComplete_pending = dentureComplete.filter(status='Submit Order').count()
        dentureComplete_inprogress = dentureComplete.filter(Q(status='Validate Data') | Q(status='Share Design') | Q(status='Review Design') | Q(status='Share Plan') | Q(status='Review Plan') | Q(status='Order Dispatched') | Q(status='Deliver Order')).count()
        dentureComplete_completed = dentureComplete.filter(status='Order Delivered').count()
        cdentureComplete_onhold = dentureComplete.filter(status='Order Onhold').count()
        dentureComplete_cancelled = dentureComplete.filter(status='Order Cancelled').count()
        dentureComplete_total = dentureComplete.count()
        dentureComplete_context = {'dentureComplete_total': dentureComplete_total, 'dentureComplete_cancelled': dentureComplete_cancelled, 'cdentureComplete_onhold': cdentureComplete_onhold, 'dentureComplete_inprogress': dentureComplete_inprogress, 'dentureComplete_pending': dentureComplete_pending, 'dentureComplete_completed': dentureComplete_completed}
        
        implantOverDenture = mainLabData.filter(item = 'Orthodontic and Pedodontic Appliances / Retainers')
        implantOverDenture_pending = implantOverDenture.filter(status='Submit Order').count()
        implantOverDenture_inprogress = implantOverDenture.filter(Q(status='Validate Data') | Q(status='Share Design') | Q(status='Review Design') | Q(status='Share Plan') | Q(status='Review Plan') | Q(status='Order Dispatched') | Q(status='Deliver Order')).count()
        implantOverDenture_completed = implantOverDenture.filter(status='Order Delivered').count()
        implantOverDenture_onhold = implantOverDenture.filter(status='Order Onhold').count()
        implantOverDenture_cancelled = implantOverDenture.filter(status='Order Cancelled').count()
        implantOverDenture_total = implantOverDenture.count()
        implantOverDenture_context = {'implantOverDenture_total': implantOverDenture_total, 'implantOverDenture_cancelled': implantOverDenture_cancelled, 'implantOverDenture_onhold': implantOverDenture_onhold, 'implantOverDenture_pending': implantOverDenture_pending, 'implantOverDenture_inprogress': implantOverDenture_inprogress, 'implantOverDenture_completed': implantOverDenture_completed}
        
        hybridDenture = mainLabData.filter(item = 'Miscellaneous')
        hybridDenture_pending = hybridDenture.filter(status='Submit Order').count()
        hybridDenture_inprogress = hybridDenture.filter(Q(status='Validate Data') | Q(status='Share Design') | Q(status='Review Design') | Q(status='Share Plan') | Q(status='Review Plan') | Q(status='Order Dispatched') | Q(status='Deliver Order')).count()
        hybridDenture_completed = hybridDenture.filter(status='Order Delivered').count()
        hybridDenture_onhold = hybridDenture.filter(status='Order Onhold').count()
        hybridDenture_cancelled = hybridDenture.filter(status='Order Cancelled').count()
        hybridDenture_total = hybridDenture.count()
        hybridDenture_context = {'hybridDenture_total': hybridDenture_total, 'hybridDenture_cancelled': hybridDenture_cancelled, 'hybridDenture_onhold': hybridDenture_onhold, 'hybridDenture_pending': hybridDenture_pending, 'hybridDenture_inprogress': hybridDenture_inprogress, 'hybridDenture_completed': hybridDenture_completed}
        
        other = mainLabData.filter(item = 'Other')
        other_pending = other.filter(status='Submit Order').count()
        other_inprogress = other.filter(Q(status='Validate Data') | Q(status='Share Design') | Q(status='Review Design') | Q(status='Share Plan') | Q(status='Review Plan') | Q(status='Order Dispatched') | Q(status='Deliver Order')).count()
        other_completed = other.filter(status='Order Delivered').count()
        other_onhold = other.filter(status='Order Onhold').count()
        other_cancelled = other.filter(status='Order Cancelled').count()
        other_total = other.count()
        other_context = {'other_total': other_total, 'other_cancelled': other_cancelled, 'other_onhold': other_onhold, 'other_pending': other_pending, 'other_inprogress': other_inprogress, 'other_completed': other_completed}
        
        guide_pending = mainGuideData.filter(status='Submit Order').count()
        guide_inprogress = mainGuideData.filter(Q(status='Validate Data') | Q(status='Share Design') | Q(status='Review Design') | Q(status='Share Plan') | Q(status='Review Plan') | Q(status='Order Dispatched') | Q(status='Deliver Order')).count()
        guide_completed = mainGuideData.filter(status='Order Cancelled').count()
        guide_onhold = mainGuideData.filter(status='Order Onhold').count()
        guide_cancelled = mainGuideData.filter(status='Order Cancelled').count()
        guide_total = mainGuideData.count()
        guide_context = {'guide_pending': guide_pending, 'guide_onhold': guide_onhold, 'guide_cancelled': guide_cancelled, 'guide_inprogress': guide_inprogress, 'guide_completed': guide_completed, 'guide_total':guide_total}

        data = {'usr': usr, 'org':org, 'branch': branch, 'main_org_id': main_org_id, 'message': 'You have signed in successfully', 'page': 'Dashboard', 'final_total_size': final_total_size, 'btnchecked': btnchecked, 'topcat':topcat, 'totalDigitalData': totalDigitalData, 'totalNonDigitalData': totalNonDigitalData, 'paid': paid, 'posted': posted,
                'corwnAndBridge_total': corwnAndBridge_total, 'corwnAndBridge_pending': corwnAndBridge_pending, 'corwnAndBridge_inprogress': corwnAndBridge_inprogress, 'corwnAndBridge_completed': corwnAndBridge_completed, 'corwnAndBridge_onhold': corwnAndBridge_onhold, 'corwnAndBridge_cancelled': corwnAndBridge_cancelled, 'total': total,
                'implantCrown_total': implantCrown_total, 'implantCrown_cancelled': implantCrown_cancelled, 'implantCrown_onhold': implantCrown_onhold, 'implantCrown_pending': implantCrown_pending, 'implantCrown_inprogress': implantCrown_inprogress, 'implantCrown_completed': implantCrown_completed,
                'customizedAbutment_total': customizedAbutment_total, 'customizedAbutment_cancelled': customizedAbutment_cancelled, 'customizedAbutment_onhold': customizedAbutment_onhold, 'customizedAbutment_pending': customizedAbutment_pending, 'customizedAbutment_inprogress': customizedAbutment_inprogress, 'customizedAbutment_completed': customizedAbutment_completed,
                'dentureComplete_total': dentureComplete_total, 'dentureComplete_cancelled': dentureComplete_cancelled, 'cdentureComplete_onhold': cdentureComplete_onhold, 'dentureComplete_inprogress': dentureComplete_inprogress, 'dentureComplete_pending': dentureComplete_pending, 'dentureComplete_completed': dentureComplete_completed,
                'implantOverDenture_total': implantOverDenture_total, 'implantOverDenture_cancelled': implantOverDenture_cancelled, 'implantOverDenture_onhold': implantOverDenture_onhold, 'implantOverDenture_pending': implantOverDenture_pending, 'implantOverDenture_inprogress': implantOverDenture_inprogress, 'implantOverDenture_completed': implantOverDenture_completed,
                'hybridDenture_total': hybridDenture_total, 'hybridDenture_cancelled': hybridDenture_cancelled, 'hybridDenture_onhold': hybridDenture_onhold, 'hybridDenture_pending': hybridDenture_pending, 'hybridDenture_inprogress': hybridDenture_inprogress, 'hybridDenture_completed': hybridDenture_completed,
                'other_total': other_total, 'other_cancelled': other_cancelled, 'other_onhold': other_onhold, 'other_pending': other_pending, 'other_inprogress': other_inprogress, 'other_completed': other_completed,
                'guide_pending': guide_pending, 'guide_onhold': guide_onhold, 'guide_cancelled': guide_cancelled, 'guide_inprogress': guide_inprogress, 'guide_completed': guide_completed, 'guide_total':guide_total}
        return render(request, 'dental_lab_dashboard.html', data)
            
    
    
    corwnAndBridge = mainLabData.filter(item = 'Crown and Bridges')
    corwnAndBridge_pending = corwnAndBridge.filter(status='Submit Order').count()
    corwnAndBridge_inprogress = corwnAndBridge.filter(Q(status='Validate Data') | Q(status='Share Design') | Q(status='Review Design') | Q(status='Share Plan') | Q(status='Review Plan') | Q(status='Order Dispatched') | Q(status='Deliver Order')).count()
    corwnAndBridge_completed = corwnAndBridge.filter(status='Order Delivered').count()
    corwnAndBridge_onhold = corwnAndBridge.filter(status='Order Onhold').count()
    corwnAndBridge_cancelled = corwnAndBridge.filter(status='Order Cancelled').count()
    corwnAndBridge_total = corwnAndBridge.count()
    corwnAndBridge_context = {'corwnAndBridge_total': corwnAndBridge_total, 'corwnAndBridge_pending': corwnAndBridge_pending, 'corwnAndBridge_inprogress': corwnAndBridge_inprogress, 'corwnAndBridge_completed': corwnAndBridge_completed, 'corwnAndBridge_onhold': corwnAndBridge_onhold, 'corwnAndBridge_cancelled': corwnAndBridge_cancelled}
    
    
    implantCrown = mainLabData.filter(item = 'Implant Specific Section')
    implantCrown_pending = implantCrown.filter(status='Submit Order').count()
    implantCrown_inprogress = implantCrown.filter(Q(status='Validate Data') | Q(status='Share Design') | Q(status='Review Design') | Q(status='Share Plan') | Q(status='Review Plan') | Q(status='Order Dispatched') | Q(status='Deliver Order')).count()
    implantCrown_completed = implantCrown.filter(status='Order Delivered').count()
    implantCrown_onhold = implantCrown.filter(status='Order Onhold').count()
    implantCrown_cancelled = implantCrown.filter(status='Order Cancelled').count()
    implantCrown_total = implantCrown.count()
    implantCrown_context = {'implantCrown_total': implantCrown_total, 'implantCrown_cancelled': implantCrown_cancelled, 'implantCrown_onhold': implantCrown_onhold, 'implantCrown_pending': implantCrown_pending, 'implantCrown_inprogress': implantCrown_inprogress, 'implantCrown_completed': implantCrown_completed}
    
    customizedAbutment = mainLabData.filter(item = 'Removable Prosthesis')
    customizedAbutment_pending = customizedAbutment.filter(status='Submit Order').count()
    customizedAbutment_inprogress = customizedAbutment.filter(Q(status='Validate Data') | Q(status='Share Design') | Q(status='Review Design') | Q(status='Share Plan') | Q(status='Review Plan') | Q(status='Order Dispatched') | Q(status='Deliver Order')).count()
    customizedAbutment_completed = customizedAbutment.filter(status='Order Delivered').count()
    customizedAbutment_onhold = customizedAbutment.filter(status='Order Onhold').count()
    customizedAbutment_cancelled = customizedAbutment.filter(status='Order Cancelled').count()
    customizedAbutment_total = customizedAbutment.count()
    customizedAbutment_context = {'customizedAbutment_total': customizedAbutment_total, 'customizedAbutment_cancelled': customizedAbutment_cancelled, 'customizedAbutment_onhold': customizedAbutment_onhold, 'customizedAbutment_pending': customizedAbutment_pending, 'customizedAbutment_inprogress': customizedAbutment_inprogress, 'customizedAbutment_completed': customizedAbutment_completed}
    
    dentureComplete = mainLabData.filter(item = 'Precision Attachment')
    dentureComplete_pending = dentureComplete.filter(status='Submit Order').count()
    dentureComplete_inprogress = dentureComplete.filter(Q(status='Validate Data') | Q(status='Share Design') | Q(status='Review Design') | Q(status='Share Plan') | Q(status='Review Plan') | Q(status='Order Dispatched') | Q(status='Deliver Order')).count()
    dentureComplete_completed = dentureComplete.filter(status='Order Delivered').count()
    cdentureComplete_onhold = dentureComplete.filter(status='Order Onhold').count()
    dentureComplete_cancelled = dentureComplete.filter(status='Order Cancelled').count()
    dentureComplete_total = dentureComplete.count()
    dentureComplete_context = {'dentureComplete_total': dentureComplete_total, 'dentureComplete_cancelled': dentureComplete_cancelled, 'cdentureComplete_onhold': cdentureComplete_onhold, 'dentureComplete_inprogress': dentureComplete_inprogress, 'dentureComplete_pending': dentureComplete_pending, 'dentureComplete_completed': dentureComplete_completed}
    
    implantOverDenture = mainLabData.filter(item = 'Orthodontic and Pedodontic Appliances / Retainers')
    implantOverDenture_pending = implantOverDenture.filter(status='Submit Order').count()
    implantOverDenture_inprogress = implantOverDenture.filter(Q(status='Validate Data') | Q(status='Share Design') | Q(status='Review Design') | Q(status='Share Plan') | Q(status='Review Plan') | Q(status='Order Dispatched') | Q(status='Deliver Order')).count()
    implantOverDenture_completed = implantOverDenture.filter(status='Order Delivered').count()
    implantOverDenture_onhold = implantOverDenture.filter(status='Order Onhold').count()
    implantOverDenture_cancelled = implantOverDenture.filter(status='Order Cancelled').count()
    implantOverDenture_total = implantOverDenture.count()
    implantOverDenture_context = {'implantOverDenture_total': implantOverDenture_total, 'implantOverDenture_cancelled': implantOverDenture_cancelled, 'implantOverDenture_onhold': implantOverDenture_onhold, 'implantOverDenture_pending': implantOverDenture_pending, 'implantOverDenture_inprogress': implantOverDenture_inprogress, 'implantOverDenture_completed': implantOverDenture_completed}
    
    hybridDenture = mainLabData.filter(item = 'Miscellaneous')
    hybridDenture_pending = hybridDenture.filter(status='Submit Order').count()
    hybridDenture_inprogress = hybridDenture.filter(Q(status='Validate Data') | Q(status='Share Design') | Q(status='Review Design') | Q(status='Share Plan') | Q(status='Review Plan') | Q(status='Order Dispatched') | Q(status='Deliver Order')).count()
    hybridDenture_completed = hybridDenture.filter(status='Order Delivered').count()
    hybridDenture_onhold = hybridDenture.filter(status='Order Onhold').count()
    hybridDenture_cancelled = hybridDenture.filter(status='Order Cancelled').count()
    hybridDenture_total = hybridDenture.count()
    hybridDenture_context = {'hybridDenture_total': hybridDenture_total, 'hybridDenture_cancelled': hybridDenture_cancelled, 'hybridDenture_onhold': hybridDenture_onhold, 'hybridDenture_pending': hybridDenture_pending, 'hybridDenture_inprogress': hybridDenture_inprogress, 'hybridDenture_completed': hybridDenture_completed}
    
    other = mainLabData.filter(type = 'Other')
    other_pending = other.filter(status='Submit Order').count()
    other_inprogress = other.filter(Q(status='Validate Data') | Q(status='Share Design') | Q(status='Review Design') | Q(status='Share Plan') | Q(status='Review Plan') | Q(status='Order Dispatched') | Q(status='Deliver Order')).count()
    other_completed = other.filter(status='Order Delivered').count()
    other_onhold = other.filter(status='Order Onhold').count()
    other_cancelled = other.filter(status='Order Cancelled').count()
    other_total = other.count()
    other_context = {'other_total': other_total, 'other_cancelled': other_cancelled, 'other_onhold': other_onhold, 'other_pending': other_pending, 'other_inprogress': other_inprogress, 'other_completed': other_completed}
    
    guide_pending = mainGuideData.filter(status='Submit Order').count()
    guide_inprogress = mainGuideData.filter(Q(status='Validate Data') | Q(status='Share Design') | Q(status='Review Design') | Q(status='Share Plan') | Q(status='Review Plan') | Q(status='Order Dispatched') | Q(status='Deliver Order')).count()
    guide_completed = mainGuideData.filter(status='Order Cancelled').count()
    guide_onhold = mainGuideData.filter(status='Order Onhold').count()
    guide_cancelled = mainGuideData.filter(status='Order Cancelled').count()
    guide_total = mainGuideData.count()
    guide_context = {'guide_pending': guide_pending, 'guide_onhold': guide_onhold, 'guide_cancelled': guide_cancelled, 'guide_inprogress': guide_inprogress, 'guide_completed': guide_completed, 'guide_total':guide_total}
    
    data = {'usr': usr, 'org':org, 'branch': branch,'main_org_id':main_org_id, 'message': 'You have signed in successfully', 'page': 'Dashboard','final_total_size': final_total_size, 'topcat':topcat, 'btnchecked': btnchecked, 'totalDigitalData': totalDigitalData, 'totalNonDigitalData': totalNonDigitalData, 'paid': paid, 'posted': posted,
            'corwnAndBridge_total': corwnAndBridge_total, 'corwnAndBridge_pending': corwnAndBridge_pending, 'corwnAndBridge_inprogress': corwnAndBridge_inprogress, 'corwnAndBridge_completed': corwnAndBridge_completed, 'corwnAndBridge_onhold': corwnAndBridge_onhold, 'corwnAndBridge_cancelled': corwnAndBridge_cancelled, 'total': total,
            'implantCrown_total': implantCrown_total, 'implantCrown_cancelled': implantCrown_cancelled, 'implantCrown_onhold': implantCrown_onhold, 'implantCrown_pending': implantCrown_pending, 'implantCrown_inprogress': implantCrown_inprogress, 'implantCrown_completed': implantCrown_completed,
            'customizedAbutment_total': customizedAbutment_total, 'customizedAbutment_cancelled': customizedAbutment_cancelled, 'customizedAbutment_onhold': customizedAbutment_onhold, 'customizedAbutment_pending': customizedAbutment_pending, 'customizedAbutment_inprogress': customizedAbutment_inprogress, 'customizedAbutment_completed': customizedAbutment_completed,
            'dentureComplete_total': dentureComplete_total, 'dentureComplete_cancelled': dentureComplete_cancelled, 'cdentureComplete_onhold': cdentureComplete_onhold, 'dentureComplete_inprogress': dentureComplete_inprogress, 'dentureComplete_pending': dentureComplete_pending, 'dentureComplete_completed': dentureComplete_completed,
            'implantOverDenture_total': implantOverDenture_total, 'implantOverDenture_cancelled': implantOverDenture_cancelled, 'implantOverDenture_onhold': implantOverDenture_onhold, 'implantOverDenture_pending': implantOverDenture_pending, 'implantOverDenture_inprogress': implantOverDenture_inprogress, 'implantOverDenture_completed': implantOverDenture_completed,
            'hybridDenture_total': hybridDenture_total, 'hybridDenture_cancelled': hybridDenture_cancelled, 'hybridDenture_onhold': hybridDenture_onhold, 'hybridDenture_pending': hybridDenture_pending, 'hybridDenture_inprogress': hybridDenture_inprogress, 'hybridDenture_completed': hybridDenture_completed,
            'other_total': other_total, 'other_cancelled': other_cancelled, 'other_onhold': other_onhold, 'other_pending': other_pending, 'other_inprogress': other_inprogress, 'other_completed': other_completed,
            'guide_pending': guide_pending, 'guide_onhold': guide_onhold, 'guide_cancelled': guide_cancelled, 'guide_inprogress': guide_inprogress, 'guide_completed': guide_completed, 'guide_total':guide_total}
    return render(request, 'dental_lab_dashboard.html', data)


def login_radio(request):
    usr = Users.objects.get(username=request.user)
    data = {'usr': usr, 'message': 'You have signed in successfully', 'page':'Dashboard','topcat':topcat}
    return render(request, 'Radiologist_dashboard.html', data)




def login_dentread(request):
    maincat = ['Radiology', 'Implantology', 'Digital Lab Services']
    topcat = Topcat.objects.filter(maincat__in = maincat)
    if request.method == "POST":
        maincat = ['Radiology', 'Implantology', 'Digital Lab Services']
        topcat = Topcat.objects.filter(maincat__in = maincat)
        username = request.POST.get('username')
        password = request.POST.get('password')
        mobile = request.POST.get('mobile')
        otp = str(request.POST.get('otp1')) + str(request.POST.get('otp2')) + str(request.POST.get('otp3')) + str(request.POST.get('otp4'))
        if username:
            usr = Users.objects.filter(username=username).first()
            gotUserId = ''
            gotUserName = ''
            gotOrgId = ''
            try:   
                gotUserId = usr.id
                gotUserName = usr.name
            except Exception as exc:
                print(exc)
                message = 'Please create an account on Dentread, before you try to login.'
            
            if usr:
                org = Organisation.objects.get(id=usr.orgid_id)
                gotOrgId = org.id
            else:
                context = {'message': 'Invalid Credentials', 'class': 'danger', 'page': 'Signin','topcat':topcat}
                return render(request, 'login_dentread.html', context)
            orgtype = str(org.orgtype)
            if orgtype == "Imaging Centre":
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    eventLog = EventLog(eventCode = 'DRET-0002', event = 'Successfull Login' , log = str(gotUserName) + ' Logged in Successfully.', orgId = gotOrgId, userId = gotUserId, time = datetime.now())
                    try:
                        eventLog.save()
                    except Exception as e:
                        message = e
                    return redirect('/login_imaging')
                else:
                    context = {'message': 'Invalid Credentials', 'class': 'danger', 'page': 'Signin','topcat':topcat}
                    return render(request, 'login_dentread.html', context)
            if orgtype == "Dental Lab":
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    eventLog2 = EventLog(eventCode = 'DRET-0002', event = 'Successfull Login' , log = str(gotUserName) + ' Logged in Successfully.', orgId = gotOrgId, userId = gotUserId, time = datetime.now())
                    try:
                        eventLog2.save()
                    except Exception as e:
                        message = e
                    return redirect('/login_lab')
                else:
                    context = {'message': 'Invalid Credentials', 'class': 'danger', 'page': 'Signin','topcat':topcat}
                    return render(request, 'login_dentread.html', context)

            if orgtype == "Dental Clinic":
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    eventLog3 = EventLog(eventCode = 'DRET-0002', event = 'Successfull Login' , log = str(gotUserName) + ' Logged in Successfully.', orgId = gotOrgId, userId = gotUserId, time = datetime.now())
                    try:
                        eventLog3.save()
                    except Exception as e:
                        message = e
                        
                    return redirect('/login_clinic')
                else:
                    context = {'message': 'Invalid Credentials', 'class': 'danger', 'page': 'Signin','topcat':topcat}
                    return render(request, 'login_dentread.html', context)
            if orgtype == "Dental Clinic Branch":
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    eventLog4 = EventLog(eventCode = 'DRET-0002', event = 'Successfull Login' , log = str(gotUserName) + ' Logged in Successfully.', orgId = gotOrgId, userId = gotUserId, time = datetime.now())
                    try:
                        eventLog4.save()
                    except Exception as e:
                        message = e
                    return redirect('/login_clinic')
                else:
                    context = {'message': 'Invalid Credentials', 'class': 'danger', 'page': 'Signin','topcat':topcat}
                    return render(request, 'login_dentread.html', context)
            if orgtype == "Radiologist":
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    eventLog5 = EventLog(eventCode = 'DRET-0002', event = 'Successfull Login' , log = str(gotUserName) + ' Logged in Successfully.', orgId = gotOrgId, userId = gotUserId, time = datetime.now())
                    try:
                        eventLog5.save()
                    except Exception as e:
                        message = e
                    return redirect('/login_radio')
                else:
                    context = {'message': 'Invalid Credentials', 'class': 'danger', 'page': 'Signin','topcat':topcat}
                    return render(request, 'login_dentread.html', context)
        else:
            usr = Users.objects.filter(contact = mobile).first()
            username = ''
            password = ''
            if usr:
                org = Organisation.objects.get(id = usr.orgid_id)
                myUser = Users.objects.get(contact = mobile)
                token = myUser.otp
                username = myUser.username
                password = myUser.password
                gotOrgId = org.id
                gotUserId = ''
                gotUserName = ''
                gotOrgId = ''
                try:   
                    gotUserId = usr.id
                    gotUserName = usr.name
                except Exception as exc:
                    print(exc)
                    message = 'Please create an account on Dentread, before you try to login.'
            else:
                context = {'message': 'Invalid Credentials', 'class': 'danger', 'page': 'Signin'}
                return render(request, 'login_dentread.html', context)
            orgtype = str(org.orgtype)

            if token == otp:
                if orgtype == "Imaging Centre":
                    user = authenticate(username=username, password=password)
                    if user is not None:
                        login(request, user)
                        delToken = Users.objects.get(username = username)
                        delToken.otp = ''
                        delToken.save()
                        eventLog = EventLog(eventCode = 'DRET-0002', event = 'Successfull Login' , log = str(gotUserName) + ' Logged in Successfully.', orgId = gotOrgId, userId = gotUserId, time = datetime.now())
                        try:
                            eventLog.save()
                        except Exception as e:
                            message = e
                        return redirect('/login_imaging')
                    else:
                        context = {'message': 'Invalid Credentials', 'class': 'danger', 'page': 'Signin','topcat':topcat}
                        return render(request, 'login_dentread.html', context)
                if orgtype == "Dental Lab":
                    user = authenticate(username=username, password=password)
                    if user is not None:
                        login(request, user)
                        delToken = Users.objects.get(username = username)
                        delToken.otp = ''
                        delToken.save()
                        eventLog2 = EventLog(eventCode = 'DRET-0002', event = 'Successfull Login' , log = str(gotUserName) + ' Logged in Successfully.', orgId = gotOrgId, userId = gotUserId, time = datetime.now())
                        try:
                            eventLog2.save()
                        except Exception as e:
                            message = e
                        return redirect('/login_lab')
                    else:
                        context = {'message': 'Invalid Credentials', 'class': 'danger', 'page': 'Signin','topcat':topcat}
                        return render(request, 'login_dentread.html', context)
                    
                if orgtype == "Dental Clinic":
                    user = authenticate(username=username, password=password)
                    if user is not None:
                        login(request, user)
                        delToken = Users.objects.get(username = username)
                        delToken.otp = ''
                        delToken.save()
                        eventLog3 = EventLog(eventCode = 'DRET-0002', event = 'Successfull Login' , log = str(gotUserName) + ' Logged in Successfully.', orgId = gotOrgId, userId = gotUserId, time = datetime.now())
                        try:
                            eventLog3.save()
                        except Exception as e:
                            message = e
                            
                        return redirect('/login_clinic')
                    else:
                        print('There')
                        context = {'message': 'Invalid Credentials', 'class': 'danger', 'page': 'Signin','topcat':topcat}
                        return render(request, 'login_dentread.html', context)
                if orgtype == "Dental Clinic Branch":
                    user = authenticate(username=username, password=password)
                    if user is not None:
                        login(request, user)
                        delToken = Users.objects.get(username = username)
                        delToken.otp = ''
                        delToken.save()
                        eventLog4 = EventLog(eventCode = 'DRET-0002', event = 'Successfull Login' , log = str(gotUserName) + ' Logged in Successfully.', orgId = gotOrgId, userId = gotUserId, time = datetime.now())
                        try:
                            eventLog4.save()
                        except Exception as e:
                            message = e
                        return redirect('/login_clinic')
                    else:
                        context = {'message': 'Invalid Credentials', 'class': 'danger', 'page': 'Signin','topcat':topcat}
                        return render(request, 'login_dentread.html', context)
                if orgtype == "Radiologist":
                    user = authenticate(username=username, password=password)
                    if user is not None:
                        login(request, user)
                        delToken = Users.objects.get(username = username)
                        delToken.otp = ''
                        delToken.save()
                        eventLog5 = EventLog(eventCode = 'DRET-0002', event = 'Successfull Login' , log = str(gotUserName) + ' Logged in Successfully.', orgId = gotOrgId, userId = gotUserId, time = datetime.now())
                        try:
                            eventLog5.save()
                        except Exception as e:
                            message = e
                        return redirect('/login_radio')
                    else:
                        context = {'message': 'Invalid Credentials', 'class': 'danger', 'page': 'Signin','topcat':topcat}
                        return render(request, 'login_dentread.html', context)
            else:
                return render(request, 'login_dentread.html', {'message': 'Invalid OTP'})
            
    page = "Signin"
    data = {'page': page,'topcat':topcat}
    return render(request, 'login_dentread.html', data)


def myprofile(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    if org.orgtype == 'Dental Clinic' or org.orgtype == 'Dental Clinic Branch':
        topcat = Topcat.objects.filter(status='Active')
    elif org.orgtype == 'Domain Owner':
        exclude = ['Digital Lab Services']
        topcat = Topcat.objects.filter(status="Active").exclude(topcat__in = exclude)
    else:
        exclude = ['Radiological Report', 'Image Analysis Report', 'Implant Planning Report']
        topcat = Topcat.objects.filter(status='Active').exclude(topcat__in = exclude)
    data = {'usr': usr, 'org': org, 'page': 'My Profile','topcat': topcat}
    return render(request, 'myprofile.html', data)


def myprofile_dent(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    
    if org.orgtype == 'Dental Clinic' or org.orgtype == 'Dental Clinic Branch':
        topcat = Topcat.objects.filter(status='Active')
    elif org.orgtype == 'Domain Owner':
        exclude = ['Digital Lab Services']
        topcat = Topcat.objects.filter(status="Active").exclude(topcat__in = exclude)
    else:
        exclude = ['Radiological Report', 'Image Analysis Report', 'Implant Planning Report']
        topcat = Topcat.objects.filter(status='Active').exclude(topcat__in = exclude)
    data = {'usr': usr, 'org': org, 'page': 'My Profile','topcat':topcat}
    return render(request, 'myprofile_dent.html', data)


def myprofile_clinic(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    if org.orgtype == 'Dental Clinic' or org.orgtype == 'Dental Clinic Branch':
        topcat = Topcat.objects.filter(status='Active')
    elif org.orgtype == 'Domain Owner':
        exclude = ['Digital Lab Services']
        topcat = Topcat.objects.filter(status="Active").exclude(topcat__in = exclude)
    else:
        exclude = ['Radiological Report', 'Image Analysis Report', 'Implant Planning Report']
        topcat = Topcat.objects.filter(status='Active').exclude(topcat__in = exclude)
    data = {'usr': usr, 'org': org, 'page': 'My Profile','topcat':topcat}
    return render(request, 'myprofile_clinic.html', data)

def myprofile_radio(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    
    data = {'usr': usr, 'org': org, 'page': 'My Profile','topcat':topcat}
    return render(request, 'myprofile_radio.html', data)


def editprofile(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    if request.method == "POST" and 'propic' in request.FILES:
        doc = request.FILES
        pic = doc['propic']
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        department = request.POST.get('department')
        status = request.POST.get('status')

        usr.name = name
        usr.propic = pic
        usr.contact = contact
        usr.email = email
        usr.department = department
        usr.status = status
        usr.save()
        return redirect('/myprofile')

    if request.method == "POST":
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        department = request.POST.get('department')
        status = request.POST.get('status')
        usr.name = name
        usr.contact = contact
        usr.email = email
        usr.department = department
        usr.status = status
        usr.save()
        return redirect('/myprofile')

    data = {'usr': usr, 'org': org, 'page': 'Edit Profile','topcat':topcat}
    return render(request, 'editprofile.html', data)

def editprofile_radio(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    if request.method == "POST" and 'propic' in request.FILES:
        doc = request.FILES
        pic = doc['propic']
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        department = request.POST.get('department')
        status = request.POST.get('status')

        usr.name = name
        usr.propic = pic
        usr.contact = contact
        usr.email = email
        usr.department = department
        usr.status = status
        usr.save()
        return redirect('/myprofile_radio')

    if request.method == "POST":
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        department = request.POST.get('department')
        status = request.POST.get('status')
        usr.name = name
        usr.contact = contact
        usr.email = email
        usr.department = department
        usr.status = status
        usr.save()
        return redirect('/myprofile_radio')
    if request.method == "POST" and 'sign' in request.FILES:
        doc = request.FILES
        sgn = doc['sign']
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        department = request.POST.get('department')
        status = request.POST.get('status')

        usr.name = name
        usr.sign = sgn
        usr.contact = contact
        usr.email = email
        usr.department = department
        usr.status = status
        usr.save()
        return redirect('/myprofile_radio')

    data = {'usr': usr, 'org': org, 'page': 'Edit Profile','topcat':topcat}
    return render(request, 'editprofile_radio.html', data)

def editprofile_dent(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    if request.method == "POST" and 'propic' in request.FILES:
        doc = request.FILES
        pic = doc['propic']
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        department = request.POST.get('department')
        status = request.POST.get('status')

        usr.name = name
        usr.propic = pic
        usr.contact = contact
        usr.email = email
        usr.department = department
        usr.status = status
        usr.save()
        return redirect('/myprofile_dent')

    if request.method == "POST":
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        department = request.POST.get('department')
        status = request.POST.get('status')
        usr.name = name
        usr.contact = contact
        usr.email = email
        usr.department = department
        usr.status = status
        usr.save()
        return redirect('/myprofile_dent')

    data = {'usr': usr, 'org': org, 'page': 'Edit Profile','topcat':topcat}
    return render(request, 'editprofile_dent.html', data)


def editprofile_clinic(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    if request.method == "POST" and 'propic' in request.FILES:
        doc = request.FILES
        pic = doc['propic']
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        department = request.POST.get('department')
        status = request.POST.get('status')

        usr.name = name
        usr.propic = pic
        usr.contact = contact
        usr.email = email
        usr.department = department
        usr.status = status
        usr.save()
        return redirect('/myprofile_clinic')

    if request.method == "POST":
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        department = request.POST.get('department')
        status = request.POST.get('status')
        usr.name = name
        usr.contact = contact
        usr.email = email
        usr.department = department
        usr.status = status
        usr.save()
        return redirect('/myprofile_clinic')

    data = {'usr': usr, 'org': org, 'page': 'Edit Profile'}
    return render(request, 'editprofile_clinic.html', data)


def orgprofile(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    users = Users.objects.filter(orgid=org)
    if org.orgtype == "Dental Lab" or org.orgtype == "Dental Lab Branch":
        include = ['Implant Surgical Guide', 'Digital Lab Services']
        topcat = Topcat.objects.filter(topcat__in = include)
    else:
        topcat = Topcat.objects.filter(status = 'Active')
    data = {'usr': usr, 'org': org, 'users': users, 'topcat': topcat, 'page': 'Organisation Profile'}

    return render(request, 'orgprofile.html', data)

def userdetails(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    users = Users.objects.get(id=id)
    data = {'usr': usr, 'org': org, 'users': users, 'page': 'User Profile'}

    return render(request, 'userdetails.html', data)


def orgprofile_dent(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    users = Users.objects.filter(orgid=org)
    topcat = Topcat.objects.filter(status = 'Active')
    
    if org.orgtype == "Dental Lab" or org.orgtype == "Dental Lab Branch":
        include = ['Implant Surgical Guide', 'Digital Lab Services']
        topcat = Topcat.objects.filter(status = 'Active').filter(topcat__in = include)
    elif org.orgtype == "Domain Owner":
        include = [ 'Digital Lab Services']
        topcat = Topcat.objects.filter(status = 'Active').exclude(topcat__in = include)
    else:
        topcat = topcat
        
    data = {'usr': usr, 'org': org, 'topcat': topcat, 'users': users, 'page': 'Organisation Profile'}

    return render(request, 'orgprofile_dent.html', data)


def orgprofile_clinic(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    users = Users.objects.filter(orgid=org)
    topcat = Topcat.objects.filter(status = 'Active')
    
    if org.orgtype == "Dental Lab" or org.orgtype == "Dental Lab Branch":
        include = ['Implant Surgical Guide', 'Digital Lab Services']
        topcat = Topcat.objects.filter(status = 'Active').filter(topcat__in = include)
    elif org.orgtype == "Domain Owner":
        include = [ 'Digital Lab Services']
        topcat = Topcat.objects.filter(status = 'Active').exclude(topcat__in = include)
    else:
        topcat = topcat
    data = {'usr': usr, 'org': org, 'topcat': topcat, 'users': users, 'page': 'Organisation Profile'}

    return render(request, 'orgprofile_clinic.html', data)


def orgdetails(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    organisation = Organisation.objects.get(id=id)
    topup = organisation.topUp
    check1 = ''
    check2 = ''
    check3 = ''
    if organisation.topUp == 50000:
        check1 = 'checked'
    elif organisation.topUp == 75000:
        check2 = 'checked'
    else:
        check3 = 'checked'
    topcat = Topcat.objects.filter(status = 'Active')
    if org.orgtype == "Dental Lab" or org.orgtype == "Dental Lab Branch":
        include = ['Implant Surgical Guide', 'Digital Lab Services']
        topcat = Topcat.objects.filter(status = 'Active').filter(topcat__in = include)
    elif org.orgtype == "Domain Owner":
        include = [ 'Digital Lab Services']
        topcat = Topcat.objects.filter(status = 'Active').exclude(topcat__in = include)
    else:
        topcat = topcat
    users = Users.objects.filter(orgid=organisation)
    data = {'usr': usr, 'org': org, 'users': users, 'check1': check1, 'topcat': topcat, 'check2': check2, 'check3': check3, 'page': 'Organisation Profile', 'organisation':organisation}

    return render(request, 'orgdetails.html', data)



def orginvoices(request, id):
    usr = Users.objects.get(username=request.user)
    org=Organisation.objects.get(id=usr.orgid_id)
    organisation = Organisation.objects.get(id=id)
    service_orders = ServiceOrder.objects.filter(orgid=organisation).filter(reforgid=org.id)
    today = datetime.today()
    check1 = "checked"
    td_service_orders = service_orders.filter(orgid=organisation).filter(date=today)
    for i in td_service_orders:
        i.referto = Organisation.objects.get(id=i.reforgid).orgname

    amount = td_service_orders.aggregate(Sum('ref_price'))
    total = amount['ref_price__sum']
    if total is None:
        total = 0

    cs = td_service_orders.filter(mode="Cash").aggregate(Sum('payable'))
    cash = cs['payable__sum']
    if cash is None:
        cash = 0

    cd = td_service_orders.filter(mode="Card").aggregate(Sum('payable'))
    card = cd['payable__sum']
    if card is None:
        card = 0

    on = td_service_orders.filter(mode="Online").aggregate(Sum('payable'))
    online = on['payable__sum']
    if online is None:
        online = 0

    if request.method == "POST":
        check1 = ""
        check2 = ""
        check3 = ""
        dat = request.POST.get('dat')
        fd = request.POST.get('fromdate')
        td = request.POST.get('todate')
        if dat == "Today":
            data = today
            check1 = "checked"
            nd_service_orders = service_orders.filter(Q(date=data))
        if dat == "Yesterday":
            data = today - timedelta(days=1)
            check2 = "checked"
            nd_service_orders = service_orders.filter(Q(date=data))
        if dat == "Thisweek":
            data = today - timedelta(weeks=1)
            nd_service_orders = service_orders.filter(Q(date__gte=data))
            check3 = "checked"
        if dat == "":
            data = None

        if data is None:
            nd_service_orders = service_orders.filter(date__range=[fd, td])

        amount = nd_service_orders.aggregate(Sum('ref_price'))
        total = amount['ref_price__sum']
        if total is None:
            total = 0

        cs = nd_service_orders.filter(mode="Cash").aggregate(Sum('payable'))
        cash = cs['payable__sum']
        if cash is None:
            cash = 0

        cd = nd_service_orders.filter(mode="Card").aggregate(Sum('payable'))
        card = cd['payable__sum']
        if card is None:
            card = 0

        on = nd_service_orders.filter(mode="Online").aggregate(Sum('payable'))
        online = on['payable__sum']
        if online is None:
            online = 0

        for i in nd_service_orders:
            i.referto = Organisation.objects.get(id=i.reforgid).orgname

        return render(request, 'orginvoices.html',
                      {'service_orders': nd_service_orders, 'total': total, 'cash': cash, 'card': card, 'online': online, 'usr': usr,
                       'org': org,
                       'check1': check1, 'check2': check2, 'check3': check3, 'page': 'Referral Invoices', 'organisation':organisation})

    return render(request, 'orginvoices.html',
                  {'service_orders': td_service_orders, 'total': total, 'cash': cash, 'card': card, 'online': online, 'usr': usr,
                   'org': org,
                   'check1': check1, 'page': 'Referral Invoices', 'organisation':organisation})



def editorgprofile(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    users = Users.objects.filter(orgid=org)
    data = {'usr': usr, 'org': org, 'users': users, 'page': 'Edit Org Profile'}
    if request.method == "POST" and 'logo' in request.FILES:
        doc = request.FILES
        pic = doc['logo']
        regFile = doc['regFile']
        gstin = doc['gstinFile']
        orgname = request.POST.get('orgname')
        address = request.POST.get('address1')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        country = request.POST.get('country')
        pickup = request.POST.get('pickup')
        org.orgname = orgname
        org.gstin = gstin
        org.regFile = regFile
        org.logo = pic
        org.address = address
        org.city = city
        org.state = state
        org.pincode = pincode
        org.country = country
        org.pickup = pickup
        org.save()
        pickup_location = str(org.orgname)+' '+str(org.state)
        phone  = str(org.contact)
        pickup_phone = ''
        for i in phone:
            if i !='(' and i !=')' and i != ' ' and i != '-' and i != '+':
                pickup_phone += i
        mycont = pickup_phone[-10:]
        clinic_contact = int(mycont)
        if pickup == 'Yes':
            pickupLcn = PickupLocation(orgId = org.id, pickup_location = pickup_location, name = str(org.ctperson_name), email = str(org.email), phone = clinic_contact, address = org.address, address_2 = org.address, city = org.city, state = org.state, country = 'India', pincode = org.pincode)
            pickupLcn.save()
            token = ShipRocketAuth.objects.get(id=1).token
            url = "https://apiv2.shiprocket.in/v1/external/settings/company/addpickup"
            payload = json.dumps({
            "pickup_location": pickupLcn.pickup_location,
            "name": pickupLcn.name,
            "email": pickupLcn.email,
            "phone": pickupLcn.phone,
            "address": pickupLcn.address,
            "address_2": "",
            "city": pickupLcn.city,
            "state": pickupLcn.state,
            "country": pickupLcn.country,
            "pin_code": pickupLcn.pincode
            })
            headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer '+str(token)
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            print(response.text)
        return redirect('/mainSettings')
    if request.method == "POST":
        orgname = request.POST.get('orgname')
        pickup = request.POST.get('pickup')
        address = request.POST.get('address1')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        country = request.POST.get('country')
        org.orgname = orgname
        org.address = address
        org.city = city
        org.state = state
        org.pincode = pincode
        org.country = country
        org.pickup = pickup
        org.save()
        pickup_location = str(org.orgname)+' '+str(org.state)
        phone  = str(org.contact)
        pickup_phone = ''
        for i in phone:
            if i !='(' and i !=')' and i != ' ' and i != '-' and i != '+':
                pickup_phone += i
        mycont = pickup_phone[-10:]
        clinic_contact = int(mycont)
        if pickup == 'Yes':
            checkPickup = PickupLocation.objects.filter(orgId = org.id)
            if checkPickup:
                for i in checkPickup:
                    i.delete()
            pickupLcn = PickupLocation(orgId = org.id, pickup_location = pickup_location, name = str(org.ctperson_name), email = str(org.email), phone = clinic_contact, address = org.address, address_2 = org.address, city = org.city, state = org.state, country = 'India', pincode = org.pincode)
            pickupLcn.save()
            token = ShipRocketAuth.objects.get(id=1).token
            url = "https://apiv2.shiprocket.in/v1/external/settings/company/addpickup"
            payload = json.dumps({
            "pickup_location": pickupLcn.pickup_location,
            "name": pickupLcn.name,
            "email": pickupLcn.email,
            "phone": pickupLcn.phone,
            "address": pickupLcn.address,
            "address_2": "",
            "city": pickupLcn.city,
            "state": pickupLcn.state,
            "country": pickupLcn.country,
            "pin_code": pickupLcn.pincode
            })
            headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer '+str(token)
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            print(response.text)
        return redirect('/mainSettings')

    return render(request, 'editorgprofile.html', data)


def editorgprofile_dent(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    users = Users.objects.filter(orgid=org)
    data = {'usr': usr, 'org': org, 'users': users, 'page': 'Edit Org Profile'}
    if request.method == "POST":
        orgname = request.POST.get('orgname')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        gstin = request.POST.get('gstin')

        org.orgname = orgname
        org.contact = contact
        org.email = email
        org.gstin = gstin
        org.save()
        return redirect('/orgprofile_dent')
    return render(request, 'editorgprofile_dent.html', data)

def editorgprofile_cust(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    organisation=Organisation.objects.get(id=id)

    data = {'usr': usr, 'org': org,  'page': 'Edit Org Profile', 'organisation':organisation}
    if request.method == "POST":
        orgname = request.POST.get('orgname')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        gstin = request.POST.get('gstin')

        organisation.orgname = orgname
        organisation.contact = contact
        organisation.email = email
        organisation.gstin = gstin
        organisation.save()
        if organisation.orgtype == "Imaging Centre":
            return redirect('/all_imaging')
        if organisation.orgtype == "Dental Clinic":
            return redirect('/all_clinic')
        if organisation.orgtype == "Radiologist":
            return redirect('/all_radio')
    return render(request, 'editorgprofile_cust.html', data)


def editorgprofile_clinic(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    users=Users.objects.filter(orgid=org)
    data = {'usr': usr, 'org': org, 'users': users, 'page': 'Edit Org Profile'}
    if request.method == "POST":
        orgname = request.POST.get('orgname')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        gstin = request.POST.get('gstin')

        org.orgname = orgname
        org.contact = contact
        org.email = email
        org.gstin = gstin
        org.save()
        return redirect('/orgprofile_clinic')
    return render(request, 'editorgprofile_clinic.html', data)


def domain_reg(request):
    if request.method == 'POST':
        orgname = request.POST.get('orgname')
        orgemail = request.POST.get('orgemail')
        address = request.POST.get('address')
        orgcontact = request.POST.get('orgcontact')
        gstin = request.POST.get('gstin')
        name = request.POST.get('name')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        username = request.POST.get('email')
        password = request.POST.get('password')
        org = Organisation(orgname=orgname, email=orgemail, address=address, contact=orgcontact, gstin=gstin,
                           orgtype="Domain Owner")
        checkorg = Organisation.objects.filter(email=orgemail).first()
        if checkorg:
            context = {'message': 'Organisation details already exists', 'class': 'danger', 'page': 'Registration'}
            return render(request, 'domain_reg.html', context)
        else:
            org.save()
        checkusr = Users.objects.filter(username=username).first()
        if checkusr:
            context = {'message': 'User details already exists', 'class': 'danger', 'page': 'Registration'}
            return render(request, 'domain_reg.html', context)
        else:
            usr = Users(name=name, email=email, contact=contact, password=password, usertype="Admin",
                        username=email, orgid=org, department="Admin", status="Active")
            usr.save()
            user = User.objects.create_user(username, email, password)
            user.save()
            usr = authenticate(username=username, password=password)
            login(request, usr)
            return redirect('/login_domain')
    page = "Registration"
    data = {'page': page}
    return render(request, 'domain_reg.html', data)


def all_settings(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    data = {'page': 'Settings', 'usr': usr}
    return render(request, 'all_settings.html', data)


def dentread_services(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    data = {'page': 'Dentread Services', 'usr': usr}
    return render(request, 'dentread_services.html', data)


def imaging_services(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    data = {'page': 'Imaging Services', 'usr': usr}
    return render(request, 'imaging_services.html', data)


def mysubs_imaging(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    subs=Subscriptions.objects.filter(orgid=org)
    today=datetime.today()
    for i in subs:
        i.consumed=ServiceOrder.objects.filter(orgid=org).count()
    data = {'page': 'My Subscriptions', 'usr': usr, 'subs':subs}
    return render(request, 'mysubs_imaging.html', data)


def buysubs_imaging(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    basic=Pack.objects.filter(type='Basic').get(applied='Imaging Centre')
    premium = Pack.objects.filter(type='Premium').get(applied='Imaging Centre')


    data = {'page': 'Buy Subscription', 'usr': usr, 'basic':basic,'premium':premium}
    return render(request, 'buysubs_imaging.html', data)

# razorpay_client = razorpay.Client(
#     auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

# def payment(request, id):
#     usr=Users.objects.get(username=request.user)
#     org=Organisation.objects.get(id=usr.orgid_id)
#     pack=Pack.objects.get(id=id)

#     amount=100
#     currency = 'INR'
#     razorpay_order = razorpay_client.order.create(dict(amount=amount,
#                                                            currency=currency,
#                                                            payment_capture='0'))

#         # order id of newly created order.
#     razorpay_order_id = razorpay_order['id']

#     callback_url = 'http://cloud.dentread.com/handlerequest/'

#         # we need to pass these details to frontend.
#     context = {}
#     context['razorpay_order_id'] = razorpay_order_id
#     context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
#     context['razorpay_amount'] = amount
#     context['currency'] = currency
#     context['name'] = usr.name
#     context['email'] = usr.email
#     context['phone'] = usr.contact
#     context['callback_url'] = callback_url
#     subs = Subscriptions(type=pack.type,  scans=pack.scans, validity=pack.validity, applied=pack.applied,
#                          price=pack.price, orgid=org,  ORDERID=razorpay_order_id, RESPMSG="Payment Pending",
#                         TXNAMOUNT=amount)
#     subs.save()

#     return render(request, 'razorpay.html', context=context)



# @csrf_exempt
# def handlerequest(request):
#     # only accept POST request.
#     if request.method == "POST":
#         try:

#             # get the required parameters from post request.
#             payment_id = request.POST.get('razorpay_payment_id', '')
#             razorpay_order_id = request.POST.get('razorpay_order_id', '')
#             signature = request.POST.get('razorpay_signature', '')
#             params_dict = {
#                 'razorpay_order_id': razorpay_order_id,
#                 'razorpay_payment_id': payment_id,
#                 'razorpay_signature': signature
#             }

#             # verify the payment signature.
#             mpack = Subscriptions.objects.get(ORDERID=razorpay_order_id)
#             result = razorpay_client.utility.verify_payment_signature(
#                 params_dict)
#             if result is None:
#                 amount = mpack.TXNAMOUNT
#                 mpack.TXNDATE = datetime.today()
#                 mpack.RESPMSG = "Payment Failed"
#                 mpack.status = "Failed"
#                 mpack.save()

#                 return render(request, 'paymentfail_imaging.html')

#             else:
#                 amount = mpack.TXNAMOUNT  # <i class="fa fa-usd" aria-hidden="true"></i> 200
#                 razorpay_client.payment.capture(payment_id, amount)
#                 mpack.TXNID = payment_id
#                 mpack.TXNDATE = datetime.today()
#                 mpack.RESPMSG = "Payment Success"
#                 mpack.status = "Active"
#                 mpack.save()
#                 data = {'mpack': mpack}


#                 # if signature verification fails.
#                 return render(request, 'paymentsuccess_imaging.html',data)
#         except:

#             # if we don't find the required parameters in POST data
#             return render(request, 'paymentprocess_imaging.html')
#     else:
#         # if other than POST request is made.
#         return HttpResponseBadRequest()


razorpay_client = razorpay.Client(

    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))


@csrf_exempt
def submitOrderPayNow(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id)
    domain = Organisation.objects.get(orgtype = "Domain Owner")
    amount = service_order.ref_price*100
    currency = 'INR'
    razorpay_order = razorpay_client.order.create(dict(amount=amount, currency=currency, payment_capture='0'))
    # order id of newly created order.
    razorpay_order_id = razorpay_order['id']
    # Callback Url
    callback_url = 'https://cloud.dentread.com/handlerequest/'
    # callback_url = 'http://127.0.0.1:8000/handlerequest/'
    # we need to pass these details to frontend.
    context = {}
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
    context['razorpay_amount'] = amount
    context['currency'] = currency
    context['name'] = org.ctperson_name
    context['email'] = org.email
    context['phone'] = org.contact
    context['callback_url'] = callback_url
    context['usr'] = usr
    context['org'] = org
    context['topcat'] = topcat
    service_order.ORDERID = razorpay_order_id
    service_order.RESPMSG = "Payment Pending"
    service_order.TXNAMOUNT = amount
    service_order.paymentStatus = 'Unpaid'
    service_order.save()
    return render(request, 'razorpay.html', context=context)


@csrf_exempt
def handlerequest(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    topcat = Topcat.objects.filter(status='Active')
    data = {'usr': usr, 'org': org, 'topcat': topcat}
    
    if request.method == "POST":
        try:
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            service_order = ServiceOrder.objects.get(ORDERID = razorpay_order_id)
            patient = Patient.objects.get(id=service_order.pid)
            result = razorpay_client.utility.verify_payment_signature(params_dict)
            if result is None:
                amount = service_order.ref_price*100
                service_order.TXNDATE = datetime.today()
                service_order.RESPMSG = "Payment Failed"
                service_order.paymentStatus = "Failed"
                service_order.save()
                return render(request, 'paymentfail_imaging.html', data)
            else:
                amount = service_order.ref_price*100  # <i class="fa fa-usd" aria-hidden="true"></i> 200
                razorpay_client.payment.capture(payment_id, amount)
                service_order.TXNID = payment_id
                service_order.TXNDATE = datetime.today()
                service_order.RESPMSG = "Payment Success"
                service_order.paymentStatus = "Paid"
                service_order.reforgid = ''
                domain = Organisation.objects.get(orgtype = "Domain Owner")
                if service_order.refstudy != 'Digital Lab Services' and service_order.refstudy != 'Implant Surgical Guide':
                    service_order.reforgid = domain.id
                else:
                    service_order.reforgid = service_order.referTo
                service_order.save()
                service_log = ServiceLog(orgid = org, repid = service_order.id,sodrid = service_order.order_id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy,log = "CREATE SERVICE ORDER", message = 'Created a service order')
                if service_order.refstudy == 'Radiological Report':
                    notificationClinic = Notification(orgid = org, sendTo = org.id, serviceOrderId = service_order.id, sent = True, service = 'Radiological Report', user = usr.name, event = 'ORDER SUBMITTED', details = 'You have successfully submitted the order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/manageReport/'+str(service_order.id))
                    notificationLab = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Radiological Report', user = usr.name, event = 'ORDER RECEIVED', details = 'You have recieved a new order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/index_dent/1')
                    notificationLab.save()
                    notificationClinic.save()
                if service_order.refstudy == 'Image Analysis Report':
                    notificationClinic = Notification(orgid = org, sendTo = org.id, serviceOrderId = service_order.id, sent = True, service = 'Image Analysis Report', user = usr.name, event = 'ORDER SUBMITTED', details = 'You have successfully submitted the order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/manageReportImage/'+str(service_order.id))
                    notificationLab = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Image Analysis Report', user = usr.name, event = 'ORDER RECEIVED', details = 'You have recieved a new order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/image_Orders/2')
                    notificationLab.save()
                    notificationClinic.save()
                if service_order.refstudy == 'Implant Planning Report':
                    notificationClinic = Notification(orgid = org, sendTo = org.id, serviceOrderId = service_order.id, sent = True, service = 'Implant Planning Report', user = usr.name, event = 'ORDER SUBMITTED', details = 'You have successfully submitted the order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/manageReportPlanning/'+str(service_order.id))
                    notificationLab = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Implant Planning Report', user = usr.name, event = 'ORDER RECEIVED', details = 'You have recieved a new order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/planning_Orders/3')
                    notificationLab.save()
                    notificationClinic.save()
                if service_order.refstudy == 'Implant Surgical Guide':
                    notificationClinic = Notification(orgid = org, sendTo = org.id, serviceOrderId = service_order.id, sent = True, service = 'Implant Surgical Guide', user = usr.name, event = 'ORDER SUBMITTED', details = 'You have successfully submitted the order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/manageReportGuide/'+str(service_order.id))
                    notificationLab = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Implant Surgical Guide', user = usr.name, event = 'ORDER RECEIVED', details = 'You have recieved a new order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/guide_orders/4')
                    notificationLab.save()
                    notificationClinic.save()
                if service_order.refstudy == 'Digital Lab Services' and service_order.preferredData == 'digitalData':
                    notificationClinic = Notification(orgid = org, sendTo = org.id, serviceOrderId = service_order.id, sent = True, service = 'Digital Lab Services', user = usr.name, event = 'ORDER SUBMITTED', details = 'You have successfully submitted the order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/manageReportDigitalLab/'+str(service_order.id))
                    notificationLab = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Digital Lab Services', user = usr.name, event = 'ORDER RECEIVED', details = 'You have recieved a new order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/lab_orders/5')
                    notificationLab.save()
                    notificationClinic.save()
                if service_order.refstudy == 'Digital Lab Services' and service_order.preferredData == 'nonDigitalData':
                    notificationClinic = Notification(orgid = org, sendTo = org.id, serviceOrderId = service_order.id, sent = True, service = 'Digital Lab Services', user = usr.name, event = 'ORDER SUBMITTED', details = 'You have successfully submitted the order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/manageReportDigitalLab/'+str(service_order.id))
                    notificationLab1 = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Digital Lab Services', user = usr.name, event = 'ORDER RECEIVED', details = 'You have recieved a new order with order ID:' +str(service_order.order_id), date = datetime.now(), hyperLink = '/lab_orders/5')
                    notificationLab2 = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Digital Lab Services', user = usr.name, event = 'PICKUP REQUEST', details = 'You are requested to pick the order (Non-digital Data) for the order ID:' + str(service_order.order_id) + ', from '+str(org.address), date = datetime.now(), hyperLink = '/lab_orders/5')
                    notificationClinic.save()
                    notificationLab1.save()
                    notificationLab2.save()
                service_log.save()
                service_order.save()
                lineItem = Prosthetic.objects.filter(repid = service_order.id)
                lineItem2 = Suricalguide.objects.filter(repid = service_order.id)
                if lineItem:
                    for i in lineItem:
                        i.reforgid = service_order.referTo
                        i.save()
                if lineItem2:
                    for j in lineItem2:
                        j.reforgid = service_order.referTo
                        j.save()
                referOrgEmail = Organisation.objects.get(id=service_order.reforgid).email
                if service_order.refstudy == 'Radiological Report' or service_order.refstudy == 'Image Analysis Report' or service_order.refstudy == 'Implant Planning Report':
                    # Send Mail code
                    orderId = str(service_order.order_id)
                    clinicName = str(org.orgname)
                    serviceName = service_order.refstudy
                    details = EmailNotification.objects.get(eventCode = 'DRET-0009')
                    connection = mail.get_connection()
                    connection.open()
                    from1 = 'info.dentread@gmail.com'
                    subject1 = 'Order ' + str(orderId) + ' submitted successfully'
                    subject2 = 'Order ' +str(orderId)+ ' received from' + str(clinicName)
                    message = "Dear, \n"+ str(usr.name) + '\n' + details.clinicSide%(serviceName, orderId) + '\nThank You \nDentread'
                    message2 = 'Dear, \nAdmin '+'\n '+ details.adminSide%(serviceName, orderId, clinicName)
                    email1 = org.email
                    # email1 = 'souravmahato7643@gmail.com'
                    email2 = 'support@dentread.com'
                    clinicSideEmail = mail.EmailMessage(subject1, message, from1, [email1], connection = connection)
                    adminSideEmail = mail.EmailMessage(subject2, message2, from1, [email2], connection = connection)
                    try:
                        connection.send_messages([clinicSideEmail, adminSideEmail])
                        connection.close()
                    except Exception as e:
                        message = e
                    eventLog = EventLog(eventCode = 'DRET-0009', event = 'New Order Submission' , log = 'A new Order hasbeen created from : ' + str(org.orgname), orgId = org.id, userId = usr.id, time = datetime.now())
                    try:
                        eventLog.save()
                    except Exception as ex:
                        eventMessage = ex
                    
                if service_order.refstudy == 'Implant Surgical Guide' or service_order.refstudy == 'Digital Lab Services':
                    # Send Mail code
                    orderId = str(service_order.order_id)
                    clinicName = org.orgname
                    serviceName = service_order.refstudy
                    details = EmailNotification.objects.get(eventCode = 'DRET-0009')
                    connection = mail.get_connection()
                    connection.open()
                    from1 = 'info.dentread@gmail.com'
                    subject1 = 'Order ' + str(orderId) + ' submitted successfully'
                    subject2 = 'Order ' +str(orderId)+ ' received from ' + str(clinicName)
                    subject3 = 'Pick-up Request For ' +str(service_order.order_id)
                    message1 = "Dear, \n"+ str(usr.name) + '\n' + details.clinicSide%(orderId, serviceName) + '\nThank You \nDentread'
                    message2 = 'Dear, \nAdmin '+'\n '+ details.adminSide%(serviceName, orderId, clinicName)
                    message3 = 'Dear, \nLab Admin \nYou are requested to pick the order (Non-digital Data) for the order ID:' + str(service_order.order_id) + ', from '+str(org.address)
                    email1 = org.email
                    email2 = referOrgEmail
                    clinicSideEmail = mail.EmailMessage(subject1, message1, from1, [email1], connection = connection)
                    adminSideEmail = mail.EmailMessage(subject2, message2, from1, [email2], connection = connection)
                    emailForPickup = ''
                    if service_order.preferredData == 'nonDigitalData':
                        emailForPickup = mail.EmailMessage(subject3, message3, from1, [email2], connection = connection)
                    try:
                        if service_order.preferredData == 'nonDigitalData':
                            connection.send_messages([clinicSideEmail, adminSideEmail, emailForPickup])
                        else:
                            connection.send_messages([clinicSideEmail, adminSideEmail])
                        connection.close()
                    except Exception as e:
                        message = e
                    eventLog = EventLog(eventCode = 'DRET-0009', event = 'New Order Submission' , log = 'A new Order hasbeen created from : ' + str(org.orgname), orgId = org.id, userId = usr.id, time = datetime.now())
                    try:
                        eventLog.save()
                    except Exception as ex:
                        eventMessage = ex
                    data = {'service_order': service_order}
                    if service_order.refstudy == 'Digital Lab Services' and service_order.preferredData == 'nonDigitalData' and service_order.requestForShipment == 'Yes':
                        return redirect('/createShipmentOrder/'+str(service_order.id))
                    return render(request, 'paymentsuccess_imaging.html', data)
        except Exception as e:
            print('Exception Message: ', e)
            # if we don't find the required parameters in POST data
            return render(request, 'paymentprocess_imaging.html', {'patient': patient, 'usr': usr, 'org': org, 'topcat': topcat})
    else:
        # if other than POST request is made.
        return HttpResponseBadRequest()

# ends here 

def dent_services(request):
    usr=Users.objects.get(username=request.user)
    org=Organisation.objects.get(id=usr.orgid_id)
    dentread_org=Organisation.objects.get(orgtype="Domain Owner")
    services=Study.objects.filter(orgid=dentread_org)
    return render(request, 'dent_services.html', {'services':services, 'usr':usr, 'org':org})


def addcentre_radio(request):
    usr=Users.objects.get(username=request.user)
    org=Organisation.objects.get(id=usr.orgid_id)
    if request.method == 'POST':
        orgname = request.POST.get('orgname')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        ctperson_name = request.POST.get('ctperson_name')
        address = request.POST.get('address')
        gstin = request.POST.get('gstin')
        orgtype = request.POST.get('orgtype')

        org = Organisation(orgname=orgname, email=email, address=address, contact=contact, gstin=gstin,
                           orgtype=orgtype, regby_email=usr.email, regby_userid=usr.id, status="Active",ctperson_name=ctperson_name)
        checkorg = Organisation.objects.filter(email=email).first()
        if checkorg:
            context = {'message': 'Organisation details already exists', 'class': 'danger', 'page': 'Registration'}
            return render(request, 'addcentre_radio.html', context)
        else:
            org.save()
            return redirect('/allcentres_radio')

    page = "Registration"
    data = {'page': page,'usr':usr, 'org':org}
    return render(request, 'addcentre_radio.html', data)

def allcentres_radio(request):
    usr=Users.objects.get(username=request.user)
    org=Organisation.objects.get(id=usr.orgid_id)
    centres=Organisation.objects.filter(regby_email=usr.email).filter(regby_userid=usr.id)
    return render(request, 'allcentres_radio.html', {'usr':usr, 'org':org, 'centres':centres, 'page':'All Ref Centres'})

def editcentre_radio(request, id):
    usr=Users.objects.get(username=request.user)
    org=Organisation.objects.get(id=usr.orgid_id)
    centre=Organisation.objects.get(id=id)
    if request.method == 'POST':
        orgname = request.POST.get('orgname')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        ctperson_name = request.POST.get('ctperson_name')
        address = request.POST.get('address')
        gstin = request.POST.get('gstin')
        orgtype = request.POST.get('orgtype')


        centre.orgname=orgname
        centre.contact=contact
        centre.ctperson_name=ctperson_name
        centre.address=address
        centre.gstin=gstin
        centre.orgtype=orgtype
        centre.save()

        return redirect('/allcentres_radio')

    page = "Registration"
    data = {'page': page, 'usr':usr, 'org':org, 'centre':centre}
    return render(request, 'editcentre_radio.html', data)

def deletecentre_radio(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    centre = Organisation.objects.get(id=id)
    centre.delete()
    return redirect('/allcentres_radio')

def updateFileStatusFirst(request, id1, id2):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    include = ['Implant Surgical Guide', 'Digital Lab Services']
    topcat = Topcat.objects.filter(topcat__in = include)
    service_order = ServiceOrder.objects.get(id=id1)
    lineItem = Suricalguide.objects.get(id=id2)
    if request.method=='POST':
        service_order.fileStatus = request.POST.get('selectBox')
        service_order.fileComment= request.POST.get('comment')
        service_order.save()
        if service_order.fileStatus == 'Reject':
            notification = Notification(orgid = org, sendTo = lineItem.orgid_id, serviceOrderId = lineItem.repid, sent = True, service = 'Implant Surgical Guide', user = usr.name, event = 'DATA REJECTED', details = 'Your given data (' +str(service_order.file) +') is not sufficient for the order ID: ' +str(service_order.order_id)+ ' .Please Re-upload the data.', date = datetime.now(), hyperLink = '/lineOrderDetails/'+str(service_order.id)+'/'+ str(lineItem.id))
            notification.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def updateFileStatusSecond(request, id1, id2):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id1)
    lineItem = Suricalguide.objects.get(id=id2)
    if request.method=='POST':
        service_order.fileStatus1 = request.POST.get('selectBox')
        service_order.fileComment1 = request.POST.get('comment')
        service_order.save()
        if service_order.fileStatus == 'Reject':
            notification = Notification(orgid = org, sendTo = lineItem.orgid_id, serviceOrderId = lineItem.repid, sent = True, service = 'Implant Surgical Guide', user = usr.name, event = 'DATA REJECTED', details = 'Your given data (' +str(service_order.file1) +') is not sufficient for the order ID: ' +str(service_order.order_id)+ ' .Please Re-upload the data.', date = datetime.now(), hyperLink = '/lineOrderDetails/'+str(service_order.id)+'/'+ str(lineItem.id))
            notification.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def iosFileStatusGuide(request, id1, id2):
    usr = Users.objects.get(username = request.user)
    org = Organisation.objects.get(id = usr.orgid_id)
    include = ['Implant Surgical Guide', 'Digital Lab Services']
    topcat = Topcat.objects.filter(topcat__in = include)
    lineItem = IOSFile.objects.get(id = id1)
    service_order = ServiceOrder.objects.get(id = lineItem.repid)
    lineItemId = Suricalguide.objects.get(id = id2)
    if request.method=='POST':
        fileStatus = request.POST.get('selectBox')
        fileComment = request.POST.get('comment')
        lineItem.fileStatus = fileStatus
        lineItem.fileComment = fileComment 
        if lineItem.fileStatus == 'Approve':
            lineItem.badge = '<span class="badge badge-success">Approved</span>'
        elif lineItem.fileStatus == 'Reject':
            lineItem.badge = '<span class="badge badge-danger">Rejected</span>'
        else:
            lineItem.badge = '<span class="badge badge-warning">Re-uploaded</span>' 
        lineItem.save()
        if lineItem.fileStatus == 'Reject':
            notification = Notification(orgid = org, sendTo = lineItem.orgid_id, serviceOrderId = lineItem.repid, sent = True, service = 'Digital Lab Services', user = usr.name, event = 'DATA REJECTED', details = 'Your given data (' +str(lineItem.fileName) +') is not sufficient for the order ID: ' +str(service_order.order_id)+ ' .Please Re-upload the data.', date = datetime.now(), hyperLink = '/lineOrderDetails/'+str(service_order.id)+'/'+ str(lineItemId.id))
            notification.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def iosFileStatus(request, id1, id2):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    include = ['Implant Surgical Guide', 'Digital Lab Services']
    topcat = Topcat.objects.filter(topcat__in = include)
    lineItem = IOSFile.objects.get(id=id1)
    service_order = ServiceOrder.objects.get(id = lineItem.repid)
    lineItemId = Prosthetic.objects.get(id = id2)
    if request.method=='POST':
        fileStatus = request.POST.get('selectBox')
        fileComment= request.POST.get('comment')
        lineItem.fileStatus = fileStatus
        lineItem.fileComment = fileComment
        
        if lineItem.fileStatus == 'Approve':
            lineItem.badge = '<span class="badge badge-success">Approved</span>'
        elif lineItem.fileStatus == 'Reject':
            lineItem.badge = '<span class="badge badge-danger">Rejected</span>'
        else:
            lineItem.badge = '<span class="badge badge-warning">Re-uploaded</span>' 
        lineItem.save()
        if lineItem.fileStatus == 'Reject':
            notification = Notification(orgid = org, sendTo = lineItem.orgid_id, serviceOrderId = lineItem.repid, sent = True, service = 'Digital Lab Services', user = usr.name, event = 'DATA REJECTED', details = 'Your given data (for -'+str(lineItem.site)+') is not sufficient for the order ID: ' +str(service_order.order_id)+ ' and the line item ID: '+str(lineItemId.item_id) + ' .Please Re-upload the data.', date = datetime.now(), hyperLink = '/lineOrderDetailsDigital/'+str(service_order.id)+'/'+ str(lineItemId.id))
            notification.save()
        
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def feedFileStatus(request, pk, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    include = ['Implant Surgical Guide', 'Digital Lab Services']
    topcat = Topcat.objects.filter(topcat__in = include)
    lineItem = Suricalguide.objects.get(id= pk)
    service_order = ServiceOrder.objects.get(id=lineItem.repid)
    feedFile = FeedFile.objects.get(id=id)
    if request.method=='POST':
        fileStatus = request.POST.get('status')
        fileComment= request.POST.get('comment')
        feedFile.fileStatus = fileStatus
        feedFile.fileComment = fileComment
        feedFile.save()
        lineItem.status = 'Review Plan'
        if feedFile.fileStatus == 'Approve':
            notification = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = lineItem.repid, sent = True, service = 'IMPLANT SURGICAL GUIDE', user = usr.name, event = 'PLAN APPROVED', details = 'Your uploaded plan file for order ID: ' +str(service_order.order_id) + ' and line item ID: '+str(lineItem.item_id) + ' has been Approved by the Clinic ' + str(org.orgname)+ '.', date = datetime.now(), hyperLink = '/lineOrderDetailsLab/'+str(service_order.id)+'/'+ str(lineItem.id))
        else:
            notification = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = lineItem.repid, sent = True, service = 'IMPLANT SURGICAL GUIDE', user = usr.name, event = 'PLAN REJECTED', details = 'Your uploaded plan file for order ID: ' +str(service_order.order_id) + ' and line item ID: '+str(lineItem.item_id) + ' has been Rejected by the Clinic ' + str(org.orgname)+ '. Please Re-upload the plan.', date = datetime.now(), hyperLink = '/lineOrderDetailsLab/'+str(service_order.id)+'/'+ str(lineItem.id))
        lineItem.save()
        notification.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def feedFileDigitalStatus(request, id1, id2):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    lineItem = Prosthetic.objects.get(id = id1)
    service_order = ServiceOrder.objects.get(id = id2)
    details = EmailNotification.objects.get(eventCode = 'DRET-0022')
    clinicName = str(org.orgname)
    orderId = str(service_order.order_id)
    lineId = str(lineItem.id)
    
    if request.method=='POST':
        lineItem.designStatus = request.POST.get('status')
        lineItem.designComment = request.POST.get('comment')
        lineItem.save()
        subject = ''
        message = ''
        current = ''
        comment = str(lineItem.designComment)
        if lineItem.designStatus == 'Approve':
            lineItem.status = 'Review Design'
            current = 'Approved'
            subject = (details.subject)%(current, clinicName, orderId)
            message = 'Dear User, \n'+(details.labSide)%(orderId, lineId, clinicName) +'\nThank You \nDentread'
            notification = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = lineItem.repid, sent = True, service = 'Digital Lab Services', user = usr.name, event = 'DESIGN APPROVED', details = 'Your uploaded design file for order ID: ' +str(service_order.order_id) + ' and line item ID: '+str(lineItem.item_id) + ' has been Approved by the Clinic ' + str(org.orgname)+ '. Please dispatch the order.', date = datetime.now(), hyperLink = '/lineOrderDetailsDigitalLab/'+str(service_order.id)+'/'+ str(lineItem.id))
        else:
            current = 'Rejected'
            subject = details.subject%(current, clinicName, orderId)
            message = 'Dear User, \n'+(details.clinicSide)%(orderId, lineId, clinicName, comment) +'\nThank You \nDentread'
            notification = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = lineItem.repid, sent = True, service = 'Digital Lab Services', user = usr.name, event = 'DESIGN REJECTED', details = 'Your uploaded design file for order ID: ' +str(service_order.order_id) + ' and line item ID: '+str(lineItem.item_id) + ' has been Rejected by the Clinic ' + str(org.orgname)+ '. Please Re-upload the design.', date = datetime.now(), hyperLink = '/lineOrderDetailsDigitalLab/'+str(service_order.id)+'/'+ str(lineItem.id))
        
        lineItem.save()
        notification.save()
        # Send Mail code
        refOrgEmail = Organisation.objects.get(id = service_order.reforgid).email
        refOrgName =  Organisation.objects.get(id = service_order.reforgid).orgname
        connection = mail.get_connection()
        connection.open()
        from1 = 'info.dentread@gmail.com'
        email1 = refOrgEmail
        mymailExicute = mail.EmailMessage(subject, message, from1, [email1], connection=connection)
        try:
            mymailExicute.send()
            connection.close()
        except Exception as e:
            message = e
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



def reset_pwd(request):
    usr = Users.objects.get(username=request.user)
    user = request.user
    org = Organisation.objects.get(id=usr.orgid_id)
    if request.method == 'POST':
        password = request.POST.get('password')
        email = request.POST.get('email')
        if user.email==email:
            new_password = request.POST.get('password')
            user.set_password(new_password)
            usr.password = new_password
            user.save()
            usr.save()
            data={'message': 'Your password has changed successfully', 'class': 'success'}
            return render(request, 'login_dentread.html', data)
        else:
            data = {'message': 'Requested user and email does not matched', 'class': 'warning'}
            return render(request, 'reset_pwd.html', data)

    data={'usr':usr, 'org':org}
    return render(request, 'reset_pwd.html',data)


def inviteuser_imaging(request):
    usr=Users.objects.get(username=request.user)
    org=Organisation.objects.get(id=usr.orgid_id)
    connection1 = get_connection(email_backend='django.core.mail.backends.smtp.EmailBackend',
                                 host='smtpout.secureserver.net',
                                 port=25,
                                 username='info@dentread.com',
                                 password='Amit@7002',
                                 use_tls=False)

    from1 = "info@dentread.com"

    if request.method=='POST':
        email = request.POST.get('email')
        name = request.POST.get('name')
        orgtype = request.POST.get('orgtype')
        msg = request.POST.get('message')
        subject="Dentread Invite"
        ckusr=Users.objects.get(email=email)
        check=Partners.objects.filter(Q(req_sender=ckusr.orgid_id) | Q(req_receiver=ckusr.orgid_id)).first()
        if check:
            message = "Request is already sent to this user"
            return render(request, 'inviteuser_imaging.html',
                         {'usr': usr, 'org': org, 'page': 'Invite', 'message': message})
        else:

            requested_user=Users.objects.filter(email=email).first()
            if requested_user:
                requested_org=Organisation.objects.get(id=requested_user.orgid_id)
                partner=Partners(req_sender=org.id, req_msg=msg, req_receiver=requested_org.id, req_status="Pending Confirmation")
                partner.save()
                try:
                    mail = EmailMultiAlternatives(subject, msg, from1, [email],
                                                  connection=connection1)
                    mail.send()
                except Exception as e:
                    print(e)

                return redirect('/allinvites')
            else:
                message="Requested user does not exist"
                return render(request, 'inviteuser_imaging.html', {'usr': usr, 'org': org, 'page': 'Invite','message':message})

    return render(request, 'inviteuser_imaging.html',{'usr':usr,'org':org, 'page':'Invite'})

def addextuser(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)

    if request.method == 'POST':
        username = request.POST.get('username')
        check_user=Users.objects.get(username=username)
        check_user.reforgid=org.id
        check_user.save()
        alert="success"
        message="External user added successfully"

        data = {'usr': usr, 'page': 'Dashboard', 'alert': alert, 'message':message}
        return render(request, 'Imaging_dashboard.html', data)
    return render(request, "addextuser.html", {'usr': usr, 'org': org})




def validateuser(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    if request.method == 'POST':
        email = request.POST.get('email')
        check_user=Users.objects.filter(username=email).first()
        if check_user:
            checkuser=Users.objects.get(username=email)
            message = "User is validated, See details and click Add"
            alert="success"
            return render(request, "addextuser.html", {'usr': usr, 'org': org, 'message':message, 'alert':alert, 'checkuser':checkuser})
        else:
            message="User not found, please check email id"
            alert = "warning"
            return render(request, "addextuser.html", {'usr': usr, 'org': org, 'message':message, 'alert':alert})
    return render(request, "addextuser.html", {'usr': usr, 'org': org})
from apiron import Timeout

def orthancdownload(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    t = Timeout(read_timeout=1000, connection_timeout=1000)
    line_item = ServiceOrder.objects.get(id=id)
    from orthanc_rest_client import Orthanc
    from requests.auth import HTTPBasicAuth
    auth = HTTPBasicAuth('dentread', 'dentread')
    import requests

    url = 'http://68.178.166.31:8042/patients/'+str(line_item.ParentStudy)+'/archive'
    return redirect(url)

def orthancdownloadImage(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    t = Timeout(read_timeout=1000, connection_timeout=1000)
    line_item = ImageAnalysis.objects.get(id=id)
    from orthanc_rest_client import Orthanc
    from requests.auth import HTTPBasicAuth
    auth = HTTPBasicAuth('dentread', 'dentread')
    import requests

    url = 'http://68.178.166.31:8042/patients/'+line_item.ParentStudy+'/archive'
    return redirect(url)

def orthancdownloadGuide(request, id, myreq):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    t = Timeout(read_timeout=1000, connection_timeout=1000)
    line_item = ServiceOrder.objects.get(id=id)
    study = ''
    if myreq == 'First':
        study = line_item.ParentStudy
    else:
        study = line_item.ParentStudy
    
    from orthanc_rest_client import Orthanc
    from requests.auth import HTTPBasicAuth
    auth = HTTPBasicAuth('dentread', 'dentread')
    import requests
    url = 'http://68.178.166.31:8042/patients/'+study+'/archive'
    return redirect(url)

def orthancdownloadPlanning(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    t = Timeout(read_timeout=1000, connection_timeout=1000)
    line_item = ImplantPlanning.objects.get(id=id)
    from orthanc_rest_client import Orthanc
    from requests.auth import HTTPBasicAuth
    auth = HTTPBasicAuth('dentread', 'dentread')
    import requests

    url = 'http://68.178.166.31:8042/patients/'+line_item.ParentStudy+'/archive'
    return redirect(url)


def downloadDicommm(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    t = Timeout(read_timeout=1000, connection_timeout=1000)
    radio_order = RadiologycalServices.objects.get(id=id)
    from orthanc_rest_client import Orthanc
    from requests.auth import HTTPBasicAuth
    auth = HTTPBasicAuth('dentread', 'dentread')
    import requests

    url = 'http://68.178.166.31:8042/patients/'+radio_order.ParentStudy+'/archive'
    return redirect(url)

def addiosfiles(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id)
    if request.method == "POST" and 'file' in request.FILES:
        for f in request.FILES.getlist('file'):
            sfile = IOSFile(file=f, repid=id, orgid=org, size = f.size, pid = service_order.pid)
            sfile.save()
            thumb = IOSFile.objects.get(id = sfile.id)
            path = str(thumb.file)
            thumb.thumbnail = path
            thumb.save()
            html = "<html><body>It is now %s.</body></html>"
            return HttpResponse(html)
    return render(request, "uploadguide_data.html", {'service_order':service_order})

def uploadimage(request, pk):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    if request.method == "POST" and 'file' in request.FILES:
        for f in request.FILES.getlist('file'):
            sfile = OtherImageFile(file = f, thumbnail = f, repid = service_order.id, orgid = org, fileName = f.name, size = f.size, pid = service_order.pid, date = date.today())
            sfile.save()
            html = "<html><body>It is now %s.</body></html>"
            return HttpResponse(html)

def updateimageFile(request, pk):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    patient = Patient.objects.get(id = service_order.pid)
    if request.method == "POST" and 'file' in request.FILES:
        for f in request.FILES.getlist('file'):
            sfile = OtherImageFile(file=f, repid = service_order.id, fileName =f.name, orgid=org, size = f.size, pid = service_order.pid)
            sfile.save()
            service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy, log = "DATA RE-UPLOADED", message = 'Upload a File', file = f.name)
            service_log.save()
            notification = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Image Analysis Report', user = usr.name, event = 'DATA RE-UPLOADED', details = 'The data for the order ID: ' +str(service_order.order_id) + ' has been re-uploaded by the Clinic ' + str(org.orgname)+ '.', date = datetime.now(), hyperLink = '/case_Details/'+str(service_order.id)+'/3')
            notification.save()
            html = "<html><body>It is now %s.</body></html>"
            return HttpResponse(html)


def uploadImageAnalysis(request, pk, id1):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    image = ImageAnalysis.objects.get(id = id1)
    if request.method == "POST" and 'file' in request.FILES:
        for f in request.FILES.getlist('file'):
            sfile = IOSFile(file=f, repid = service_order.id, sodrid = image.sodrid, orgid=org, size = f.size)
            sfile.save()
            html = "<html><body>It is now %s.</body></html>"
            return HttpResponse(html)
        
    return render(request, "refer_dentread.html", {'service_order': service_order, 'image': image})

def uploadGuideData(request, pk, id1):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    image = Suricalguide.objects.get(id = id1)
    if request.method == "POST" and 'file' in request.FILES:
        for f in request.FILES.getlist('file'):
            sfile = IOSFile(file=f, fileName = f.name, repid = service_order.id, sodrid = image.sodrid, orgid=org, size = f.size)
            sfile.save()
            html = "<html><body>It is now %s.</body></html>"
            return HttpResponse(html)

def uploadGuideDataAgain(request, id1, id2):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    sfile = IOSFile.objects.get(id = id1)
    service_order = ServiceOrder.objects.get(id= sfile.repid)
    lineItem = Suricalguide.objects.get(id = id2)
    if request.method == "POST" and 'file' in request.FILES:
        for f in request.FILES.getlist('file'):
            sfile.file = f
            sfile.fileName = f.name
            sfile.size = f.size
            sfile.fileStatus = 'Re-uploaded'
            sfile.fileComment = ''
            sfile.badge = '<span class="badge badge-warning">Re-uploaded</span>'
            notification = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = sfile.sodrid, sent = True, service = 'Implant Surgical Guide', user = usr.name, event = 'DATA RE-UPLOADED', details = 'The data for the order ID: ' +str(service_order.order_id) +  ' has been Re-uploaded by the Clinic ' + str(org.orgname)+ '.', date = datetime.now(), hyperLink = '/lineOrderDetailsLab/'+str(service_order.id)+'/'+str(lineItem.id))
            sfile.save()
            notification.save()
            html = "<html><body>It is now %s.</body></html>"
            return HttpResponse(html)

def updateImageAnalysisFile(request, pk, id1):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    image = ImageAnalysis.objects.get(id = id1)
    patient = Patient.objects.get(id = service_order.pid)
    if request.method == "POST" and 'file' in request.FILES:
        for f in request.FILES.getlist('file'):
            sfile = IOSFile(file=f, repid = service_order.id, sodrid = image.sodrid, orgid=org, size = f.size)
            sfile.save()
            service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy, log = "EDITED SERVICE ORDER", message = 'Upload a File', file = f.name)
            service_log.save()
            notification = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Image Analysis Report', user = usr.name, event = 'DATA RE-UPLOADED', details = 'The data for the order ID: ' +str(service_order.order_id) + ' and line item ID: '+str(image.item_id) + ' has been re-uploaded by the Clinic ' + str(org.orgname)+ '.', date = datetime.now(), hyperLink = '/case_DetailsImage/'+str(service_order.id)+'/3')
            notification.save()
            html = "<html><body>It is now %s.</body></html>"
            return HttpResponse(html)
        
    return render(request, "refer_dentread.html", {'service_order': service_order, 'image': image})

def uploadPlanningImage(request, pk, id1):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    image = ImplantPlanning.objects.get(id = id1)
    if request.method == "POST" and 'file' in request.FILES:
        for f in request.FILES.getlist('file'):
            sfile = IOSFile(file=f, repid = service_order.id, sodrid = image.sodrid, orgid=org, size = f.size)
            sfile.save()
            html = "<html><body>It is now %s.</body></html>"
            return HttpResponse(html)
        
    return render(request, "refer_radiologycal.html", {'service_order': service_order, 'image': image})

def updatePlanningImage(request, pk):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    patient = Patient.objects.get(id = service_order.pid)
    if request.method == "POST" and 'file' in request.FILES:
        for f in request.FILES.getlist('file'):
            sfile = OtherImageFile(file=f, repid = service_order.id, orgid=org, size = f.size)
            sfile.save()
            service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy, log = "EDITED SERVICE ORDER", message = 'Upload a File', file = f.name)
            service_log.save()
            notification = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Implant Planning Report', user = usr.name, event = 'DATA RE-UPLOADED', details = 'The data for the order ID: ' +str(service_order.order_id) + ' has been re-uploaded by the Clinic ' + str(org.orgname)+ '.', date = datetime.now(), hyperLink = '/case_DetailsPlanning/'+str(service_order.id)+'/3')
            notification.save()
            html = "<html><body>It is now %s.</body></html>"
            return HttpResponse(html)

def updateGuideImage(request, pk, id1):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    patient = Patient.objects.get(id = service_order.pid)
    image = Suricalguide.objects.get(id = id1)
    if request.method == "POST" and 'file' in request.FILES:
        for f in request.FILES.getlist('file'):
            sfile = IOSFile(file=f, repid = service_order.id, sodrid = image.sodrid, orgid=org, size = f.size)
            sfile.save()
            service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy, log = "EDITED SERVICE ORDER", message = 'Upload a File', file = f.name)
            service_log.save()
            html = "<html><body>It is now %s.</body></html>"
            return HttpResponse(html)


from .serializers import GuideSerializers, IOSFileSerializers, FeedFileSerializers, ImageSerializers, ImplantSerializers, ServiceOrderSerializers
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

@csrf_exempt
def dicomAPI(request, pk):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    if request.method =='GET':
        files = ServiceOrder.objects.filter(repid = service_order.id) 
        file = ServiceOrderSerializers(files, many=True)
        return JsonResponse(file.data, safe=False)

@csrf_exempt
def notification(request):
    usr = Users.objects.get(username = request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    topcat = Topcat.objects.filter(status = 'Active')
    myCart = ['Radiological Report', 'Implant Planning Report', 'Image Analysis Report', 'Implant Surgical Guide']
    yourCart = ['Implant Surgical Guide', 'Digital Lab Services']
    if org.orgtype == 'Domain Owner':
        topcat = Topcat.objects.filter(status = 'Active').filter(topcat__in = myCart)
    elif org.orgtype == 'Dental Lab':
        topcat = Topcat.objects.filter(status = 'Active').filter(topcat__in = yourCart)
    else:
        topcat = topcat
    if request.method =='GET':
        data = Notification.objects.filter(sendTo = org.id)
        notification = NotificationSerializers(data, many = True)
        for i in data:
            i.date = (i.date).strftime("%d-%m-%Y %H:%M")
        total = data.count()
        read = Notification.objects.filter(sendTo = org.id).filter(read = True).count()
        unread = Notification.objects.filter(sendTo = org.id).filter(read = False).count()
        page = ''
        if org.orgtype == 'Domain Owner':
            page = 'NotificationDomain.html'
        else:
            page = 'Notification.html'
        context = {'data': data, 'usr': usr, 'org': org, 'topcat': topcat, 'total': total, 'read': read, 'unread': unread}
        return render (request, page, context)

def notificationNumber(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    if request.method =='GET':
        noti = Notification.objects.filter(sendTo = org.id).filter(read = False)
        notification = NotificationSerializers(noti, many=True)
        return JsonResponse(len(notification.data), safe=False)

def updateNotificationRead(request, id, hyper):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id = usr.orgid_id)
    if request.method == 'GET':
        notification = Notification.objects.get(id = id)
        notification.read = True
        notification.save()
        return redirect(hyper)



def planningDicomAPI(request, pk, id1):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    image = ImplantPlanning.objects.get(id = id1)
    if request.method =='GET':
        files = ImplantPlanning.objects.filter(sodrid = image.id) 
        file = ImplantSerializers(files, many=True)
        return JsonResponse(file.data, safe=False)

def imageDicomAPI(request, pk, id1):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    image = ImageAnalysis.objects.get(id = id1)
    if request.method =='GET':
        files = ImageAnalysis.objects.filter(sodrid = image.id) 
        file = ImageSerializers(files, many=True)
        return JsonResponse(file.data, safe=False)

def guideDicomAPI(request, pk, id1):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk) 
    image = Suricalguide.objects.get(id = id1)
    if request.method =='GET':
        files = Suricalguide.objects.filter(sodrid = image.id) 
        file = GuideSerializers(files, many=True)
        return JsonResponse(file.data, safe=False)



def viewImage(request, pk):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    if request.method =='GET':
        files = OtherImageFile.objects.filter(repid=service_order.id)   
        file = OtherImageFileSerializers(files, many=True)
        return JsonResponse(file.data, safe=False)

def viewUploadedImage(request, pk):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    if request.method =='GET':
        files = OtherImageFile.objects.filter(repid=service_order.repid)  
        file = OtherImageFileSerializers(files, many=True)
        return JsonResponse(file.data, safe=False)
    
from .models import LabOrderItem
from .serializers import LabOrderItemSerializers, LabMaterialSerializers, SubMaterialSerializers

def allLabOrderItems(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    getOrg = Organisation.objects.get(id=id)
    orgid = getOrg.id
    if request.method == 'GET':
        allCollection = LabOrderItem.objects.filter(orgid = orgid)
        collection = LabOrderItemSerializers(allCollection, many=True)
        return JsonResponse(collection.data, safe=False)

def allLabMaterial(request, id1, id2):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    getOrg = Organisation.objects.get(id = id1)
    getItem = LabItem.objects.get(id = id2)
    if request.method == 'GET':
        allMaterial = LabMaterial.objects.filter(orgid = getOrg).filter(itemId = getItem)
        material = LabMaterialSerializers(allMaterial, many=True)
        return JsonResponse(material, safe=False)


def allLabOrderItem(request, id1, id2, id3):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    getOrg = Organisation.objects.get(id = id1)
    getItem = LabItem.objects.get(id = id2)
    getMaterial = LabMaterial.objects.get(id = id3)
    if request.method == 'GET':
        allOrderForm = LabOrderItem.objects.filter(orgid = getOrg).filter(itemId = getItem).filter(materialId = getMaterial)
        allOrder = LabOrderItemSerializers(allOrderForm, many=True)
        return JsonResponse(allOrder.data, safe=False)

def findSubMaterial(request, id1, id2):
    usr = Users.objects.get(username=request.user)
    getOrg = Organisation.objects.get(id = id1)
    getMaterial = LabMaterial.objects.get(id = id2)
    if request.method == 'GET':
        allSubMaterial = SubMaterial.objects.filter(orgid = getOrg).filter(materialId = getMaterial)
        subMaterial = SubMaterialSerializers(allSubMaterial, many=True)
        return JsonResponse(subMaterial.data, safe=False)

def viewUploadedGuideData(request, pk, id1):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    image = Suricalguide.objects.get(id = id1)
    if request.method =='GET':
        files = IOSFile.objects.filter(repid=service_order.repid).filter(sodrid = image.id)   
        file = IOSFileSerializers(files, many=True)
        return JsonResponse(file.data, safe=False)

def viewGuideData(request, pk, id1):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    image = Suricalguide.objects.get(id = id1)
    if request.method =='GET':
        files = IOSFile.objects.filter(repid=service_order.repid).filter(sodrid = image.id)   
        file = IOSFileSerializers(files, many=True)
        return JsonResponse(file.data, safe=False)

def viewReUploadedLabData(request, pk, id1, id2):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    image = Prosthetic.objects.get(id = id1)
    iosFile = IOSFile.objects.get(id=id2)
    if request.method =='GET':
        files = IOSFile.objects.filter(repid=service_order.repid).filter(id=iosFile.id)
        file = IOSFileSerializers(files, many=True)
        return JsonResponse(file.data, safe=False)

def viewPlanningImage(request, pk):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    if request.method =='GET':
        files = OtherImageFile.objects.filter(repid=service_order.repid)  
        file = OtherImageFileSerializers(files, many=True)
        return JsonResponse(file.data, safe=False)

def viewGuideImage(request, pk, id1):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    image = Suricalguide.objects.get(id = id1)
    if request.method =='GET':
        files = IOSFile.objects.filter(repid=service_order.repid).filter(sodrid = image.id)   
        file = IOSFileSerializers(files, many=True)
        return JsonResponse(file.data, safe=False)


def ViewImagePDF(request, pk, id):
    user = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=user.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    image = ImageAnalysis.objects.get(id = id)
    if request.method =='GET':
        files = FeedFile.objects.filter(repid=service_order.repid).filter(sodrid = image.id)   
        file = FeedFileSerializers(files, many=True)
        return JsonResponse(file.data, safe=False)

def downloadGuidePdf(request, pk, id1, id2):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=pk)
    line_item = Suricalguide.objects.get(id=id1)
    patient = Patient.objects.get(id=service_order.pid)
    service_log = ServiceLog(orgid = org, patient=patient.name, repid = service_order.id,sodrid = service_order.order_id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy,log = "REPORT DOWNLOADED FOR ORDER LINE ITEM", message ='Report Downloaded', line_item = line_item.item_id)
    service_log.save()
    cfile = FeedFile.objects.get(id=id2)
    # for i in cfile:
    url = cfile.file.url
        # main = '/' + url
        # return redirect(main)
    return redirect(url)

def downloadLabPlanPdf(request, pk, id1, id2):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=pk)
    line_item = Prosthetic.objects.get(id=id1)
    patient = Patient.objects.get(id=service_order.pid)
    service_log = ServiceLog(orgid = org, patient=patient.name, repid = service_order.id,sodrid = service_order.order_id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy,log = "DESIGN DOWNLOADED FOR ORDER LINE ITEM", message ='Report Downloaded', line_item = line_item.item_id)
    nauty = Notification.objects.filter(serviceOrderId = service_order.id).filter(lineItemId = line_item.id).filter(event = 'DESIGN DOWNLOADED')
    if nauty.count() == 0:    
        notification = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = line_item.repid, sent = True, service = 'Digital Lab Services', user = usr.name, event = 'DESIGN DOWNLOADED', details = 'Your uploaded design file for order ID: ' +str(service_order.order_id) + ' and line item ID: '+str(line_item.item_id) + ' has been successfully downloaded by the Clinic ' + str(org.orgname)+ '.', date = datetime.now(), hyperLink = '/lineOrderDetailsDigitalLab/'+str(service_order.id)+'/'+str(line_item.id))
        notification.save()
    service_log.save()
    cfile = FeedFile.objects.get(id=id2)
    url = cfile.file.url
    return redirect(url)

def ViewGuidePDF(request, pk, id):
    user = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=user.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    image = Suricalguide.objects.get(id = id)
    if request.method =='GET':
        files = FeedFile.objects.filter(repid=service_order.repid).filter(sodrid = image.id)   
        file = FeedFileSerializers(files, many=True)
        return JsonResponse(file.data, safe=False)

def ViewGuideLabPDF(request, pk, id):
    user = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=user.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    image = Prosthetic.objects.get(id = id)
    if request.method =='GET':
        files = FeedFile.objects.filter(repid=service_order.repid).filter(sodrid = image.id)   
        file = FeedFileSerializers(files, many=True)
        return JsonResponse(file.data, safe=False)

def ViewPlanningPDF(request, pk, id):
    user = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=user.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    image = ImplantPlanning.objects.get(id = id)
    if request.method =='GET':
        files = FeedFile.objects.filter(repid=service_order.repid).filter(sodrid = image.id)   
        file = FeedFileSerializers(files, many=True)
        return JsonResponse(file.data, safe=False)

def ViewRadioImagePDF(request, pk, id):
    user = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=user.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    image = RadiologycalServices.objects.get(id = id)
    if request.method =='GET':
        files = FeedFile.objects.filter(repid=service_order.repid).filter(sodrid = image.id)   
        file = FeedFileSerializers(files, many=True)
        return JsonResponse(file.data, safe=False)


from apiron import Timeout
import threading
import zipfile
class UploadDcm(threading.Thread):
    def __init__(self, f, pk):
        self.f = f.read()
        self.pk = pk
        threading.Thread.__init__(self)
    def run(self):
        t = Timeout(read_timeout=1000, connection_timeout=1000)
        from orthanc_rest_client import Orthanc
        from requests.auth import HTTPBasicAuth
        auth = HTTPBasicAuth('dentread', 'dentread')
        orthanc = Orthanc('http://68.178.166.31:8042', auth=auth, warn_insecure=False)
        ort = orthanc.add_instance(self.f, timeout_spec=t)
        for i in ort:
            ParentPatient = i.get('ParentPatient', None)
            ParentStudy = i.get('ParentStudy', None)
            instance = i.get('ID', None)
            Path = i.get('Path', None)
            for i in ParentPatient:
                i = ParentPatient
            for j in ParentStudy:
                j = ParentStudy
            for k in instance:
                k = instance
            for l in Path:
                l = Path

            tag = orthanc.get_study(j)
            data = tag.get('MainDicomTags', None)
            StudyInstanceUID = data.get('StudyInstanceUID')
            service_order = ServiceOrder.objects.get(id=self.pk)
            service_order.ParentPatient = i
            service_order.ParentStudy = j
            service_order.StudyInstanceUID = StudyInstanceUID
            service_order.upload = "uploaded"
            service_order.instance = k
            service_order.Path = l
            service_order.save()
            if service_order.instance != None:
                auth = HTTPBasicAuth('dentread', 'dentread')
                url = 'http://68.178.166.31:8042/instances/'+str(service_order.instance)+'/preview'
                params = {"quality": 100}
                headers = {
                "Content-Type": "image/jpeg",
                }
                response = requests.get(url, headers=headers, auth = auth, params=params)
                a = str(service_order.name)
                filename = a.replace(" ", "_")
                sink_path = 'static/dicomThumb/'+filename
                try:
                    if response.status_code == 200:
                        data = response.content
                        with open(str(sink_path)+".png", "wb") as f:
                            f.write(response.content)
                            f.close()
                        service_order.thumbnail = sink_path + '.png'
                        service_order.save()
                except Exception as e:
                    print(e)
            html = "<html><body>It is now %s.</body></html>"
            return HttpResponse(html)

def uploadDcmFile(request, pk):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    if request.method == "POST" and 'file' in request.FILES:
        doc = request.FILES
        f = doc['file']
        service_order.file = f.name
        service_order.size = f.size
        service_order.save()
        UploadDcm(f,pk).start()
        return HttpResponse("OK")

def updateDcmFileRadio(request, pk):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    patient = Patient.objects.get(id=service_order.pid)
    if request.method == "POST" and 'file' in request.FILES:
        doc = request.FILES
        f = doc['file']
        service_order = ServiceOrder.objects.get(id=pk)
        service_order.file = f.name
        service_order.size = f.size
        service_order.save()
        service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy, log = "EDITED SERVICE ORDER", message = 'Upload a Dicom File', file = f.name)
        service_log.save()
        notification = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Radiological Report', user = usr.name, event = 'DATA RE-UPLOADED', details = 'The data for the order ID: ' +str(service_order.order_id) + ' has been re-uploaded by the Clinic ' + str(org.orgname)+ '.', date = datetime.now(), hyperLink = '/radiological_Details/'+str(service_order.id)+'/1')
        notification.save()
        UploadDcm(f,pk).start()
        return HttpResponse("OK")

def updateDcmFileImage(request, pk):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    patient = Patient.objects.get(id=service_order.pid)
    if request.method == "POST" and 'file' in request.FILES:
        doc = request.FILES
        f = doc['file']
        service_order = ServiceOrder.objects.get(id=pk)
        service_order.file = f.name
        service_order.size = f.size
        service_order.save()
        service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy, log = "EDITED SERVICE ORDER", message = 'Upload a Dicom File', file = f.name)
        service_log.save()
        notification = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Image Analysis Report', user = usr.name, event = 'DATA RE-UPLOADED', details = 'The data for the order ID: ' +str(service_order.order_id) + ' has been re-uploaded by the Clinic ' + str(org.orgname)+ '.', date = datetime.now(), hyperLink = '/case_Details/'+str(service_order.id)+'/2')
        notification.save()
        UploadDcm(f,pk).start()
        return HttpResponse("OK")

def planningDcmFileUpload(request, pk, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    patient = Patient.objects.get(id=service_order.pid)
    if request.method == "POST" and 'file' in request.FILES:
        doc = request.FILES
        f = doc['file']
        service_order.file = f.name
        service_order.size = f.size
        service_order.save()
        service_log = ServiceLog(orgid = org, patient = patient.name, repid = service_order.id, sodrid = service_order.order_id, user = usr.name, usertype = usr.department,service_name = service_order.refstudy, log = "EDITED SERVICE ORDER", message = 'Upload a Dicom File', file = f.name)
        service_log.save()
        notification = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Implant Planning Report', user = usr.name, event = 'DATA RE-UPLOADED', details = 'The data for the order ID: ' +str(service_order.order_id) + ' has been re-uploaded by the Clinic ' + str(org.orgname)+ '.', date = datetime.now(), hyperLink = '/case_DetailsPlanning/'+str(service_order.id)+'/3')
        notification.save()
        UploadDcm(f,pk).start()
        return HttpResponse("OK")

# Upload Dicom for Implant Planning Services
class UploadDicomcm(threading.Thread):
    def __init__(self, f, pk, id):
        self.f = f.read()
        self.pk = pk
        self.id = id
        threading.Thread.__init__(self)
    def run(self):
        t = Timeout(read_timeout=1000, connection_timeout=1000)
        from orthanc_rest_client import Orthanc
        from requests.auth import HTTPBasicAuth
        auth = HTTPBasicAuth('dentread', 'dentread')
        orthanc = Orthanc('http://68.178.166.31:8042', auth=auth, warn_insecure=False)
        ort = orthanc.add_instance(self.f, timeout_spec=t)
        for i in ort:
            ParentPatient = i.get('ParentPatient', None)
            ParentStudy = i.get('ParentStudy', None)
            for i in ParentPatient:
                i = ParentPatient
            for j in ParentStudy:
                j = ParentStudy

            tag = orthanc.get_study(j)
            data = tag.get('MainDicomTags', None)
            StudyInstanceUID = data.get('StudyInstanceUID')
            service_order = ServiceOrder.objects.get(id=self.pk)
            image_order = ImplantPlanning.objects.get(id = self.id)
            
            image_order.ParentPatient = i
            service_order.ParentPatient = i
            image_order.ParentStudy = j
            service_order.ParentStudy = j
            image_order.StudyInstanceUID = StudyInstanceUID
            service_order.StudyInstanceUID = StudyInstanceUID
            image_order.repid = service_order.id
            image_order.upload = "uploaded"
            service_order.upload = "uploaded"
            service_order.save()
            image_order.save()
            html = "<html><body>It is now %s.</body></html>"
            return HttpResponse(html)

from apiron import Timeout
import threading
import zipfile
class UploadGuideDicom(threading.Thread):
    def __init__(self, f, pk):
        self.f = f.read()
        self.pk = pk
        threading.Thread.__init__(self)
    def run(self):
        t = Timeout(read_timeout=1000, connection_timeout=1000)
        from orthanc_rest_client import Orthanc
        from requests.auth import HTTPBasicAuth
        auth = HTTPBasicAuth('dentread', 'dentread')
        orthanc = Orthanc('http://68.178.166.31:8042', auth=auth, warn_insecure=False)
        ort = orthanc.add_instance(self.f, timeout_spec=t)
        for i in ort:
            ParentPatient = i.get('ParentPatient', None)
            ParentStudy = i.get('ParentStudy', None)
            instance = i.get('ID', None)
            Path = i.get('Path', None)
            for i in ParentPatient:
                i = ParentPatient
            for j in ParentStudy:
                j = ParentStudy
            for k in instance:
                k = instance
            for l in Path:
                l = Path

            tag = orthanc.get_study(j)
            data = tag.get('MainDicomTags', None)
            StudyInstanceUID = data.get('StudyInstanceUID')
            service_order = ServiceOrder.objects.get(id=self.pk)
            service_order.ParentPatient = i
            service_order.ParentStudy = j
            service_order.StudyInstanceUID = StudyInstanceUID
            service_order.upload = "uploaded"
            service_order.instance = k
            service_order.Path = l
            service_order.save()
            if service_order.instance != None:
                auth = HTTPBasicAuth('dentread', 'dentread')
                url = 'http://68.178.166.31:8042/instances/'+str(service_order.instance)+'/preview'
                params = {"quality": 100}
                headers = {
                "Content-Type": "image/jpeg",
                }
                response = requests.get(url, headers=headers, auth = auth, params=params)
                a = str(service_order.name)
                filename = a.replace(" ", "_")
                sink_path = 'static/dicomThumb/'+filename
                try:
                    if response.status_code == 200:
                        data = response.content
                        with open(str(sink_path)+".png", "wb") as f:
                            f.write(response.content)
                            f.close()
                        service_order.thumbnail = sink_path + '.png'
                        service_order.save()
                except Exception as e:
                    print(e)
            html = "<html><body>It is now %s.</body></html>"
            return HttpResponse(html)

def uploadGuideDcmFileAgain(request, pk, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    image_order = Suricalguide.objects.get(id = id)
    if request.method == "POST" and 'file' in request.FILES:
        doc = request.FILES
        f = doc['file']
        service_order = ServiceOrder.objects.get(id = pk)
        service_order.file = f.name
        service_order.size = f.size
        service_order.fileStatus = 'Re-uploaded'
        service_order.fileComment = ''
        notification = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Implant Surgical Guide', user = usr.name, event = 'DATA RE-UPLOADED', details = 'The data for the order ID: ' +str(service_order.order_id) + ' and line item ID: '+str(image_order.item_id) + ' has been re-uploaded by the Clinic ' + str(org.orgname)+ '.', date = datetime.now(), hyperLink = '/lineOrderDetailsLab/'+str(service_order.id)+'/'+str(image_order.id))
        service_order.save()
        notification.save()
        UploadGuideDicom(f,pk).start()
        return HttpResponse("OK")

def guideDcmFileUpload(request, pk):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    if request.method == "POST" and 'file' in request.FILES:
        doc = request.FILES
        f = doc['file']
        service_order.file = f.name
        service_order.size = f.size
        service_order.save()
        UploadGuideDicom(f,pk).start()
        return HttpResponse("OK")

from apiron import Timeout
import threading
import zipfile
class UploadGuideDicomSecond(threading.Thread):
    def __init__(self, f, pk):
        self.f = f.read()
        self.pk = pk
        threading.Thread.__init__(self)
    def run(self):
        t = Timeout(read_timeout=1000, connection_timeout=1000)
        from orthanc_rest_client import Orthanc
        from requests.auth import HTTPBasicAuth
        auth = HTTPBasicAuth('dentread', 'dentread')
        orthanc = Orthanc('http://68.178.166.31:8042', auth=auth, warn_insecure=False)
        ort = orthanc.add_instance(self.f, timeout_spec=t)
        for i in ort:
            ParentPatient = i.get('ParentPatient', None)
            ParentStudy = i.get('ParentStudy', None)
            for i in ParentPatient:
                i = ParentPatient
            for j in ParentStudy:
                j = ParentStudy

            tag = orthanc.get_study(j)
            data = tag.get('MainDicomTags', None)
            StudyInstanceUID = data.get('StudyInstanceUID')
            service_order = ServiceOrder.objects.get(id = self.pk)
            service_order.ParentPatient1 = i
            service_order.ParentStudy1 = j
            service_order.StudyInstanceUID1 = StudyInstanceUID
            service_order.upload1 = "uploaded"
            service_order.save()
            html = "<html><body>It is now %s.</body></html>"
            return HttpResponse(html)

def guideDcmFileUploadSecond(request, pk):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    if request.method == "POST" and 'file' in request.FILES:
        doc = request.FILES
        f = doc['file']
        service_order = ServiceOrder.objects.get(id = pk)
        service_order.file1 = f.name
        service_order.size1 = f.size
        service_order.save()
        UploadGuideDicomSecond(f,pk).start()
        return HttpResponse("OK")

def guideDcmFileUploadSecondAgain(request, pk, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    image_order = Suricalguide.objects.get(id = id)
    if request.method == "POST" and 'file' in request.FILES:
        doc = request.FILES
        f = doc['file']
        service_order.file1 = f.name
        service_order.size1 = f.size
        service_order.fileStatus1 = 'Re-uploaded'
        service_order.fileComment1 = ''
        notification = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Implant Surgical Guide', user = usr.name, event = 'DATA RE-UPLOADED', details = 'The data for the order ID: ' +str(service_order.order_id) + ' and line item ID: '+str(image_order.item_id) + ' has been re-uploaded by the Clinic ' + str(org.orgname)+ '.', date = datetime.now(), hyperLink = '/lineOrderDetailsLab/'+str(service_order.id)+'/'+str(image_order.id))
        service_order.save()
        notification.save()
        UploadGuideDicomSecond(f,pk).start()
        return HttpResponse("OK")

def addOtherImages(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id)

    if request.method == "POST" and 'file' in request.FILES:

        for f in request.FILES.getlist('otherImagefile'):
            ofile = OtherImageFile(file=f, repid=id, orgid=org, size = f.size)
            ofile.save()

            html = "<html><body>It is now %s.</body></html>"
            return HttpResponse(html)
    return render(request, "uploadguide_data.html", {'service_order':service_order})

def driveindex(request):
    return render(request, "drive.html")

def orthanctest(request):

    return render(request, "driveupload.html", {'service_order':'service_order'})



from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def driveresp(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)

    if request.method == "POST":
        response_json = request.POST
        response_json = json.dumps(response_json)
        data = json.loads(response_json)

        link=data.get('alternateLink', None)
        fileid=data.get('id', None)
        tid=Tempid.objects.filter(orgid=org).get(status="pending")
        service_order=ServiceOrder.objects.get(id=tid.repid)
        service_order.driveid=fileid
        service_order.drivelink=link
        service_order.save()
        tid.delete()
        return JsonResponse({'status': 'Save'})


@csrf_exempt
def tempid(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    if request.method == "POST":
        repid=request.POST.get('service_orderid')
        checkid=Tempid.objects.filter(repid=repid).first()
        if checkid:
            print("no")
        else:
            tid=Tempid(repid=repid, status="pending", orgid=org)
            tid.save()
            return JsonResponse({'status': 'Save'})
    return HttpResponse("ok")

def orthanctest1(request):
    usr=Users.objects.get
    import json
    import requests
    headers = {
        "Authorization": "Bearer ya29.a0AVA9y1uxElRXnQyT9nFdxgFVpBA5P7xrTJvMJh2JfpPe_-OdhyYwMkBfI-XbrTXY5-w4GziJhfFbXNoLQyzKH360G5g6IXFCjdVFvjo17749zo1W6NbQvt5-QtwTB6yjWFFAVQcJzFwqgfyQFyzZkIG2mcJe"}
    para = {
        "name": "rzp.csv",
    }
    files = {
        'data': ('metadata', json.dumps(para), 'application/json; charset=UTF-8'),
        'file': open("./rzp.csv", "rb")
    }
    r = requests.post(
        "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
        headers=headers,
        files=files
    )
    return render(request, 'orthanctest.html')

import matplotlib
matplotlib.use('Agg')
from stl import mesh
from mpl_toolkits import mplot3d
from matplotlib import pyplot
import matplotlib.pyplot as plt
import numpy as np
import cv2
import numpy
from plyfile import PlyData, PlyElement

from mpl_toolkits.mplot3d import Axes3D

def uploadLabData(request, pk, target):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    fFile = IOSFile.objects.filter(repid = service_order.id).filter(site=target)
    if fFile.count() == 0:
        if request.method == "POST" and 'file' in request.FILES:
            for f in request.FILES.getlist('file'):
                sfile = IOSFile(file=f, fileName = f.name,site = target, repid = service_order.id, orgid=org, size = f.size, pid = service_order.pid)
                sfile.save()
                fsfile = IOSFile.objects.get(id = sfile.id)
                a  = str(fsfile.file.url)
                b = a[1:]
                c = b.split('/')[2].split('.')[0]
                original_path = b
                path = 'static/thumb/'
                file_name = str(c)
                original_fileName = original_path.split('/')[-1]
                fileFormat_1 = original_fileName.find('.stl')
                fileFormat_2 = original_fileName.find('.ply')
                checkFileFormat_1 = original_fileName[fileFormat_1:]
                checkFileFormat_2 = original_fileName[fileFormat_2:]
                if checkFileFormat_1 == '.stl':
                    try:
                        # Load the STL file
                        your_mesh = mesh.Mesh.from_file(b)
                        fig = plt.figure()
                        ax = fig.add_subplot(111, projection='3d')
                        # Plot the mesh
                        ax.add_collection3d(mplot3d.art3d.Poly3DCollection(your_mesh.vectors, facecolors='#D76ABD', edgecolors='black'))
                        # Set the axis limits
                        ax.set_xlim(your_mesh.min_[0], your_mesh.max_[0])
                        ax.set_ylim(your_mesh.min_[1], your_mesh.max_[1])
                        ax.set_zlim(your_mesh.min_[2], your_mesh.max_[2])
                        
                        plt.savefig(path + file_name +".jpg", dpi = 300, format = 'jpg')
                        fsfile.thumbnail = path + file_name +".jpg"
                        fsfile.save()
                    except Exception as e:
                        print(e)
                elif checkFileFormat_2 == '.ply':
                    try:
                        # Load the ply file
                        plydata = PlyData.read(b)
                        # Extract vertex coordinates from the PLY file
                        x = plydata['vertex'].data['x']
                        y = plydata['vertex'].data['y']
                        z = plydata['vertex'].data['z']
                        # Create a 3D scatter plot using Matplotlib
                        fig = plt.figure()
                        ax = fig.add_subplot(111, projection='3d')
                        ax.scatter(x, y, z, s=1, c=z, cmap='jet', facecolors='#D76ABD')
                        plt.axis('off')
                        plt.savefig(path + file_name +".jpg", dpi=300, format = 'jpg')
                        # save The File path
                        fsfile.thumbnail = path + file_name +".jpg"
                        fsfile.save()
                    except Exception as exc:
                        print(exc)
                    
    else:
        for i in fFile:
            sfile = IOSFile.objects.get(id = i.id)
            if request.method == "POST" and 'file' in request.FILES:
                for f in request.FILES.getlist('file'):
                    sfile.file = f
                    sfile.fileName = f.name
                    sfile.size = f.size
                    sfile.save()
                    fsfile = IOSFile.objects.get(id = sfile.id)
                    a  = str(fsfile.file.url)
                    b = a[1:]
                    c = b.split('/')[2].split('.')[0]
                    original_path = b
                    path = 'static/thumb/'
                    file_name = str(c)
                    original_fileName = original_path.split('/')[-1]
                    fileFormat_1 = original_fileName.find('.stl')
                    fileFormat_2 = original_fileName.find('.ply')
                    checkFileFormat_1 = original_fileName[fileFormat_1:]
                    checkFileFormat_2 = original_fileName[fileFormat_2:]
                    if checkFileFormat_1 == '.stl':
                        try:
                            # Load the STL file
                            your_mesh = mesh.Mesh.from_file(b)
                            fig = plt.figure()
                            ax = fig.add_subplot(111, projection='3d')
                            # Plot the mesh
                            ax.add_collection3d(mplot3d.art3d.Poly3DCollection(your_mesh.vectors, facecolors='#D76ABD', edgecolors='black'))
                            # Set the axis limits
                            ax.set_xlim(your_mesh.min_[0], your_mesh.max_[0])
                            ax.set_ylim(your_mesh.min_[1], your_mesh.max_[1])
                            ax.set_zlim(your_mesh.min_[2], your_mesh.max_[2])
                            
                            plt.savefig(path + file_name +".jpg", dpi = 300, format = 'jpg')
                            fsfile.thumbnail = path + file_name +".jpg"
                            fsfile.save()
                        except Exception as e:
                            print(e)
                    elif checkFileFormat_2 == '.ply':
                        try:
                            # Load the ply file
                            plydata = PlyData.read(b)
                            # Extract vertex coordinates from the PLY file
                            x = plydata['vertex'].data['x']
                            y = plydata['vertex'].data['y']
                            z = plydata['vertex'].data['z']
                            # Create a 3D scatter plot using Matplotlib
                            fig = plt.figure()
                            ax = fig.add_subplot(111, projection='3d')
                            ax.scatter(x, y, z, s=1, c=z, cmap='jet', facecolors='#D76ABD')
                            plt.axis('off')
                            plt.savefig(path + file_name +".jpg", dpi=300, format = 'jpg')
                            # save The File path
                            fsfile.thumbnail = path + file_name +".jpg"
                            fsfile.save()
                        except Exception as exc:
                            print(exc)
    html = "<html><body>It is now %s.</body></html>"
    return HttpResponse(html)

def deleteIos(request, pk, target):
    img = IOSFile.objects.filter(repid = pk).filter(site = target)
    for i in img: 
        deleteId = i.id
        imgDel = IOSFile.objects.get(id= deleteId)
        imgDel.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def uploadLabDataAgain(request, id1, id2):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    sfile = IOSFile.objects.get(id = id1)
    lineItem = Prosthetic.objects.get(id = id2)
    service_order = ServiceOrder.objects.get(id = sfile.repid)
    labEmail = Organisation.objects.get(id = service_order.reforgid).email
    labName = Organisation.objects.get(id = service_order.reforgid).orgname
    if request.method == "POST" and 'file' in request.FILES:
        for f in request.FILES.getlist('file'):
            sfile.file = f
            sfile.fileName = f.name
            sfile.size = f.size
            sfile.fileStatus = 'Re-uploaded'
            sfile.fileComment = ''
            sfile.badge = '<span class="badge badge-warning">Re-uploaded</span>'
            sfile.save()
            html = "<html><body>It is now %s.</body></html>"
            notification = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = sfile.sodrid, sent = True, service = 'Digital Lab Services', user = usr.name, event = 'DATA RE-UPLOADED', details = 'The data for the order ID: ' +str(service_order.order_id) + ' and line item ID: '+str(lineItem.item_id) + ' has been re-uploaded by the Clinic ' + str(org.orgname)+ '.', date = datetime.now(), hyperLink = '/lineOrderDetailsDigitalLab/'+str(service_order.id)+'/'+str(lineItem.id))
            notification.save()
            # Send Mail code
            details = EmailNotification.objects.get(eventCode = 'DRET-0018')
            connection = mail.get_connection()
            connection.open()
            orderId = service_order.order_id
            organisationName = org.orgname
            firstId = str(service_order.id)
            secId = str(lineItem.id)
            from1 = 'info.dentread@gmail.com'
            subject = details.subject%(organisationName, orderId)
            message = "Dear User, \n " + details.labSide%(organisationName, orderId, firstId, secId) +'\nThank You \nDentread'
            email1 = labEmail
            mymailExicute = mail.EmailMessage(subject, message, from1, [email1], connection=connection)
            try:
                mymailExicute.send()
                connection.close()
            except Exception as e:
                message = e
            return HttpResponse(html)

def viewLabImage(request, pk, id1):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = pk)
    image = Prosthetic.objects.get(id = id1)
    if request.method =='GET':
        files = IOSFile.objects.filter(repid=service_order.repid).filter(sodrid = image.id)
        iosFile = IOSFile.objects.filter(repid = service_order.id) 
        sfile = IOSFileSerializers(files, many=True)
        iosFilec = IOSFileSerializers(iosFile, many=True)
        # all_files = file.data.append(len(iosFilecount.data))
        file = sfile.data
        iosFilecount = len(iosFilec.data)
        return JsonResponse(file, safe=False)
        
def holdOrder(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    lineItem = Prosthetic.objects.get(id=id)
    service_order = ServiceOrder.objects.get(id = lineItem.repid)
    if request.method == "POST":
        cancellationReason = request.POST.get('cancellationReason')
        status = request.POST.get('statusInput')
        lineItem.status = status
        lineItem.cancellationReason = cancellationReason
        lineItem.cancellationDateTime = datetime.now()
        message = ''
        event = ''
        if status == 'Order Cancelled':
            event = 'ORDER CANCELLED'
            message = 'cancelled'
        elif status == 'Order On-Hold':
            event = 'ORDER ON-HOLD'
            message = 'put on-Hold'
            prevStatus = request.POST.get('prevStatus') 
            lineItem.prevStatus = prevStatus
        else:
            status = 'Order Un-Hold'
            event = 'ORDER RELEASED'
            message = 'released'
        notificationClinic = Notification(orgid = org, sendTo = org.id, serviceOrderId = service_order.id, sent = True, service = 'Digital Lab Services', user = usr.name, event = event, details = 'Your order with order ID: ' +str(service_order.order_id)+ ' has been successfully ' + str(message), date = datetime.now(), hyperLink = '/lineOrderDetailsDigital/'+str(service_order.id)+'/'+str(lineItem.id))
        notificationLab = Notification(orgid = org, sendTo = service_order.reforgid, serviceOrderId = service_order.id, sent = True, service = 'Digital Lab Services', user = usr.name, event = status, details = 'The order with order ID:' +str(service_order.order_id)+ ' has been '+str(message)+' by the '+ str(org.orgname), date = datetime.now(), hyperLink = '/lineOrderDetailsDigitalLab/'+str(service_order.id)+'/'+str(lineItem.id))
        notificationLab.save()
        notificationClinic.save()
        lineItem.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def lab_order(request):
    usr = Users.objects.get(username=request.user)
    org=Organisation.objects.get(id=usr.orgid_id)
    data = {'usr': usr, 'message': 'You have signed in successfully', 'page':'Dashboard', 'org':org}
    return render(request, 'lab_order.html', data)

def accept_invite(request, id):
    usr=Users.objects.get(username=request.user)
    org=Organisation.objects.get(id=usr.orgid_id)
    partner=Partners.objects.get(id=id)
    partner.req_status="Accepted"
    partner.response_date=date.today()
    partner.save()
    return redirect('/allinvites')

def deny_invite(request, id):
    usr=Users.objects.get(username=request.user)
    org=Organisation.objects.get(id=usr.orgid_id)
    partner=Partners.objects.get(id=id)
    partner.req_status="Denied"
    partner.response_date=date.today()
    partner.save()
    return redirect('/allinvites')

def refer_partner(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order=ServiceOrder.objects.get(id=id)
    partner=Partners.objects.filter(Q(req_sender=org.id)| Q(req_receiver=org.id) ).filter(req_status="Accepted")
    for i in partner:
        checkpartner=Organisation.objects.filter(id=i.req_sender).first()
        if checkpartner:
            i.partner=checkpartner
        else:
            i.partner=Organisation.objects.filter(id=i.req_receiver)


    return render(request, 'choosepartner.html', {'partner':partner, 'service_order':service_order, 'usr':usr, 'org':org})


def partner_order(request, id1, id2):
    context = {}
    context['id1'] = id1
    context['id2'] = id2
    partner=Organisation.objects.get(id=id1)
    service_order=ServiceOrder.objects.get(id=id2)
    if partner.orgtype == "Dental Lab":
        return render(request,'lab_order.html')
    return render(request, 'lab_order.html' )

def error_404_view(request, exception):
    return render(request, '404.html')

def requestForInvoice(request, patient, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id)
    domainOwner = Organisation.objects.get(orgtype = "Domain Owner")
    date = datetime.today().date()
    
    #Icons And Currency
    icon = ''
    currency = ''
    if org.country == 'IN':
        currency = 'price'
        icon = '<i class="fa-solid fa-indian-rupee-sign"></i>'
    else:
        currency = 'dollarPrice'
        icon = '<i class="fa-solid fa-dollar-sign"></i>'
    
    # Finance Info Information
    MRP = service_order.ref_price
    HSC = ''
    GST = ''
    CGST = ''
    SGST = ''
    IGST = ''
    Discount = ''
    DiscountPersentage = ''
    netAmount = ''
    totalTax = ''
    
    if service_order.refstudy == 'Radiological Report':
        HSC = '999316'
        GST = '0%'
        CGST = '0%'
        SGST = '0%'
        IGST = '0%'
        Discount = 0
        DiscountPersentage = '0%'
        netAmount = MRP
        totalTax = 0
        lineItems = RadiologycalServices.objects.filter(orgid = org).filter(repid = service_order.id)
    elif service_order.refstudy == 'Image Analysis Report':
        HSC = '999316'
        GST = '0%'
        CGST = '0%'
        SGST = '0%'
        IGST = '0%'
        Discount = 0
        DiscountPersentage = '0%'
        netAmount = 0
        totalTax = 0
        lineItems = ImageAnalysis.objects.filter(orgid = org).filter(repid = service_order.id)
    else:
        HSC = '9021'
        GST = '18%'
        CGST = '9%'
        SGST = '9%'
        IGST = '18%'
        Discount = 0
        DiscountPersentage = '0%'
        netAmount = 0
        totalTax = ((MRP - Discount)*18/100)
        lineItems = ImplantPlanning.objects.filter(orgid = org).filter(repid = service_order.id)
    context = {'service_order': service_order,'icon': icon, 'currency': currency, 'netAmount': netAmount,'org': org, 'HSC': HSC, 'GST':GST, 'CGST': CGST, 'SGST': SGST,'IGST': IGST, 'Discount': Discount,'totalTax': totalTax, 'usr': usr,'date': date, 'DiscountPersentage': DiscountPersentage, 'lineItems': lineItems, 'domainOwner': domainOwner}
    return render(request, 'ManagePayment/paymentInvoice.html', context)

def requestForInvoiceLab(request, patient, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id=id)
    referOrg = Organisation.objects.get(id = service_order.reforgid)
    date = datetime.today().date()
    extraLabItem = ExtraLabItem.objects.filter(repid = service_order.id)
    
    #Icons And Currency
    icon = ''
    currency = ''
    if org.country == 'IN':
        currency = 'price'
        icon = '<i class="fa-solid fa-indian-rupee-sign"></i>'
    else:
        currency = 'dollarPrice'
        icon = '<i class="fa-solid fa-dollar-sign"></i>'
    
    # Finance Info Information
    MRP = service_order.ref_price
    HSC = ''
    GST = ''
    CGST = ''
    SGST = ''
    IGST = ''
    Discount = ''
    DiscountPersentage = ''
    netAmount = ''
    totalTax = ''
    if service_order.refstudy == 'Implant Surgical Guide':
        HSC = '9021'
        GST = '18%'
        CGST = '9%'
        SGST = '9%'
        IGST = '18%'
        Discount = 0
        DiscountPersentage = '0%'
        netAmount = (MRP - Discount)+((MRP - Discount)*18/100)
        totalTax = ((MRP - Discount)*18/100)
        lineItems = Suricalguide.objects.filter(orgid = org).filter(repid = service_order.id)
    else:
        HSC = '9021'
        GST = '12%'
        CGST = '6%'
        SGST = '6%'
        IGST = '12%'
        Discount = 0
        DiscountPersentage = '0%'
        netAmount = (MRP - Discount)+((MRP - Discount)*12/100)
        totalTax = ((MRP - Discount)*12/100)
        lineItems = Prosthetic.objects.filter(orgid = org).filter(repid = service_order.id)
    context = {'service_order': service_order,'icon': icon, 'currency': currency, 'netAmount': netAmount,'org': org, 'HSC': HSC, 'GST':GST, 'CGST': CGST, 'SGST': SGST,'IGST': IGST, 'Discount': Discount,'totalTax': totalTax, 'usr': usr,'date': date, 'DiscountPersentage': DiscountPersentage, 'lineItems': lineItems, 'referOrg': referOrg, 'extraLabItem': extraLabItem}
    return render(request, 'ManagePayment/paymentInvoiceLab.html', context)

def accountStatement(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    include = ['Implant Surgical Guide', 'Digital Lab Services']
    topcat = Topcat.objects.filter(topcat__in = include)
    today = datetime.today()
    thisWeek = today - timedelta(weeks=1)
    end_date = today.date()
    start_date = thisWeek.date()
    check_transfer = ServiceOrder.objects.filter(reforgid = org.id).filter(refstudy='Digital Lab Services').filter(paymentStatus = 'Paid').filter(Q(date__gte = thisWeek))
    allTransfer = check_transfer.values('ref_price')
    totalTransfer = allTransfer.aggregate(Sum('ref_price'))
    transfer = totalTransfer['ref_price__sum']
    if transfer == None:
        transfer = '0.0'
    service_order = ServiceOrder.objects.filter(reforgid = org.id).filter(refstudy='Digital Lab Services').filter(Q(date__gte = thisWeek))
    price = service_order.values('ref_price')
    sum = price.aggregate(Sum('ref_price'))
    ref_price = sum['ref_price__sum']
    if ref_price == None:
        ref_price = 0
    totalExpense = '--'
    GST = (ref_price*12/100)
    myOrder = Prosthetic.objects.filter(reforgid=org.id).filter(Q(date__gte = thisWeek))
    crown = myOrder.filter(item = 'Crown and Bridges')
    implant = myOrder.filter(item = 'Implant Specific Section')
    removable = myOrder.filter(item = 'Removable Prosthesis')
    precision = myOrder.filter(item = 'Precision Attachment')
    ortho = myOrder.filter(item = 'Orthodontic and Pedodontic Appliances / Retainers')
    miscellaneous = myOrder.filter(item = 'Miscellaneous')
    context = {'usr': usr, 'org': org, 'topcat': topcat, 'ref_price': ref_price, 'totalExpense': totalExpense, 'GST': GST, 'transfer': transfer, 'start_date': start_date, 'end_date': end_date, 'crown': crown, 'implant': implant, 'removable': removable, 'precision': precision, 'ortho': ortho, 'miscellaneous': miscellaneous}
    return render(request, 'ManagePayment/AccountStatement.html', context)

def partnerBusinessReport(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    include = ['Implant Surgical Guide', 'Digital Lab Services']
    topcat = Topcat.objects.filter(topcat__in = include)
    today = datetime.today()
    surgical_guide = Suricalguide.objects.filter(reforgid = org.id).filter(date = today)
    myOrder = Prosthetic.objects.filter(reforgid=org.id).filter(date = today)
    #============================>
    totalOrder = surgical_guide.count()
    
    arrg = surgical_guide.values('price')
    priceSum = arrg.aggregate(Sum('price'))
    totalRevenue = priceSum['price__sum']
    if totalRevenue == None:
        totalRevenue = 0
    
    allOrg = surgical_guide.values('orgid')
    org_list = []
    for i in range(len(allOrg)):
        if allOrg[i] not in allOrg[i + 1:]:
            org_list.append(allOrg[i])
    customerAnalysis = len(org_list)
    returnAmount = 0
    refundAmount = 0
    
    #==========================>>
    crown = myOrder.filter(item = 'Crown and Bridges')
    #Count The Unit
    all_unit_crown = crown.values('unit')
    totalUnit_crown = all_unit_crown.aggregate(Sum('unit'))
    crown_unit = totalUnit_crown['unit__sum']
    if crown_unit == None:
        crown_unit = 0
    
    #Count The Price
    all_price_crown = crown.values('price')
    sum_price_crown = all_price_crown.aggregate(Sum('price'))
    total_price_crown = sum_price_crown['price__sum']
    if total_price_crown == None:
        total_price_crown = 0
    
    #Count The Organisations
    all_org_crown = crown.values('orgid')
    res_list = []
    for i in range(len(all_org_crown)):
        if all_org_crown[i] not in all_org_crown[i + 1:]:
            res_list.append(all_org_crown[i])
    total_org_crown = len(res_list)
    
    # Order Refund / Return 
    cancellation = crown.filter(status = 'Order Cancelled')
    amount = cancellation.values('price')
    totalAmount = amount.aggregate(Sum('price'))
    cancellationAmount_crown = totalAmount['price__sum']
    if cancellationAmount_crown == None:
        cancellationAmount_crown = 0
    cancellationCount_crown = cancellation.count()
    
    #========================================>>
    implant = myOrder.filter(item = 'Implant Specific Section')
    #Count The Unit
    all_unit_implant = implant.values('unit')
    totalUnit_implant = all_unit_implant.aggregate(Sum('unit'))
    implant_unit = totalUnit_implant['unit__sum']
    if implant_unit == None:
        implant_unit = 0
    
    #Count The Price
    all_price_implant = implant.values('price')
    sum_price_implant = all_price_implant.aggregate(Sum('price'))
    total_price_implant = sum_price_implant['price__sum']
    if total_price_implant == None:
        total_price_implant = 0
    
    #Count The Organisations
    all_org_implant = implant.values('orgid')
    mylist_list = []
    for i in range(len(all_org_implant)):
        if all_org_implant[i] not in all_org_implant[i + 1:]:
            mylist_list.append(all_org_implant[i])
    total_org_implant = len(mylist_list)
    
    # Order Refund / Return 
    cancellation_implant = implant.filter(status = 'Order Cancelled')
    amount_implant = cancellation_implant.values('price')
    totalAmount_implant = amount_implant.aggregate(Sum('price'))
    cancellationAmount_implant = totalAmount_implant['price__sum']
    if cancellationAmount_implant == None:
        cancellationAmount_implant = 0
    cancellationCount_implant = cancellation_implant.count()
    
    #=====================================>>
    removable = myOrder.filter(item = 'Removable Prosthesis')
    #Count The Unit
    all_unit_removable = removable.values('unit')
    totalUnit_removable = all_unit_removable.aggregate(Sum('unit'))
    removable_unit = totalUnit_removable['unit__sum']
    if removable_unit == None:
        removable_unit = 0
    
    #Count The Price
    all_price_removable = removable.values('price')
    sum_price_removable = all_price_removable.aggregate(Sum('price'))
    total_price_removable = sum_price_removable['price__sum']
    if total_price_removable == None:
        total_price_removable = 0
    
    #Count The Organisations
    all_org_removable = removable.values('orgid')
    removablelist_list = []
    for i in range(len(all_org_removable)):
        if all_org_removable[i] not in all_org_removable[i + 1:]:
            removablelist_list.append(all_org_removable[i])
    total_org_removable = len(removablelist_list)
    
    # Order Refund / Return 
    cancellation_removable = removable.filter(status = 'Order Cancelled')
    amount_removable = cancellation_implant.values('price')
    totalAmount_removable = amount_removable.aggregate(Sum('price'))
    cancellationAmount_removable = totalAmount_removable['price__sum']
    if cancellationAmount_removable == None:
        cancellationAmount_removable = 0
    cancellationCount_removable = cancellation_removable.count()
   
    #==================================>
    precision = myOrder.filter(item = 'Precision Attachment')
    
    #Count The Unit
    all_unit_precision = precision.values('unit')
    totalUnit_precision = all_unit_precision.aggregate(Sum('unit'))
    precision_unit = totalUnit_precision['unit__sum']
    if precision_unit == None:
        precision_unit = 0
    #Count The Price
    all_price_precision = precision.values('price')
    sum_price_precision = all_price_precision.aggregate(Sum('price'))
    total_price_precision = sum_price_precision['price__sum']
    if total_price_precision == None:
        total_price_precision = 0
    
    #Count The Organisations
    all_org_precision = precision.values('orgid')
    top_list = []
    for i in range(len(all_org_precision)):
        if all_org_precision[i] not in all_org_precision[i + 1:]:
            top_list.append(all_org_precision[i])
    total_org_implant = len(top_list)
    
    # Order Refund / Return 
    cancellation_precision = precision.filter(status = 'Order Cancelled')
    amount_precision = cancellation_precision.values('price')
    totalAmount_precision = amount_precision.aggregate(Sum('price'))
    cancellationAmount_precision = totalAmount_precision['price__sum']
    if cancellationAmount_precision == None:
        cancellationAmount_precision = 0
    cancellationCount_precision = cancellation_precision.count()
    
    #==========================================>>
    ortho = myOrder.filter(item = 'Orthodontic and Pedodontic Appliances / Retainers')
    #Count The Unit
    all_unit_ortho = ortho.values('unit')
    totalUnit_ortho = all_unit_ortho.aggregate(Sum('unit'))
    ortho_unit = totalUnit_ortho['unit__sum']
    if ortho_unit == None:
        ortho_unit = 0
    
    #Count The Price
    all_price_ortho = ortho.values('price')
    sum_price_ortho = all_price_ortho.aggregate(Sum('price'))
    total_price_ortho = sum_price_ortho['price__sum']
    if total_price_ortho == None:
        total_price_ortho = 0
    
    #Count The Organisations
    all_org_ortho = ortho.values('orgid')
    new_list = []
    for i in range(len(all_org_ortho)):
        if all_org_ortho[i] not in all_org_ortho[i + 1:]:
            new_list.append(all_org_ortho[i])
    total_org_ortho = len(new_list)
    
    # Order Refund / Return 
    cancellation_ortho = ortho.filter(status = 'Order Cancelled')
    amount_ortho = cancellation_ortho.values('price')
    totalAmount_ortho = amount_ortho.aggregate(Sum('price'))
    cancellationAmount_ortho = totalAmount_ortho['price__sum']
    if cancellationAmount_ortho == None:
        cancellationAmount_ortho = 0
    cancellationCount_ortho = cancellation_ortho.count()
    
     
    #################################
    
    #=======================================>>
    mis = myOrder.filter(item = 'Miscellaneous')
    #Count The Unit
    all_unit_mis = mis.values('unit')
    totalUnit_mis = all_unit_mis.aggregate(Sum('unit'))
    mis_unit = totalUnit_mis['unit__sum']
    if mis_unit == None:
        mis_unit = 0
    
    #Count The Price
    all_price_mis = mis.values('price')
    sum_price_mis = all_price_mis.aggregate(Sum('price'))
    total_price_mis = sum_price_mis['price__sum']
    if total_price_mis == None:
        total_price_mis = 0
    
    #Count The Organisations
    all_org_mis = mis.values('orgid')
    mis_list = []
    for i in range(len(all_org_mis)):
        if all_org_mis[i] not in all_org_mis[i + 1:]:
            mis_list.append(all_org_mis[i])
    total_org_mis = len(mis_list)
    
    # Order Refund / Return 
    cancellation_mis = mis.filter(status = 'Order Cancelled')
    amount_mis = cancellation_mis.values('price')
    totalAmount_mis = amount_mis.aggregate(Sum('price'))
    cancellationAmount_mis = totalAmount_mis['price__sum']
    if cancellationAmount_mis == None:
        cancellationAmount_mis = 0
    cancellationCount_mis = cancellation_mis.count()
    
    #Handle POST Method For Filter Data
    if request.method == "POST":
        check1 = ""
        check2 = ""
        check3 = ""
        dat = request.POST.get('dat')
        fd = request.POST.get('fromdate')
        td = request.POST.get('todate')
        if dat == "Today":
            data = today
            check1 = "checked"
            surgical_guide = Suricalguide.objects.filter(reforgid = org.id).filter(Q(date=data))
            myOrder = Prosthetic.objects.filter(reforgid=org.id).filter(Q(date=data))
            
        if dat == "Thisweek":
            data = today - timedelta(weeks=1)
            check2 = "checked"
            surgical_guide = Suricalguide.objects.filter(reforgid = org.id).filter(Q(date__gte=data))
            myOrder = Prosthetic.objects.filter(reforgid=org.id).filter(Q(date__gte=data))
        if dat == "Thismonth":
            data = today - relativedelta(days = 30)
            check3 = "checked"
            surgical_guide = Suricalguide.objects.filter(reforgid = org.id).filter(Q(date__gte=data))
            myOrder = Prosthetic.objects.filter(reforgid=org.id).filter(Q(date__gte=data))
        if dat == "":
            data = None

        if data is None:
            surgical_guide = Suricalguide.objects.filter(reforgid = org.id).filter(date__range=[fd, td])
            myOrder = Prosthetic.objects.filter(reforgid=org.id).filter(date__range=[fd, td])
        #============================>
        totalOrder = surgical_guide.count()

        arrg = surgical_guide.values('price')
        priceSum = arrg.aggregate(Sum('price'))
        totalRevenue = priceSum['price__sum']
        if totalRevenue == None:
            totalRevenue = 0

        allOrg = surgical_guide.values('orgid')
        org_list = []
        for i in range(len(allOrg)):
            if allOrg[i] not in allOrg[i + 1:]:
                org_list.append(allOrg[i])
        customerAnalysis = len(org_list)
        returnAmount = 0
        refundAmount = 0

        #==========================>>
        crown = myOrder.filter(item = 'Crown and Bridges')
        #Count The Unit
        all_unit_crown = crown.values('unit')
        totalUnit_crown = all_unit_crown.aggregate(Sum('unit'))
        crown_unit = totalUnit_crown['unit__sum']
        if crown_unit == None:
            crown_unit = 0

        #Count The Price
        all_price_crown = crown.values('price')
        sum_price_crown = all_price_crown.aggregate(Sum('price'))
        total_price_crown = sum_price_crown['price__sum']
        if total_price_crown == None:
            total_price_crown = 0

        #Count The Organisations
        all_org_crown = crown.values('orgid')
        res_list = []
        for i in range(len(all_org_crown)):
            if all_org_crown[i] not in all_org_crown[i + 1:]:
                res_list.append(all_org_crown[i])
        total_org_crown = len(res_list)

        # Order Refund / Return 
        cancellation = crown.filter(status = 'Order Cancelled')
        amount = cancellation.values('price')
        totalAmount = amount.aggregate(Sum('price'))
        cancellationAmount_crown = totalAmount['price__sum']
        if cancellationAmount_crown == None:
            cancellationAmount_crown = 0
        cancellationCount_crown = cancellation.count()

        #========================================>>
        implant = myOrder.filter(item = 'Implant Specific Section')
        #Count The Unit
        all_unit_implant = implant.values('unit')
        totalUnit_implant = all_unit_implant.aggregate(Sum('unit'))
        implant_unit = totalUnit_implant['unit__sum']
        if implant_unit == None:
            implant_unit = 0

        #Count The Price
        all_price_implant = implant.values('price')
        sum_price_implant = all_price_implant.aggregate(Sum('price'))
        total_price_implant = sum_price_implant['price__sum']
        if total_price_implant == None:
            total_price_implant = 0

        #Count The Organisations
        all_org_implant = implant.values('orgid')
        mylist_list = []
        for i in range(len(all_org_implant)):
            if all_org_implant[i] not in all_org_implant[i + 1:]:
                mylist_list.append(all_org_implant[i])
        total_org_implant = len(mylist_list)

        # Order Refund / Return 
        cancellation_implant = implant.filter(status = 'Order Cancelled')
        amount_implant = cancellation_implant.values('price')
        totalAmount_implant = amount_implant.aggregate(Sum('price'))
        cancellationAmount_implant = totalAmount_implant['price__sum']
        if cancellationAmount_implant == None:
            cancellationAmount_implant = 0
        cancellationCount_implant = cancellation_implant.count()

        #=====================================>>
        removable = myOrder.filter(item = 'Removable Prosthesis')
        #Count The Unit
        all_unit_removable = removable.values('unit')
        totalUnit_removable = all_unit_removable.aggregate(Sum('unit'))
        removable_unit = totalUnit_removable['unit__sum']
        if removable_unit == None:
            removable_unit = 0

        #Count The Price
        all_price_removable = removable.values('price')
        sum_price_removable = all_price_removable.aggregate(Sum('price'))
        total_price_removable = sum_price_removable['price__sum']
        if total_price_removable == None:
            total_price_removable = 0

        #Count The Organisations
        all_org_removable = removable.values('orgid')
        removablelist_list = []
        for i in range(len(all_org_removable)):
            if all_org_removable[i] not in all_org_removable[i + 1:]:
                removablelist_list.append(all_org_removable[i])
        total_org_removable = len(removablelist_list)

        # Order Refund / Return 
        cancellation_removable = removable.filter(status = 'Order Cancelled')
        amount_removable = cancellation_implant.values('price')
        totalAmount_removable = amount_removable.aggregate(Sum('price'))
        cancellationAmount_removable = totalAmount_removable['price__sum']
        if cancellationAmount_removable == None:
            cancellationAmount_removable = 0
        cancellationCount_removable = cancellation_removable.count()

        #==================================>
        precision = myOrder.filter(item = 'Precision Attachment')

        #Count The Unit
        all_unit_precision = precision.values('unit')
        totalUnit_precision = all_unit_precision.aggregate(Sum('unit'))
        precision_unit = totalUnit_precision['unit__sum']
        if precision_unit == None:
            precision_unit = 0
        #Count The Price
        all_price_precision = precision.values('price')
        sum_price_precision = all_price_precision.aggregate(Sum('price'))
        total_price_precision = sum_price_precision['price__sum']
        if total_price_precision == None:
            total_price_precision = 0

        #Count The Organisations
        all_org_precision = precision.values('orgid')
        top_list = []
        for i in range(len(all_org_precision)):
            if all_org_precision[i] not in all_org_precision[i + 1:]:
                top_list.append(all_org_precision[i])
        total_org_implant = len(top_list)

        # Order Refund / Return 
        cancellation_precision = precision.filter(status = 'Order Cancelled')
        amount_precision = cancellation_precision.values('price')
        totalAmount_precision = amount_precision.aggregate(Sum('price'))
        cancellationAmount_precision = totalAmount_precision['price__sum']
        if cancellationAmount_precision == None:
            cancellationAmount_precision = 0
        cancellationCount_precision = cancellation_precision.count()

        #==========================================>>
        ortho = myOrder.filter(item = 'Orthodontic and Pedodontic Appliances / Retainers')
        #Count The Unit
        all_unit_ortho = ortho.values('unit')
        totalUnit_ortho = all_unit_ortho.aggregate(Sum('unit'))
        ortho_unit = totalUnit_ortho['unit__sum']
        if ortho_unit == None:
            ortho_unit = 0

        #Count The Price
        all_price_ortho = ortho.values('price')
        sum_price_ortho = all_price_ortho.aggregate(Sum('price'))
        total_price_ortho = sum_price_ortho['price__sum']
        if total_price_ortho == None:
            total_price_ortho = 0

        #Count The Organisations
        all_org_ortho = ortho.values('orgid')
        new_list = []
        for i in range(len(all_org_ortho)):
            if all_org_ortho[i] not in all_org_ortho[i + 1:]:
                new_list.append(all_org_ortho[i])
        total_org_ortho = len(new_list)

        # Order Refund / Return 
        cancellation_ortho = ortho.filter(status = 'Order Cancelled')
        amount_ortho = cancellation_ortho.values('price')
        totalAmount_ortho = amount_ortho.aggregate(Sum('price'))
        cancellationAmount_ortho = totalAmount_ortho['price__sum']
        if cancellationAmount_ortho == None:
            cancellationAmount_ortho = 0
        cancellationCount_ortho = cancellation_ortho.count()

            
        #################################

        #=======================================>>
        mis = myOrder.filter(item = 'Miscellaneous')
        #Count The Unit
        all_unit_mis = mis.values('unit')
        totalUnit_mis = all_unit_mis.aggregate(Sum('unit'))
        mis_unit = totalUnit_mis['unit__sum']
        if mis_unit == None:
            mis_unit = 0

        #Count The Price
        all_price_mis = mis.values('price')
        sum_price_mis = all_price_mis.aggregate(Sum('price'))
        total_price_mis = sum_price_mis['price__sum']
        if total_price_mis == None:
            total_price_mis = 0

        #Count The Organisations
        all_org_mis = mis.values('orgid')
        mis_list = []
        for i in range(len(all_org_mis)):
            if all_org_mis[i] not in all_org_mis[i + 1:]:
                mis_list.append(all_org_mis[i])
        total_org_mis = len(mis_list)

        # Order Refund / Return 
        cancellation_mis = mis.filter(status = 'Order Cancelled')
        amount_mis = cancellation_mis.values('price')
        totalAmount_mis = amount_mis.aggregate(Sum('price'))
        cancellationAmount_mis = totalAmount_mis['price__sum']
        if cancellationAmount_mis == None:
            cancellationAmount_mis = 0
        cancellationCount_mis = cancellation_mis.count()
        context = {'usr': usr, 'org': org, 'topcat': topcat, 'check1': check1, 'check2': check2, 'check3': check3,
               'crown_unit': crown_unit, 'total_price_crown': total_price_crown, 'total_org_crown': total_org_crown, 'cancellationAmount_crown': cancellationAmount_crown, 'cancellationCount_crown': cancellationCount_crown,
               'implant_unit': implant_unit, 'total_price_implant': total_price_implant, 'total_org_implant': total_org_implant, 'cancellationAmount_implant': cancellationAmount_implant, 'cancellationCount_implant': cancellationCount_implant,
               'removable_unit': removable_unit, 'total_price_removable': total_price_removable, 'total_org_removable': total_org_removable, 'cancellationCount_removable': cancellationCount_removable, 'cancellationAmount_removable': cancellationAmount_removable,
               'precision_unit': precision_unit, 'total_price_precision': total_price_precision, 'total_org_implant': total_org_implant, 'cancellationCount_precision': cancellationCount_precision, 'cancellationAmount_precision': cancellationAmount_precision,
               'ortho_unit': ortho_unit, 'total_price_ortho': total_price_ortho, 'total_org_ortho': total_org_ortho, 'cancellationCount_ortho': cancellationCount_ortho, 'cancellationAmount_ortho': cancellationAmount_ortho,
               'mis_unit': mis_unit, 'total_price_mis': total_price_mis, 'total_org_mis': total_org_mis, 'cancellationCount_mis': cancellationCount_mis, 'cancellationAmount_mis': cancellationAmount_mis,
               'totalOrder': totalOrder, 'totalRevenue': totalRevenue, 'customerAnalysis': customerAnalysis, 'returnAmount': returnAmount, 'refundAmount': refundAmount
               }
        return render(request, 'LabOrder/PartnerBusinessReport.html', context)
    
    context = {'usr': usr, 'org': org, 'topcat': topcat,
               'crown_unit': crown_unit, 'total_price_crown': total_price_crown, 'total_org_crown': total_org_crown, 'cancellationAmount_crown': cancellationAmount_crown, 'cancellationCount_crown': cancellationCount_crown,
               'implant_unit': implant_unit, 'total_price_implant': total_price_implant, 'total_org_implant': total_org_implant, 'cancellationAmount_implant': cancellationAmount_implant, 'cancellationCount_implant': cancellationCount_implant,
               'removable_unit': removable_unit, 'total_price_removable': total_price_removable, 'total_org_removable': total_org_removable, 'cancellationCount_removable': cancellationCount_removable, 'cancellationAmount_removable': cancellationAmount_removable,
               'precision_unit': precision_unit, 'total_price_precision': total_price_precision, 'total_org_implant': total_org_implant, 'cancellationCount_precision': cancellationCount_precision, 'cancellationAmount_precision': cancellationAmount_precision,
               'ortho_unit': ortho_unit, 'total_price_ortho': total_price_ortho, 'total_org_ortho': total_org_ortho, 'cancellationCount_ortho': cancellationCount_ortho, 'cancellationAmount_ortho': cancellationAmount_ortho,
               'mis_unit': mis_unit, 'total_price_mis': total_price_mis, 'total_org_mis': total_org_mis, 'cancellationCount_mis': cancellationCount_mis, 'cancellationAmount_mis': cancellationAmount_mis,
               'totalOrder': totalOrder, 'totalRevenue': totalRevenue, 'customerAnalysis': customerAnalysis, 'returnAmount': returnAmount, 'refundAmount': refundAmount
               }
    return render(request, 'LabOrder/PartnerBusinessReport.html', context)

def manageOrderItems(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    include = ["Implant Surgical Guide", "Digital Lab Services"]
    topcat = Topcat.objects.filter(topcat__in = include)
    labItem = LabItem.objects.all()
    labOrderItem = LabOrderItem.objects.filter(orgid = org)
    footNotes = AddOnLabServices.objects.filter(orgid = org)
    for j in footNotes:
        if j.itemId:
            j.itemId = LabItem.objects.get(id = j.itemId).item
    context = {'usr': usr, 'org': org, 'topcat': topcat, 'labItem': labItem, 'labOrderItem': labOrderItem, 'footNotes': footNotes}
    return render(request, 'LabOrder/product_listing.html', context)

def settleAccount(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    allLab = Organisation.objects.filter(orgtype = 'Dental Lab')
    include = ["Implant Surgical Guide", "Digital Lab Services"]
    topcat = Topcat.objects.filter(status = 'Active').exclude(topcat__in = include)
    today = datetime.today()
    thisWeek = today - timedelta(weeks=1)
    end_date = today.date()
    start_date = thisWeek.date()
    accountInfo = AccountSettlement.objects.filter(settleStatus = 'No')
    for i in accountInfo:
        i.Organisation = Organisation.objects.get(id = i.Organisation).orgname
    context = {'usr': usr, 'org': org, 'allLab': allLab, 'topcat': topcat, 'end_date': end_date, 'start_date': start_date, 'accountInfo': accountInfo}
    return render(request, 'LabOrder/settleAccount.html', context)
def addOrderItems(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    if request.method == 'POST':
        item = request.POST.get('item')
        type = request.POST.get('type')
        method = request.POST.get('method')
        material = request.POST.get('material')
        submethod = request.POST.get('submethod')
        application = request.POST.get('application')
        warranty = request.POST.get('warranty')
        price = request.POST.get('price')
        details = request.POST.get('description')
        itemId = ''
        if item == 'Crown and Bridges':
            labItem = LabItem.objects.get(item = 'Crown and Bridges')
            itemId = labItem
        elif item == 'Implant Specific Section':
            labItem = LabItem.objects.get(item = 'Implant Specific Section')
            itemId = labItem
        elif item == 'Removable Prosthesis':
            labItem = LabItem.objects.get(item = 'Removable Prosthesis')
            itemId = labItem
        elif item == 'Precision Attachment':
            labItem = LabItem.objects.get(item = 'Precision Attachment')
            itemId = labItem
        elif item == 'Orthodontic and Pedodontic Appliances / Retainers':
            labItem = LabItem.objects.get(item = 'Orthodontic and Pedodontic Appliances / Retainers')
            itemId = labItem
        else:
            labItem = LabItem.objects.get(item = 'Miscellaneous')
            itemId = labItem
        materialId = ''
        checkMaterial = LabMaterial.objects.filter(material = material)
        if checkMaterial:
            for i in checkMaterial:
                materialId = i
        else:
            newMaterial = LabMaterial(orgid = org, itemId = itemId, material = material)
            newMaterial.save()
            materialId = LabMaterial.objects.get(id = newMaterial.id)
        labOrderItem = LabOrderItem(orgid = org, item = item, itemId = itemId, type = type, method = method, material = material, materialId = materialId, submethod = submethod, application = application, warranty = warranty, price = price, details = details)
        labOrderItem.save()
        return redirect('/manageOrderItems')
def addFootNotes(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    if request.method == 'POST':
        item = request.POST.get('footnote-item')
        addOnService = request.POST.get('add-on-item')
        price = request.POST.get('footnote-price')
        descriptions = request.POST.get('footnote-description')
        itemId = ''
        if item == 'Crown and Bridges':
            labItem = LabItem.objects.get(item = 'Crown and Bridges')
            itemId = labItem.id
        elif item == 'Implant Specific Section':
            labItem = LabItem.objects.get(item = 'Implant Specific Section')
            itemId = labItem.id
        elif item == 'Removable Prosthesis':
            labItem = LabItem.objects.get(item = 'Removable Prosthesis')
            itemId = labItem.id
        elif item == 'Precision Attachment':
            labItem = LabItem.objects.get(item = 'Precision Attachment')
            itemId = labItem.id
        elif item == 'Orthodontic and Pedodontic Appliances / Retainers':
            labItem = LabItem.objects.get(item = 'Orthodontic and Pedodontic Appliances / Retainers')
            itemId = labItem.id
        else:
            labItem = LabItem.objects.get(item = 'Miscellaneous')
            itemId = labItem.id
        addOnLabService = AddOnLabServices(orgid = org, itemId = itemId, addOnService = addOnService, price = price, descriptions = descriptions, unit = 1)
        addOnLabService.save()
        return redirect('/manageOrderItems')

def removeLabOrderItem(request, id):
    labOrderItem = LabOrderItem.objects.get(id=id)
    labOrderItem.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def removeExtraItem(request, id):
    addOnLabServices = AddOnLabServices.objects.get(id=id)
    addOnLabServices.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def editOrderItem(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    if request.method == 'POST':
        labOrderItem = LabOrderItem.objects.get(id = id)
        labOrderItem.item = request.POST.get('item-edit')
        labOrderItem.type = request.POST.get('type-edit')
        labOrderItem.method = request.POST.get('method-edit')
        labOrderItem.material = request.POST.get('material-edit')
        labOrderItem.submethod = request.POST.get('submethod-edit')
        labOrderItem.application = request.POST.get('application-edit')
        labOrderItem.warranty = request.POST.get('warranty-edit')
        labOrderItem.price = request.POST.get('price-edit')
        labOrderItem.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def editExtraItem(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    if request.method == 'POST':
        addOnLabServices = AddOnLabServices.objects.get(id = id)
        addOnLabServices.itemId = request.POST.get('footnote-item-edit')
        addOnLabServices.addOnService = request.POST.get('add-on-item-edit')
        addOnLabServices.price = request.POST.get('footnote-price-edit')
        addOnLabServices.descriptions = request.POST.get('footnote-description-edit')
        addOnLabServices.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def enablePaymentOption(request, id):
    if request.method == 'POST':
        org = Organisation.objects.get(id = id)
        org.paymentOption = request.POST.get('payment-switch')
        org.topUp = request.POST.get('credit')
        org.topUpAvailable = request.POST.get('credit')
        org.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def inviteClinic(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    myIntrest = ['Implant Surgical Guide', 'Digital Lab Services']
    topcat = Topcat.objects.filter(status = 'Active').filter(topcat__in = myIntrest)
    context = {'usr': usr, 'org': org, 'topcat': topcat}
    return render(request, 'lab_invite.html', context)

def clinicInvitation(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    orgId = str(org.id)
    if request.method == 'POST':
        clinic_name = request.POST.get('clinic_name')
        clinic_email = request.POST.get('clinic_email')
        message = ''
        # Send Mail code
        connection = mail.get_connection()
        connection.open()
        from1 = 'info.dentread@gmail.com'
        subject = 'Invitation to Join ' +str(org.orgname)
        message = 'Dear \n' +str(clinic_name)+ ', \nPlease join my network on Dentread for a superior digital experience. Dentread is a Cloud based secure, Digital Dentistry Platform for Image Data and Services Management. To learn more, visit https://www.dentread.com . To Register on Dentread visit the given link - https://cloud.dentread.com/joinLabInvitation/'+str(orgId)+'/DRET-0039-CDL-INV-03 \nBest regards, \n'+str(org.orgname)
        email1 = clinic_email
        mailToClinic = mail.EmailMessage(subject, message, from1, [email1], connection=connection)
        try:
            mailToClinic.send()
            connection.close()
            message = 'Invite Send Successfully'
        except Exception as e:
            message = e
        context = {'usr': usr, 'org': org, 'topcat': topcat, 'message': message}
        return render(request, 'lab_invite.html', context)

def joinLabInvitation(request, id, invScr):
    joinOrg = Organisation.objects.get(id = id)
    labId = joinOrg.id
    invScr = invScr
    details = EmailNotification.objects.get(eventCode = 'DRET-0001')
    if request.method == 'POST' and  request.FILES:
        doc = request.FILES
        logo = doc['logo']
        orgname = request.POST.get('orgname')
        orgemail = request.POST.get('orgemail')
        address = request.POST.get('address')
        orgcontact = request.POST.get('orgcontact')
        gstin = request.POST.get('gstin')
        name = request.POST.get('name')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        username = request.POST.get('email')
        password = request.POST.get('password')
        city = request.POST.get('cityname')
        state = request.POST.get('statename')
        country = request.POST.get('country')
        pincode = request.POST.get('pincode')
        regNo = request.POST.get('regNo')

        org = Organisation(orgname=orgname, regNo=regNo, email=orgemail, logo=logo, address = address + ', ' +str(city)+', ' + str(state)+ ', ' + str(country)+' '+'('+str(pincode)+')' , contact=orgcontact, gstin=gstin, city=city, state=state, country=country, pincode=pincode, orgtype="Dental Clinic", status="Active", preferredLab = labId)
        checkorg = Organisation.objects.filter(email=orgemail).first()
        if checkorg:
            context = {'message': 'Organisation details already exists', 'class': 'danger', 'page': 'Registration'}
            return render(request, 'clinic_reg.html', context)
        else:
            org.save()
        checkusr = Users.objects.filter(username=username).first()
        if checkusr:
            context = {'message': 'User details already exists', 'class': 'danger', 'page': 'Registration'}
            return render(request, 'clinic_reg.html', context)
        else:
            usr = Users(name=name, email=email, contact=contact, password=password, usertype="Admin", username=email,
                        orgid=org, department="Admin", status="Active")
            usr.save()
            user = User.objects.create_user(username, email, password)
            user.save()
            org.regby_email = usr.email
            org.regby_userid = usr.id
            gotUserId = usr.id
            gotOrgId = org.id
            org.ctperson_name = usr.name
            org.org_id = str(org.id)
            org.preferredLab = labId
            org.save()
            usr = authenticate(username=username, password=password)
            login(request, usr)
            
            # Send Mail code
            details = EmailNotification.objects.get(eventCode = 'DRET-0001')
            var1 = str(org.orgname)
            connection = mail.get_connection()
            connection.open()
            from1 = 'info.dentread@gmail.com'
            subject = details.subject%(var1)
            message = details.clinicSide%(var1) + '\nThank You \nDentread'
            message2 = details.adminSide%(var1)
            email1 = user.email
            email2 = 'support@dentread.com'
            mymailExicute = mail.EmailMessage(subject, message, from1, [email1], connection=connection)
            mymailExicute2 = mail.EmailMessage(subject, message2, from1, [email2], connection=connection)
            try:
                mymailExicute.send()
                mymailExicute2.send()
                connection.close()
            except Exception as e:
                message = e
            eventLog = EventLog(eventCode = 'DRET-0001', event = subject , log = 'A new Organisation Registered to dentread, named : ' + str(org.orgname), orgId = gotOrgId, userId = gotUserId, time = datetime.now())
            try:
                eventLog.save()
            except Exception as ex:
                eventMessage = ex
            return redirect('/login_clinic')
    if request.method == 'POST':
        orgname = request.POST.get('orgname')
        orgemail = request.POST.get('orgemail')
        address = request.POST.get('address')
        orgcontact = request.POST.get('orgcontact')
        gstin = request.POST.get('gstin')
        name = request.POST.get('name')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        username = request.POST.get('email')
        password = request.POST.get('password')
        city = request.POST.get('cityname')
        state = request.POST.get('statename')
        country = request.POST.get('country')
        pincode = request.POST.get('pincode')
        regNo = request.POST.get('regNo')

        org = Organisation(orgname=orgname, regNo=regNo, email=orgemail, address = address + ', ' +str(city)+', ' + str(state)+ ', ' + str(country)+' '+'('+str(pincode)+')' , contact=orgcontact, gstin=gstin, city=city, state=state, country=country, pincode=pincode, orgtype="Dental Clinic", status="Active", preferredLab=labId)
        checkorg = Organisation.objects.filter(email=orgemail).first()
        if checkorg:
            context = {'message': 'Organisation details already exists', 'class': 'danger', 'page': 'Registration'}
            return render(request, 'clinic_reg.html', context)
        else:
            org.save()
        checkusr = Users.objects.filter(username=username).first()
        if checkusr:
            context = {'message': 'User details already exists', 'class': 'danger', 'page': 'Registration'}
            return render(request, 'clinic_reg.html', context)
        else:
            usr = Users(name=name, email=email, contact=contact, password=password, usertype="Admin", username=email,
                        orgid=org, department="Admin", status="Active")
            usr.save()
            user = User.objects.create_user(username, email, password)
            user.save()
            org.regby_email = usr.email
            org.regby_userid = usr.id
            gotUserId = usr.id
            gotOrgId = org.id
            org.ctperson_name = usr.name
            org.org_id = str(org.id)
            org.preferredLab = labId
            org.save()
            usr = authenticate(username=username, password=password)
            login(request, usr)
            
            # Send Mail code
            details = EmailNotification.objects.get(eventCode = 'DRET-0001')
            var1 = str(org.orgname)
            connection = mail.get_connection()
            connection.open()
            from1 = 'info.dentread@gmail.com'
            subject = details.subject%(var1)
            message = details.clinicSide%(var1) + '\nThank You \nDentread'
            message2 = details.adminSide%(var1)
            email1 = user.email
            email2 = 'support@dentread.com'
            mymailExicute = mail.EmailMessage(subject, message, from1, [email1], connection=connection)
            mymailExicute2 = mail.EmailMessage(subject, message2, from1, [email2], connection=connection)
            try:
                mymailExicute.send()
                mymailExicute2.send()
                connection.close()
            except Exception as e:
                message = e
            eventLog = EventLog(eventCode = 'DRET-0001', event = subject , log = 'A new Organisation Registered to dentread, named : ' + str(org.orgname), orgId = gotOrgId, userId = gotUserId, time = datetime.now())
            try:
                eventLog.save()
            except Exception as ex:
                eventMessage = ex
            return redirect('/login_clinic')
    page = "Registration"
    data = {'page': page, 'labId': labId, 'invScr': invScr}
    return render(request, 'invitedClinicReg.html', data)

def labWalletInfo(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    mycart = ['Implant Surgical Guide', 'Digital Lab Services']
    topcat = Topcat.objects.filter(topcat__in = mycart)
    walletInfo = ''
    try:
        walletInfo = LabWalletInfo.objects.get(orgId = org)
    except Exception as e:
        message = 'Add Balance To Your Accout'
    
    WalletExp = WalletExpenses.objects.filter(labId = org.id)
    for i in WalletExp:
        i.logo = Organisation.objects.get(id = i.orgId).logo
    walletCount = WalletExp.count()
    if request.method == "POST":
        year = request.POST.get('year')
        month = request.POST.get('month')
        month = int(month)
        month += 1
        walletInfo = ''
        try:
            walletInfo = LabWalletInfo.objects.get(orgId = org)
        except Exception as e:
            message = 'Add Balance To Your Accout'
        
        WalletExp = WalletExpenses.objects.filter(labId = org.id).filter(date__year = year).filter(date__month = month)
        for i in WalletExp:
            i.logo = Organisation.objects.get(id = i.orgId).logo
        walletCount = WalletExp.count()
        context = {'usr': usr, 'org': org, 'walletInfo': walletInfo, 'WalletExp': WalletExp, 'walletCount': walletCount, 'topcat': topcat}
        return render(request, 'lab_wallet.html', context)
    context = {'usr': usr, 'org': org, 'walletInfo': walletInfo, 'WalletExp': WalletExp, 'walletCount': walletCount, 'topcat': topcat}
    return render(request, 'lab_wallet.html', context)

def addToWalletBalance(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    amount = 50000*100
    currency = 'INR'
    mycart = ['Implant Surgical Guide', 'Digital Lab Services']
    topcat = Topcat.objects.filter(topcat__in = mycart)
    razorpay_order = razorpay_client.order.create(dict(amount=amount, currency=currency, payment_capture='0'))
    # order id of newly created order.
    razorpay_order_id = razorpay_order['id']
    # Callback Url
    callback_url = 'https://cloud.dentread.com/handlerequest/'
    # callback_url = 'http://127.0.0.1:8000/handlerMethod/'
    # we need to pass these details to frontend.
    context = {}
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
    context['razorpay_amount'] = amount
    context['currency'] = currency
    context['name'] = org.ctperson_name
    context['email'] = org.email
    context['phone'] = org.contact
    context['callback_url'] = callback_url
    context['usr'] = usr
    context['org'] = org
    context['topcat'] = topcat
    labInfo = LabWalletInfo.objects.filter(orgId = org)
    if labInfo:
        labWall = LabWalletInfo.objects.get(orgId = org)
        labWall.ORDERID = razorpay_order_id
        labWall.TXNAMOUNT = amount
        labWall.RESPMSG = "Payment Pending"
        labWall.save()
    else:
        wallet_info = LabWalletInfo(orgId = org, ORDERID = razorpay_order_id, TXNAMOUNT = amount, RESPMSG = "Payment Pending")
        wallet_info.save()
    return render(request, 'razorpay.html', context=context)


@csrf_exempt
def handlerMethod(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    mycart = ['Implant Surgical Guide', 'Digital Lab Services']
    topcat = Topcat.objects.filter(topcat__in = mycart)
    data = {'usr': usr, 'org': org, 'topcat': topcat}
    if request.method == "POST":
        try:
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            requestedTransaction = LabWalletInfo.objects.get(ORDERID = razorpay_order_id)
            result = razorpay_client.utility.verify_payment_signature(params_dict)
            if result is None:
                amount = 50000*100
                requestedTransaction.TXNDATE = datetime.today()
                requestedTransaction.RESPMSG = "Payment Failed"
                requestedTransaction.save()
                return render(request, 'paymentfail_imaging.html', data)
            else:
                amount = 50000*100
                razorpay_client.payment.capture(payment_id, amount)
                requestedTransaction.TXNID = payment_id
                requestedTransaction.TXNDATE = datetime.today()
                requestedTransaction.RESPMSG = "Payment Success"
                restAmount = requestedTransaction.restBalance
                myamt = 50000
                if restAmount == None:
                    restAmount = 0    
                requestedTransaction.totalBalance = (requestedTransaction.totalBalance + myamt) 
                requestedTransaction.save()
                data = {'usr': usr, 'requestedTransaction': requestedTransaction, 'org': org, 'topcat': topcat}
                # if signature verification fails.
                walletExp = WalletExpenses(orgId = org.id, organisationName = org.orgname, date=date.today(), amount = myamt, labId = org.id, status = 'Credited')
                try:
                    walletExp.save()
                except Exception as e:
                    print('exc', e)
                return render(request, 'paymentSuccess.html', data)
        except Exception as e:
            print('Exception', e)
            # if we don't find the required parameters in POST data  
            return render(request, 'paymentProcessed.html', {'usr': usr, 'org': org, 'topcat': topcat})
    else:
        # if other than POST request is made.
        return HttpResponseBadRequest()
    
    


def markAllAsRead(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    if request.method == "GET":
        noti = Notification.objects.filter(sendTo=org.id).filter(read = False)
        for i in noti:
            i.read = True
            try:
                i.save()
            except Exception as e:
                print(e)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def imageDataManagement(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    topcat = Topcat.objects.filter(status = 'Active')  
    service_order = ''
    patient = ''
    iosImage = IOSFile.objects.all()
    
    if org.orgtype == "Dental Clinic" or org.orgtype == "Dental Clinic Branch":
        topcat = Topcat.objects.filter(status = 'Active')
        service_order = ServiceOrder.objects.filter(orgid = org).exclude(reforgid__isnull = True)
        ids = []
        for i in service_order:
            ids.append(i.pid)
        patient = Patient.objects.filter(id__in = ids)
        for j in patient:
            j.name = j.name.title()
        iosImage = IOSFile.objects.filter(orgid = org)
    else:
        include = ['Implant Surgical Guide', 'Digital Lab Services']
        topcat = Topcat.objects.filter(topcat__in = include)
        service_order = ServiceOrder.objects.filter(reforgid = org.id)
        ids = []
        for i in service_order:
            ids.append(i.pid)
        patient = Patient.objects.filter(id__in = ids)
    page = "Image Data Management"
    data = {'usr': usr, 'patient': patient, 'page': page, 'org':org, 'topcat':topcat, 'service_order': service_order, 'iosImage': iosImage}
    return render(request, "ImageDataManagement/ImageDataManagement.html", data)


@csrf_exempt
def requestForImage(request, pk):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    patient = Patient.objects.get(id = pk)
    if request.method =='GET':
        #Get Dicom Data
        serveceOrder = ServiceOrder.objects.filter(pid = patient.id).exclude(reforgid__isnull = True)
        dicomData = ServiceOrderSerializers(serveceOrder, many=True)
        dicomThumbnail = dicomData.data
        #GET STL Data
        IOSfiles = IOSFile.objects.filter(pid = patient.id)   
        IOSfile = IOSFileSerializers(IOSfiles, many=True)
        iosThumbnail = IOSfile.data
        # Other Image Data
        otherImages = OtherImageFile.objects.filter(pid = patient.id)
        otherImage = OtherImageFileSerializers(otherImages, many=True)
        otherThumbnail = otherImage.data
        context = {'dicomThumbnail': dicomThumbnail, 'iosThumbnail': iosThumbnail, 'otherThumbnail': otherThumbnail}
        return JsonResponse(context, safe=False)

import random
def requestForOtp(request):
    if request.method == 'POST':
        mobile = request.POST.get('mobile')
        checkMobile = Users.objects.filter(contact = mobile).first
        otp = str(random.randint(1000,9999))
        if checkMobile:
            us = Users.objects.get(contact = mobile)
            us.otp = otp
            us.save()
            mobile = str(mobile)
            authkey = "390876AXCuN6Ma63f719c6P1"
            template_id = "63f707a4d6fc0522b03b0b72"
            OTP = otp
            # message = "Your OTP for login to dentread is: "+str(otp)+". Please don't share the OTP with others"
            payload = {
                "mobile": mobile,
                "otp": otp,
                "template_id" : "63f707a4d6fc0522b03b0b72"
            }
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "Authkey": authkey
            }
            url = "https://control.msg91.com/api/v5/otp?template_id="+template_id+"&mobile="+mobile+"&authkey="+authkey
            response = requests.post(url, json=payload, headers=headers)
            print(response.text)
            a = response.json()
            return JsonResponse({'message': 'OTP has been sent to your mobile Number'})
        else:
            return JsonResponse({'message': 'Oops ! Please entre the correct Mobile Number'})
    return JsonResponse({'message': 'Oops ! Please entre the correct Mobile Number'})

def mainSettings(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    findAdmin = org.admin
    admin = ''
    if findAdmin:
        admin = Users.objects.get(id = findAdmin)
    else:
        admin = usr
    users = Users.objects.filter(orgid_id = org)
    topcat = ''
    if org.orgtype == "Dental Lab" or org.orgtype == "Dental Lab Branch":
        include = ['Implant Surgical Guide', 'Digital Lab Services']
        topcat = Topcat.objects.filter(topcat__in = include)
    else:
        topcat = Topcat.objects.filter(status = 'Active')
    
    clinicWallet = ClinicWalletInfo.objects.filter(orgId = org)
    total_balance = ''
    if clinicWallet:
        wall = ClinicWalletInfo.objects.get(orgId = org)
        total_balance = wall.totalBalance
    if total_balance == 'NULL':
        total_balance = 0
    
    pack = Pack.objects.filter(status = 'Active')
    details = PackDetails.objects.all()
    WalletExp = WalletExpenses.objects.filter(orgId = org.id)
    subs = Subscriptions.objects.filter(orgid = org.id)
    subscriptions = ''
    if subs:
        subscriptions = Subscriptions.objects.get(orgid = org.id)
    print(subscriptions)
    context = {'pack': pack, 'details': details, 'usr': usr, 'org': org, 'admin': admin, 'total_balance': total_balance, 'users': users, 'topcat': topcat, 'WalletExp': WalletExp, 'subscriptions': subscriptions}
    return render(request, "main_setting.html", context)

def editAdmin(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id = usr.orgid_id)
    edit_user = Users.objects.get(id = id)
    if request.method == "POST" and 'propic' in request.FILES:
        doc = request.FILES
        edit_user.propic = doc['propic']
        edit_user.name = request.POST.get('admin-name')
        edit_user.contact = request.POST.get('admin-mobile')
        test = request.POST.get('admin-mobile')
        edit_user.email = request.POST.get('admin-email')
        edit_user.usertype = request.POST.get('admin-role')
        edit_user.status = request.POST.get('admin-status')
        edit_user.save()
        return redirect('/mainSettings')
    if request.method == "POST":
        edit_user.name = request.POST.get('admin-name')
        edit_user.contact = request.POST.get('admin-mobile')
        edit_user.email = request.POST.get('admin-email')
        edit_user.usertype = request.POST.get('admin-role')
        edit_user.status = request.POST.get('admin-status')
        edit_user.save()
        return redirect('/mainSettings')
    context = {'usr': usr, 'org': org}
    return render(request, "main_setting.html", context)

def editMyProfile(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id = usr.orgid_id)
    edit_user = Users.objects.get(id = id)
    if request.method == "POST":
        edit_user.name = request.POST.get('user-name')
        edit_user.contact = request.POST.get('user-mobile')
        edit_user.email = request.POST.get('user-email')
        edit_user.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def pwdChange(request):
    usr = Users.objects.get(username=request.user)
    user = request.user
    org = Organisation.objects.get(id=usr.orgid_id)
    findAdmin = org.admin
    admin = ''
    if findAdmin:
        admin = Users.objects.get(id = findAdmin)
    else:
        admin = usr
    if request.method == 'POST':
        new_password = request.POST.get('password')
        user.set_password(new_password)
        usr.password = new_password
        user.save()
        usr.save()
        context = {'usr': usr, 'org': org, 'admin': admin, 'message': 'Your password has changed successfully', 'class': 'success'}
        return render(request, "main_setting.html", context)

def changeUserPwd(request):
    usr = Users.objects.get(username=request.user)
    user = request.user
    org = Organisation.objects.get(id=usr.orgid_id)
    if request.method == 'POST':
        new_password = request.POST.get('password')
        user.set_password(new_password)
        usr.password = new_password
        user.save()
        usr.save()
        context = {'usr': usr, 'org': org, 'message': 'Your password has changed successfully', 'class': 'success'}
        return render(request, "profileDetails.html", context)

def addUserClinicNew(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    if org.orgtype == "Dental Lab":
        include = ['Implant Surgical Guide', 'Digital Lab Services']
        topcat = Topcat.objects.filter(topcat__in = include)
    else:
        topcat = Topcat.objects.filter(status = 'Active')
    if request.method == "POST" and 'propic' in request.FILES:
        doc = request.FILES
        pic = doc['propic']
        name = request.POST.get('name')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        username = request.POST.get('username')
        password = request.POST.get('password')
        department = request.POST.get('department')
        status = request.POST.get('status')
        newuser = Users(name = name, email=email, contact=contact, username=username, password=password, orgid=org, department=department, propic=pic, status=status)
        checkuser = User.objects.filter(username=username).first()
        checkContact = User.objects.filter(contact=contact).first()
        if checkuser:
            context = {'message': 'User already exists', 'class': 'danger', 'page': 'Add User', 'org': org}
            return render(request, 'CreateUser.html', context)
        elif checkContact:
            context = {'message': 'User already exists', 'class': 'danger', 'page': 'Add User', 'org': org}
            return render(request, 'CreateUser.html', context)
        else:
            user = User.objects.create_user(username, email, password)
            user.save()
            newuser.save()
            
            # Send Mail code
            user_name = str(newuser.name)
            clinic_name = str(org.orgname)
            user_id = str(newuser.username)
            user_password = str(newuser.password)
            details = EmailNotification.objects.get(eventCode = 'DRET-0008')
            connection = mail.get_connection()
            connection.open()
            from1 = 'info.dentread@gmail.com'
            subject = details.subject%(user_name, clinic_name)
            message = 'Dear '+str(user_name)+ '\n' + details.clinicSide%(clinic_name, user_id, user_password) + '\nThank You \nDentread'
            email1 = email
            email2 = 'info@dentread.com'
            mymailExicute = mail.EmailMessage(subject, message, from1, [email1], connection=connection)
            try:
                mymailExicute.send()
                connection.close()
            except Exception as e:
                message = e
            eventLog = EventLog(eventCode = 'DRET-0008', event = subject , log = 'A new User Registered to dentread, named : ' + str(org.orgname) + 'Form '+(org.orgname), orgId = org.id, userId = usr.id, time = datetime.now())
            try:
                eventLog.save()
            except Exception as ex:
                eventMessage = ex
            return redirect('/mainSettings')
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        username = request.POST.get('username')
        password = request.POST.get('password')
        department = request.POST.get('department')
        status = request.POST.get('status')
        newuser = Users(name=name, email=email, contact=contact,
                        username=username, password=password, orgid=org, department=department,
                        status=status)
        checkuser = User.objects.filter(username=username).first()
        if checkuser:
            context = {'message': 'User already exists', 'class': 'danger', 'page': 'Add User', 'org': org}
            return render(request, 'CreateUser.html', context)
        else:
            user = User.objects.create_user(username, email, password)
            user.save()
            newuser.save()
            # Send Mail code
            user_name = str(newuser.name)
            clinic_name = str(org.orgname)
            user_id = str(newuser.username)
            user_password = str(newuser.password)
            details = EmailNotification.objects.get(eventCode = 'DRET-0008')
            connection = mail.get_connection()
            connection.open()
            from1 = 'info.dentread@gmail.com'
            subject = details.subject%(user_name, clinic_name)
            message = message = 'Dear '+str(user_name)+ '\n' + details.clinicSide%(clinic_name, user_id, user_password) + '\nThank You \nDentread'
            email1 = email
            email2 = 'info@dentread.com'
            mymailExicute = mail.EmailMessage(subject, message, from1, [email1], connection=connection)
            try:
                mymailExicute.send()
                connection.close()
            except Exception as e:
                message = e
            eventLog = EventLog(eventCode = 'DRET-0008', event = subject , log = 'A new User Registered to dentread, named : ' + str(org.orgname) + 'Form '+(org.orgname), orgId = org.id, userId = usr.id, time = datetime.now())
            try:
                eventLog.save()
            except Exception as ex:
                eventMessage = ex
            return redirect('/mainSettings')
    context = { 'page': 'Add User', 'org': org,'topcat': topcat, 'usr':usr}
    return render(request, 'CreateUser.html', context)

def profileDetails(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    topcat = ''
    if org.orgtype == 'Dental Clinic' or org.orgtype == 'Dental Clinic Branch':
        topcat = Topcat.objects.filter(status='Active')
    elif org.orgtype == 'Domain Owner':
        exclude = ['Digital Lab Services']
        topcat = Topcat.objects.filter(status="Active").exclude(topcat__in = exclude)
    else:
        exclude = ['Radiological Report', 'Image Analysis Report', 'Implant Planning Report']
        topcat = Topcat.objects.filter(status='Active').exclude(topcat__in = exclude)
    data = {'usr': usr, 'org': org, 'page': 'My Profile','topcat': topcat}
    return render(request, 'profileDetails.html', data)


def editUserProfile(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    if request.method == "POST" and 'propic' in request.FILES:
        doc = request.FILES
        pic = doc['propic']
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        department = request.POST.get('department')
        status = request.POST.get('status')

        usr.name = name
        usr.propic = pic
        usr.contact = contact
        usr.email = email
        usr.department = department
        usr.status = status
        usr.save()
        return redirect('/profileDetails')

    if request.method == "POST":
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        department = request.POST.get('department')
        status = request.POST.get('status')
        usr.name = name
        usr.contact = contact
        usr.email = email
        usr.department = department
        usr.status = status
        usr.save()
        return redirect('/profileDetails')
    data = {'usr': usr, 'org': org, 'page': 'Edit Profile','topcat':topcat}
    return render(request, 'editUserProfile.html', data)

def fullBranchDetails(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    organisation = Organisation.objects.get(id=id)
    topcat = ''
    if org.orgtype == 'Dental Clinic' or org.orgtype == 'Dental Clinic Branch':
        topcat = Topcat.objects.filter(status='Active')
    elif org.orgtype == 'Domain Owner':
        exclude = ['Digital Lab Services']
        topcat = Topcat.objects.filter(status="Active").exclude(topcat__in = exclude)
    else:
        exclude = ['Radiological Report', 'Image Analysis Report', 'Implant Planning Report']
        topcat = Topcat.objects.filter(status='Active').exclude(topcat__in = exclude)
    man = organisation.managerId
    manager = ''
    try:
        if man: 
            manager = Users.objects.get(id = man)
    except Exception as e:
        return None
    
    users = Users.objects.filter(orgid_id = organisation)
    data = {'usr': usr, 'org': org, 'topcat':topcat, 'organisation': organisation, 'manager': manager, 'users': users}
    return render(request, 'BranchSettings.html', data)


def editBranchProfile(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    organisation = Organisation.objects.get(id=id)
    if request.method == "POST" and 'logo' in request.FILES:
        doc = request.FILES
        pic = doc['logo']
        organisation.orgname = request.POST.get('orgname')
        organisation.address = request.POST.get('address')
        organisation.city = request.POST.get('city')
        organisation.state = request.POST.get('state')
        organisation.pincode = request.POST.get('pincode')
        organisation.country = request.POST.get('country')
        organisation.logo = pic
        organisation.save()
        return redirect('/fullBranchDetails/'+str(organisation.id))
    if request.method == "POST":
        organisation.orgname = request.POST.get('orgname')
        organisation.address = request.POST.get('address')
        organisation.city = request.POST.get('city')
        organisation.state = request.POST.get('state')
        organisation.pincode = request.POST.get('pincode')
        organisation.country = request.POST.get('country')
        organisation.save()
        return redirect('/fullBranchDetails/'+str(organisation.id))
    return redirect('/fullBranchDetails/'+str(organisation.id))

def editManagerDetails(request, id1, id2):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    manager = Users.objects.get(id = id1)
    organisation = Organisation.objects.get(id=id2)
    if request.method == "POST":
        manager.name = request.POST.get('manager-name')
        manager.status = request.POST.get('manager-status')
        manager.usertype = request.POST.get('manager-role')
        manager.save()
        return redirect('/fullBranchDetails/'+str(organisation.id))
    if request.method == "POST" and 'propic' in request.FILES:
        doc = request.FILES
        pic = doc['propic']
        manager.name = request.POST.get('manager-name')
        manager.status = request.POST.get('manager-status')
        manager.usertype = request.POST.get('manager-role')
        manager.propic = pic
        manager.save()
        return redirect('/fullBranchDetails/'+str(organisation.id))
    return redirect('/fullBranchDetails/'+str(organisation.id))

def addToWalletClinic(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    if request.method == "POST":
        request_amount = request.POST.get('amount')
        req_amount = int(request_amount)
        amount = req_amount*100
        currency = 'INR'
        topcat = Topcat.objects.filter(status = 'Active')
        razorpay_order = razorpay_client.order.create(dict(amount=amount, currency=currency, payment_capture='0'))
        # order id of newly created order.
        razorpay_order_id = razorpay_order['id']
        # Callback Url
        # callback_url = 'https://cloud.dentread.com/handlerequest/'
        callback_url = 'http://127.0.0.1:8000/handlerProcess/'
        # we need to pass these details to frontend.
        context = {}
        context['razorpay_order_id'] = razorpay_order_id
        context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
        context['razorpay_amount'] = amount
        context['currency'] = currency
        context['name'] = org.ctperson_name
        context['email'] = org.email
        context['phone'] = org.contact
        context['callback_url'] = callback_url
        context['usr'] = usr
        context['org'] = org
        context['topcat'] = topcat
        labInfo = ClinicWalletInfo.objects.filter(orgId = org)
        if labInfo:
            labWall = ClinicWalletInfo.objects.get(orgId = org)
            labWall.ORDERID = razorpay_order_id
            labWall.TXNAMOUNT = amount
            labWall.RESPMSG = "Payment Pending"
            labWall.request_amount = request_amount
            labWall.save()
        else:
            wallet_info = ClinicWalletInfo(orgId = org, ORDERID = razorpay_order_id, TXNAMOUNT = amount, RESPMSG = "Payment Pending", request_amount=request_amount)
            wallet_info.save()
    return render(request, 'razorpay.html', context=context)


@csrf_exempt
def handlerProcess(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    topcat = Topcat.objects.filter(status = 'Active')
    data = {'usr': usr, 'org': org, 'topcat': topcat}
    if request.method == "POST":
        try:
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            requestedTransaction = ClinicWalletInfo.objects.get(ORDERID = razorpay_order_id)
            result = razorpay_client.utility.verify_payment_signature(params_dict)
            if result is None:
                amount = requestedTransaction.request_amount*100
                requestedTransaction.TXNDATE = datetime.today()
                requestedTransaction.RESPMSG = "Payment Failed"
                requestedTransaction.save()
                return render(request, 'paymentfail_imaging.html', data)
            else:
                amount = requestedTransaction.request_amount*100
                razorpay_client.payment.capture(payment_id, amount)
                requestedTransaction.TXNID = payment_id
                requestedTransaction.TXNDATE = datetime.today()
                requestedTransaction.RESPMSG = "Payment Success"
                labInfo = ClinicWalletInfo.objects.filter(orgId = org)
                restAmount = ''
                if labInfo:
                    labWall = ClinicWalletInfo.objects.get(orgId = org)
                    restAmount = labWall.totalBalance
                actual_amt = requestedTransaction.request_amount
                razorpay_fee = (requestedTransaction.request_amount)*2.5/100
                myamt = int(actual_amt) - int(razorpay_fee)
                if restAmount == None:
                    restAmount = 0    
                requestedTransaction.totalBalance = (restAmount + myamt) 
                requestedTransaction.save()
                data = {'usr': usr, 'requestedTransaction': requestedTransaction, 'org': org, 'topcat': topcat}
                # if signature verification fails.
                walletExp = WalletExpenses(orgId = org.id, organisationName = org.orgname, date = date.today(), amount = myamt, labId = org.id, status = 'Credited')
                try:
                    walletExp.save()
                except Exception as e:
                    print('exc', e)
                return render(request, 'paymentSuccess.html', data)
        except Exception as e:
            print('Exception', e)
            # if we don't find the required parameters in POST data  
            return render(request, 'paymentProcessed.html', {'usr': usr, 'org': org, 'topcat': topcat})
    else:
        # if other than POST request is made.
        return HttpResponseBadRequest()
    
def activateSubscription(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    today = datetime.today()
    startDate2 = today + timedelta(days = 30)
    startDate3 = today + timedelta(days = 60)
    if request.method == "POST":
        myId = request.POST.get('orgId')
        id = int(myId)
        organisation = Organisation.objects.get(id = id)
        subscription = Subscriptions.objects.filter(orgid = organisation.id)
        choose = request.POST.get('selected-plan')
        choosed = ''
        if choose == 'classic-plan':
            choosed = 'Dentread Classic'
        elif choose == 'premium-plan':
            choosed = 'Dentread Premium'
        else:
            choosed = 'Dentread Basic'
        
        pack = Pack.objects.get(type = choosed)
        choosed_type = pack.id
        duration = request.POST.get('plan-amount')
        type = ''
        status = 'Active'
        orgId = organisation
        startDate = datetime.today()
        print(startDate)
        endDate = ''
        Storage = 0
        VCA = 0
        XRAY = 0
        CBCT = 0
        price = 0
        applied = 'Dental Clinic'
        if choosed_type:
            pack = Pack.objects.get(id = choosed_type)
            type = pack.type
            status = 'Active' 
            if type == 'Dentread Premium' and duration == 'Month':
                endDate = startDate + timedelta(days=30)
                VCA = pack.VCA
                XRAY = pack.XRAY
                CBCT = pack.XRAY
                Storage = 5
                price = pack.price
                checkFS = FreeService.objects.filter(orgId = organisation.id)
                if checkFS:
                    for i in checkFS:
                        fS = FreeService.objects.get(orgId = organisation.id)
                        fS.delete()
                else:
                    free = FreeService(orgId = organisation.id, pack = pack.type, status = 'Active', service = 'Dentread Credit', VCA1 = 3, Storage1 = 50, firstMonth = 3, startDate1 = today)
                    free.save()
            elif type == 'Dentread Premium' and duration == 'Quarter':
                endDate = startDate + timedelta(days=90)
                VCA = pack.VCA * 3
                XRAY = pack.XRAY * 3
                CBCT = pack.XRAY * 3
                Storage = 5
                price = pack.price2
                print('price',price)
                checkFS = FreeService.objects.filter(orgId = organisation.id)
                if checkFS:
                    for i in checkFS:
                        fS = FreeService.objects.get(orgId = organisation.id)
                        fS.delete()
                else:
                    free = FreeService(orgId = organisation.id, pack = pack.type, status = 'Active', service = 'Dentread Credit', VCA1 = 3, VCA2 = 3, VCA3 = 3, Storage1 = 50, Storage2 = 50, Storage3 = 50, firstMonth = 3, secondMonth = 3, thirdMonth = 3, startDate1 = today, startDate2 = startDate2, startDate3 = startDate3)
                    free.save()
            elif type == 'Dentread Classic' and duration != None:
                organisation.paymentOption = 'payLater'
                organisation.topUp = request.POST.get('plan-amount')
                organisation.topUpAvailable = request.POST.get('plan-amount')
                organisation.save()
                endDate = today + timedelta(days=365)
                VCA = 0
                XRAY = 0
                CBCT = 0
                Storage = 5
                price = pack.price
            else:
                endDate = today + timedelta(days=365)
                VCA = 0
                XRAY = 0
                CBCT = 0
                Storage = 5
                price = pack.price
            if subscription:
                sub = Subscriptions.objects.get(orgid = organisation.id)
                sub.type = type
                sub.status = status
                sub.startDate = startDate
                sub.endDate = endDate
                Storage = Storage
                sub.VCA = VCA
                sub.XRAY = XRAY
                sub.CBCT = CBCT
                sub.applied = applied
                sub.price = price
                sub.save()
                organisation.subscription = type
                organisation.subscriptionId = choosed_type
                organisation.save()
            else:
                sucs = Subscriptions(orgid = organisation.id, type = type, status = status, startDate = startDate, Storage = Storage, endDate = endDate, VCA = VCA, XRAY = XRAY, CBCT = CBCT, applied = applied, price = price)
                sucs.save()
                organisation.subscription = type
                organisation.subscriptionId = choosed_type
                organisation.save()
    exclude = ['Dental Clinic Branch', 'Dental Lab Branch', 'Imaging Centre Branch']
    centre = Organisation.objects.all().exclude(orgtype__in = exclude)
    for i in centre:
        users = Users.objects.filter(orgid=i)
        i.users = users.count()
    exclude = ['Digital Lab Services']
    topcat = Topcat.objects.filter(status="Active").exclude(topcat__in = exclude)
    
    pack = Pack.objects.filter(status = 'Active')
    details = PackDetails.objects.all()
    message = 'Plan Updated Successfully'
    data = {'usr': usr, 'org': org,'topcat': topcat, 'centre': centre, 'pack': pack, 'details': details, 'message': message}
    return redirect('/all_imaging')

def allShipment(request):
    usr = Users.objects.get(username = request.user)
    org = Organisation.objects.get(id = usr.orgid_id)
    service_order = ShipmentOrderDetails.objects.filter(orgId = org.id).exclude(order_id__isnull = True)
    for i in service_order:
        i.order_status = ServiceOrder.objects.get(id = i.repid).status
    context = {'usr': usr, 'org': org, 'service_order': service_order, 'topcat': topcat}
    return render(request, 'allShipment.html', context)

def shipmentHistory(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    repId = ServiceOrder.objects.get(id=id)
    patient = Patient.objects.get(id = repId.pid)
    service_order = ShipmentOrderDetails.objects.filter(repid = repId.id).exclude(order_id__isnull = True)
    context = {'usr': usr, 'org': org, 'service_order': service_order, 'repId': repId, 'topcat': topcat, 'patient': patient}
    return render(request, 'shipmentHistory.html', context)

def generateMenifest(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    shp = ShipmentOrderDetails.objects.get(id = id)
    order_id = str(shp.order_id)
    token = str(ShipRocketAuth.objects.get(id = 1).token)
    
    url = "https://apiv2.shiprocket.in/v1/external/manifests/print"
    payload = json.dumps({
    "order_ids": [
        order_id
    ]
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer '+ token
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    manifest_url = ''
    if response.status_code == 200:
        data = response.json()
        manifest_url = data["manifest_url"]
        return redirect(manifest_url)
    else:
        return JsonResponse({'status': 'Manifest not generated yet, please try after some time'})

def generateLabel(request, id):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    shp = ShipmentOrderDetails.objects.get(id = id)
    shipment_id = str(shp.shipment_id)
    token = str(ShipRocketAuth.objects.get(id = 1).token)
    url = "https://apiv2.shiprocket.in/v1/external/courier/generate/label"
    payload = json.dumps({
    "shipment_id": [
        shipment_id
    ]
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer '+ token
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    label_url = ''
    if response.status_code == 200:
        data = response.json()
        label_url = data["label_url"]
        return redirect(label_url)
    else:
        return JsonResponse({'status': 'Label is not generated yet, please try after some time'})

def payNowStatusCode(request):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    code = 200
    return render(request, 'Alerts/PayNowShipment.html', {'code': code})

def requestForStlFile(request, id):
    service_order = ServiceOrder.objects.get(id = id)
    stlFile = IOSFile.objects.filter(repid = service_order.id)
    stlCheck = False
    fileName = ''
    for i in stlFile:
        fileName = i.fileName
        if fileName.endswith('.stl'):
            stlCheck = True
    firstfile = stlFile.first()
    firstId = firstfile.id
    site = firstfile.site
    data = {'service_order': service_order, 'site': site, 'stlFile': stlFile, 'stlCheck': stlCheck, 'firstId': firstId}
    return render(request, 'viewStlSecond.html', data)

def viewLabStlImage(request, id, site):
    service_order = ServiceOrder.objects.get(id = id)
    stlFile = IOSFile.objects.filter(repid = service_order.id)
    stlCheck = False
    fileName = ''
    file = IOSFile.objects.filter(repid = service_order.id).filter(site = site)
    firstfile = ''
    if file:
        firstfile = file.first()
        fileName = firstfile.fileName
        if fileName.endswith('.stl'):
            stlCheck = True
    firstId = firstfile.id
    site = site
    data = {'service_order': service_order, 'site': site, 'stlFile': stlFile, 'stlCheck': stlCheck, 'firstId': firstId}
    return render(request, 'viewStlSecond.html', data)

def reverseEngineering(request, id1, id2):
    service_order = ServiceOrder.objects.get(repid = id1)
    stlFile = IOSFile.objects.filter(repid = service_order.id)
    file = IOSFile.objects.get(id = id2)
    fileName = ''
    stlCheck = False
    fileName = file.fileName
    if fileName.endswith('.stl'):
        stlCheck = True
    
    firstId = IOSFile.objects.get(id = id2).id
    site = IOSFile.objects.get(id = id2).site
    data = {'stlFile': stlFile, 'site': site, 'service_order': service_order,'stlCheck': stlCheck, 'firstId': firstId}
    return render(request, 'viewStlSecond.html', data)

def renderSTLFile(request, pk):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    cfile = IOSFile.objects.get(id=pk)
    url = cfile.file.url
    return redirect(url)


def requestPlanningFile(request, id1, id2):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = id1)
    lineItem = Prosthetic.objects.get(id = id2)
    stlFile = FeedFile.objects.filter(repid=service_order.id).filter(sodrid = lineItem.id)
    stlCheck = False
    fileName = ''
    for i in stlFile:
        fileName = i.fileName
        if fileName.endswith('.stl'):
            stlCheck = True
    firstfile = stlFile.first()
    firstId = firstfile.id
    data = {'service_order': service_order, 'lineItem': lineItem, 'stlFile': stlFile, 'stlCheck': stlCheck, 'firstId': firstId}
    return render(request, 'viewPlanningStlFile.html', data)


def reverseEngg(request, id1, id2, id3):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(repid = id1)
    lineItem = Prosthetic.objects.get(id = id2)
    stlFile = FeedFile.objects.filter(repid=service_order.id).filter(sodrid = lineItem.id)
    file = FeedFile.objects.get(id = id3)
    fileName = ''
    stlCheck = False
    fileName = file.fileName
    if fileName.endswith('.stl'):
        stlCheck = True
    firstId = FeedFile.objects.get(id = id3).id
    data = {'stlFile': stlFile, 'service_order': service_order,'stlCheck': stlCheck, 'firstId': firstId}
    return render(request, 'viewPlanningStlFile.html', data)

def renderPlanningFile(request, pk):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    cfile = FeedFile.objects.get(id=pk)
    url = cfile.file.url
    return redirect(url)

def requestGuidePlanFile(request, id1, id2):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = id1)
    lineItem = Suricalguide.objects.get(id = id2)
    stlFile = FeedFile.objects.filter(repid=service_order.id).filter(sodrid = lineItem.id)
    stlCheck = False
    fileName = ''
    for i in stlFile:
        fileName = i.fileName
        if fileName.endswith('.stl'):
            stlCheck = True
    firstfile = stlFile.first()
    firstId = firstfile.id
    data = {'service_order': service_order, 'lineItem': lineItem, 'stlFile': stlFile, 'stlCheck': stlCheck, 'firstId': firstId}
    return render(request, 'viewPlanningStlFile.html', data)

def reverseEnggGuide(request, id1, id2, id3):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(repid = id1)
    lineItem = Suricalguide.objects.get(id = id2)
    stlFile = FeedFile.objects.filter(repid=service_order.id).filter(sodrid = lineItem.id)
    fileName = ''
    stlCheck = False
    file = FeedFile.objects.get(id = id3)
    fileName = file.fileName
    if fileName.endswith('.stl'):
        stlCheck = True
    firstId = FeedFile.objects.get(id = id3).id
    data = {'stlFile': stlFile, 'service_order': service_order,'stlCheck': stlCheck, 'firstId': firstId}
    return render(request, 'viewPlanningStlFile.html', data)

#Guide DesignFile
#If DesignFile Is a stlFile
def surgicalGuideFile(request, id1, id2):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(id = id1)
    lineItem = Suricalguide.objects.get(id = id2)
    stlFile = DesignFile.objects.filter(repid=service_order.id).filter(sodrid = lineItem.id)
    stlCheck = False
    fileName = ''
    for i in stlFile:
        fileName = i.fileName
        if fileName.endswith('.stl'):
            stlCheck = True
    firstfile = stlFile.first()
    firstId = firstfile.id
    data = {'service_order': service_order, 'lineItem': lineItem, 'stlFile': stlFile, 'stlCheck': stlCheck, 'firstId': firstId}
    return render(request, 'viewSurgiDesignFile.html', data)

def prepareTheNextFile(request, id1, id2, id3):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    service_order = ServiceOrder.objects.get(repid = id1)
    lineItem = Suricalguide.objects.get(id = id2)
    stlFile = DesignFile.objects.filter(repid=service_order.id).filter(sodrid = lineItem.id)
    fileName = ''
    stlCheck = False
    file = DesignFile.objects.get(id = id3)
    fileName = file.fileName
    if fileName.endswith('.stl'):
        stlCheck = True
    firstId = DesignFile.objects.get(id = id3).id
    data = {'stlFile': stlFile, 'service_order': service_order,'stlCheck': stlCheck, 'firstId': firstId}
    return render(request, 'viewSurgiDesignFile.html', data)

def renderIntoDesignFile(request, pk):
    usr = Users.objects.get(username=request.user)
    org = Organisation.objects.get(id=usr.orgid_id)
    cfile = DesignFile.objects.get(id=pk)
    url = cfile.file.url
    return redirect(url)


    