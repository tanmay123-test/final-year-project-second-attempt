try:
    from car_service.fuel_request_queue_service import fuel_request_queue_service
    print('✅ Queue service import successful')
    
    # Test the service directly
    result = fuel_request_queue_service.get_available_fuel_requests(1)
    print(f'Queue service test: {result.get("success", False)}')
    
except Exception as e:
    print(f'❌ Import error: {e}')
