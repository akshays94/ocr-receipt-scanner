from django.urls import path
from django.views.generic import TemplateView

import ocr_receipt_scanner.claims.views as views


app_name = "claims"

urlpatterns = [
    path("", view=views.Home.as_view(), name="home"),
    path("upload-receipt/", view=views.UploadReceipt.as_view(), name="upload-receipt"),
    path("success/", TemplateView.as_view(template_name="claims/pages/claim-success.html"), name="claim-success")
    # path("~update/", view=user_update_view, name="update"),
    # path("<str:username>/", view=user_detail_view, name="detail"),
]