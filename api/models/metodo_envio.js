const { DataTypes } = require('sequelize');
const sequelize = require('../config/db');

const MetodoEnvio = sequelize.define('MetodoEnvio', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  metodo: {
    type: DataTypes.STRING,
    allowNull: false
  },
  costo: {
    type: DataTypes.FLOAT,
    allowNull: false
  }
}, {
  tableName: 'metodos_envio',
  timestamps: false
});

module.exports = MetodoEnvio;
