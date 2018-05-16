from django.shortcuts import render
from crop_info import models
import json
# Create your views here.


def get_cateone(request):
    info = {'水果':{'核果仁果类':{"苹果":{"品种":["红富士"]}}}}
    data = {}
    cate_one_obj = models.CategoryOne.objects.all()
    for cate_one in cate_one_obj:
        cate_two_obj = cate_one.categorytwo_set.all()
        data[cate_one.name] = {}
        for cate_two in cate_two_obj:
            data[cate_one.name][cate_two.name] = {}
            cate_three_obj = cate_two.categorythree_set.all()
            for cate_three in cate_three_obj:
                data[cate_one.name][cate_two.name][cate_three.name] = {}
                shangpin = cate_three.commodity_set.all()
                spa = models.Specification.objects.filter(commodity__in=shangpin)
                address_list = shangpin.values_list('place_of_dispatch').distinct()
                address = []
                for h in address_list:
                    address.append(h[0].replace("\t", " ").replace("\n", " "))
                data[cate_one.name][cate_two.name][cate_three.name]["地区"] = address
                name = spa.values('name').distinct()
                for i in name:
                    value = spa.filter(**i).values_list('value').distinct()
                    value_list = []
                    for v in value:
                        value_list.append(v[0])
                    data[cate_one.name][cate_two.name][cate_three.name][i['name']] = value_list

    dd = json.dumps(data)
    with open('data.json', 'w') as f:
        f.write(json.dumps(data))
    return render(request, 'index.html', {'cate': dd})
