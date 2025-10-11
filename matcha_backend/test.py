"""
Test file for Notification System with WebSocket and REST API testing
Tests real-time notifications, API endpoints, and multi-user scenarios
"""

import logging
import socketio
import requests
import time
import json
import threading
from datetime import datetime
logger = logging.getLogger(__name__)

# Configuration
BASE_URL = "http://localhost:5000"  # Update with your server URL
WS_URL = "http://localhost:5000"    # Update with your WebSocket URL

# Test users with their access tokens
USERS = {
    "test1": {
        "user_id": 1,
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3NjAyMjYyODMsInR5cGUiOiJhY2Nlc3MifQ.DQNWz05v49QeeulbuXeiDuYwtl_xf-EP-9qFSX0LzFg"
    },
    "test2": {
        "user_id": 2,
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyLCJleHAiOjE3NjAyMjI2NjMsInR5cGUiOiJhY2Nlc3MifQ.0Ht-MLGtNJqeiej2fhW02OaXBRjC5YbALSLdPXmA2hw"
    },
    "test3": {
        "user_id": 2,  # Note: Same user_id as test2
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyLCJleHAiOjE3NjAyMjI2NjMsInR5cGUiOiJhY2Nlc3MifQ.0Ht-MLGtNJqeiej2fhW02OaXBRjC5YbALSLdPXmA2hw"
        # "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjozLCJleHAiOjE3NjAyMTk0MTYsInR5cGUiOiJhY2Nlc3MifQ.ltR0pHbI35Ybr_q-vYzqJfaaNnOG7fKWrvroQYlNMEk"
    }
}


class NotificationTester:
    """Main test class for notification system"""
    
    def __init__(self, username):
        self.username = username
        self.user_data = USERS[username]
        self.user_id = self.user_data["user_id"]
        self.token = self.user_data["access_token"]
        self.sio = socketio.Client()
        self.notifications_received = []
        self.setup_socket_handlers()
    
    def setup_socket_handlers(self):
        """Setup WebSocket event handlers"""
        
        @self.sio.on('connect')
        def on_connect():
            print(f"[{self.username}] ✅ Connected to WebSocket")
        
        @self.sio.on('connected')
        def on_connected(data):
            print(f"[{self.username}] ✅ Server confirmed connection: {data}")
        
        @self.sio.on('disconnect')
        def on_disconnect():
            print(f"[{self.username}] ❌ Disconnected from WebSocket")
        
        @self.sio.on('new_notification')
        def on_notification(data):
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{self.username}] 🔔 [{timestamp}] New notification received:")
            print(f"    {json.dumps(data, indent=4)}")
            self.notifications_received.append(data)
        
        @self.sio.on('unread_count')
        def on_unread_count(data):
            print(f"[{self.username}] 📊 Unread count: {data.get('count', 0)}")
        
        @self.sio.on('error')
        def on_error(data):
            print(f"[{self.username}] ⚠️ Error: {data}")
    
    def connect_websocket(self):
        """Connect to WebSocket server"""
        try:
            headers = {
                'Authorization': f'Bearer {self.token}'
            }
            # Add user_id as query parameter
            connection_url = f"{WS_URL}?user_id={self.user_id}"
            self.sio.connect(
                connection_url,
                headers=headers,
                transports=['websocket'],
                wait_timeout=10
            )
            print(f"[{self.username}] ✅ WebSocket connection established")
            return True
        except Exception as e:
            print(f"[{self.username}] ❌ WebSocket connection failed: {e}")
            return False
    
    def disconnect_websocket(self):
        """Disconnect from WebSocket server"""
        if self.sio.connected:
            self.sio.disconnect()
            print(f"[{self.username}] ❌ Disconnected from WebSocket")
    
    def get_headers(self):
        """Get HTTP headers with auth token"""
        return {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    def get_notifications(self, limit=20, offset=0, unread_only=False):
        """Fetch notifications via REST API"""
        try:
            url = f"{BASE_URL}/api/notifications/get_notifications"
            payload = {
                "limit": limit,
                "offset": offset,
                "unread_only": unread_only
            }
            response = requests.post(url, json=payload, headers=self.get_headers())
            
            if response.status_code == 200:
                data = response.json()
                print(f"[{self.username}] 📬 Fetched {data.get('count', 0)} notifications")
                return data.get('notifications', [])
            else:
                print(f"[{self.username}] ❌ Failed to fetch notifications: {response.status_code}")
                return []
        except Exception as e:
            print(f"[{self.username}] ❌ Error fetching notifications: {e}")
            return []
    
    def get_unread_count(self):
        """Get unread notification count"""
        try:
            url = f"{BASE_URL}/api/notifications/unread_count"
            response = requests.get(url, headers=self.get_headers())
            
            if response.status_code == 200:
                data = response.json()
                count = data.get('unread_count', 0)
                print(f"[{self.username}] 📊 Unread count: {count}")
                return count
            else:
                print(f"[{self.username}] ❌ Failed to get unread count: {response.status_code}")
                return 0
        except Exception as e:
            print(f"[{self.username}] ❌ Error getting unread count: {e}")
            return 0
    
    def mark_notification_seen(self, notification_id):
        """Mark a notification as seen"""
        try:
            url = f"{BASE_URL}/api/notifications/{notification_id}/mark_seen"
            print(url)
            response = requests.put(url, headers=self.get_headers())
            
            if response.status_code == 200:
                print(f"[{self.username}] ✅ Marked notification {notification_id} as seen")
                return True
            else:
                print(f"[{self.username}] ❌ Failed to mark as seen: {response.status_code}")
                return False
        except Exception as e:
            print(f"[{self.username}] ❌ Error marking as seen: {e}")
            return False
    
    # def mark_all_seen(self):
    #     """Mark all notifications as seen"""
    #     try:
    #         url = f"{BASE_URL}/api/notifications/mark_all_seen"
    #         response = requests.put(url, headers=self.get_headers())
            
    #         if response.status_code == 200:
    #             data = response.json()
    #             print(f"[{self.username}] ✅ Marked all notifications as seen")
    #             return True
    #         else:
    #             print(f"[{self.username}] ❌ Failed to mark all as seen: {response.status_code}")
    #             return False
    #     except Exception as e:
    #         print(f"[{self.username}] ❌ Error marking all as seen: {e}")
    #         return False
    
    def delete_notification(self, notification_id):
        """Delete a notification"""
        try:
            url = f"{BASE_URL}/api/notifications/{notification_id}"
            response = requests.delete(url, headers=self.get_headers())
            
            if response.status_code == 200:
                print(f"[{self.username}] ✅ Deleted notification {notification_id}")
                return True
            else:
                print(f"[{self.username}] ❌ Failed to delete: {response.status_code}")
                return False
        except Exception as e:
            print(f"[{self.username}] ❌ Error deleting notification: {e}")
            return False


# Test Scenarios

def test_single_user_connection():
    """Test 1: Single user connects and receives notifications"""
    print("\n" + "="*60)
    print("TEST 1: Single User Connection and Notification Reception")
    print("="*60)
    
    tester = NotificationTester("test1")
    
    tester.disconnect_websocket()
    
    # Connect to WebSocket
    if tester.connect_websocket():
        print("✅✅✅ Connection successful")
        
        # Get initial unread count
        tester.get_unread_count()
        
        # Fetch notifications
        notifications = tester.get_notifications(limit=5)
        logger.info(f"👉👉👉👉👉Initial notifications: {notifications}")
        # Wait for real-time notifications
        print("\n⏳ Waiting for real-time notifications (10 seconds)...")
        time.sleep(10)
        
        # Disconnect
        tester.disconnect_websocket()
    
    print(f"\n📊 Total notifications received via WebSocket: {len(tester.notifications_received)}")


def test_multi_user_connections():
    """Test 2: Multiple users connected simultaneously"""
    print("\n" + "="*60)
    print("TEST 2: Multiple Users Connected Simultaneously")
    print("="*60)
    
    testers = []
    
    # Connect all users
    for username in ["test1", "test2", "test3"]:
        tester = NotificationTester(username)
        if tester.connect_websocket():
            testers.append(tester)
            time.sleep(1)  # Stagger connections
    
    print(f"\n✅ Connected {len(testers)} users")
    
    # Wait for notifications
    print("\n⏳ Listening for notifications (15 seconds)...")
    time.sleep(15)
    
    # Disconnect all
    for tester in testers:
        tester.disconnect_websocket()
    
    # Summary
    print("\n📊 Summary of received notifications:")
    for tester in testers:
        print(f"  {tester.username}: {len(tester.notifications_received)} notifications")


def test_notification_operations():
    """Test 3: Test all notification operations"""
    print("\n" + "="*60)
    print("TEST 3: Notification Operations (CRUD)")
    print("="*60)
    
    tester = NotificationTester("test1")
    
    # Connect
    tester.connect_websocket()
    time.sleep(2)
    
    # 1. Get all notifications
    print("\n1️⃣ Fetching all notifications...")
    notifications = tester.get_notifications(limit=10)
    
    # 2. Get unread only
    print("\n2️⃣ Fetching unread notifications only...")
    unread_notifications = tester.get_notifications(limit=10, unread_only=True)
    
    # 3. Get unread count
    print("\n3️⃣ Getting unread count...")
    unread_count = tester.get_unread_count()
    
    # 4. Mark one as seen (if any exist)
    if notifications:
        print("\n4️⃣ Marking first notification as seen...")
        tester.mark_notification_seen(notifications[0]['notification_id'])
        time.sleep(1)
        tester.get_unread_count()
    
    # 5. Mark all as seen
    print("\n5️⃣ Marking all notifications as seen...")
    # tester.mark_all_seen()
    # time.sleep(1)
    tester.get_unread_count()
    
    # 6. Delete a notification (if any exist)
    if notifications and len(notifications) > 1:
        print("\n6️⃣ Deleting a notification...")
        tester.delete_notification(notifications[1]['notification_id'])
    
    # Disconnect
    tester.disconnect_websocket()


def test_reconnection():
    """Test 4: Test reconnection behavior"""
    print("\n" + "="*60)
    print("TEST 4: Reconnection Behavior")
    print("="*60)
    
    tester = NotificationTester("test1")
    
    # First connection
    print("\n1️⃣ First connection...")
    tester.connect_websocket()
    time.sleep(3)
    
    # Disconnect
    print("\n2️⃣ Disconnecting...")
    tester.disconnect_websocket()
    time.sleep(2)
    
    # Reconnect
    print("\n3️⃣ Reconnecting...")
    tester.connect_websocket()
    time.sleep(3)
    
    # Get notifications after reconnect
    print("\n4️⃣ Fetching notifications after reconnect...")
    tester.get_notifications(limit=5)
    
    tester.disconnect_websocket()


def test_concurrent_operations():
    """Test 5: Concurrent operations from same user"""
    print("\n" + "="*60)
    print("TEST 5: Concurrent Operations (Same User, Multiple Sessions)")
    print("="*60)
    
    # test2 and test3 have same user_id (user 2)
    tester2 = NotificationTester("test2")
    tester3 = NotificationTester("test3")
    
    # Connect both
    tester2.connect_websocket()
    time.sleep(1)
    tester3.connect_websocket()
    
    print("\n✅ Both sessions connected for user 2")
    
    # Wait for notifications
    print("\n⏳ Listening for notifications (10 seconds)...")
    time.sleep(10)
    
    # Both should receive the same notifications
    print(f"\n📊 Session test2 received: {len(tester2.notifications_received)} notifications")
    print(f"📊 Session test3 received: {len(tester3.notifications_received)} notifications")
    
    # Disconnect
    tester2.disconnect_websocket()
    tester3.disconnect_websocket()


def run_all_tests():
    """Run all test scenarios"""
    print("\n" + "="*60)
    print("🧪 NOTIFICATION SYSTEM TEST SUITE")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"WebSocket URL: {WS_URL}")
    print(f"Test Users: {len(USERS)}")
    print("="*60)
    
    tests = [
        ("Single User Connection", test_single_user_connection),
        ("Multi-User Connections", test_multi_user_connections),
        ("Notification Operations", test_notification_operations),
        ("Reconnection Behavior", test_reconnection),
        ("Concurrent Operations", test_concurrent_operations)
    ]
    
    for test_name, test_func in tests:
        try:
            test_func()
            time.sleep(2)  # Pause between tests
        except Exception as e:
            print(f"\n❌ Test '{test_name}' failed with error: {e}")
    
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED")
    print("="*60)


# Interactive menu
def interactive_menu():
    """Interactive test menu"""
    while True:
        print("\n" + "="*60)
        print("🧪 NOTIFICATION SYSTEM TEST MENU")
        print("="*60)
        print("1. Test Single User Connection")
        print("2. Test Multi-User Connections")
        print("3. Test Notification Operations (CRUD)")
        print("4. Test Reconnection Behavior")
        print("5. Test Concurrent Operations")
        print("6. Run All Tests")
        print("7. Custom Test (Stay Connected)")
        print("0. Exit")
        print("="*60)
        
        choice = input("\nSelect test (0-7): ").strip()
        
        if choice == "0":
            print("👋 Exiting...")
            break
        elif choice == "1":
            test_single_user_connection()
        elif choice == "2":
            test_multi_user_connections()
        elif choice == "3":
            test_notification_operations()
        elif choice == "4":
            test_reconnection()
        elif choice == "5":
            test_concurrent_operations()
        elif choice == "6":
            run_all_tests()
        elif choice == "7":
            custom_test()
        else:
            print("❌ Invalid choice")


def custom_test():
    """Custom test - stay connected and monitor"""
    print("\n" + "="*60)
    print("CUSTOM TEST: Long-running Connection Monitor")
    print("="*60)
    
    username = input("Select user (test1/test2/test3): ").strip()
    if username not in USERS:
        print("❌ Invalid username")
        return
    
    tester = NotificationTester(username)
    tester.connect_websocket()
    
    print("\n✅ Connected. Press Ctrl+C to disconnect and exit")
    print("Monitoring notifications in real-time...\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Stopping...")
        tester.disconnect_websocket()
        print(f"📊 Total notifications received: {len(tester.notifications_received)}")


if __name__ == "__main__":
    # You can run specific tests or use interactive menu
    
    # Option 1: Run all tests automatically
    # run_all_tests()
    
    # Option 2: Interactive menu
    interactive_menu()
    
    # Option 3: Run specific test
    # test_single_user_connection()