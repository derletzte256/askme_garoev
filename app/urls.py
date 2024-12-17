from django.urls import path

from app import views

urlpatterns = [path('', views.index, name='index'),
               path('', views.index, name='ask'),
               path('hot/', views.hot, name='hot'),
               path('question/<int:question_id>/', views.question, name='question'),
               path('ask/', views.ask, name='ask'),
               path('tag/<str:tag_name>/', views.tag, name='tag'),
               path('login/', views.login, name='login'),
               path('logout/', views.logout, name='logout'),
               path('signup/', views.signup, name='signup'),
               path('profile/edit/', views.profile_edit, name='profile.edit'),
               path('profile/<int:profile_id>/', views.profile, name='profile'),
               path('like_question/', views.like_question, name='like_question'),
               path('like_answer/', views.like_answer, name='like_answer'),
               path('approve_answer/', views.approve_answer, name='approve_answer'),
               ]
