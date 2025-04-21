from django.urls import path
from . import views as v

app_name = 'dash'  

urlpatterns = [
    path('',view=v.dash_main,name="dash"),
    path('<int:id>/',view=v.dash_one,name="one"),
    path('projects/<str:view>/',view=v.dash_projects,name="projects"),
    path('transactions/',view=v.dash_transactions,name="transactions"),
    path('transactions/advance/',view=v.dash_advance,name="trans_advance"),
    path('transactions/spend/',view=v.dash_spend,name="trans_spend"),
    path('update/<str:project_id>/<str:spend_id>/<str:advance_id>/',view=v.dash_update,name="update"),


]
