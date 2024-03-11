### Introduction

For this project I create a RESTful API that allows employees from a company to make vacation requests. There is also an API for managers to approve or reject vacation requests, to view all current requests, and to quickly get a list of all vacations requests that are overlapping with each other. The APIs are designed using Python and Flask.

### Features

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
    - See an overview for each individual employee by employee id.
    - See an overview of overlapping vacation requests.
    - Process an individual vacation request and either approve or reject it.
    - A manager would reject a particular request if there are too many vacation requests overlapping around the same time period. 

The vacation requests made by employees have the following JSON structure:
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