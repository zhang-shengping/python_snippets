#!/bin/python

import sys

def hex_binary(value):
    int_value=int(value, base=16)
    bin_value=bin(int_value)[2:].zfill(8)
    return bin_value

def binary_hex(value):
    int_value=int(value, base=2)
    hex_value=hex(int_value)[2:].zfill(2)
    return hex_value

def gen_masquerade_mac(mac):
    temp_mac = mac.split(":")

    first_byte = temp_mac[0]
    binary = hex_binary(first_byte)
    binary = binary[:6] + "1" + binary[-1]
    hexa = binary_hex(binary)

    temp_mac = [hexa] + temp_mac[1:] 
    masquerade_mac = ":".join(temp_mac)
    return masquerade_mac

def input(value):
    if len(value) != 2:
        print("Please provider BigIP Base MAC.")
        print("Such as \n python main.py 08:01:D7:01:02:03")
        sys.exit(1)
    return value[1]

if __name__ == "__main__":
    mac = input(sys.argv)
    print("Input BigIP Base MAC is %s" % mac)
    mas = gen_masquerade_mac(mac)
    print("\nMasquerade MAC is %s\n" % mas)
