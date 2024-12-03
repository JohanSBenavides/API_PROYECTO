const { DataTypes } = require('sequelize');
const sequelize = require('../config/db');

const Orden = sequelize.define('Orden', {
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
  fecha_orden: {
    type: DataTypes.DATE,
    defaultValue: DataTypes.NOW
  }
}, {
  tableName: 'ordenes',
  timestamps: false
});

module.exports = Orden;
