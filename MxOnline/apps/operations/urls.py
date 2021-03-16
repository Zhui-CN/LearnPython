from django.urls import re_path, path
from operations.views import AddFavView, CommentView

urlpatterns = [
    re_path(r"^fav/$", AddFavView.as_view(), name="fav"),
    re_path(r"^comment/$", CommentView.as_view(), name="comment"),
]
