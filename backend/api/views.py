from django.shortcuts import render
import os
# Create your views here.
from django.http import JsonResponse, HttpResponse
from langchain_pipeline.langraph_pipeline import LangGraphPipeline
from django.conf import settings

def frontend_view(request):
    """Serves the React frontend."""
    frontend_path = os.path.join(settings.BASE_DIR, "static/frontend/index.html")
    
    try:
        with open(frontend_path, "r") as f:
            return HttpResponse(f.read(), content_type="text/html")
    except FileNotFoundError:
        return HttpResponse("React build not found. Please run 'npm run build'.", status=404)

def process_message(request):
    """API endpoint to process chat messages using LangChain pipeline."""
    if request.method == "GET":
        user_message = request.GET.get("message", "")
        use_agent = request.GET.get("use_agent", "false").lower() == "true"

        pipeline = LangGraphPipeline()
        response = pipeline.run_pipeline(user_message, use_agent)

        return JsonResponse({"response": response})
