const sequelize = require('./config/db');
const Producto = require('./models/producto');
// Importa los demás modelos de manera similar
// const Categoria = require('./models/categoria');
// const CarritoCompras = require('./models/carrito_compras');
// ... (el resto de modelos)

async function initializeDatabase() {
  try {
    // Este método sincroniza la base de datos con los modelos (si no existen las tablas, las crea)
    await sequelize.sync({ force: true });  // Crea las tablas desde cero

    console.log('Base de datos sincronizada y tablas creadas correctamente.');
    
    // Aquí puedes agregar datos de prueba si lo deseas, por ejemplo:
    // await Producto.create({ nombre: 'Producto de prueba', descripcion: 'Descripción', precio: 100, stock: 10 });

  } catch (error) {
    console.error('Error al sincronizar la base de datos:', error);
  }
}

initializeDatabase();
