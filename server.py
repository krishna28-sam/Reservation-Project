import socket
import json
import threading
import ssl
import time
import uuid
from datetime import datetime

PORT = 5000
MAX_CLIENTS = 5
HOST = 'localhost'

# Data structure: 10 seats, each with booking info
seats = {i: None for i in range(1, 11)}  # None = available, else = {name, reservation_id}
data_lock = threading.Lock()
active_clients = 0
client_lock = threading.Lock()

def load_data():
    """Load bookings from data.json if exists"""
    global seats
    try:
        with open('data.json', 'r') as f:
            data = json.load(f)
            # Convert string keys back to integers (JSON converts int keys to strings)
            seats = {int(k): v for k, v in data.items()}
            print("[SERVER] Data loaded from data.json")
    except FileNotFoundError:
        print("[SERVER] No existing data.json, starting fresh")
        save_data()

def save_data():
    """Save bookings to data.json"""
    with open('data.json', 'w') as f:
        json.dump(seats, f, indent=2)

def view_seats():
    """Return all seat statuses"""
    with data_lock:
        response = {"status": "success", "seats": {}}
        for seat_num, booking in seats.items():
            if booking is None:
                response["seats"][str(seat_num)] = "available"
            else:
                response["seats"][str(seat_num)] = "booked by " + booking.get('name', 'Unknown')
    return response

def book_seat(seat_num, name):
    """Book a seat for a user"""
    with data_lock:
        seat_num = int(seat_num)
        if seat_num < 1 or seat_num > 10:
            return {"status": "fail", "reason": "Invalid seat number"}
        
        if seats[seat_num] is not None:
            return {"status": "fail", "reason": "Seat " + str(seat_num) + " already booked"}
        
        reservation_id = str(uuid.uuid4())[:8]
        seats[seat_num] = {"name": name, "reservation_id": reservation_id}
        save_data()
        return {"status": "success", "reservation_id": reservation_id, "seat": seat_num}

def cancel_booking(reservation_id):
    """Cancel a booking by reservation ID"""
    with data_lock:
        for seat_num, booking in seats.items():
            if booking and booking["reservation_id"] == reservation_id:
                seats[seat_num] = None
                save_data()
                return {"status": "success", "message": "Booking cancelled for seat " + str(seat_num)}
        
        return {"status": "fail", "reason": "Reservation ID not found"}

def handle_client(conn, addr, client_id):
    """Handle client requests"""
    global active_clients
    
    try:
        start_time = time.time()
        
        # Receive request
        data = conn.recv(1024).decode()
        request = json.loads(data)
        
        # Process request
        action = request.get("action")
        response = None
        
        if action == "view_seats":
            response = view_seats()
        elif action == "book_seat":
            response = book_seat(request.get("seat"), request.get("name"))
        elif action == "cancel_booking":
            response = cancel_booking(request.get("reservation_id"))
        else:
            response = {"status": "fail", "reason": "Invalid action"}
        
        # Send response
        conn.send(json.dumps(response).encode())
        
        # Print stats
        process_time = (time.time() - start_time) * 1000
        ts = datetime.now().strftime('%H:%M:%S')
        print("[" + ts + "] Client " + str(client_id) + " | Action: " + str(action) + " | Time: " + str(round(process_time, 2)) + "ms | Active clients: " + str(active_clients))
        
    except Exception as e:
        print("[ERROR] Client " + str(client_id) + ": " + str(e))
        try:
            conn.send(json.dumps({"status": "fail", "reason": "Server error"}).encode())
        except:
            pass
    finally:
        with client_lock:
            active_clients -= 1
        conn.close()

def start_server():
    """Start server and accept connections"""
    global active_clients
    
    # Load existing data
    load_data()
    
    # Create SSL context
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain("cert.pem", "key.pem")
    
    # Create server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    
    # Wrap with SSL
    server_socket = context.wrap_socket(server_socket, server_side=True)
    
    print("[SERVER] Running on " + HOST + ":" + str(PORT))
    print("[SERVER] Max clients: " + str(MAX_CLIENTS))
    print("[SERVER] Waiting for connections...\n")
    
    client_id = 0
    try:
        while True:
            # Check max clients
            if active_clients >= MAX_CLIENTS:
                conn, addr = server_socket.accept()
                try:
                    response = json.dumps({"status": "fail", "reason": "Server busy"})
                    conn.send(response.encode())
                except:
                    pass
                conn.close()
                print("[SERVER] Connection rejected: " + str(addr) + " (Server busy)")
                continue
            
            # Accept connection
            try:
                conn, addr = server_socket.accept()
                with client_lock:
                    active_clients += 1
                    client_id += 1
                
                ts = datetime.now().strftime('%H:%M:%S')
                print("[" + ts + "] Client " + str(client_id) + " connected from " + str(addr))
                
                # Handle in thread
                thread = threading.Thread(target=handle_client, args=(conn, addr, client_id))
                thread.daemon = True
                thread.start()
            except Exception as e:
                print("[ERROR] Accept: " + str(e))
    
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
