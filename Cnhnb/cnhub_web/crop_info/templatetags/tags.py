from django import template
from django.utils.safestring import mark_safe
from crop_info import models

register = template.Library()


@register.simple_tag
def get_spa(id):
    em = ''
    cateone = models.CategoryThree.objects.get(id=id)
    shangpin = cateone.commodity_set.all()
    address_list = shangpin.values_list('place_of_dispatch').distinct()
    address = ''
    for h in address_list:
        address = address + h[0] + ',&nbsp;&nbsp;'
    em += '<p style="margin-left: 60px;" class="context"><span class="ss">地区:</span>：%s</p>' % address
    spa = models.Specification.objects.filter(commodity__in=shangpin)
    name = spa.values('name').distinct()
    for i in name:
        v = ''
        value = spa.filter(**i).values_list('value').distinct()
        for a in value:
            v = v + a[0] + ',&nbsp;&nbsp;'

        em += '<p style="margin-left: 60px;" class="context"><span class="ss">%s</span>：%s</p>' % (i['name'], v)


    return mark_safe(em)
