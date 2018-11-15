from django.urls import path
import ocr_receipt_scanner.claims.views as views

# from ocr_receipt_scanner.users.views import (
# 	Home
# )

app_name = "claims"

urlpatterns = [
    path("", view=views.Home.as_view(), name="home"),
    path("upload-receipt/", view=views.UploadReceipt.as_view(), name="upload-receipt"),
    # path("~update/", view=user_update_view, name="update"),
    # path("<str:username>/", view=user_detail_view, name="detail"),
]