import socket
import struct

def get_question_section(data):
    cursor = 12
    while True:
        label_len = data[cursor]
        cursor+=1

        if(label_len>=192):
            cursor+=2
            break

        if(label_len==0):
            break
        else:
            cursor += label_len

    cursor+=4
    return data[12:cursor]

def get_question_domain(data):
    cursor = 12
    while True:
        label_len = data[cursor]
        cursor+=1

        if(label_len>=192):
            cursor+=2
            break

        if(label_len==0):
            break
        else:
            cursor += label_len

    return data[12:cursor]

def find_opcode(x):
    i=14
    p=0
    while(i>=11):
        if(x&((1<<i))):
            p+= (1<<i)
        i-=1
    
    return p

def find_rd(x):
    return (x&(1<<8))

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

            #DNS HEADER
            packet_id = data[0:2]

            #flags
            incoming_flag = struct.unpack("!H" , data[2:4])[0]

            QR1_flag = (1<<15)
            OPcode_flag = find_opcode(incoming_flag)
            AA_flag = 0
            TC_flag = 0
            RD_flag = find_rd(incoming_flag)
            RA_flag = 0
            Z_flag =0
            RCODE_flag=0

            if(OPcode_flag != 0):
                RCODE_flag=4

            final_flag = QR1_flag + OPcode_flag + AA_flag + TC_flag + RD_flag + RA_flag + Z_flag + RCODE_flag

            QDCount =0
            ANCount =0
            NSCount =0
            ARCount =0

            #DNS QUESTION
            question = get_question_section(data)
            incoming_qd_count = struct.unpack("!H" , data[4:6])[0]
            QDCount=incoming_qd_count

            #DNS ANSWER
            answer_name = get_question_domain(data) #same as the question domain
            answer_type = 1
            answer_class = 1
            answer_TTL = 60
            answer_RDLEN = 4
            answer_RDATA = b"\x08\x08\x08\x08"
            ANCount= QDCount

            answer_number_parts = struct.pack("!HHIH",answer_type,answer_class,answer_TTL,answer_RDLEN)
            answer = answer_name + answer_number_parts + answer_RDATA

            #UPDATED DNS HEADER ELEMENTS
            header_number_parts = struct.pack("!HHHHH",final_flag,QDCount,ANCount,NSCount,ARCount)
            header = packet_id+header_number_parts
            #struct.pack() converts glued integers to bytes (crushes them into specific molded shape and size)
            # !HHHHH is the big-endian format , each H is for each argument in the function , this string is called the format string
            #format string tells the function how to crush the data
            # ! -> big endian indicator (fill the bits in network byte order (do not reverse it))
            # H -> expect an unsigned short int

            #DNS RESPONSE
            response = header+question+answer

            udp_socket.sendto(response, address)


        except Exception as e:
            print(f"Error receiving data: {e}")
            break


if __name__ == "__main__":
    main()
