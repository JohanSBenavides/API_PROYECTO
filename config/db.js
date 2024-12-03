const { Sequelize } = require('sequelize');

// Crear una instancia de Sequelize para la base de datos MySQL
const sequelize = new Sequelize('phphone', 'usuario', 'contraseña', {
  host: 'localhost',
  dialect: 'mysql',
  logging: false,  // Para desactivar el log de SQL en consola
});

const testConnection = async () => {
  try {
    await sequelize.authenticate();
    console.log('Conexión a la base de datos establecida correctamente.');
  } catch (error) {
    console.error('No se pudo conectar a la base de datos:', error);
  }
};

// Test de conexión
testConnection();

module.exports = sequelize;
