## Introduction

For this project, I created a RESTful API that allows employees from a company to make vacation requests. There are also API endpoints for managers to approve or reject vacation requests, view all current requests, and get a list of all requests that are overlapping with each other.
This API was designed using Python and Flask.

## Features

- API routes that allow employees to:
    - See their vacation requests.
		- Filter requests by status (approved, pending, rejected).
    - See their number of remaining vacation days.
    - Make a new request by start date and end date.
    - The request will only be allowed if they have not exhausted their total vacation limit.
    - The vacation limit varies per employee. The default is 20 days per year.
    - The API ensures that vacation days do not include weekends when processing new requests.
- API routes that allow managers to:
    - See an overview of all vacation requests.
        - Filter requests by status (approved or pending).
    - See an overview for each employee by employee id.
    - See an overview of overlapping vacation requests.
    - Process an individual vacation request and either approve or reject it.
    - A manager would reject a particular request if there are too many vacation requests overlapping around the same dates. 

Vacation requests have the following JSON structure:
```
{
  "request_id": REQUEST_ID,
  "applicant": EMPLOYEE_ID,
  "status": STATUS, // may be: "approved", "rejected", "pending"
  "processed_by": MANAGER_ID,
  "request_submitted_at": "2020-08-09T12:57:13.506Z",
  "vacation_start_date" "2020-08-24T00:00:00.000Z",
  "vacation_end_date" "2020-09-04T00:00:00.000Z",
}
```

## Instructions for Testing the API

To test the API, follow these steps:

### 1. Install Required Dependencies

To install the necessary dependencies, execute the following commands in your terminal:

```pip install flask```<br>
```pip install requests```

### 2. (Optional) Modify the test file

If necessary, you can modify the ```tests.py``` file. Open the file ```tests.py``` and replace the ```employee_id```,  ```manager_id``` and ```request_id``` if needed.

### 3. Run the Unit Tests

To run the unit tests, follow these steps:  
**Step 1:** Open a terminal window and execute the command:<br>
```python app.py``` <br>
This command starts the Flask server

**Step 2:** Open another terminal window and execute the command:  
```python tests.py```  
This command runs the unit tests against the API.

Feel free to follow the format in the ```tests.py``` file and add more tests as needed.

# Code Explanation
## 1. Initial Setup

The code starts by importing necessary modules and initializes the API by creating an instance of Flask.

```
from flask import Flask, jsonify, request
from datetime import datetime, timedelta

app = Flask(__name__)
```
Here, we import the ```Flask``` module to create a web application, along with ```jsonify``` and ```request```.
- ```jsonify```: to convert our responses into JSON objects
- ```request```: to access data from incoming HTTP requests, such as query parameters or JSON payloads

```Datetime``` and ```timedelta``` are used for managing dates. They are used to calculate the number of vacations days requested.
## 2. Initialization of Data and Helper Functions:
### 2.1 Initializing Data
Next, we define initial data structures for storing vacation requests, employees, and managers:
```
# Initialize vacation requests list
vacation_requests = []

# Initialize the employees and managers dictionaries with dummy data
employees = {1: {"name": "John Doe", "remaining_vacation_days": 20},
             2: {"name": "Jane Smith", "remaining_vacation_days": 20}
             }

managers = {1: {"name": "Manager 1"},
            2: {"name": "Manager 2"}
            }
```
Here, ```vacation_requests```, stores all the vacation requests made by employees.  
We use a dictionary for to store ```employees``` and ```managers``` data. A dictionary makes it simple to retrieve the data quickly in O(1) time complexity.
### 2.2 Helper Functions
```
def get_employee(employee_id):
    """
    Get employee information by ID.
    """
    if employee_id in employees:
        return employees[employee_id]
    raise ValueError(f"Employee not found with ID: {employee_id}")
```
The ```get_employee``` helper function retrieves employee information by their ID. If the employee ID exists in the employees dictionary, it returns the corresponding data. Otherwise, it raises a ValueError.

```

def is_manager(manager_id):
    """
    Check if the given ID belongs to a manager.
    """
    if manager_id in managers:
        return True
    return False
```
The ```is_manager``` function checks if a given ID belongs to a manager. If the manager ID exists in the managers dictionary, it returns True; otherwise, it returns False.
## 3. Employee API Endpoints:
The following functions define endpoints for managing employee vacation requests:

### 3.1 Get Endpoints
#### Get Vacation Requests
This function handles GET requests to look up vacation requests for a specific employee. It returns all requests associated with the given employee ID and filters them based on status (approved, pending, or rejected).
```
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
```

#### Get Remaining Vacation Days 
This function handles GET requests to look up the vacation days that remain for a specific employee. If the employee ID is not found, it returns a 404 error.
```
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
```

### 3.2 Post Endpoint
The function ```make_vacation_request()``` handles POST requests to create a new vacation request for an employee. It validates the request data, calculates the duration of the vacation, checks if the employee has enough remaining vacation days, updates the remaining vacation days, and appends the new request to the list of vacation requests.

The ```@app.post``` decorator defines a POST route for creating a new request for a specific employee. The ```employee_id``` is provided as part of the URL path.
```
@app.post('/employees/<int:employee_id>/requests')
def make_vacation_request(employee_id):
    """
    POST endpoint to create a new vacation request for an employee.
    """
    employee = get_employee(employee_id)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404
```
This code looks up the employee information based on the provided ```employee_id```. If not found, it returns a JSON response with a 404 error message.
##### Calculating the Number of Vacation Days  
```
    data = request.json
    if not data or 'vacation_start_date' not in data or 'vacation_end_date' not in data:
        return jsonify({"error": "Invalid request data"}), 400
```
Here, the code extracts the JSON data from the request. It checks if the ```vacation_start_date``` and ```vacation_end_date``` are in the request data. If not, it returns 400 error message (Invalid request).


```
start_date = datetime.fromisoformat(data['vacation_start_date'])
end_date = datetime.fromisoformat(data['vacation_end_date'])

if end_date <= start_date:
    return jsonify({"error": "End date must be after start date"}), 400
```

```
request_duration = (end_date - start_date).days + 1
business_day = 0
current_date = start_date

for i in range(request_duration):
    if current_date.weekday() < 5:
        business_day += 1
    current_date += timedelta(days=1)

vacation_duration = business_day
```

The lines above calculate the duration of the vacation request in business days (excluding weekends). It iterates over each day between the start and end dates, counting only weekdays (Monday through Friday).

```
if employee["remaining_vacation_days"] < vacation_duration:
    return jsonify({"error": "Not enough remaining vacation days"}), 400
```
This condition checks if the employee has enough remaining vacation days to cover the requested duration. 
#### Adding New Vacation Requests
```
employee["remaining_vacation_days"] -= vacation_duration

vacation_requests.append({
    "request_id": len(vacation_requests) + 1,
    "applicant": employee_id,
    "status": "pending",
    "processed_by": None,
    "request_submitted_at": datetime.now().isoformat(),
    "vacation_start_date": start_date.isoformat(),
    "vacation_end_date": end_date.isoformat(),
})

return jsonify({"message": "Vacation request submitted"}), 201
```
The code updates the remaining vacation days for the employee. Then, it appends the vacation request to the list of requests, and returns a JSON response with a success message and a status code of 201 (Created).

## 4. Manager API Endpoints:

The following functions define the endpoints for managing manager actions related to employee vacation requests:
### 4.1 Get Endpoints
#### Get Vacation Requests
This function handles GET requests to look up vacation requests using a manager ID. It retrieves and filters them based on the status provided (approved, rejected, pending). 
```
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
```

#### Get Overlapping Vacation Requests
The function ```get_overlapping_requests() ```handles GET requests to retrieve an overview of overlapping vacation requests for a specific manager. It compares each pair of vacation requests to check for overlap and returns a list of overlapping requests.
```
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
            request1 = vacation_requests[i]
            request2 = vacation_requests[j]
```
An empty list ```overlapping_requests``` will be used to store pairs of overlapping vacation requests (request1 and request2).
```
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
```
This condition checks if the current pair of vacation requests meet certain criteria for overlap:
1. The applicants for both requests are different.
2. Both requests have been approved.
3. There is an overlap in the vacation period. There are four possibilities for overlap: 
   - request1 starts before request2 and ends after request2 starts or ends
   - request2 starts before request1 and ends after request1 starts or ends.


                overlapping_requests.append((request1, request2))

    return jsonify(overlapping_requests), 200
If the condition for overlap is met, the pair of overlapping vacation requests is appended to the overlapping_requests list.

Finally, the function returns a JSON response containing the list of overlapping request pairs. 


### 4.2 Put Endpoint
The function ```process_request()``` handles PUT requests to update an individual vacation request by a manager. It checks if the manager is authorized, validates the request data, and updates the status of the request based on the manager's decision.

The function begins by checking if the provided manager_id belongs to a manager using the is_manager function. If the provided ID is not associated with a manager, an "Unauthorized" error response is returned.

```
if not is_manager(manager_id):
    return jsonify({"error": "Unauthorized"}), 401
```
```
data = request.json
if not data or 'status' not in data:
    return jsonify({"error": "Invalid request data"}), 400

status = data['status']
if status not in ['approved', 'rejected']:
    return jsonify({"error": "Invalid status"}), 400
```
After validating the request data, the function checks if the given status is either "approved" or "rejected." If not, an "Invalid status" error response is returned.

```
request_to_process = None
for req in vacation_requests:
    if req['request_id'] == request_id:
        request_to_process = req
        break
if not request_to_process:
    return jsonify({"error": "Request not found"}), 404
    
if request_to_process['status'] == 'pending':
    request_to_process['status'] = status
    request_to_process['processed_by'] = manager_id
    return jsonify({"message": f"Request has been {status}"}), 200
else:
    return jsonify({"error": "Request has already been processed"}), 400
```


The function then validates that the request exists using the request_id.  
If the request has been pending, the function updates the request status to the provided status ("approved" or "rejected") and records the manager ID who processed the request.  
A success message and status code 200 is returned.<br>
If the request has already been processed (i.e., its status is not "pending"), an error response (400) is returned.


## 5. Running the API

Finally, the code checks if the script is being run directly and starts the Flask application.
```
if __name__ == '__main__':
    app.run(debug=True)
```
Setting ```debug=True``` enables debugging mode, which provide more detailed error messages, and automatically restarts the server when code changes are detected during development.
