"""empty message

Revision ID: 182632f0ce99
Revises: 
Create Date: 2025-04-13 20:54:59.807809

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '182632f0ce99'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('categoria',
    sa.Column('id_categoria', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id_categoria')
    )
    op.create_table('producto',
    sa.Column('id_producto', sa.Integer(), nullable=False),
    sa.Column('producto_nombre', sa.String(length=100), nullable=False),
    sa.Column('producto_precio', sa.Float(), nullable=False),
    sa.Column('producto_stock', sa.Integer(), nullable=False),
    sa.Column('descripcion', sa.String(length=255), nullable=False),
    sa.Column('producto_foto', sa.String(length=100), nullable=False),
    sa.Column('categoria_id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id_producto')
    )
    op.create_table('rol',
    sa.Column('rol_id', sa.Integer(), nullable=False),
    sa.Column('nombre_rol', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('rol_id')
    )
    op.create_table('usuario',
    sa.Column('id_usuario', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('nombre', sa.String(length=100), nullable=True),
    sa.Column('numerodoc', sa.Integer(), nullable=True),
    sa.Column('correo', sa.String(length=100), nullable=False),
    sa.Column('contrasena_hash', sa.String(length=255), nullable=True),
    sa.Column('rol_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['rol_id'], ['rol.rol_id'], ),
    sa.PrimaryKeyConstraint('id_usuario'),
    sa.UniqueConstraint('correo')
    )
    op.create_table('carrito',
    sa.Column('id_carrito', sa.Integer(), nullable=False),
    sa.Column('id_usuario', sa.Integer(), nullable=True),
    sa.Column('fecha', sa.DateTime(), nullable=True),
    sa.Column('total', sa.Integer(), nullable=False),
    sa.Column('procesado', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['id_usuario'], ['usuario.id_usuario'], ),
    sa.PrimaryKeyConstraint('id_carrito')
    )
    op.create_table('orden',
    sa.Column('id_orden', sa.Integer(), nullable=False),
    sa.Column('id_usuario', sa.Integer(), nullable=True),
    sa.Column('fecha_orden', sa.DateTime(), nullable=True),
    sa.Column('monto_total', sa.Integer(), nullable=False),
    sa.Column('estado', sa.Enum('pendiente', 'procesando', 'pagada', 'enviada', 'cancelada', name='estado_orden'), nullable=True),
    sa.ForeignKeyConstraint(['id_usuario'], ['usuario.id_usuario'], ),
    sa.PrimaryKeyConstraint('id_orden')
    )
    op.create_table('carrito_producto',
    sa.Column('id_carrito_producto', sa.Integer(), nullable=False),
    sa.Column('id_carrito', sa.Integer(), nullable=False),
    sa.Column('id_producto', sa.Integer(), nullable=False),
    sa.Column('cantidad', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id_carrito'], ['carrito.id_carrito'], ),
    sa.ForeignKeyConstraint(['id_producto'], ['producto.id_producto'], ),
    sa.PrimaryKeyConstraint('id_carrito_producto')
    )
    op.create_table('envio',
    sa.Column('id_envio', sa.Integer(), nullable=False),
    sa.Column('id_orden', sa.Integer(), nullable=True),
    sa.Column('direccion', sa.String(length=255), nullable=False),
    sa.Column('fecha', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['id_orden'], ['orden.id_orden'], ),
    sa.PrimaryKeyConstraint('id_envio')
    )
    op.create_table('factura',
    sa.Column('id_factura', sa.Integer(), nullable=False),
    sa.Column('id_orden', sa.Integer(), nullable=True),
    sa.Column('factura_fecha', sa.DateTime(), nullable=True),
    sa.Column('monto_total', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id_orden'], ['orden.id_orden'], ),
    sa.PrimaryKeyConstraint('id_factura')
    )
    op.create_table('pago',
    sa.Column('id_pago', sa.Integer(), nullable=False),
    sa.Column('id_orden', sa.Integer(), nullable=True),
    sa.Column('monto', sa.Integer(), nullable=False),
    sa.Column('fecha_pago', sa.DateTime(), nullable=True),
    sa.Column('metodo_pago', sa.Enum('tarjeta', 'paypal', 'transferencia', name='metodo_pago'), nullable=True),
    sa.Column('estado', sa.Enum('pendiente', 'completado', 'rechazado', name='estado_pago'), nullable=True),
    sa.ForeignKeyConstraint(['id_orden'], ['orden.id_orden'], ),
    sa.PrimaryKeyConstraint('id_pago')
    )
    op.create_table('detalle_factura',
    sa.Column('id_detalle_factura', sa.Integer(), nullable=False),
    sa.Column('id_factura', sa.Integer(), nullable=True),
    sa.Column('id_producto', sa.Integer(), nullable=True),
    sa.Column('cantidad', sa.Integer(), nullable=False),
    sa.Column('precio_unitario', sa.Integer(), nullable=False),
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
    op.drop_table('carrito_producto')
    op.drop_table('orden')
    op.drop_table('carrito')
    op.drop_table('usuario')
    op.drop_table('rol')
    op.drop_table('producto')
    op.drop_table('categoria')
    # ### end Alembic commands ###
