from django.urls import path

from vstore.views import StoreView, StoreItemDetail

app_name='vstore'

urlpatterns = [
    path('store/', StoreView.as_view(), name='storefront_urlpattern'),
    path('store/<int:id>/', StoreItemDetail.as_view(), name='store_item_detail_urlpattern'),
]
