const { DataTypes } = require('sequelize');
const sequelize = require('../config/db');

const EstadoEnvio = sequelize.define('EstadoEnvio', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  estado: {
    type: DataTypes.STRING,
    allowNull: false
  }
}, {
  tableName: 'estado_envio',
  timestamps: false
});

module.exports = EstadoEnvio;
