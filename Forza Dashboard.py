#!/usr/env/python
# -*- coding: utf-8 -*-
'''

Copyright (c) 2022 Chris Faig

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''






import json
import socket
from struct import unpack

class ForzaDataPacket:
 
    sled_format = '<iIfffffffffffffffffffffffffffffffffffffffffffffffffffiiiii'

    dash_format = '<iIfffffffffffffffffffffffffffffffffffffffffffffffffffiiiiifffffffffffffffffHBBBBBBbbb'
    
# '<' é usado para especificar a ordem dos bytes 'little-endian'. Isso significa que o byte de menor valor é armazenado no endereço de memória mais baixo.
# 'i' e 'I' são usados para especificar um número inteiro com sinal e sem sinal, respectivamente. Ambos são de 4 bytes (ou 32 bits).
# 'f' é usado para especificar um número de ponto flutuante de precisão simples de 4 bytes (ou 32 bits).
# 'H' é usado para especificar um número inteiro sem sinal de 2 bytes (ou 16 bits).
# 'B' e 'b' são usados para especificar um número inteiro sem sinal e com sinal, respectivamente, de 1 byte (ou 8 bits).
# Então, por exemplo, o formato 'sled_format' inicia com <iI, o que significa que os dados começam com um número inteiro de 4 bytes (com sinal), seguido por um número inteiro de 4 bytes (sem sinal).
# Depois disso, vêm 63 'f's, o que significa que os próximos 63 campos são números de ponto flutuante de precisão simples de 4 bytes.
# Em seguida, existem quatro 'i's, o que significa que os próximos quatro campos são números inteiros de 4 bytes (com sinal).
# No caso do 'dash_format', os campos adicionais após os 'i's são uma combinação de números de ponto flutuante, números inteiros e bytes, conforme especificado pelos caracteres de formatação.



    sled_props = [
        'is_race_on', 'timestamp_ms',
        'engine_max_rpm', 'engine_idle_rpm', 'current_engine_rpm',
        'acceleration_x', 'acceleration_y', 'acceleration_z',
        'velocity_x', 'velocity_y', 'velocity_z',
        'angular_velocity_x', 'angular_velocity_y', 'angular_velocity_z',
        'yaw', 'pitch', 'roll',
        'norm_suspension_travel_FL', 'norm_suspension_travel_FR',
        'norm_suspension_travel_RL', 'norm_suspension_travel_RR',
        'tire_slip_ratio_FL', 'tire_slip_ratio_FR',
        'tire_slip_ratio_RL', 'tire_slip_ratio_RR',
        'wheel_rotation_speed_FL', 'wheel_rotation_speed_FR',
        'wheel_rotation_speed_RL', 'wheel_rotation_speed_RR',
        'wheel_on_rumble_strip_FL', 'wheel_on_rumble_strip_FR',
        'wheel_on_rumble_strip_RL', 'wheel_on_rumble_strip_RR',
        'wheel_in_puddle_FL', 'wheel_in_puddle_FR',
        'wheel_in_puddle_RL', 'wheel_in_puddle_RR',
        'surface_rumble_FL', 'surface_rumble_FR',
        'surface_rumble_RL', 'surface_rumble_RR',
        'tire_slip_angle_FL', 'tire_slip_angle_FR',
        'tire_slip_angle_RL', 'tire_slip_angle_RR',
        'tire_combined_slip_FL', 'tire_combined_slip_FR',
        'tire_combined_slip_RL', 'tire_combined_slip_RR',
        'suspension_travel_meters_FL', 'suspension_travel_meters_FR',
        'suspension_travel_meters_RL', 'suspension_travel_meters_RR',
        'car_ordinal', 'car_class', 'car_performance_index',
        'drivetrain_type', 'num_cylinders'
    ]

    dash_props = ['position_x', 'position_y', 'position_z',
                  'speed', 'power', 'torque',
                  'tire_temp_FL', 'tire_temp_FR',
                  'tire_temp_RL', 'tire_temp_RR',
                  'boost', 'fuel', 'dist_traveled',
                  'best_lap_time', 'last_lap_time',
                  'cur_lap_time', 'cur_race_time',
                  'lap_no', 'race_pos',
                  'accel', 'brake', 'clutch', 'handbrake',
                  'gear', 'steer',
                  'norm_driving_line', 'norm_ai_brake_diff']
    
    
    # Método de inicialização
    def __init__(self, data, packet_format='dash'):
        self.packet_format = packet_format
        if packet_format == 'sled':
            for prop_name, prop_value in zip(self.sled_props, unpack(self.sled_format, data)):
                setattr(self, prop_name, prop_value)
        else:
            for prop_name, prop_value in zip(self.sled_props + self.dash_props, unpack(self.dash_format, data)):
                setattr(self, prop_name, prop_value)

    # Método para converter as propriedades do pacote de dados em formato JSON
    def to_json(self):
        if self.packet_format == 'sled':
            return json.dumps({prop_name: getattr(self, prop_name) for prop_name in self.sled_props})
        return json.dumps({prop_name: getattr(self, prop_name) for prop_name in self.sled_props + self.dash_props})

# Função para ouvir os pacotes UDP e imprimir os dados de velocidade
def dump_stream(port, packet_format='dash'):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('', port))
    while True:
        message, address = server_socket.recvfrom(1024)
        fdp = ForzaDataPacket(message, packet_format=packet_format)
        print(fdp.to_json())  # Imprime as propriedades do pacote de dados em formato JSON


class ForzaDataReader:
    def __init__(self, ip="0.0.0.0", port=1024, data_format=ForzaDataPacket.sled_format):
        self.ip = ip
        self.port = port
        self.data_format = data_format

    def start(self):
        # Configurando a conexão com o servidor
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.ip, self.port))

        while True:
            # Aguardando por dados do jogo Forza
            data, addr = sock.recvfrom(1024)

            # Interpretando os dados recebidos usando a classe ForzaDataPacket
            packet = ForzaDataPacket(data, self.data_format)

            # Verificando se a corrida está em andamento
            if packet.is_race_on == 1:
                # Imprimindo os dados interpretados
                print(packet.to_json())


if __name__ == "__main__":
    # Criando uma nova instância de ForzaDataReader para ler dados do Forza
    reader = ForzaDataReader()

    # Iniciando o leitor
    reader.start()
