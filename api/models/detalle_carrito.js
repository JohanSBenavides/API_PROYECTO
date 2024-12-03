const { DataTypes } = require('sequelize');
const sequelize = require('../config/db');

const DetalleCarrito = sequelize.define('DetalleCarrito', {
  carrito_id: {
    type: DataTypes.INTEGER,
    allowNull: false,
    references: {
      model: 'carrito_compras',
      key: 'id'
    }
  },
  producto_id: {
    type: DataTypes.INTEGER,
    allowNull: false,
    references: {
      model: 'productos',
      key: 'id'
    }
  },
  cantidad: {
    type: DataTypes.INTEGER,
    allowNull: false
  },
  subtotal: {
    type: DataTypes.FLOAT,
    allowNull: false
  }
}, {
  tableName: 'detalle_carrito',
  timestamps: false
});

module.exports = DetalleCarrito;
