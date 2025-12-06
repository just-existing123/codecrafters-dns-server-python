import socket
import struct

def get_question_domain(data):
    cursor = 12
    domain_cnt=0
    while True:
        label_len = data[cursor]
        cursor+=1

        if(label_len==0):
            break
        else:
            cursor += label_len

    cursor+=4
    return data[12:cursor]

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # TODO: Uncomment the code below to pass the first stage
    #
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(("127.0.0.1", 2053))
    
    while True:
        try:
            data, address = udp_socket.recvfrom(512)

            print(f"dbg : data : {data}")

        #    DNS HEADER FORMAT (12 bytes total) (1 byte = 8 bits)

        # +---------------------+---------------------+
        # |            ID (16)                        |    --> Packet_ID
        # +---------------------+---------------------+
        # | QR (1) | Opcode (4) | AA (1) | TC (1) | RD (1)| RA (1) | Z (3) | RCODE (4)|   --> FLAGS
        # +---------------------+---------------------+
        # |            QDCOUNT (16)                 |
        # +---------------------+---------------------+
        # |            ANCOUNT (16)                 |
        # +---------------------+---------------------+
        # |            NSCOUNT (16)                 |
        # +---------------------+---------------------+
        # |            ARCOUNT (16)                 |
        # +---------------------+---------------------+

        # FIELD EXPLANATION:

        # ID        : 16-bit identifier set by client (used to match replies)
        # QR        : Query(0) or Response(1)
        # Opcode    : Type of query (0 = standard)
        # AA        : Authoritative Answer (set in responses)
        # TC        : Truncated message
        # RD        : Recursion Desired
        # RA        : Recursion Available
        # Z         : Reserved (must be 0)
        # RCODE     : Response code (0 = No error)

        # QDCOUNT   : Number of questions
        # ANCOUNT   : Number of answer RRs
        # NSCOUNT   : Number of authority RRs
        # ARCOUNT   : Number of additional RRs
    
            response = b""

            packet_id = data[0:2]
            tester_id = b"1234"
            question = get_question_domain(data)

            incoming_qd_count = struct.unpack("!H" , data[4:6])[0]

            QR1flag = (1<<15)

            QDCount = incoming_qd_count
            ANCount =0
            NSCount =0
            ARCount =0

            header = struct.pack("!HHHHH",QR1flag,QDCount,ANCount,NSCount,ARCount)
            #struct.pack() converts glued integers to bytes (crushes them into specific molded shape and size)
            # !HHHHH is the big-endian format , each H is for each argument in the function , this string is called the format string
            #format string tells the function how to crush the data
            # ! -> big endian indicator (fill the bits in network byte order (do not reverse it))
            # H -> expect an unsigned short int

            # response = packet_id+header
            response = packet_id_id+header+(question.encode())

            udp_socket.sendto(response, address)


        except Exception as e:
            print(f"Error receiving data: {e}")
            break


if __name__ == "__main__":
    main()
