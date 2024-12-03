const { DataTypes } = require('sequelize');
const sequelize = require('../config/db');
const Producto = require('./producto'); // Relacionar con el modelo Producto

const CarritoCompras = sequelize.define('CarritoCompras', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  usuario_id: {
    type: DataTypes.INTEGER,
    allowNull: false
  },
  fecha_creacion: {
    type: DataTypes.DATE,
    defaultValue: DataTypes.NOW
  }
}, {
  tableName: 'carrito_compras',
  timestamps: false
});

// Relación entre CarritoCompras y Producto (Muchos a Muchos, con una tabla intermedia)
CarritoCompras.belongsToMany(Producto, { through: 'detalle_carrito', foreignKey: 'carrito_id' });
Producto.belongsToMany(CarritoCompras, { through: 'detalle_carrito', foreignKey: 'producto_id' });

module.exports = CarritoCompras;
