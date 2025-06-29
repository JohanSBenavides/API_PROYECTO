"""empty message

Revision ID: 027249347f0e
Revises: fe506c6dfd29
Create Date: 2025-06-08 00:12:00.445902

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '027249347f0e'
down_revision = 'fe506c6dfd29'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('carrito', 'procesado',
        existing_type=sa.SMALLINT(),
        type_=sa.Boolean(),
        existing_nullable=True,
        postgresql_using='CASE WHEN procesado = 1 THEN true ELSE false END')

    op.drop_index('idx_id_usuario', table_name='carrito')
    op.drop_constraint('carrito_ibfk_1', 'carrito', type_='foreignkey')
    op.create_foreign_key(None, 'carrito', 'usuario', ['id_usuario'], ['id_usuario'])
    op.drop_column('carrito', 'trial174')
    op.drop_index('idx_id_carrito', table_name='carrito_producto')
    op.drop_index('idx_id_producto', table_name='carrito_producto')
    op.drop_constraint('carrito_producto_ibfk_2', 'carrito_producto', type_='foreignkey')
    op.drop_constraint('carrito_producto_ibfk_1', 'carrito_producto', type_='foreignkey')
    op.create_foreign_key(None, 'carrito_producto', 'carrito', ['id_carrito'], ['id_carrito'])
    op.create_foreign_key(None, 'carrito_producto', 'producto', ['id_producto'], ['id_producto'])
    op.drop_column('carrito_producto', 'trial174')
    op.drop_column('categoria', 'trial174')
    op.drop_index('idx_id_factura', table_name='detalle_factura')
    op.drop_constraint('detalle_factura_ibfk_1', 'detalle_factura', type_='foreignkey')
    op.drop_constraint('detalle_factura_ibfk_2', 'detalle_factura', type_='foreignkey')
    op.create_foreign_key(None, 'detalle_factura', 'factura', ['id_factura'], ['id_factura'])
    op.create_foreign_key(None, 'detalle_factura', 'producto', ['id_producto'], ['id_producto'])
    op.drop_column('detalle_factura', 'trial174')
    op.drop_constraint('envio_ibfk_2', 'envio', type_='foreignkey')
    op.drop_constraint('envio_ibfk_1', 'envio', type_='foreignkey')
    op.create_foreign_key(None, 'envio', 'factura', ['id_factura'], ['id_factura'])
    op.create_foreign_key(None, 'envio', 'usuario', ['usuario_id'], ['id_usuario'])
    op.drop_column('envio', 'trial174')
    op.drop_index('idx_id_pago', table_name='factura')
    op.drop_constraint('factura_ibfk_1', 'factura', type_='foreignkey')
    op.create_foreign_key(None, 'factura', 'pago', ['id_pago'], ['id_pago'])
    op.drop_column('factura', 'trial174')
    op.drop_constraint('historial_stock_ibfk_1', 'historial_stock', type_='foreignkey')
    op.create_foreign_key(None, 'historial_stock', 'producto', ['id_producto'], ['id_producto'])
    op.drop_column('historial_stock', 'trial178')
    op.alter_column('orden', 'estado',
        existing_type=sa.String(),
        type_=sa.Enum('pendiente', 'pagado', 'cancelado', name='estado_orden'),
        existing_nullable=False,
        postgresql_using="estado::estado_orden")

    op.drop_constraint('orden_ibfk_1', 'orden', type_='foreignkey')
    op.drop_constraint('orden_ibfk_2', 'orden', type_='foreignkey')
    op.create_foreign_key(None, 'orden', 'usuario', ['id_usuario'], ['id_usuario'])
    op.create_foreign_key(None, 'orden', 'factura', ['id_factura'], ['id_factura'])
    op.drop_column('orden', 'trial178')
    op.execute("""
        ALTER TABLE pago
        ALTER COLUMN metodo_pago
        TYPE metodo_pago
        USING metodo_pago::metodo_pago
    """)
    op.execute("ALTER TABLE pago ALTER COLUMN estado TYPE estado_pago USING estado::estado_pago")
    op.drop_constraint('pago_ibfk_1', 'pago', type_='foreignkey')
    op.create_foreign_key(None, 'pago', 'carrito', ['id_carrito'], ['id_carrito'])
    op.drop_column('pago', 'trial174')
    op.create_unique_constraint(None, 'paypal_detalle', ['id_pago'])
    op.drop_constraint('paypal_detalle_ibfk_1', 'paypal_detalle', type_='foreignkey')
    op.create_foreign_key(None, 'paypal_detalle', 'pago', ['id_pago'], ['id_pago'])
    op.drop_column('paypal_detalle', 'trial178')
    op.drop_column('producto', 'trial174')
    op.drop_index('idx_nombre_rol', table_name='rol')
    op.create_unique_constraint(None, 'rol', ['nombre_rol'])
    op.drop_column('rol', 'trial174')
    op.create_unique_constraint(None, 'tarjeta_detalle', ['id_pago'])
    op.drop_constraint('tarjeta_detalle_ibfk_1', 'tarjeta_detalle', type_='foreignkey')
    op.create_foreign_key(None, 'tarjeta_detalle', 'pago', ['id_pago'], ['id_pago'])
    op.drop_column('tarjeta_detalle', 'trial178')
    op.drop_constraint('transferencia_detalle_ibfk_1', 'transferencia_detalle', type_='foreignkey')
    op.create_foreign_key(None, 'transferencia_detalle', 'pago', ['id_pago'], ['id_pago'])
    op.drop_column('transferencia_detalle', 'trial178')
    op.drop_index('idx_correo', table_name='usuario')
    op.drop_index('idx_rol_id', table_name='usuario')
    op.create_unique_constraint(None, 'usuario', ['correo'])
    op.drop_constraint('usuario_ibfk_1', 'usuario', type_='foreignkey')
    op.create_foreign_key(None, 'usuario', 'rol', ['rol_id'], ['rol_id'])
    op.drop_column('usuario', 'trial174')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('usuario', sa.Column('trial174', sa.CHAR(length=1), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'usuario', type_='foreignkey')
    op.create_foreign_key('usuario_ibfk_1', 'usuario', 'rol', ['rol_id'], ['rol_id'], onupdate='RESTRICT', ondelete='RESTRICT')
    op.drop_constraint(None, 'usuario', type_='unique')
    op.create_index('idx_rol_id', 'usuario', ['rol_id'], unique=False)
    op.create_index('idx_correo', 'usuario', ['correo'], unique=True)
    op.add_column('transferencia_detalle', sa.Column('trial178', sa.CHAR(length=1), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'transferencia_detalle', type_='foreignkey')
    op.create_foreign_key('transferencia_detalle_ibfk_1', 'transferencia_detalle', 'pago', ['id_pago'], ['id_pago'], onupdate='RESTRICT', ondelete='RESTRICT')
    op.add_column('tarjeta_detalle', sa.Column('trial178', sa.CHAR(length=1), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'tarjeta_detalle', type_='foreignkey')
    op.create_foreign_key('tarjeta_detalle_ibfk_1', 'tarjeta_detalle', 'pago', ['id_pago'], ['id_pago'], onupdate='RESTRICT', ondelete='RESTRICT')
    op.drop_constraint(None, 'tarjeta_detalle', type_='unique')
    op.add_column('rol', sa.Column('trial174', sa.CHAR(length=1), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'rol', type_='unique')
    op.create_index('idx_nombre_rol', 'rol', ['nombre_rol'], unique=True)
    op.add_column('producto', sa.Column('trial174', sa.CHAR(length=1), autoincrement=False, nullable=True))
    op.add_column('paypal_detalle', sa.Column('trial178', sa.CHAR(length=1), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'paypal_detalle', type_='foreignkey')
    op.create_foreign_key('paypal_detalle_ibfk_1', 'paypal_detalle', 'pago', ['id_pago'], ['id_pago'], onupdate='RESTRICT', ondelete='RESTRICT')
    op.drop_constraint(None, 'paypal_detalle', type_='unique')
    op.add_column('pago', sa.Column('trial174', sa.CHAR(length=1), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'pago', type_='foreignkey')
    op.create_foreign_key('pago_ibfk_1', 'pago', 'carrito', ['id_carrito'], ['id_carrito'], onupdate='RESTRICT', ondelete='RESTRICT')
    op.alter_column('pago', 'estado',
               existing_type=sa.Enum('pendiente', 'completado', 'rechazado', name='estado_pago'),
               type_=sa.VARCHAR(length=10),
               existing_nullable=True)
    op.alter_column('pago', 'metodo_pago',
               existing_type=sa.Enum('tarjeta', 'paypal', 'transferencia', name='metodo_pago'),
               type_=sa.VARCHAR(length=13),
               existing_nullable=True)
    op.add_column('orden', sa.Column('trial178', sa.CHAR(length=1), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'orden', type_='foreignkey')
    op.drop_constraint(None, 'orden', type_='foreignkey')
    op.create_foreign_key('orden_ibfk_2', 'orden', 'usuario', ['id_usuario'], ['id_usuario'], onupdate='RESTRICT', ondelete='RESTRICT')
    op.create_foreign_key('orden_ibfk_1', 'orden', 'factura', ['id_factura'], ['id_factura'], onupdate='RESTRICT', ondelete='RESTRICT')
    op.alter_column('orden', 'estado',
               existing_type=sa.Enum('pendiente', 'procesando', 'pagada', 'enviada', 'cancelada', name='estado_orden'),
               type_=sa.VARCHAR(length=10),
               existing_nullable=True)
    op.add_column('historial_stock', sa.Column('trial178', sa.CHAR(length=1), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'historial_stock', type_='foreignkey')
    op.create_foreign_key('historial_stock_ibfk_1', 'historial_stock', 'producto', ['id_producto'], ['id_producto'], onupdate='RESTRICT', ondelete='RESTRICT')
    op.add_column('factura', sa.Column('trial174', sa.CHAR(length=1), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'factura', type_='foreignkey')
    op.create_foreign_key('factura_ibfk_1', 'factura', 'pago', ['id_pago'], ['id_pago'], onupdate='RESTRICT', ondelete='RESTRICT')
    op.create_index('idx_id_pago', 'factura', ['id_pago'], unique=False)
    op.add_column('envio', sa.Column('trial174', sa.CHAR(length=1), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'envio', type_='foreignkey')
    op.drop_constraint(None, 'envio', type_='foreignkey')
    op.create_foreign_key('envio_ibfk_1', 'envio', 'factura', ['id_factura'], ['id_factura'], onupdate='RESTRICT', ondelete='RESTRICT')
    op.create_foreign_key('envio_ibfk_2', 'envio', 'usuario', ['usuario_id'], ['id_usuario'], onupdate='RESTRICT', ondelete='RESTRICT')
    op.add_column('detalle_factura', sa.Column('trial174', sa.CHAR(length=1), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'detalle_factura', type_='foreignkey')
    op.drop_constraint(None, 'detalle_factura', type_='foreignkey')
    op.create_foreign_key('detalle_factura_ibfk_2', 'detalle_factura', 'producto', ['id_producto'], ['id_producto'], onupdate='RESTRICT', ondelete='RESTRICT')
    op.create_foreign_key('detalle_factura_ibfk_1', 'detalle_factura', 'factura', ['id_factura'], ['id_factura'], onupdate='RESTRICT', ondelete='RESTRICT')
    op.create_index('idx_id_factura', 'detalle_factura', ['id_factura'], unique=False)
    op.add_column('categoria', sa.Column('trial174', sa.CHAR(length=1), autoincrement=False, nullable=True))
    op.add_column('carrito_producto', sa.Column('trial174', sa.CHAR(length=1), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'carrito_producto', type_='foreignkey')
    op.drop_constraint(None, 'carrito_producto', type_='foreignkey')
    op.create_foreign_key('carrito_producto_ibfk_1', 'carrito_producto', 'carrito', ['id_carrito'], ['id_carrito'], onupdate='RESTRICT', ondelete='RESTRICT')
    op.create_foreign_key('carrito_producto_ibfk_2', 'carrito_producto', 'producto', ['id_producto'], ['id_producto'], onupdate='RESTRICT', ondelete='RESTRICT')
    op.create_index('idx_id_producto', 'carrito_producto', ['id_producto'], unique=False)
    op.create_index('idx_id_carrito', 'carrito_producto', ['id_carrito'], unique=False)
    op.add_column('carrito', sa.Column('trial174', sa.CHAR(length=1), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'carrito', type_='foreignkey')
    op.create_foreign_key('carrito_ibfk_1', 'carrito', 'usuario', ['id_usuario'], ['id_usuario'], onupdate='RESTRICT', ondelete='RESTRICT')
    op.create_index('idx_id_usuario', 'carrito', ['id_usuario'], unique=False)
    op.alter_column('carrito', 'procesado',
               existing_type=sa.Boolean(),
               type_=sa.SMALLINT(),
               existing_nullable=True)
    # ### end Alembic commands ###
