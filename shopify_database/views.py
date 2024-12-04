import threading
from subprocess import run, CalledProcessError
from rest_framework.decorators import action
from .serializers import ProductSerializer
from .models import Product
from rest_framework import viewsets

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
        return Response(serializer.data)




# Helper function to run commands
def run_command(command):
    try:
        run(command, shell=True, check=True)
    except CalledProcessError as e:
        print(f"Error occurred: {e}")
# Function to run a command with sshpass for password authentication
def run_command_with_password(command, password):
    # Add sshpass to the command
    full_command = f"sshpass -p {password} {command}"
    run(full_command, shell=True, check=True)

# Function to run commands with password using sshpass
def run_command_with_password(command, password):
    try:
        # Use sshpass to run the command
        full_command = f"sshpass -p {password} {command}"
        subprocess.run(full_command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        raise e

@api_view(['POST'])
def sync_databases(request):
    try:
        # Log the incoming request data
        print("Request data:", request.data)

        source_db = request.data.get('source_db')
        target_nodes = request.data.get('target_nodes', [])
        ssh_password = request.data.get('ssh_password')  # Get SSH password from request data

        # Ensure the required fields are provided
        if not source_db or not target_nodes or not ssh_password:
            return Response({"detail": "source_db, target_nodes, and ssh_password are required."}, status=400)

        # Step 1: Dump the source database
        dump_file = f"./backups/{source_db}_dump.sql"
        dump_command = f"pg_dump -U node1_user -h localhost -p 5432 {source_db} > {dump_file}"
        print(f"Running command: {dump_command}")
        subprocess.run(dump_command, shell=True, check=True)

        # Step 2: Transfer dump to the target nodes and initialize them
        threads = []
        for node in target_nodes:
            # SCP command to transfer the dump file to the target node using sshpass for password
            scp_command = f"scp -o StrictHostKeyChecking=no ./backups/{source_db}_dump.sql user@{node}:"
            thread = threading.Thread(target=run_command_with_password, args=(scp_command, ssh_password))
            threads.append(thread)
            thread.start()

        # Wait for all transfer threads to finish
        for thread in threads:
            thread.join()

        # Step 3: Initialize target database by restoring the dump
        for node in target_nodes:
            init_command = f"sshpass -p {ssh_password} ssh -o StrictHostKeyChecking=no user@{node} 'psql -U node1_user -h {node} -p 5432 {source_db} < /{source_db}_dump.sql'"
            print(f"Running command: {init_command}")
            run_command_with_password(init_command, ssh_password)

        # Clean up dump file
        clean_command = f"rm {dump_file}"
        subprocess.run(clean_command, shell=True, check=True)

        return Response({"message": "Databases synced successfully."}, status=200)

    except subprocess.CalledProcessError as e:
        print(f"Error during database sync: {str(e)}")
        return Response({"detail": f"Error during database sync: {str(e)}"}, status=500)



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