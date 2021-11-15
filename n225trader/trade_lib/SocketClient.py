import socket

HOST = "127.0.0.1"
PORT = 8000

CRLF = "\r\n"


def main():
    # IPv4のTCP通信用のオブジェクトを作る
    # note: socket.AF_INET はIPv4
    # note: socket.SOCK_STREAM はTPC
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 指定したホストとポートに接続
    client.connect((HOST, PORT))

    # HTTPのリクエストを作る
    message_lists = [
        'GET / HTTP/1.1',
        'host:127.0.0.1'
    ]
    send_message = ""
    for message in message_lists:
        send_message += message + CRLF

    # see: https://triple-underscore.github.io/RFC2616-ja.html#section-4
    # ヘッダーフィールドの後の最初の空行でリクエストは終わり
    send_message += CRLF

    # バイナリで送る
    send_binary = send_message.encode()
    client.send(send_binary)

    # 流れてくるメッセージを読み込む
    recieve_messages = []
    bytes_recd = 0
    MSGLEN = 4096
    while bytes_recd < MSGLEN:
        recieve = client.recv(min(MSGLEN - bytes_recd, 2048))
        if recieve == b"":
            # とりあえず空が来たら終わる
            break
        recieve_messages.append(recieve)
        bytes_recd = bytes_recd + len(recieve)

    print(b"".join(recieve_messages))


if __name__ == "__main__":
    main()