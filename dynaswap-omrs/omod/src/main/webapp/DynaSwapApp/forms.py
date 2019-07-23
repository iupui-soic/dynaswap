from django import forms
from DynaSwapApp.models import Roles
 
class allRoles(forms.Form):

    roleList = []

    for role in Roles.objects.all():
        roleList.append([role.role, role.role])

    allRoleChoices = forms.ChoiceField(choices=roleList)
    # DatabaseType=forms.ChoiceField(choices=[('sqlserver','SQLServer'),('oracle','Oracle')])
