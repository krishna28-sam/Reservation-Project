import socket
import json
import ssl

HOST = 'localhost'
PORT = 5000

def create_ssl_connection():
    """Create SSL connection to server"""
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock = context.wrap_socket(sock, server_hostname=HOST)
    sock.connect((HOST, PORT))
    return sock

def send_request(action, **kwargs):
    """Send request to server and get response"""
    try:
        sock = create_ssl_connection()
        request = {"action": action}
        request.update(kwargs)
        
        sock.send(json.dumps(request).encode())
        response = json.loads(sock.recv(1024).decode())
        sock.close()
        
        return response
    except ConnectionRefusedError:
        return {"status": "fail", "reason": "Cannot connect to server"}
    except Exception as e:
        return {"status": "fail", "reason": str(e)}

def view_seats():
    """View all available seats"""
    response = send_request("view_seats")
    
    if response["status"] == "success":
        print("\n--- Seat Status ---")
        for seat, status in response["seats"].items():
            print(f"Seat {seat}: {status}")
        print()
    else:
        print(f"\nError: {response.get('reason')}\n")

def book_seat():
    """Book a seat"""
    try:
        seat_num = int(input("Enter seat number (1-10): "))
        name = input("Enter your name: ")
        
        response = send_request("book_seat", seat=seat_num, name=name)
        
        if response["status"] == "success":
            print(f"\n✓ Booking successful!")
            print(f"  Seat: {response['seat']}")
            print(f"  Reservation ID: {response['reservation_id']}\n")
        else:
            print(f"\n✗ Booking failed: {response.get('reason')}\n")
    except ValueError:
        print("\n✗ Invalid seat number\n")

def cancel_booking():
    """Cancel a booking"""
    reservation_id = input("Enter reservation ID: ")
    response = send_request("cancel_booking", reservation_id=reservation_id)
    
    if response["status"] == "success":
        print(f"\n✓ {response['message']}\n")
    else:
        print(f"\n✗ Cancellation failed: {response.get('reason')}\n")

def show_menu():
    """Display menu"""
    print("\n--- Reservation System ---")
    print("1. View seats")
    print("2. Book seat")
    print("3. Cancel booking")
    print("4. Exit")
    print()

def main():
    """Client main loop"""
    print("Connecting to server...")
    
    while True:
        show_menu()
        choice = input("Enter choice (1-4): ").strip()
        
        if choice == "1":
            view_seats()
        elif choice == "2":
            book_seat()
        elif choice == "3":
            cancel_booking()
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, try again.\n")

if __name__ == "__main__":
    main()
