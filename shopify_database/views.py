import threading
from datetime import time
from subprocess import run, CalledProcessError

from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from requests.adapters import HTTPAdapter
from rest_framework.decorators import action
from setuptools import logging
from urllib3 import Retry

from .serializers import ProductSerializer, ScrapingResponseSerializer
from .models import Product
from rest_framework import viewsets
import time


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        # Use the 'db' query parameter to select the correct database
        db = self.request.query_params.get('db', 'default')  # default to 'default'
        return Product.objects.using(db).all()

    def perform_create(self, serializer):
        db = self.request.query_params.get('db', 'default')
        serializer.save(using=db)

    @action(detail=False, methods=['post'], url_path='bulk-insert')
    def bulk_insert(self, request):
        """
        Handle bulk insert of products.
        Expects a list of products in the request body.
        """
        db = request.query_params.get('db', 'default')
        data = request.data  # List of products

        # Make sure data is a list
        if isinstance(data, list):
            # Pass the db context to the serializer
            serializer = ProductSerializer(data=data, many=True, context={'db': db})

            if serializer.is_valid():
                # Save the data to the specified database
                serializer.save()
                return Response({"message": "Bulk insert successful."}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Request data should be a list of products."}, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('query', '')
        db = request.query_params.get('db', 'default')
        products = Product.objects.using(db).filter(title__icontains=query)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Product
from .serializers import ProductSerializer

@api_view(['GET'])
def aggregate_search(request):
    query = request.query_params.get('query', '')
    databases = ['default', 'node2', 'node3']  # List of your databases
    results = []

    if not query:
        return Response({"detail": "Query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

    for db in databases:
        try:
            # Query the database for products matching the query
            products = Product.objects.using(db).filter(title__icontains=query)
            serializer = ProductSerializer(products, many=True)
            results.extend(serializer.data)  # Merge results from all databases
        except Exception as e:
            # Handle database connection errors gracefully
            results.append({"db": db, "error": f"Failed to query database: {str(e)}"})

    return Response(results)

# api/views.py
import subprocess
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        db = self.request.query_params.get('db', 'default')  # default to 'default'
        return Product.objects.using(db).all()

    def perform_create(self, serializer):
        db = self.request.query_params.get('db', 'default')
        serializer.save(using=db)

    @action(detail=False, methods=['post'], url_path='bulk-insert')
    def bulk_insert(self, request):
        db = request.query_params.get('db', 'default')
        data = request.data  # List of products

        # Ensure data is a list
        if isinstance(data, list):
            serializer = ProductSerializer(data=data, many=True, context={'db': db})
            if serializer.is_valid():
                serializer.save(using=db)
                return Response({"message": "Bulk insert successful."}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Request data should be a list of products."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('query', '')
        db = request.query_params.get('db', 'default')
        products = Product.objects.using(db).filter(title__icontains=query)
        serializer = ProductSerializer(products, many=True)
        import time
        import threading
        import subprocess
        from subprocess import CalledProcessError
        from django.http import JsonResponse
        from rest_framework.decorators import api_view
        from rest_framework.response import Response

        # Function to run a command with password authentication
# def run_command_with_password(command, password):
#     try:
#         # Use sshpass to run the command
#         full_command = f"{command}"
#         subprocess.run(full_command, shell=True, check=True)
#     except subprocess.CalledProcessError as e:
#         print(f"Command failed: {e}")
#         raise e
#
# @api_view(['POST'])
# def sync_databases(request):
#     try:
#         # Log the incoming request data
#         print("Request data:", request.data)
#
#         source_db = request.data.get('source_db')
#         target_nodes = request.data.get('target_nodes', [])
#         ssh_password = request.data.get('ssh_password')  # Get SSH password from request data
#
#         if not source_db or not target_nodes or not ssh_password:
#             return Response({"detail": "source_db, target_nodes, and ssh_password are required."}, status=400)
#
#         # Step 1: Dump the source database
#         dump_file = f"./backups/{source_db}_dump.sql"
#         dump_command = f"pg_dump -U node1_user -h localhost -p 5432 {source_db} > {dump_file}"
#         print(f"Running command: {dump_command}")
#
#         start_dump_time = time.time()
#         subprocess.run(dump_command, shell=True, check=True)
#         end_dump_time = time.time()
#         dump_time_taken = end_dump_time - start_dump_time
#         print(f"Database dump completed in {dump_time_taken:.2f} seconds.")
#
#         # Step 2: Transfer dump to the target nodes
#         transfer_times = {}
#         threads = []
#         for node in target_nodes:
#             scp_command = f"scp -o StrictHostKeyChecking=no ./backups/{source_db}_dump.sql user@{node}:"
#             transfer_start_time = time.time()
#
#             thread = threading.Thread(target=run_command_with_password, args=(scp_command, ssh_password))
#             threads.append((thread, node, transfer_start_time))
#             thread.start()
#
#         # Wait for all transfer threads to finish
#         for thread, node, transfer_start_time in threads:
#             thread.join()
#             transfer_end_time = time.time()
#             transfer_times[node] = transfer_end_time - transfer_start_time
#             print(f"Transfer to {node} completed in {transfer_times[node]:.2f} seconds.")
#
#         # Step 3: Restore dump on target nodes
#         restore_times = {}
#         for node in target_nodes:
#             init_command = f"sshpass -p {ssh_password} ssh -o StrictHostKeyChecking=no user@{node} 'psql -U node1_user -h {node} -p 5432 {source_db} < /{source_db}_dump.sql'"
#             print(f"Running command: {init_command}")
#
#             restore_start_time = time.time()
#             run_command_with_password(init_command, ssh_password)
#             restore_end_time = time.time()
#             restore_times[node] = restore_end_time - restore_start_time
#             print(f"Restore on {node} completed in {restore_times[node]:.2f} seconds.")
#
#         # Clean up dump file
#         clean_command = f"rm {dump_file}"
#         subprocess.run(clean_command, shell=True, check=True)
#
#         analytics = {
#             "dump_time": f"{dump_time_taken:.2f} seconds",
#             "transfer_times": {node: f"{time_taken:.2f} seconds" for node, time_taken in
#                                transfer_times.items()},
#             "restore_times": {node: f"{time_taken:.2f} seconds" for node, time_taken in restore_times.items()},
#         }
#         return Response({"message": "Databases synced successfully.", "analytics": analytics}, status=200)
#
#     except subprocess.CalledProcessError as e:
#         print(f"Error during database sync: {str(e)}")
#         return Response({"detail": f"Error during database sync: {str(e)}"}, status=500)
import os
import subprocess
import threading
import time
from rest_framework.response import Response
from rest_framework.decorators import api_view

def run_command_with_password(command, password):
    try:
        # Use sshpass to run the command
        full_command = f"sshpass -p {password} {command}"
        subprocess.run(full_command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        raise e


def get_node_storage(node, ssh_password):
    try:
        # Run a command to get available storage on the target node
        command = f"sshpass -p {ssh_password} ssh -o StrictHostKeyChecking=no user@{node} 'df -h / --output=avail | tail -1'"
        result = subprocess.check_output(command, shell=True, text=True).strip()
        print(f"Available storage on {node}: {result}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"Failed to get storage info for {node}: {e}")
        return "Unknown"


@api_view(['POST'])
def sync_databases(request):
    try:
        # Log the incoming request data
        print("Request data:", request.data)

        source_db = request.data.get('source_db')
        target_nodes = request.data.get('target_nodes', [])
        ssh_password = request.data.get('ssh_password')  # Get SSH password from request data

        if not source_db or not target_nodes or not ssh_password:
            return Response({"detail": "source_db, target_nodes, and ssh_password are required."}, status=400)

        # Step 1: Dump the source database
        dump_file = f"./backups/{source_db}_dump.sql"
        dump_command = f"pg_dump -U node1_user -h localhost -p 5432 {source_db} > {dump_file}"
        print(f"Running command: {dump_command}")

        start_dump_time = time.time()
        subprocess.run(dump_command, shell=True, check=True)
        end_dump_time = time.time()
        dump_time_taken = end_dump_time - start_dump_time
        print(f"Database dump completed in {dump_time_taken:.2f} seconds.")

        # Step 2: Transfer dump to the target nodes
        transfer_times = {}
        threads = []
        for node in target_nodes:
            scp_command = f"scp -o StrictHostKeyChecking=no {dump_file} user@{node}:/tmp/"
            transfer_start_time = time.time()

            thread = threading.Thread(target=run_command_with_password, args=(scp_command, ssh_password))
            threads.append((thread, node, transfer_start_time))
            thread.start()

        # Wait for all transfer threads to finish
        for thread, node, transfer_start_time in threads:
            thread.join()
            transfer_end_time = time.time()
            transfer_times[node] = transfer_end_time - transfer_start_time
            print(f"Transfer to {node} completed in {transfer_times[node]:.2f} seconds.")

        # Step 3: Check node health and storage
        node_health = {}
        node_storage = {}
        for node in target_nodes:
            try:
                health_command = f"sshpass -p {ssh_password} ssh -o StrictHostKeyChecking=no user@{node} 'echo Node is Up'"
                subprocess.check_output(health_command, shell=True, text=True).strip()
                node_health[node] = "Up"
            except subprocess.CalledProcessError:
                node_health[node] = "Down"

            # Retrieve available storage
            node_storage[node] = get_node_storage(node, ssh_password)

        # Step 4: Restore dump on target nodes (only if the node is up)
        restore_times = {}
        for node in target_nodes:
            if node_health[node] == "Up":
                restore_command = f"sshpass -p {ssh_password} ssh -o StrictHostKeyChecking=no user@{node} 'psql -U node1_user -h {node} -p 5432 {source_db} < /tmp/{source_db}_dump.sql'"
                print(f"Running command: {restore_command}")

                restore_start_time = time.time()
                run_command_with_password(restore_command, ssh_password)
                restore_end_time = time.time()
                restore_times[node] = restore_end_time - restore_start_time
                print(f"Restore on {node} completed in {restore_times[node]:.2f} seconds.")
            else:
                print(f"Skipping restore for {node} as the node is down.")

        # Clean up dump file locally
        if os.path.exists(dump_file):
            try:
                os.remove(dump_file)
                print("Local dump file deleted.")
            except Exception as e:
                print(f"Error deleting dump file: {e}")

        # Construct analytics data
        analytics = {
            "dump_time": f"{dump_time_taken:.2f} seconds",
            "transfer_times": {node: f"{time_taken:.2f} seconds" for node, time_taken in transfer_times.items()},
            "restore_times": {node: f"{time_taken:.2f} seconds" for node, time_taken in restore_times.items()},
            "node_health": node_health,
            "node_storage": node_storage,
        }

        return Response({"message": "Databases synced successfully.", "analytics": analytics}, status=200)

    except subprocess.CalledProcessError as e:
        print(f"Error during database sync: {str(e)}")
        return Response({"detail": f"Error during database sync: {str(e)}"}, status=500)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return Response({"detail": f"Unexpected error: {str(e)}"}, status=500)


# Aggregate Search API
@api_view(['GET'])
def aggregate_search(request):
    query = request.query_params.get('query', '')
    databases = request.query_params.getlist('db', ['default', 'node2', 'nod    e3'])  # Default to all nodes
    results = []

    if not query:
        return Response({"detail": "Query parameter is required."}, status=400)

    for db in databases:
        try:
            products = Product.objects.using(db).filter(title__icontains=query)
            serializer = ProductSerializer(products, many=True)
            results.extend(serializer.data)
        except Exception as e:
            results.append({"db": db, "error": f"Failed to query database: {str(e)}"})

    return Response(results)

class DashboardTemplateView(TemplateView):
    template_name = 'inventory.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nodes'] = ['node1', 'node2', 'node3']
        return context

class Dashboard1TemplateView(TemplateView):
    template_name = 'student-dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nodes'] = ['node1', 'node2', 'node3']
        return context

#
# import paramiko
# from scp import SCPClient
# from time import time
# import subprocess
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
#
#
# def dump_database(source_db):
#     """Dump the database locally."""
#     dump_file = f"./backups/{source_db}_dump.sql"
#     dump_command = f"pg_dump -U node1_user -h localhost -p 5432 {source_db} > {dump_file}"
#
#     try:
#         start_time = time()
#         subprocess.run(dump_command, shell=True, check=True)
#         dump_time = time() - start_time
#         return dump_file, dump_time
#     except subprocess.CalledProcessError as e:
#         raise Exception(f"Database dump failed: {str(e)}")
#
#
# def transfer_file_via_ssh(node, ssh_password, dump_file, username="user"):
#     """Transfer the file to the target node using SSH with password."""
#     try:
#         ssh = paramiko.SSHClient()
#         ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#
#         # Connect to the target node using password authentication
#         ssh.connect(hostname=node, username=username, password=ssh_password)
#
#         # Transfer the file using SCP
#         with SCPClient(ssh.get_transport()) as scp:
#             remote_path = f"/home/{username}/{dump_file.split('/')[-1]}"
#             scp.put(dump_file, remote_path)
#
#         ssh.close()
#         return remote_path
#     except Exception as e:
#         raise Exception(f"File transfer to {node} failed: {str(e)}")
#
#
# @api_view(['POST'])
# def sync_databases(request):
#     """API to dump and transfer the database to target nodes."""
#     source_db = request.data.get('source_db')
#     target_nodes = request.data.get('target_nodes', [])
#     ssh_password = request.data.get('ssh_password')  # SSH password for authentication
#
#     if not source_db or not target_nodes or not ssh_password:
#         return Response({"error": "source_db, target_nodes, and ssh_password are required."}, status=400)
#
#     try:
#         # Step 1: Dump the database
#         dump_file, dump_time = dump_database(source_db)
#
#         # Step 2: Transfer the file to each target node
#         transfer_details = []
#         for node in target_nodes:
#             print(f"Transferring to {node}...")
#             remote_path = transfer_file_via_ssh(node, ssh_password, dump_file)
#             transfer_details.append({"node": node, "remote_path": remote_path})
#
#         return Response({
#             "message": "Operation completed successfully.",
#             "dump_time": dump_time,
#             "transfers": transfer_details
#         })
#     except Exception as e:
#         return Response({"error": str(e)}, status=500)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from bs4 import BeautifulSoup
import requests
import re

# Define the price patterns (same as the ones in your script)
price_patterns = [
    r'[\$€£₹¥₩₽₦₵₪฿៛₫₲₴₭₮₵₠₡₢₣₤₧₨₩₯₺₼₾₹]\s?\d+(?:,\d{3})*(?:\.\d{1,2})?',  # Common and extended currency symbols (prefix)
    r'\d+(?:,\d{3})*(?:\.\d{1,2})?\s?[\$€£₹¥₩₽₦₵₪฿៛₫₲₴₭₮₵₠₡₢₣₤₧₨₩₯₺₼₾₹]',  # Postfix currency symbols
    r'[\d,]+\.\d{1,2}\s?(USD|EUR|GBP|INR|JPY|CAD|AUD|CNY|CHF|AED|SAR|KWD|QAR|OMR|BHD|EGP)',  # Currency names (extended)
    r'[\$€£₹¥₩₽₦₵₪฿៛₫₲₴₭₮₵₠₡₢₣₤₧₨₩₯₺₼₾₹]?\s?\d+(?:\.\d{1,2})?\s?[-–]\s?[\$€£₹¥₩₽₦₵₪฿៛₫₲₴₭₮₵₠₡₢₣₤₧₨₩₯₺₼₾₹]?\s?\d+(?:\.\d{1,2})?',  # Price ranges
    r'(only|just|starting at|from)?\s?[\$€£₹¥₩₽₦₵₪฿៛₫₲₴₭₮₵₠₡₢₣₤₧₨₩₯₺₼₾₹]?\s?\d+(?:\.\d{1,2})?',  # Inline prices
    r'price["\']?\s?:\s?["\']?\d+(?:\.\d{1,2})?',  # JSON or attributes
    r'was\s?[\$€£₹¥₩₽₦₵₪฿៛₫₲₴₭₮₵₠₡₢₣₤₧₨₩₯₺₼₾₹]?\s?\d+(?:\.\d{1,2})?,?\s?now\s?[\$€£₹¥₩₽₦₵₪฿៛₫₲₴₭₮₵₠₡₢₣₤₧₨₩₯₺₼₾₹]?\s?\d+(?:\.\d{1,2})?',  # Discounted prices
    r'(class|id|name)["\']?\s?:?\s?["\']?(price|cost)["\']?[^>]*>?\s?[\$€£₹¥₩₽₦₵₪฿៛₫₲₴₭₮₵₠₡₢₣₤₧₨₩₯₺₼₾₹]?\s?\d+(?:\.\d{1,2})?',  # HTML attributes
    r'[\$€£₹¥₩₽₦₵₪฿៛₫₲₴₭₮₵₠₡₢₣₤₧₨₩₯₺₼₾₹]\d{1,3}(?:,\d{3})*\b',  # Shorthand currency without decimals
    r'[\$€£₹¥₩₽₦₵₪฿៛₫₲₴₭₮₵₠₡₢₣₤₧₨₩₯₺₼₾₹]\s?\d+(?:,\d{3})*(?:\.\d+)?',  # Currency followed by a decimal number
    r'(sale|discount)\s?price\s?[:=]\s?[\$€£₹¥₩₽₦₵₪฿៛₫₲₴₭₮₵₠₡₢₣₤₧₨₩₯₺₼₾₹]?\s?\d+(?:,\d{3})*(?:\.\d+)?',  # Sale or discount price
    r'(per|each)\s?[\$€£₹¥₩₽₦₵₪฿៛₫₲₴₭₮₵₠₡₢₣₤₧₨₩₯₺₼₾₹]?\s?\d+(?:,\d{3})*(?:\.\d+)?',  # Per unit pricing
    r'(above|below|over|under|around|approx)\s?[\$€£₹¥₩₽₦₵₪฿៛₫₲₴₭₮₵₠₡₢₣₤₧₨₩₯₺₼₾₹]?\s?\d+(?:,\d{3})*(?:\.\d+)?',  # Approximate price
    r'([\$€£₹¥₩₽₦₵₪฿៛₫₲₴₭₮₵₠₡₢₣₤₧₨₩₯₺₼₾₹]?\d+(?:,\d{3})*(?:\.\d+)?\s?x\s?\d+)',  # Bundled pricing (e.g., $10 x 5)
    r'(total|subtotal)\s?[:=]\s?[\$€£₹¥₩₽₦₵₪฿៛₫₲₴₭₮₵₠₡₢₣₤₧₨₩₯₺₼₾₹]?\s?\d+(?:,\d{3})*(?:\.\d+)?',  # Total or subtotal
    r'(min|max|average|avg|median)\s?(price|cost)\s?[:=]\s?[\$€£₹¥₩₽₦₵₪฿៛₫₲₴₭₮₵₠₡₢₣₤₧₨₩₯₺₼₾₹]?\s?\d+(?:,\d{3})*(?:\.\d+)?',  # Statistical prices
    r'free\s?\(?\s?[\$€£₹¥₩₽₦₵₪฿៛₫₲₴₭₮₵₠₡₢₣₤₧₨₩₯₺₼₾₹]?\s?\d*(?:\.\d+)?\)?',  # Free pricing with or without optional cost
    r'(bundle|package)\s?(of)?\s?[\$€£₹¥₩₽₦₵₪฿៛₫₲₴₭₮₵₠₡₢₣₤₧₨₩₯₺₼₾₹]?\s?\d+(?:,\d{3})*(?:\.\d+)?',  # Package pricing
    r'(regular\s?price)\s?[:=]\s?[\$€£₹¥₩₽₦₵₪฿៛₫₲₴₭₮₵₠₡₢₣₤₧₨₩₯₺₼₾₹]?\s?\d+(?:,\d{3})*(?:\.\d+)?',  # Regular prices
]

#
# class ScrapeProductsView(APIView):
#     def get(self, request, *args, **kwargs):
#         # Define the parent sitemap URL
#         parent_sitemap_url = "https://zuhd.store/sitemap.xml"
#
#         # Function to fetch and parse XML sitemap
#         def fetch_sitemap(url):
#             try:
#                 response = requests.get(url, timeout=10)
#                 if response.status_code == 200:
#                     return BeautifulSoup(response.content, "xml")
#                 else:
#                     print(f"Failed to fetch sitemap: {url} (Status Code: {response.status_code})")
#             except requests.exceptions.RequestException as e:
#                 print(f"Error fetching sitemap: {url} - {e}")
#             return None
#
#         # Function to scrape product details
#         def scrape_product_details(product_url):
#             product_data = {
#                 "url": product_url,
#                 "price": None,
#                 "meta_title": None,
#                 "meta_description": None,
#                 "image_url": None
#             }
#             try:
#                 response = requests.get(product_url, timeout=10)
#                 if response.status_code == 200:
#                     html = response.text
#                     # Extract price using regex patterns
#                     for pattern in price_patterns:
#                         match = re.search(pattern, html)
#                         if match:
#                             product_data["price"] = match.group()
#                             break
#
#                     # Extract meta title and description
#                     soup = BeautifulSoup(html, "html.parser")
#                     product_data["meta_title"] = soup.find("title").text if soup.find("title") else None
#                     meta_description = soup.find("meta", attrs={"name": "description"})
#                     product_data["meta_description"] = meta_description["content"] if meta_description else None
#                 else:
#                     print(f"Failed to fetch product page: {product_url} (Status Code: {response.status_code})")
#             except requests.exceptions.RequestException as e:
#                 print(f"Error fetching product details for {product_url}: {e}")
#             return product_data
#
#         # Function to process product sitemaps
#         def process_product_sitemap(sitemap_url):
#             product_details = []
#             sitemap = fetch_sitemap(sitemap_url)
#             if sitemap:
#                 for url_tag in sitemap.find_all("url"):
#                     try:
#                         product_url = url_tag.find("loc").text
#                         image_url = url_tag.find("image:loc").text if url_tag.find("image:loc") else None
#                         if image_url:  # Only proceed if image_url is present
#                             product_data = scrape_product_details(product_url)
#                             product_data["image_url"] = image_url
#                             product_details.append(product_data)
#                     except Exception as e:
#                         print(f"Error processing product URL: {e}")
#             return product_details
#
#         # Main logic to process sitemaps and gather all product details
#         parent_sitemap = fetch_sitemap(parent_sitemap_url)
#         all_product_details = []
#         if parent_sitemap:
#             product_sitemaps = [
#                 sitemap.find("loc").text for sitemap in parent_sitemap.find_all("sitemap")
#                 if "products" in sitemap.find("loc").text
#             ]
#             for product_sitemap_url in product_sitemaps:
#                 print(f"Processing sitemap: {product_sitemap_url}")
#                 all_product_details.extend(process_product_sitemap(product_sitemap_url))
#
#         return Response(all_product_details, status=status.HTTP_200_OK)
#
import time
import threading
import requests
import csv
import argparse
import sqlite3
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import together
import os
from django.http import JsonResponse
from django.views import View

# Load API key from environment variable
api_key = os.getenv('TOGETHER_API_KEY')

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import sys
import threading

import threading
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
import threading
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from .models import Product  # Adjust based on your model import location
import together

import threading
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from shopify_database.models import Product
import together
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Product  # Import the Product model
from .serializers import ScrapingResponseSerializer


import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Product  # Import the Product model
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

# Logger setup (add this at the top of your file)
logger = logging.getLogger(__name__)

class ScrapeShopifyData(APIView):
    def post(self, request):
        niche = request.data.get("niche")
        city = request.data.get("city")
        country = request.data.get("country")

        if not all([niche, city, country]):
            return Response({"message": "Missing parameters."}, status=status.HTTP_400_BAD_REQUEST)

        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager

        # Use webdriver-manager to get the correct version of chromedriver
        options = Options()
        options.add_argument('--headless')  # Ensure Chrome runs in headless mode
        options.add_argument('--no-sandbox')  # Required for running in some environments (e.g., Docker, VMs)
        options.add_argument('--disable-dev-shm-usage')  # Disable /dev/shm usage (useful in containers or VMs)
        options.add_argument('--remote-debugging-port=9222')  # Enable debugging port
        options.add_argument('--disable-gpu')  # Disable GPU acceleration (helpful in headless mode)
        options.add_argument('--disable-software-rasterizer')  # Disable software rendering

        # Add your ChromeDriver service
        chrome_driver_path = ChromeDriverManager().install()
        service = Service(executable_path=chrome_driver_path)

        driver = webdriver.Chrome(service=service, options=options)


        # Open Google
        driver.get("https://www.google.com")

        # Print the title of the page to verify it loaded correctly
        print(driver.title)  # Should print "Google"

        # Close the driver

        urls = []
        try:
            driver.get('https://www.google.com')
            search_box = driver.find_element(By.NAME, "q")
            search_query = f'inurl:myshopify.com {niche} in {city},{country}'
            search_box.send_keys(search_query)
            search_box.send_keys(Keys.RETURN)
            time.sleep(2)  # Not ideal, use WebDriverWait instead

            # Extract URLs from search results
            links = driver.find_elements(By.CSS_SELECTOR, "a")
            for link in links:
                url = link.get_attribute("href")
                if url and "myshopify.com/" in url:
                    urls.append(url)

            urls = list(set(urls))  # Remove duplicates
        finally:
            driver.quit()

        processed_urls = []
        for url in urls:
            parsed_url = urlparse(url)
            domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
            sitemap_url = f"{domain}/sitemap.xml"
            processed_urls.append(sitemap_url)

        print(processed_urls)

        try:
            all_product_details = []
            total_sitemaps = len(processed_urls)
            start_time = time.time()

            for idx, sitemap_url in enumerate(processed_urls):
                remaining_sitemaps = total_sitemaps - idx
                print(f"Processing parent sitemap: {sitemap_url} ({idx + 1}/{total_sitemaps}). {remaining_sitemaps} sitemaps left.")
                parent_sitemap = self.fetch_sitemap(sitemap_url)
                if parent_sitemap:
                    product_sitemaps = [sitemap.find("loc").text for sitemap in parent_sitemap.find_all("sitemap") if "products" in sitemap.find("loc").text]
                    total_urls = len(product_sitemaps)
                    for url_idx, product_sitemap_url in enumerate(product_sitemaps):
                        remaining_urls = total_urls - url_idx
                        print(f"Processing product sitemap: {product_sitemap_url} ({url_idx + 1}/{total_urls}). {remaining_urls} URLs left.")
                        all_product_details.extend(self.process_product_sitemap(product_sitemap_url, city, niche, country))

                        elapsed_time = time.time() - start_time
                        avg_time_per_url = elapsed_time / (idx * total_urls + url_idx + 1)
                        estimated_time_left = avg_time_per_url * (total_sitemaps * total_urls - (idx * total_urls + url_idx + 1))
                        print(f"Estimated time left: {estimated_time_left:.2f} seconds.")
                else:
                    print(f"Skipping {sitemap_url} as it did not return a valid response.")
                print(f"Completed {sitemap_url}. {remaining_sitemaps - 1} sitemaps left.")

            self.save_to_db(all_product_details)

            return Response({
                "message": "Scraping completed successfully.",
                "data": all_product_details
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def generate_product_price(self, product_title, product_description, country_name, city_name, niche, api_key):
        try:
            client = together.Client(api_key=api_key)

            prompt = (
                "You are a pricing expert. Based on the following details, provide the expected price of the product "
                "ONLY as a number followed by the currency sign. Do not include any extra text or words.\n\n"
                f"Product Title: {product_title}\n"
                f"Product Description: {product_description}\n"
                f"Country: {country_name}\n"
                f"City: {city_name}\n"
                f"Niche: {niche}\n\n"
                "What is the expected price of the product?"
            )

            response = client.chat.completions.create(
                model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.2
            )

            price = response.choices[0].message.content.strip()
            return price

        except Exception as e:
            logger.error(f"Error generating price with Together AI: {e}")
            return None

    def fetch_sitemap(self, url):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return BeautifulSoup(response.content, "xml")
            else:
                logger.error(f"Failed to fetch sitemap: {url} (Status Code: {response.status_code})")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching sitemap: {url} - {e}")
        return None

    def scrape_product_details(self, product_url, city, niche, country):
        product_data = {
            "url": product_url,
            "title": None,
            "description": None,
            "image_url": None,
            "price": None,
            "city": city,
            "country": country,
            "niche": niche
        }
        try:
            response = requests.get(product_url, timeout=10)
            if response.status_code == 200:
                html = response.text
                soup = BeautifulSoup(html, "html.parser")
                product_data["title"] = soup.find("title").text if soup.find("title") else None
                meta_description = soup.find("meta", attrs={"name": "description"})
                product_data["description"] = meta_description["content"] if meta_description else None
                product_data['price'] = self.generate_product_price(product_data["title"], product_data["description"], country,
                                                               city, niche, "8e20cf957a59cbfa992c3587d9f684ee0b7209e5b00ac4be07ecce36c0cdf92c")
            else:
                logger.error(f"Failed to fetch product page: {product_url} (Status Code: {response.status_code})")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching product details for {product_url}: {e}")
        return product_data

    def process_product_sitemap(self, sitemap_url, city, niche, country):
        product_details = []
        sitemap = self.fetch_sitemap(sitemap_url)
        if sitemap:
            url_tags = sitemap.find_all("url")
            total_urls = len(url_tags)
            if total_urls == 0:
                logger.warning("No URLs found in the sitemap.")
                return product_details

            for index, url_tag in enumerate(url_tags):
                try:
                    product_url = url_tag.find("loc").text
                    image_url = url_tag.find("image:loc").text if url_tag.find("image:loc") else None
                    if image_url:
                        # Make sure city, niche, and country are passed
                        product_data = self.scrape_product_details(product_url, city, niche, country)
                        product_data["image_url"] = image_url
                        product_details.append(product_data)

                    percentage_done = (index + 1) / total_urls * 100
                    print(f"Processed {index + 1}/{total_urls} URLs ({percentage_done:.2f}% completed).")
                except Exception as e:
                    logger.error(f"Error processing product URL: {e}")

        return product_details

    def save_to_db(self, product_details):
        products = [Product(**product) for product in product_details]
        Product.objects.bulk_create(products)
