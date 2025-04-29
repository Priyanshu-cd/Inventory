from django.shortcuts import render
from django.http import HttpResponse , Http404 , HttpResponseRedirect
from dash import models
from dash import forms
from django.urls import reverse
from django.db.models import Sum
from django.utils import timezone


from itertools import chain
from operator import attrgetter


# Create your views here.
# ---------------------------------
# 1. dash/
# ---------------------------------
def dash_main(request):
    if request.method == 'GET':
        org=models.Organization.objects.first()
        projects=org.projects.all()

    return render(request,"dash/main.html",{"all_pro":projects})

# ---------------------------------
# 2. dash/<int:id>/
# ---------------------------------
def dash_one(request,id):
    try:
        org=models.Organization.objects.first()
        project=org.projects.get(id=id)
        try:
            total_adv=models.AdvanceDetail.objects.filter(project=project).count()
            total_exp=models.Inventory.objects.filter(project=project).count()
        except Exception as r:
            print(r)
        response=render(request,"dash/one.html",{"upper_text":f"{project.name}","project":project,
                                                 "total_adv":total_adv, "total_exp":total_exp,
                                                 "total_trans":total_exp+total_adv})
        response.set_cookie("id",project.id)
        response.set_cookie("one",True)
        return response
    except:
        raise Http404()

# ---------------------------------
# 3. dash/projects/ (all,add)
# ---------------------------------
def dash_projects(request,view):
    title="Projects"
    org=models.Organization.objects.first()

    if view=="all":
        projects=org.projects.all().order_by('-id')
        # adv=projects.aggregate(Sum(""))
        response =render(request,"dash/projects.html",{"view":str(view),"all_pro":projects})
        response.delete_cookie("id")
        response.delete_cookie("date")
        response.delete_cookie("one")
        return response
    elif view=="add":
        title="Add Project"
        if request.method=='POST':
            form=forms.ProjectForm(request.POST)
            if form.is_valid():
                project = form.save(commit=False)
                project.organization_id = org.id
                project.save()
                return HttpResponseRedirect(reverse("dash:projects",args=['all'] ))
        else:
            form=forms.ProjectForm()
        response =render(request,"dash/projects.html",{"form":form,"view":str(view)})
        response.delete_cookie("id")
        response.delete_cookie("date")
        response.delete_cookie("one")
        return response
    else:
        raise Http404
    
# ---------------------------------
# 4. dash/transactions/
# ---------------------------------
def dash_transactions(request):
    filters=forms.FilterForm(request.POST or None)
    cookie=request.COOKIES

    id=cookie.get('id')
    date=cookie.get('date')

    filters.fields['project'].initial=id
    filters.fields['date'].initial=date

    data=None
    if id  is None and date is None:
        upper_text="All"
        

        adv = models.AdvanceDetail.objects.all()
        inv = models.Inventory.objects.all()

        data= sorted(chain(adv, inv), key=attrgetter('date'), reverse=True)

    elif id is None and date is not None:
        upper_text="All"

        adv = models.AdvanceDetail.objects.filter(date=date)
        inv = models.Inventory.objects.filter(date=date)

        data= sorted(chain(adv, inv), key=attrgetter('date'), reverse=True)

    elif date is None and id is not None:
        org=models.Organization.objects.first()
        project=org.projects.get(id=id)
        upper_text=project.name

        adv = models.AdvanceDetail.objects.filter(project_id=id)
        inv = models.Inventory.objects.filter(project_id=id)

        data= sorted(chain(adv, inv), key=attrgetter('date'), reverse=True)
    else:
        org=models.Organization.objects.first()
        project=org.projects.get(id=id)
        upper_text=project.name

        adv = models.AdvanceDetail.objects.filter(project_id=id,date=date)
        inv = models.Inventory.objects.filter(project_id=id,date=date)

        data= sorted(chain(adv, inv), key=attrgetter('date'), reverse=True)
        
        
    response = render(request,"dash/transactions.html",{"upper_text":f"{upper_text} -",
                        "filters":filters,
                        "data":data,
                        "view":"all"})
    if request.method=='POST':
        if filters.is_valid(): 
            filter_project = filters.cleaned_data.get("project")
            filter_date = filters.cleaned_data.get("date")
            response = HttpResponseRedirect(reverse("dash:transactions" ))
            if filter_project  is None and filter_date is None:
                response.delete_cookie("id")
                response.delete_cookie("date")
            elif filter_project is None and filter_date is not None:
                response.delete_cookie("id")
                response.set_cookie("date",f"{filter_date}")
            elif filter_date is None and filter_project is not None:
                response.delete_cookie("date")
                response.set_cookie("id",f"{filter_project.id}")
            else:
                response.set_cookie("id",f"{filter_project.id}")
                response.set_cookie("date",f"{filter_date}")
            return response

    return response

# ---------------------------------
# 5. dash/transactions/spend
# ---------------------------------
def dash_spend(request):
    form = forms.ExpenseForm(request.POST or None)
    filters=forms.FilterForm(request.POST or None)
    cookie=request.COOKIES

    id=cookie.get('id')
    date=cookie.get('date')

    filters.fields['project'].initial=id
    form.fields['project'].initial=id

    filters.fields['date'].initial=date

    #Form initials:
    form.fields['quantity'].initial = 1

    if id  is None and date is None:
        data=models.Inventory.objects.all()
    elif id is None and date is not None:
        data=models.Inventory.objects.filter(date=date)
    elif date is None and id is not None:
        data=models.Inventory.objects.filter(project_id=id)
    else:
        
        if date:
            data = models.Inventory.objects.filter(project_id=id, date=date)
        else:
            data = models.Inventory.objects.filter(project_id=id)


    try:
        org=models.Organization.objects.first()
        project=org.projects.get(id=id)
        upper_text=project.name
    except Exception as e:
        upper_text="All"

    if request.method == 'POST':
        if form.is_valid():
            form_data = form.cleaned_data
            form_project=form_data['project']

            instance=form.save(commit=False)
            instance.total_buy = form_data['buy_price'] * form_data['quantity']
            instance.total_sell = form_data['sell_price'] * form_data['quantity']
            instance.total_profit = instance.total_sell - instance.total_buy

            form_project.buy_total +=instance.total_buy
            form_project.sell_total +=instance.total_sell
            form_project.advance_total -= instance.total_sell
            form_project.profit_total += instance.total_profit
            form_project.save()

            instance.save()
            return HttpResponseRedirect(reverse("dash:transactions"))
        
        if filters.is_valid(): 
            filter_project = filters.cleaned_data.get("project")
            filter_date = filters.cleaned_data.get("date")
            response = HttpResponseRedirect(reverse("dash:trans_spend" ))
            if filter_project  is None and filter_date is None:
                response.delete_cookie("id")
                response.delete_cookie("date")
            elif filter_project is None and filter_date is not None:
                response.delete_cookie("id")
                response.set_cookie("date",f"{filter_date}")
            elif filter_date is None and filter_project is not None:
                response.delete_cookie("date")
                response.set_cookie("id",f"{filter_project.id}")
            else:
                response.set_cookie("id",f"{filter_project.id}")
                response.set_cookie("date",f"{filter_date}")
            return response
        

    return render(request, "dash/transactions.html", {
        "notify": " -Spend",
        "form": form,
        "view": "exp",
        "data":data,
        "filters":filters,
        "upper_text":f"{upper_text} -",
    })


# ---------------------------------
# 6. dash/transactions/advance
# ---------------------------------
def dash_advance(request):
    form = forms.AdvanceForm(request.POST or None)
    filters=forms.FilterForm(request.POST or None)
    cookie=request.COOKIES

    id=cookie.get('id')
    date=cookie.get('date')

    filters.fields['project'].initial=id
    form.fields['project'].initial=id

    filters.fields['date'].initial=date

    if id  is None and date is None:
        data=models.AdvanceDetail.objects.all().order_by('-date')
    elif id is None and date is not None:
        data=models.AdvanceDetail.objects.filter(date=date)
    elif date is None and id is not None:
        data=models.AdvanceDetail.objects.filter(project_id=id).order_by('-date')
    else:
        
        if date:
            data = models.AdvanceDetail.objects.filter(project_id=id, date=date)
        else:
            data = models.AdvanceDetail.objects.filter(project_id=id)


    try:
        org=models.Organization.objects.first()
        project=org.projects.get(id=id)
        upper_text=project.name
    except Exception as e:
        upper_text="All"

    if request.method == 'POST':
        if form.is_valid():
            form_data = form.cleaned_data
            form_project=form_data['project']

            instance=form.save(commit=False)
            form_project.advance_total += instance.amount
            form_project.lifetime_advance += instance.amount
            form_project.save()
            instance.save()
            return HttpResponseRedirect(reverse("dash:transactions"))
        
        if filters.is_valid(): 
            filter_project = filters.cleaned_data.get("project")
            filter_date = filters.cleaned_data.get("date")
            response = HttpResponseRedirect(reverse("dash:trans_advance" ))
            if filter_project  is None and filter_date is None:
                response.delete_cookie("id")
                response.delete_cookie("date")
            elif filter_project is None and filter_date is not None:
                response.delete_cookie("id")
                response.set_cookie("date",f"{filter_date}")
            elif filter_date is None and filter_project is not None:
                response.delete_cookie("date")
                response.set_cookie("id",f"{filter_project.id}")
            else:
                response.set_cookie("id",f"{filter_project.id}")
                response.set_cookie("date",f"{filter_date}")
            return response
        

    return render(request, "dash/transactions.html", {
        "notify": " -Advance",
        "form": form,
        "view": "adv",
        "data":data,
        "filters":filters,
        "upper_text":f"{upper_text} -",
    })

# ---------------------------------
# 7. dash/update/?(project)/?(exp)/?(adv)   /None...
# ---------------------------------
def dash_update(request,project_id,spend_id,advance_id):
    title=""

    if project_id !="None" and spend_id == "None" and advance_id == "None":
        form_type="project"
        try:
            project = models.Project.objects.get(id=int(project_id))
            title=project.name
        except:
            title=form_type
            raise Http404()
        form=forms.ProjectForm(instance=project)


    elif  spend_id != "None" and project_id != "None" and advance_id== "None":
        form_type="spend"
        try:
            spend = models.Inventory.objects.get(project_id=int(project_id),id=int(spend_id))
            title=spend.product_name

        except:
            title=form_type
            raise Http404()
        form=forms.ExpenseForm(instance=spend or request.POST)


    elif  advance_id != "None" and project_id != "None" and spend_id== "None":
        form_type="advance"

        try:
            advance = models.AdvanceDetail.objects.get(project_id=int(project_id),id=int(advance_id))
            title=advance.description
        except:
            title=form_type
            raise Http404()
        form=forms.AdvanceForm(instance=advance or request.POST) 
    else:
        raise Http404()
    
    if request.method == "POST":

        if request.POST.get('action')=="save":
            if form_type=="project":
                form = forms.ProjectForm(request.POST, instance=project)

                if form.is_valid():
                    form.save()
                    return HttpResponseRedirect(reverse("dash:projects",args=["all"]))
                else:
                    form=forms.ProjectForm(instance=project)

            elif form_type=="advance":
                form = forms.AdvanceForm(request.POST, instance=advance)

                if form.is_valid():
        
                    form_data = form.cleaned_data
                    form_project=form_data.get('project')
                    before_detail = models.AdvanceDetail.objects.get(project=form_project,id=advance_id)

                    instance=form.save(commit=False)

                    form_project.advance_total -= before_detail.amount
                    form_project.advance_total += instance.amount

                    form_project.lifetime_advance -= before_detail.amount
                    form_project.lifetime_advance += instance.amount

                    form_project.save()
                    instance.save()
                    return HttpResponseRedirect(reverse("dash:trans_advance"))
                else:
                    form=forms.ProjectForm(instance=project)
            elif form_type=="spend":
                form = forms.ExpenseForm(request.POST, instance=spend)
                if form.is_valid():
                    form_data = form.cleaned_data
                    form_project=form_data.get('project')
                    before_detail = models.Inventory.objects.get(project=form_project,id=spend_id)

                    instance=form.save(commit=False)

                # resotre project:
                    form_project.buy_total -= before_detail.total_buy
                    form_project.sell_total -= before_detail.total_sell
                    form_project.profit_total -= before_detail.total_profit
                    form_project.advance_total += before_detail.total_sell
                    form_project.save()

                #spend execute:
                    instance.total_buy = form_data['buy_price'] * form_data['quantity']
                    instance.total_sell = form_data['sell_price'] * form_data['quantity']
                    instance.total_profit = instance.total_sell - instance.total_buy

                    form_project.buy_total +=instance.total_buy
                    form_project.sell_total +=instance.total_sell
                    form_project.advance_total -= instance.total_sell
                    form_project.profit_total += instance.total_profit
                    form_project.save()
                    instance.save()
                    return HttpResponseRedirect(reverse("dash:trans_spend"))
                else:
                    form=forms.ExpenseForm(instance=project)

        elif request.POST.get('action')=="delete":
            print("delete")
            if form_type =="project":
                project.delete()

            elif form_type=="advance":
                before_detail = models.AdvanceDetail.objects.get(id=advance_id)

                form_project=before_detail.project
                print("before",form_project.__dict__)
                form_project.advance_total -= before_detail.amount
                form_project.lifetime_advance -= before_detail.amount
                print("after",form_project.__dict__)
                advance.delete()
                form_project.save()

            elif form_type=="spend":
                # spend.delete()
                print("spend delete")
                before_detail = models.Inventory.objects.get(id=spend_id)

                form_project=before_detail.project
                # print("before",form_project.__dict__)
                form_project.sell_total -= before_detail.total_sell
                form_project.buy_total -= before_detail.total_buy
                form_project.profit_total -= before_detail.total_profit

                form_project.advance_total += before_detail.total_sell
                # print("after",form_project.__dict__)
                spend.delete()
                form_project.save()
            return HttpResponseRedirect(reverse("dash:dash"))

    response=render(request,"dash/update.html",{"title":title,"form":form})
    return response