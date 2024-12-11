"""Creacion de las tablas

Revision ID: fec82afd3056
Revises: 
Create Date: 2024-12-07 18:44:10.358492

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fec82afd3056'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Rol',
    sa.Column('id_rol', sa.Integer(), nullable=False),
    sa.Column('nombre_rol', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id_rol')
    )
    op.create_table('categoria',
    sa.Column('id_categoria', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id_categoria')
    )
    op.create_table('producto',
    sa.Column('id_producto', sa.Integer(), nullable=False),
    sa.Column('producto_nombre', sa.String(length=100), nullable=True),
    sa.Column('producto_precio', sa.Integer(), nullable=True),
    sa.Column('producto_stock', sa.Integer(), nullable=True),
    sa.Column('categoria_id', sa.Integer(), nullable=True),
    sa.Column('descripcion', sa.String(length=255), nullable=True),
    sa.Column('producto_foto', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['categoria_id'], ['categoria.id_categoria'], ),
    sa.PrimaryKeyConstraint('id_producto')
    )
    op.create_table('usuario',
    sa.Column('id_usuario', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('nombre', sa.String(length=100), nullable=True),
    sa.Column('numerodoc', sa.Integer(), nullable=True),
    sa.Column('correo', sa.String(length=100), nullable=False),
    sa.Column('contrasena_hash', sa.String(length=255), nullable=True),
    sa.Column('rol_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['rol_id'], ['Rol.id_rol'], ),
    sa.PrimaryKeyConstraint('id_usuario'),
    sa.UniqueConstraint('correo')
    )
    op.create_table('carrito',
    sa.Column('id_carrito', sa.Integer(), nullable=False),
    sa.Column('id_usuario', sa.Integer(), nullable=True),
    sa.Column('fecha', sa.Integer(), nullable=True),
    sa.Column('total', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id_usuario'], ['usuario.id_usuario'], ),
    sa.PrimaryKeyConstraint('id_carrito')
    )
    op.create_table('orden',
    sa.Column('id_orden', sa.Integer(), nullable=False),
    sa.Column('id_usuario', sa.Integer(), nullable=True),
    sa.Column('fecha_orden', sa.Date(), nullable=True),
    sa.Column('monto_total', sa.Integer(), nullable=True),
    sa.Column('estado', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['id_usuario'], ['usuario.id_usuario'], ),
    sa.PrimaryKeyConstraint('id_orden')
    )
    op.create_table('detalle_carrito',
    sa.Column('id_detalle', sa.Integer(), nullable=False),
    sa.Column('id_carrito', sa.Integer(), nullable=True),
    sa.Column('id_producto', sa.Integer(), nullable=True),
    sa.Column('cantidad', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id_carrito'], ['carrito.id_carrito'], ),
    sa.ForeignKeyConstraint(['id_producto'], ['producto.id_producto'], ),
    sa.PrimaryKeyConstraint('id_detalle')
    )
    op.create_table('envio',
    sa.Column('id_envio', sa.Integer(), nullable=False),
    sa.Column('id_orden', sa.Integer(), nullable=True),
    sa.Column('direccion', sa.String(length=50), nullable=True),
    sa.Column('fecha', sa.Date(), nullable=True),
    sa.ForeignKeyConstraint(['id_orden'], ['orden.id_orden'], ),
    sa.PrimaryKeyConstraint('id_envio')
    )
    op.create_table('factura',
    sa.Column('id_factura', sa.Integer(), nullable=False),
    sa.Column('id_orden', sa.Integer(), nullable=True),
    sa.Column('factura_fecha', sa.Date(), nullable=True),
    sa.Column('monto_total', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id_orden'], ['orden.id_orden'], ),
    sa.PrimaryKeyConstraint('id_factura')
    )
    op.create_table('pago',
    sa.Column('id_pago', sa.Integer(), nullable=False),
    sa.Column('id_orden', sa.Integer(), nullable=True),
    sa.Column('monto', sa.Integer(), nullable=True),
    sa.Column('fecha_pago', sa.Date(), nullable=True),
    sa.Column('metodo_pago', sa.String(length=50), nullable=True),
    sa.Column('estado', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['id_orden'], ['orden.id_orden'], ),
    sa.PrimaryKeyConstraint('id_pago')
    )
    op.create_table('detalle_factura',
    sa.Column('id_detalle_factura', sa.Integer(), nullable=False),
    sa.Column('id_factura', sa.Integer(), nullable=True),
    sa.Column('id_producto', sa.Integer(), nullable=True),
    sa.Column('cantidad', sa.Integer(), nullable=False),
    sa.Column('precio_unitario', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id_factura'], ['factura.id_factura'], ),
    sa.ForeignKeyConstraint(['id_producto'], ['producto.id_producto'], ),
    sa.PrimaryKeyConstraint('id_detalle_factura')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('detalle_factura')
    op.drop_table('pago')
    op.drop_table('factura')
    op.drop_table('envio')
    op.drop_table('detalle_carrito')
    op.drop_table('orden')
    op.drop_table('carrito')
    op.drop_table('usuario')
    op.drop_table('producto')
    op.drop_table('categoria')
    op.drop_table('Rol')
    # ### end Alembic commands ###