from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from api.views.auth import RegisterView
from api.views.tags import TagListCreateView, TagDetailView
from api.views.profiles import ProfileListCreateView, ProfileDetailView, ProfileTagView, ProfileTagDeleteView
from api.views.rules import RuleListCreateView, RuleDetailView, RuleRunView, SegmentRuleListView, SegmentRuleDetailView
from api.views.results import ResultListView, ResultDetailView

urlpatterns = [
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', RegisterView.as_view(), name='register'),

    path('tags/', TagListCreateView.as_view(), name='tag-list'),
    path('tags/<int:pk>/', TagDetailView.as_view(), name='tag-detail'),

    path('profiles/', ProfileListCreateView.as_view(), name='profile-list'),
    path('profiles/<int:pk>/', ProfileDetailView.as_view(), name='profile-detail'),
    path('profiles/<int:pk>/tags/', ProfileTagView.as_view(), name='profile-tag-add'),
    path('profiles/<int:pk>/tags/<int:tag_id>/', ProfileTagDeleteView.as_view(), name='profile-tag-delete'),

    path('rules/', RuleListCreateView.as_view(), name='rule-list'),
    path('rules/<int:pk>/', RuleDetailView.as_view(), name='rule-detail'),
    path('rules/<int:pk>/run/', RuleRunView.as_view(), name='rule-run'),

    path('segment-rules/', SegmentRuleListView.as_view(), name='segment-rule-list'),
    path('segment-rules/<int:pk>/', SegmentRuleDetailView.as_view(), name='segment-rule-detail'),

    path('results/', ResultListView.as_view(), name='result-list'),
    path('results/<int:pk>/', ResultDetailView.as_view(), name='result-detail'),
]
