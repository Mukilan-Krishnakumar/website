from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView

from core.models import Post
from mkdwn2html.utils import extract_title
from mkdwn2html.actions.mkdwn2html_actions import ConvertMarkdownContentToHtml


# Create your views here.


class HomePageView(APIView):
    def get(self, request):
        posts = Post.objects.all()
        return render(request, "home.html", {"posts": posts})


class StaticSiteView(APIView):
    def get(self, request, slug):
        try:
            post = Post.objects.get(slug=slug)
            content = (
                ConvertMarkdownContentToHtml(post.mkdwn_content).execute().to_html()
            )
            return render(request, "post.html", {"content": content})
        except Post.DoesNotExist:
            return JsonResponse({"error": "wrong path"})
