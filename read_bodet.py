import serial

from classes import parse_game_data

# settings for serial connections
PORT = "/dev/ttyUSB0"
BAUDRATE = 9600

# logging
f = open("log.txt", "w")

try:
    with serial.Serial(
        PORT,
        BAUDRATE,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=0.2,
    ) as ser:
        print(f"Lese {PORT} mit {BAUDRATE} Baud ...")
        print("Beenden mit Ctrl+C")

        parse_game_data.init_json()

        while True:
            data = ser.read(256)
            if data:
                # print(repr(data))
                f.write("\nSerial data:")
                f.write(repr(data))
                parse_game_data.parse_data(repr(data))


except KeyboardInterrupt:
    print("\nDatenauslesung abgrebrochen.")
except serial.SerialException as e:
    print("Serieller Fehler:", e)
f.close()
