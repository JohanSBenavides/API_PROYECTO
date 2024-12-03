const { DataTypes } = require('sequelize');
const sequelize = require('../config/db');
const Usuario = require('./usuario'); // Suponiendo que tienes un modelo de usuario

const Factura = sequelize.define('Factura', {
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
  fecha_factura: {
    type: DataTypes.DATE,
    defaultValue: DataTypes.NOW
  }
}, {
  tableName: 'facturas',
  timestamps: false
});

module.exports = Factura;
