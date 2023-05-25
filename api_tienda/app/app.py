from flask import Flask, request, jsonify
from flask_migrate import Migrate
from models import db, Producto, Cliente, Carrito, ProductoCarrito, Compra
from flask_cors import CORS, cross_origin
from logging import exception
import requests
import json

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Conten-Type'
app.url_map.strict_slashes = False
app.config['DEBUG'] = False
app.config['ENV'] = 'development'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db.init_app(app)

Migrate(app, db)

@app.route('/')
def index():
    return 'Bienvenido'

#Productos--------------------


#Solicitar todos los productos 
@app.route('/productos', methods=['GET'])
def getProductos():
    user = Producto.query.all()
    user = list(map(lambda x: x.serialize(), user))
    return jsonify(user),200

#Agregar producto
@app.route('/productos', methods=['POST'])
def addProductos():
    user = Producto()
    user.id_producto = request.json.get('id_producto')
    user.nombre = request.json.get('nombre')
    user.valor_venta = request.json.get('valor_venta')
    user.stock = request.json.get('stock')
    Producto.save(user)

    return jsonify(user.serialize()),200

#Solicitar un producto
@app.route('/productos/<id_producto>', methods=['GET'])
def getProducto(id_producto):
    user = Producto.query.get(id_producto)
    return jsonify(user.serialize()),200
   

#Eliminar un producto 
@app.route('/productos/<id_producto>', methods=['DELETE'])
def deleteProducto(id_producto):
    user = Producto.query.get(id_producto)
    Producto.delete(user)
    return jsonify(user.serialize()),200


#Actualizar un producto 
@app.route('/productos/<id_producto>', methods=['PUT'])
def updateProducto(id_producto):
    user = Producto.query.get(id_producto)

    user.id_producto = request.json.get('id_producto')
    user.valor_venta = request.json.get('valor_venta')
    user.stock = request.json.get('stock')

    Producto.update(user)

    return jsonify(user.serialize()),200

#Clientes--------------------

#Solicitar todos los clientes 
@app.route('/clientes', methods=['GET'])
def getClientes():
    user = Cliente.query.all()
    user = list(map(lambda x: x.serialize(), user))
    return jsonify(user),200

#Agregar Cliente
@app.route('/clientes', methods=['POST'])
def addCliente():
    user = Cliente()
    user.rut = request.json.get('rut')
    user.tarjeta = request.json.get('tarjeta')
    Cliente.save(user)

    return jsonify(user.serialize()),200


#Solicitar un cliente
@app.route('/clientes/<rut>', methods=['GET'])
def getCliente(rut):
    user = Cliente.query.get(rut)
    return jsonify(user.serialize()),200

#Carrito--------------------

#Solicitar los carritos 
@app.route('/carritos', methods=['GET'])
def getCarritos():
    user = Carrito.query.all()
    user = list(map(lambda x: x.serialize(), user))
    return jsonify(user),200

#Agregar Carritos
@app.route('/carritos', methods=['POST'])
def addCarrito():
    user = Carrito()
    user.id_carrito = request.json.get('id_carrito')
    user.rut = request.json.get('rut')
    user.total = request.json.get('total')
    Carrito.save(user)

    return jsonify(user.serialize()),200

#Eliminar Carrito
@app.route('/carritos/<id_carrito>', methods=['DELETE'])
def deleteCarrito(id_carrito):
    user = Carrito.query.get(id_carrito)
    Carrito.delete(user)
    return jsonify(user.serialize()),200

#ProductoCarrito--------------------


#Agregar Producto a Carrito 
@app.route('/productocarrito', methods=['POST'])
def addProductoCarrito():

    id_producto = request.json.get('id_producto')
    id_carrito = request.json.get('id_carrito')
    cantidad = request.json.get('cantidad')

    precio_producto = Producto.query.filter_by(id_producto=id_producto).first().valor_venta

    subtotal = precio_producto * cantidad


    carrito = Carrito.query.get(id_carrito)
    total_carrito = carrito.total

    nuevo_total_carrito = total_carrito + subtotal
    carrito.total = nuevo_total_carrito
    db.session.commit()

    user = ProductoCarrito(id_producto=id_producto, id_carrito=id_carrito, cantidad=cantidad)
    db.session.add(user)
    db.session.commit()

    return jsonify(user.serialize()),200

#Solicitar todos los ProductoCarrito 
@app.route('/productocarrito', methods=['GET'])
def getProductoCarritos():
    user = ProductoCarrito.query.all()
    user = list(map(lambda x: x.serialize(), user))
    return jsonify(user),200


#Eliminar producto del carrito
@app.route('/productocarrito/<id_producto>/<id_carrito>', methods=['DELETE'])
def deleteProductoCarrito(id_producto,id_carrito):
    user = ProductoCarrito.query.filter_by(id_producto=id_producto, id_carrito=id_carrito).first()

   
    cantidad = user.cantidad
    precio_producto = Producto.query.filter_by(id_producto=id_producto).first().valor_venta
    subtotal = precio_producto * cantidad

    carrito = Carrito.query.get(id_carrito)
    total_carrito = carrito.total

    nuevo_total_carrito = total_carrito - subtotal
    carrito.total = nuevo_total_carrito

    db.session.delete(user)
    db.session.commit()

    return jsonify(user.serialize()), 200

#Compra--------

#Agregar Compra
@app.route('/compra', methods=['POST'])
def createCompra():
    carrito_id = request.json['id_carrito']
    carrito = Carrito.query.get(carrito_id)

    n_tarjeta = request.json['n_tarjeta']
    fecha_v = request.json['fecha_v']
    cvv = request.json['cvv']

    payload = {
        "monto": carrito.total,
        "nro_tarjeta": n_tarjeta,
        "fecha_v": fecha_v,
        "cvv": cvv
        # "rut": "11123123-1"
    }

    # Realizar la solicitud a la API externa
    api_url = "http://tbkemu/execute_sale"

    response = requests.post(api_url, json=payload)
    print(response)
    print(response.json())
   
    # Procesar la respuesta de la API externa
    if response.status_code == 200:
        response_data = response.json()
        print("------")
        print(response_data['status'])
        print(type(response_data['status']))

        if response_data['status']:
            print(response_data)
            # Si el status es True, guardar la id_transaccion en la tabla compra
            print("------")
            print(type(carrito.total))
            print(carrito.total)
            print("------")

            compra = Compra(id_carrito=carrito_id, total=carrito.total, transaccion=response_data['id_transaction'])
            db.session.add(compra)
            db.session.commit()

            # Descuento del campo stock en la tabla producto
            productos_carrito = ProductoCarrito.query.filter_by(id_carrito=carrito_id).all()
            for producto_carrito in productos_carrito:
                producto = Producto.query.get(producto_carrito.id_producto)
                cantidad = producto_carrito.cantidad
                producto.stock -= cantidad
                db.session.commit()

            ProductoCarrito.query.filter_by(id_carrito=carrito_id).delete()
            Carrito.query.filter_by(id_carrito=carrito_id).delete()
            db.session.commit()

            return jsonify({"message": "Compra creada exitosamente."}), 200
        else:
            response_data = response.json()
            mensaje = response_data.get("msg")
            return jsonify({"message": mensaje}), 500

    else:
        return jsonify({"message": "Error en la solicitud a la API externa."}), response.status_code

#Lista de compras    
@app.route('/compras', methods=['GET'])
def getCompras():
    user = Compra.query.all()
    user = list(map(lambda x: x.serialize(), user))
    return jsonify(user),200

#Tarjetas--------------------

#Lista de todas las tarjetas 
@app.route('/tarjetas', methods=['GET'])
def getTarjetas():
    # Realizar la solicitud POST a la API de FastAPI
    api_url = "http://tbkemu/view_all_card"
    response = requests.post(api_url)
    
    # Procesar la respuesta de la API de FastAPI
    if response.status_code == 200:
        response_data = response.json()
        return jsonify(response_data), 200
    
    return jsonify({"error": "No se pudo obtener la lista de tarjetas"}), 500



if __name__ == '__main__':
    app.run(debug=True, port=4000)



