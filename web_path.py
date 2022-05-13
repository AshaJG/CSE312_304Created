import codecs
import hashlib
import socketserver
import binascii
import json

from textwrap import wrap

import database
from server import MyTCPHandler
from response import generate_Response101
from router import Route
from request import Request


def add_webPaths(router):
    router.add_route(Route('GET', "/websocket", web_home))


def web_home(request: Request, handler: socketserver.BaseRequestHandler):
    # Establish the Handshake Connection
    GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    key_received = request.headers.get('Sec-WebSocket-Key')
    socketKey_made = make_socketKey(GUID, key_received)
    response = generate_Response101(socketKey_made)
    handler.request.sendall(response)

    # connecting a user to a web-socket connection
    username = request.cookies.get('username')
    handler.websocket_connections.append(handler)

    handler.ws_users[username] = handler
    print("users to connection", handler.ws_users, flush=True)
    print("users only", handler.ws_users.keys(), flush=True)

    # keep the websocket connections open
    while True:
        websocket_frames_received = handler.request.recv(1024)
        if len(websocket_frames_received) == 0:
            continue
        # print("data received ", websocket_frames_received, flush=True)
        websocket_header = websocket_frames_received
        websocket_header_array = webFrame_to_binary(websocket_header)

        opcode = int(websocket_header_array[0]) & 15
        payload_length = websocket_header[1] & 127

        frame_buffer = websocket_header_array
        frame_bufferCount = len(frame_buffer)

        if opcode == 8:
            handler.ws_users.pop(username)
            handler.websocket_connections.remove(handler)
            print("users now", MyTCPHandler.ws_users.pop(username), flush=True)
            break
        else:
            # WHEN PAYLOAD IS 126
            if payload_length < 126:
                print("payload is under 126")
                actual_payload = payload_length

                # Check if it needs to buffer

                if int(actual_payload) > len(frame_buffer):
                    buffer = implement_buffer(actual_payload, frame_buffer, frame_bufferCount, handler)
                    fullBuffer = buffer
                else:
                    fullBuffer = frame_buffer

                masking_key = fullBuffer[2:6]
                payload_dataOnly = fullBuffer[6:]
                ws_toSend = execute_rest(payload_dataOnly, masking_key, username, request)
                print("here 1")

                # send a websocket frame to all the websocket connections
                for connection in handler.websocket_connections:
                    print("connection in ", connection)
                    connection.request.sendall(ws_toSend)

                # handler.request.sendall(ws_toSend)
    print("outside of loop")


# function responsible for the socket_key
def make_socketKey(GUID, key_received):
    key_received_GUID = key_received + GUID
    key_received_encoded = key_received_GUID.encode()
    hashed = hashlib.sha1(key_received_encoded).hexdigest()
    hashed_b64 = codecs.encode(codecs.decode(hashed, 'hex'), 'base64')
    strip_hashed_key = hashed_b64.strip()
    print("socket_key:", strip_hashed_key, flush=True)
    return strip_hashed_key


# buffering
def implement_buffer(actual_payload, f_buffer, handler):
    payload_length = actual_payload
    frame_buffer = f_buffer[8:]
    frame_bufferCount = len(frame_buffer)

    while frame_bufferCount < payload_length:
        print("Buffering...", "buffer count ", frame_bufferCount, "payload length:", payload_length, flush=True)

        data_received = handler.request.recv(1024)
        transf_data = webFrame_to_binary(data_received)
        frame_buffer += transf_data
        frame_bufferCount = len(frame_buffer)
        amt_left = abs(payload_length - len(frame_buffer))

    else:
        remaining = abs(payload_length - len(frame_buffer))
        data_received_left = handler.request.recv(remaining)
        transf_dataX = webFrame_to_binary(data_received_left)
        frame_buffer += transf_dataX

    left = payload_length - len(frame_buffer)
    print("How much is left to receive", left, flush=True)
    print("the len we working with on the buffer ", len(frame_buffer), flush=True)
    return frame_buffer


# functions responsible for converting a webFrame byte array to a list of binary string
def webFrame_to_binary(input_received):
    comma = b','
    slash = b'\\'
    converted = []

    byte_array = input_received
    for byte in byte_array:
        # the bytes in their decimal form
        ind_char = [char for char in byte_array]
        # turns the frame into binary
        converted = ascii_to_binary(ind_char)
    return converted


# helper function for webFrame_to_binary
def ascii_to_binary(array):
    end_result = []
    for bit in array:
        hex_value = hex(bit)
        hex_value_s = str(hex_value)
        hex_value_sliced = hex_value_s[2:]
        res = "{0:08b}".format(int(hex_value_sliced, 16))
        end_result.append(res)
    # print("the end_result", res)
    # print("this", end_result)
    return end_result


# function that takes the first 4 bytes in the payload function to get prep for masking
def prep_payloadMasking(list_payload):
    p_list = list_payload[:4]
    p_listJoint = ''.join(map(str, p_list))
    # print (p_list)
    # print (p_listJoint)
    return p_listJoint


# function that is responsible for XOR
# responsible for performing XOR on the individual bytes
def masked_withXor(mList, pList):
    masked_list = mList
    pay_list = pList
    applied_XOR = []
    for masked_bit, payload_bit in zip(masked_list, pay_list):
        value_XOR = int(masked_bit) ^ int(payload_bit)
        applied_XOR.append(value_XOR)
    final = make_each_string(applied_XOR)
    # print (final)
    return final


def make_each_string(masked_list):
    masked_stringsList = []
    for i in masked_list:
        masked_stringsList.append(str(i))
    # one big string
    join_everything = ''.join(map(str, masked_stringsList))
    # format into 8 bytes
    format_into8 = wrap(join_everything, 8)
    return format_into8


# function that is responsible for removing the first 4 bytes from list and leaving the rest
def format_payload(list_payload):
    payload_list = list_payload[4:]
    # print ("the list in the function count ", len(payload_list))
    # print(payload_list)
    return payload_list


# function responsible for parsing the payload to get deciphered
def parse_payload(p_only, masked_key):
    final = []
    payload_count = len(p_only)
    while payload_count > 4:
        prep_payload = prep_payloadMasking(p_only)
        joint_maskingString = ''.join(map(str, masked_key))
        # call function for XOR each bit with the masked key and prep payload
        xor_value = masked_withXor(prep_payload, joint_maskingString)
        final.extend(xor_value)
        # removal = call function for removal of first 4bytes of payload
        removal = format_payload(p_only)
        # update the payload_data = removal
        p_only = removal
        payload_count -= 4
    else:
        # count the elements left in the payload
        remaining = len(p_only)
        # wrap_m the mask key saved gets sliced down to the amount of elements left in payload
        wrapped_maskKey = masked_key[0:remaining]
        join_maskKey = ''.join(map(str, wrapped_maskKey))
        join_payR = ''.join(map(str, p_only))
        xor_value_left = masked_withXor(join_maskKey, join_payR)
        # add the last masked bytes to the list
        final.extend(xor_value_left)
        # update the payload_data to end the while loop
        payload_data = []
    # print("payload masked out", final, flush=True)
    return final


# format the message to how we would see it
def plaintext_msg(parsed_msg):
    msg_received_BigString = ''.join(map(str, parsed_msg))
    value = int(str(msg_received_BigString), 2)
    formedString = binascii.unhexlify('%x' % value)
    # print("format the msg", formedString, flush=True)
    # print("type is ", type(formedString), flush=True)
    formedString_decode = formedString.decode()
    formedString_dict = json.loads(formedString_decode)
    # print("format the msg", formedString_dict, flush=True)
    # print("type is ", type(formedString_dict), flush=True)
    return formedString_dict


def build_webframe(msg):
    print("Building WebFrame...")
    frame = []
    web_frame = bytes()

    fin_to_opcodeString = '10000001'
    fbit_toSend = int(fin_to_opcodeString, 2)
    # calculate the length of the body

    body = (json.dumps(msg)).encode()

    body_len = len(body)

    if body_len < 126:
        print("in the 1st loop")
        # format the payload length
        res1 = "{:07b}".format(body_len)
        res2 = "0" + res1
        # pack the frame to send
        pbit_toSend = int(res2, 2)
        frame = [fbit_toSend, pbit_toSend]
        web_frame = bytes(frame)
        web_frame += body
        print(web_frame)
    return web_frame


# function responsible for executing the rest of the instruction to finish the process
def execute_rest(pLoad, mKey, username, request):
    post_dict = {}
    payload_dataOnly = pLoad
    masking_key = mKey

    msg_parsed = parse_payload(payload_dataOnly, masking_key)
    print("the msg_parsed", msg_parsed, type(msg_parsed), flush=True)

    # format the parsed payload to what we can understand
    formedString_dict = plaintext_msg(msg_parsed)
    print("recognizable : ", formedString_dict, flush=True)

    # get the post_id received
    like_postId = formedString_dict.get('post_ID')
    print("the like_postId", like_postId, flush=True)
    like_received = formedString_dict.get('like')
    print("the like received", like_received, flush=True)


    # just increment the number
    count_likes = increment_likes(like_postId)
    print("count_likes", count_likes, flush=True)

    # BUILD THE WEB FRAME BACK TO SEND
    liked_dict = {'post_ID': like_postId, 'like': str(count_likes)}
    print("what happened,", liked_dict, flush=True)

    # save to db
    something = database.create_likeId(liked_dict)
    print("line 292", something, flush=True)

    print("line 294", liked_dict, flush=True)
    send_dict = {'post_ID': like_postId, 'like': int(count_likes)}
    record_toSend = database.find_post(like_postId)

    ws_send = build_webframe(record_toSend)
    print("send back", ws_send, flush=True)
    return ws_send


def increment_likes(like_postId):
    record_postID = database.find_post(like_postId)
    # print("the like received in increment", like_received, flush = True )
    print("record post id db", record_postID)
    count = 0
    if record_postID is not None:
        print("execute this 1")
        already_likes = record_postID.get('like')
        print("already_likes:", already_likes, type(already_likes), flush=True)
        count = int(already_likes) + 1
        print("the count :", count , flush=True)
        database.update_postCount(like_postId,count)
    else:
        print("execute that 2")
        count += 1
        print("already_likes:", count, type(count), flush=True)
    print("count:", count, type(count), flush=True)
    return count
