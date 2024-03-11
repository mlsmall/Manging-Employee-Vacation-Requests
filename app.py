from flask import Flask, jsonify, request
from datetime import datetime, timedelta

app = Flask(__name__)

# Initialize vacation requests list
vacation_requests = []
# Initialize the employees and managers dictionaries with dummy data
# All employee and manager data can be added here
employees = {1: {"name": "John Doe", "remaining_vacation_days": 20},
             2: {"name": "Jane Smith", "remaining_vacation_days": 20}
             }

managers = {1: {"name": "Manager 1"},
            2: {"name": "Manager 2"}
            }

def get_employee(employee_id):
    """
    Get employee information by ID.
    """
    if employee_id in employees:
        return employees[employee_id]
    raise ValueError(f"Employee not found with ID: {employee_id}")

def is_manager(manager_id):
    """
    Check if the given ID belongs to a manager.
    """
    if manager_id in managers:
        return True
    return False

# Employee API endpoints
@app.get('/employees/<int:employee_id>/requests')
def get_employee_requests(employee_id):
    """
    Get endpoint to retrieve vacation requests for a specific employee.
    """
    status = request.args.get('status')  # Filter by status
    employee_requests = [req for req in vacation_requests if req['applicant'] == employee_id]
    if status:
        employee_requests = [req for req in employee_requests if req['status'] == status]
    return jsonify(employee_requests), 200


@app.get('/employees/<int:employee_id>/remaining_days')
def get_remaining_vacation_days(employee_id):
    """
    Get remaining vacation days for a specific employee.
    """
    employee = get_employee(employee_id)
    if employee:
        return jsonify({"remaining_vacation_days": employee["remaining_vacation_days"]})
    else:
        return jsonify({"error": "Employee not found"}), 404

@app.post('/employees/<int:employee_id>/requests')
def make_vacation_request(employee_id):
    """
    POST endpoint to create a new vacation request for an employee.
    """
    employee = get_employee(employee_id)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404

    # The request requires the vacation start and end dates
    data = request.json
    if not data or 'vacation_start_date' not in data or 'vacation_end_date' not in data:
        return jsonify({"error": "Invalid request data"}), 400 # parameters missing or invalid

    # Start date and end date of the vacation
    start_date = datetime.fromisoformat(data['vacation_start_date'])
    end_date = datetime.fromisoformat(data['vacation_end_date'])

    if end_date <= start_date:
        return jsonify({"error": "End date must be after start date"}), 400

    # Calculate the duration of the vacation request
    # Only counts weekdays as days of vacation requested
    request_duration = (end_date - start_date).days + 1
    business_day = 0
    current_date = start_date

    for i in range(request_duration):
        if current_date.weekday() < 5: # Business days are Monday through Friday (0 - 4).
            business_day += 1
        current_date += timedelta(days=1)

    vacation_duration = business_day

    # Check if the employee has enough remaining vacation days
    if employee["remaining_vacation_days"] < vacation_duration:
        return jsonify({"error": "Not enough remaining vacation days"}), 400 # parameters missing or invalid

    # Update the remaining vacation days of the employee
    employee["remaining_vacation_days"] -= vacation_duration

    # Add the vacation request to the list
    vacation_requests.append({
        "request_id": len(vacation_requests) + 1,
        "applicant": employee_id,
        "status": "pending",
        "processed_by": None, # the vacation request has not been processed by the manager yet
        "request_submitted_at": datetime.now().isoformat(),
        "vacation_start_date": start_date.isoformat(),
        "vacation_end_date": end_date.isoformat(),
    })

    return jsonify({"message": "Vacation request submitted"}), 201


# Manager API endpoints
@app.get('/managers/<int:manager_id>/requests')
def get_manager_requests(manager_id):
    """
    Get vacation requests for a specific manager.
    """
    if not is_manager(manager_id):
        return jsonify({"error": "Unauthorized"}), 401 # credentials missing or invalid

    status = request.args.get('status')  # Filter by status if provided
    manager_requests = vacation_requests[:]
    if status:
        manager_requests = [req for req in manager_requests if req['status'] == status]

    return jsonify(manager_requests)

@app.get('/managers/<int:manager_id>/overlapping_requests')
def get_overlapping_requests(manager_id):
    """
    Get an overview of overlapping vacation requests for a specific manager.
    """
    if not is_manager(manager_id):
        # Return unauthorized error if the manager is not authorized
        return jsonify({"error": "Unauthorized"}), 401

    overlapping_requests = []
    for i in range(len(vacation_requests)):
        for j in range(i + 1, len(vacation_requests)):
            # Compare each pair of vacation requests to check for overlap
            request1 = vacation_requests[i]
            request2 = vacation_requests[j]
            if (
                request1['applicant'] != request2['applicant'] and
                request1['status'] == 'approved' and
                request2['status'] == 'approved' and
                (
                    request1['vacation_start_date'] <= request2['vacation_start_date'] <= request1['vacation_end_date'] or
                    request1['vacation_start_date'] <= request2['vacation_end_date'] <= request1['vacation_end_date'] or
                    request2['vacation_start_date'] <= request1['vacation_start_date'] <= request2['vacation_end_date'] or
                    request2['vacation_start_date'] <= request1['vacation_end_date'] <= request2['vacation_end_date']
                )
            ):
                # If requests overlap, add them to the list of overlapping requests
                overlapping_requests.append((request1, request2)), 200

    return jsonify(overlapping_requests)

@app.put('/managers/<int:manager_id>/requests/<int:request_id>')
def process_request(manager_id, request_id):
    """
    Process an individual vacation request by a manager.
    """
    if not is_manager(manager_id):
        return jsonify({"error": "Unauthorized"}), 401 # credentials missing or invalid

    # The status is required in the request to process it
    data = request.json
    if not data or 'status' not in data:
        return jsonify({"error": "Invalid request data"}), 400 # parameters missing or invalid

    status = data['status']
    if status not in ['approved', 'rejected']:
        return jsonify({"error": "Invalid status"}), 400 # parameters missing or invalid

    # Asserting the request exists
    request_to_process = None
    for req in vacation_requests:
        if req['request_id'] == request_id:
            request_to_process = req
            break
    if not request_to_process:
        return jsonify({"error": "Request not found"}), 404

    if request_to_process['status'] == 'pending':  # Check if request is still pending
        request_to_process['status'] = status
        request_to_process['processed_by'] = manager_id
        return jsonify({"message": f"Request has been {status}"}), 200  # Return success message
    else:
        return jsonify({"error": "Request has already been processed"}), 400  # Return error message


if __name__ == '__main__':
    app.run(debug=True)