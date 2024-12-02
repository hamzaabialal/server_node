from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Product, Log, Pipeline
from .scraper_main_node import run_scraper
from .serializers import ProductSerializer, PipelineSerializer, LogSerializer

class BulkProductInsertView(APIView):
    def post(self, request):
        serializer = ProductSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Products inserted successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogView(APIView):
    def post(self, request):
        serializer = LogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Log inserted successfully"}, status=status.HTTP_201_CREATED)

    def get(self, request, pipeline_id):
        logs = Log.objects.filter(pipeline_id=pipeline_id)
        serializer = LogSerializer(logs, many=True)
        return Response(serializer.data)

class PipelineView(APIView):
    def post(self, request):
        serializer = PipelineSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Pipeline inserted successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        pipelines = Pipeline.objects.all()
        serializer = PipelineSerializer(pipelines, many=True)
        return Response(serializer.data)

    def put(self, request, pipeline_id):
        pipeline = Pipeline.objects.get(id=pipeline_id)
        serializer = PipelineSerializer(pipeline, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Pipeline updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pipeline_id):
        pipeline = Pipeline.objects.get(id=pipeline_id)
        pipeline.delete()
        return Response({"message": "Pipeline deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class ScrapeDataView(APIView):
    def post(self, request):
        # Get the parameters from the request
        niche = request.data.get('niche')
        city = request.data.get('city')
        country = request.data.get('country')

        if not niche or not city or not country:
            return Response({"error": "Missing required parameters"}, status=status.HTTP_400_BAD_REQUEST)

        # Run the scraper
        scraped_data = run_scraper(niche, city, country)

        # Return the saved data in the response
        return Response({"message": "Scraping successful", "data": scraped_data.data}, status=status.HTTP_200_OK)