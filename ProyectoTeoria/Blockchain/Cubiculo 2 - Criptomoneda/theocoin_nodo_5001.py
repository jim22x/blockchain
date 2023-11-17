# -*- coding: utf-8 -*-

import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

#Paso 1 - armando el blockchain

class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof=1,previous_hash='0')
        self.nodes = set()
        
    def add_node (self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        
        
        
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json(['length'])
                chain = response.json(['chain'])
                
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
                    
            if longest_chain:
                self.chain = longest_chain
                return True
            return False
    
    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain)+1, 
                 'timestamp':str(datetime.datetime.now()),
        'proof' : proof,
        'previous_hash':previous_hash,
        'transactions': self.transactions}
        self.transactions = []
        self.chain.append(block)
        return block
    
    def add_transaction(self, emisor, receptor, monto):
        self.transaction.append({'emisor': emisor,
                                 'receptor': receptor,
                                 'monto': monto})
        previous_block = self.get_previous_block()
        return previous_block['index']+1
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def proof_of_work(self,previous_proof):
        new_proof = 1
        check_proof = False
        
        while check_proof is False:
            
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
           
            if hash_operation[:4] == '0000':
                check_proof = True
            
            else:
                new_proof +=1
            
            return new_proof
        
    def hash(self,block):
        encoded_block = json.dumps(block,sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
        
        
    def is_chain_valid(self,chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']  
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index +=1
        
        return True

#Paso 2: Minar la blockchain

app = Flask(__name__) #creando aplicación básica en flask


#Creando una dirección para el puerto 5001
node_address = str(uuid4()).replace('-', '')

#Creando Blockchain
blockchain = Blockchain()

#-Minando nuevo bloque

@app.route('/mine_block', methods =['GET']) #decorador y definiendo el URL que nos servira para hacer el getrequest que nos permitira minar el bloque

def mine_block():
    previous_block = blockchain.get_previous_block() #Empezamos obteniendo el previosblock, y luego obtenemos el bloque anterior
    previous_proof = previous_block['proof'] #Y recuperamos el proof del bloque anterior
    proof = blockchain.proof_of_work(previous_proof) #Con esto solo tomamos el argumento del previvousProof
    previous_hash = blockchain.hash(previous_block) # Para llamar al create block, necesitamos el hash qye cual llamamos.
    #Ahora con estos parametros recolectamos, ya podremos crear el bloque

    blockchain.add_transaction(emisor=node_address,receptor='Jarek', monto=1)
    block = blockchain.create_block(proof,previous_hash)#Tomamos los parametros y acontinuación vamos a crear una variable que contenga todo el bloque y nos devuelva un mensaje
    response = {'message':'Felicidades, minaste un bloque',
                'index':block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions':block['transactions']}
    return jsonify(response), 200 #200 es un mensaje de HTTP CODES el cual nos dará una confirmación del bloque minado
    

#-Obteniendo la cadena completa

@app.route('/get_chain', methods =['GET']) #De igual forma con este decorador, definimos la URL a utilizar para obtener la cadena
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    
    #el jsonify es para poder interactuar con el archivo mediante postman
    return jsonify(response), 200

#Validamos la cadena de bloques
@app.route('/is_valid', methods =['GET']) #De igual forma con este decorador, definimos la URL a utilizar para obtener la cadena
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'Todo está correcto- El BLOCKCHAIN es VALIDO'}
    else:
        response = {'message': 'Tenemos un problema -  El BLOCKCHAIN NO es VALIDO'}
    return jsonify(response), 200

#Corriendo el app


#Agregando nueva transación al blockchain

@app.route('/add_transantion', methods =['POST']) #De igual forma con este decorador, definimos la URL a utilizar para obtener la cadena
def add_transaction():
    json = request.get_json()
    transaction_keys = ['emisor', 'receptor', 'monto']
    if not all (key in json for key  in transaction_keys):
        return 'Algún elemento de la transacción esta faltante', 400
    
    index = blockchain.add_transaction(json['emisor'], json['receptor'], json['monto'])
    response = {'message': f'La transsación sera añadida al bloque {index}'}
    return jsonify(response), 201


#Paso 3 -  Descentralizando el blockchain

#Conectando nuevos nodos

@app.route('/connect_node', methods =['POST']) #De igual forma con este decorador, definimos la URL a utilizar para obtener la cadena
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    
    if nodes is None:
        return "No node", 401
    
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'Todos los nodos estan conectados. El theocoin contiene los siguiente nodos: ',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response),201

#Reemplazando por la más larga
@app.route('/replace_chain', methods =['GET']) #De igual forma con este decorador, definimos la URL a utilizar para obtener la cadena
def replace_chain():
    is_chain_replace = blockchain.replace_chain()
    if is_chain_replace:
        response = {'message': 'Los nodos tenian diferentes cadenas. Se reemplazo la cadena por la más larga',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'Todo bien. La cadena era la más larga',
                    'actual_chain': blockchain.chain}
    return jsonify(response), 200


app.run(host='0.0.0.0', port='5001')























