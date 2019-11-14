from django.urls import path, re_path
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'vms'

urlpatterns = [
    path('', login_required(views.VmsView.as_view()), name='vms-list'),
    path('create', login_required(views.VmCreateView.as_view()), name='vm-create'),
    re_path(r'^mount/(?P<vm_uuid>[0-9a-z-]{32})/$', login_required(views.VmMountDiskView.as_view()), name='vm-mount-disk')
]

