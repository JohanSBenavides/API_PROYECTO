const { DataTypes } = require('sequelize');
const sequelize = require('../config/db');
const Usuario = require('./usuario'); // Suponiendo que tienes un modelo de usuario
const Producto = require('./producto');

const Compras = sequelize.define('Compras', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  usuario_id: {
    type: DataTypes.INTEGER,
    allowNull: false
  },
  total: {
    type: DataTypes.FLOAT,
    allowNull: false
  },
  fecha_compra: {
    type: DataTypes.DATE,
    defaultValue: DataTypes.NOW
  }
}, {
  tableName: 'compras',
  timestamps: false
});

// Relación entre Compras y Producto
Compras.belongsToMany(Producto, { through: 'detalle_compra', foreignKey: 'compra_id' });
Producto.belongsToMany(Compras, { through: 'detalle_compra', foreignKey: 'producto_id' });

module.exports = Compras;
