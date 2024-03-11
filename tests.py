import unittest
import requests


class TestAPI(unittest.TestCase):
    """
    Test cases for the Employee Vacation and Manager Requests APIs.

    This class contains test methods to verify the functionality
    of the Employee Vacation and Manager Requests API endpoints.

    The tests cover various scenarios.
    For employees:
    - Filtering and retrieving vacation requests.
    - Making new vacation requests.
    - Checking remaining vacation days
    For managers:
    - Filtering and retrieving vacation requests.
    - See all overlapping employees vacation requests.
    - Processing vacation requests as approved or rejected.
    """

    local_url = 'http://127.0.0.1:5000'
    employee_id = 1 # Replace the employee_id and manager_id with valid IDs from your data
    manager_id = 1
    request_id = 1 # Replace the request_id with a valid request ID from your data

    def test_01_employee_requests(self):
        """
        Filter and print vacation requests for employee ID by status (approved, pending, or rejected)
        """
        print("Initial employee vacation requests:")

        response = requests.get(f'{self.local_url}/employees/{self.employee_id}/requests?status=approved')
        print(f"Requests approved for employee {self.employee_id}:", response.json())
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

        # Pending
        response = requests.get(f'{self.local_url}/employees/{self.employee_id}/requests?status=pending')
        print(f"Requests pending for employee {self.employee_id}:", response.json())
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

        # Rejected
        response = requests.get(f'{self.local_url}/employees/{self.employee_id}/requests?status=rejected')
        print(f"Requests rejected for employee {self.employee_id}:", response.json())
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_02_remaining_vacation_days(self):
        # See the remaining vacation days for an employee
        response = requests.get(f'{self.local_url}/employees/{self.employee_id}/remaining_days')
        print(f"Remaining vacation days for employee {self.employee_id}:", response.json())
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)

    def test_03_make_vacation_request(self):
        """
        Make a new vacation request using an employee ID
        """
        new_request = {
            "vacation_start_date": "2024-03-01T00:00:00.000Z",
            "vacation_end_date": "2024-03-05T00:00:00.000Z"
        }
        response = requests.post(f'{self.local_url}/employees/{self.employee_id}/requests', json=new_request)
        print("New vacation request:", response.json())
        self.assertEqual(response.status_code, 201)  # Corrected to 201
        self.assertIsInstance(response.json(), dict)

    def test_04_remaining_vacation_days(self):
        """
        See how many vacation days are remaining using an employee ID
        """
        response = requests.get(f'{self.local_url}/employees/{self.employee_id}/remaining_days')
        print(f"Remaining vacation days for employee {self.employee_id} after new request:", response.json())
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)

    def test_05_manager_requests(self):
        """
        See all employees vacation requests using a manager ID
        """
        print("Manager API Calls")

        # See all vacation requests
        response = requests.get(f'{self.local_url}/managers/{self.manager_id}/requests')
        print("Total vacations requests:", response.json())
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

        # Filter requests by status (Approved or Pending)
        # Approved
        response = requests.get(f'{self.local_url}/managers/{self.manager_id}/requests?status=approved')
        print("Approved Requests:", response.json())
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

        # Pending
        response = requests.get(f'{self.local_url}/managers/{self.manager_id}/requests?status=pending')
        print("Pending Requests:", response.json())
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_06_manager_overlapping_requests(self):
        """
        See all overlapping employees vacation requests using a manager ID
        """
        response = requests.get(f'{self.local_url}/managers/{self.manager_id}/overlapping_requests')
        print("Manager Overlapping Requests:", response.json())
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_07_process_request(self):
        """
        Process a vacation request using a manger ID and request ID. Can be processed as "approved" or "rejected"
        """
        request_data = {"status": "approved"}  # or "rejected"
        response = requests.put(f'{self.local_url}/managers/{self.manager_id}/requests/{self.request_id}',
                                json=request_data)
        print(f"Process vacation request {self.request_id}:", response.json())
        # The response will return a status code of 400 if the request_id has already been approved or rejected
        self.assertTrue(response.status_code == 200 or response.status_code == 400)
        self.assertIsInstance(response.json(), dict)

    def test_08_employee_requests(self):
        """
        Filter and print vacation requests for employee ID by status (approved, pending, or rejected)
        """
        print("Employee requests after vacation was approved:")
        # Approved
        response = requests.get(f'{self.local_url}/employees/{self.employee_id}/requests?status=approved')
        print(f"Requests approved for employee {self.employee_id}:", response.json())
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        for employee_request in response.json():
            self.assertTrue(employee_request['status'] == 'approved')

        # Pending
        response = requests.get(f'{self.local_url}/employees/{self.employee_id}/requests?status=pending')
        print(f"Requests pending for employee {self.employee_id}:", response.json())
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

        # Rejected
        response = requests.get(f'{self.local_url}/employees/{self.employee_id}/requests?status=rejected')
        print(f"Requests rejected for employee {self.employee_id}:", response.json())
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)


if __name__ == '__main__':
    unittest.main()



