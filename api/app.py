from flask import Flask
from flask_restful import Api, Resource, reqparse, abort
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import backref


app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

class Usuarios(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(32))
    categorias=db.relationship("Categorias", cascade='all, delete-orphan',backref="usuario")
    
 
class Categorias(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_usuario=db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    id_madre = db.Column(db.Integer, db.ForeignKey('categorias.id'))
    nombre = db.Column(db.String(32))
    orden = db.Column(db.Integer) 
    hijos = db.relationship("Categorias", cascade='all, delete-orphan')



class CategoriasSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Categorias
    id = ma.auto_field()
    id_madre = ma.auto_field()
    nombre = ma.auto_field()
    orden = ma.auto_field()
    id_usuario=ma.auto_field()
    hijos = ma.auto_field()

class UsuariosSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Usuarios
    id = ma.auto_field()
    nombre= ma.auto_field()
    categorias=ma.auto_field()
        

#################################################### AGREGA
categorias_post_args = reqparse.RequestParser()
categorias_post_args.add_argument('nombre', type=str, help="Nombre de la categoria requerido", required=True)
categorias_post_args.add_argument('id_madre', type=int)
#################################################### ELIMINA
categorias_delete_args = reqparse.RequestParser()
categorias_delete_args.add_argument('id', type=int, help="id de la categoria requerido", required=True)
#################################################### MODIFICA
categorias_put_args = reqparse.RequestParser()
categorias_put_args.add_argument('id', type=int)
categorias_put_args.add_argument('nombre', type=str)
categorias_put_args.add_argument('id1', type=int)
categorias_put_args.add_argument('id2', type=int)
#####################################################

class CategoriasApi(Resource):

    def post(self,user_id):
        args = categorias_post_args.parse_args()
        try:
            cats = Usuarios.query.get(user_id).categorias
            categorias_schema = CategoriasSchema()
            nueva = Categorias (
                id_usuario = user_id,
                id_madre = args["id_madre"],
                nombre = args["nombre"]
            )
            db.session.add(nueva)  
            db.session.commit()
            nueva.orden = nueva.id
            db.session.commit()
            return categorias_schema.dump(nueva), 201
        except:
            return abort(401)

    def get(self,user_id):
        try: 
            cats = Usuarios.query.get(user_id).categorias
            categorias_schema = CategoriasSchema(many=True)
            return categorias_schema.dump(cats)
        except:
            return abort(404)

    def put(self):   
        args = categorias_put_args.parse_args()
        if args['id']:
            cat = Categorias.query.get(args["id"])
            if args["nombre"]:
                cat.nombre = args["nombre"]
            db.session.commit()
            return "Modificacion de nombre exitosa", 200

        else:
            if args['id1'] and args['id2']:
                cat1 = Categorias.query.get(args['id1'])
                cat2 = Categorias.query.get(args['id2'])
                if cat1.id_madre == cat2.id_madre:
                    cat1.orden,cat2.orden = cat2.orden,cat1.orden
                    db.session.commit()
                    return "Modificacion de orden exitosa", 200
                    
        return "ERROR", 400

    def delete(self,user_id):
        args = categorias_delete_args.parse_args()
        try:
            cat = Categorias.query.get(args['id'])
            if cat.id_usuario == user_id and cat!= None:
                db.session.delete(cat) #Elimina en cascada todos sus hijos!
                db.session.commit()
                return 'nos vimo', 200
            return abort(400)
        except:
            return abort(404)
api.add_resource(CategoriasApi,'/categorias/<int:user_id>')


if __name__ == "__main__":
    app.run(debug=True)

