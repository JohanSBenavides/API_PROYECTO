const { DataTypes } = require('sequelize');
const sequelize = require('../config/db');

// Definición del modelo 'Producto'
const Producto = sequelize.define('Producto', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  nombre: {
    type: DataTypes.STRING,
    allowNull: false
  },
  descripcion: {
    type: DataTypes.STRING,
    allowNull: false
  },
  precio: {
    type: DataTypes.FLOAT,
    allowNull: false
  },
  stock: {
    type: DataTypes.INTEGER,
    allowNull: false
  }
}, {
  tableName: 'productos', // Nombre de la tabla en la base de datos
  timestamps: false // Si no deseas campos de timestamps (createdAt, updatedAt)
});

module.exports = Producto;
