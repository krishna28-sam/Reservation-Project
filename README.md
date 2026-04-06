# Distributed Reservation System

A simple seat reservation system using Python sockets with SSL encryption and concurrent client support.

## Features

- **TCP Sockets**: Multi-client server with threading
- **Thread Safety**: Concurrency control using `threading.Lock` to prevent race conditions
- **SSL Security**: Encrypted communication between client and server
- **Data Persistence**: Bookings saved to `data.json`
- **Congestion Control**: Max 5 concurrent clients
- **Performance Monitoring**: Logs request processing time

## Setup

### Prerequisites

Generate SSL certificates:
```bash
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes
```

### Running

**Terminal 1 - Start Server:**
```bash
python server.py
```

**Terminal 2+ - Start Client(s):**
```bash
python client.py
```

## Usage

1. **View Seats**: Check availability of all seats
2. **Book Seat**: Reserve a seat with your name (get reservation ID)
3. **Cancel Booking**: Cancel using reservation ID
4. **Exit**: Close client

## Architecture

- `server.py`: TCP server with SSL, threading, locks, auto-save to JSON
- `client.py`: CLI client with SSL connection support
- `data.json`: Persistent storage of bookings
