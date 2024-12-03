const CarritoCompras = require('../models/carrito_compras');
const Producto = require('../models/producto');

// Obtener todos los carritos
exports.getAllCarritos = async (req, res) => {
  try {
    const carritos = await CarritoCompras.findAll();
    res.json(carritos);
  } catch (error) {
    res.status(500).json({ message: 'Error al obtener los carritos', error });
  }
};

// Obtener un carrito por ID
exports.getCarritoById = async (req, res) => {
  const { id } = req.params;
  try {
    const carrito = await CarritoCompras.findByPk(id);
    if (!carrito) {
      return res.status(404).json({ message: 'Carrito no encontrado' });
    }
    res.json(carrito);
  } catch (error) {
    res.status(500).json({ message: 'Error al obtener el carrito', error });
  }
};

// Crear un nuevo carrito
exports.createCarrito = async (req, res) => {
  const { usuario_id } = req.body;
  try {
    const carrito = await CarritoCompras.create({ usuario_id });
    res.status(201).json(carrito);
  } catch (error) {
    res.status(500).json({ message: 'Error al crear el carrito', error });
  }
};

// Actualizar un carrito
exports.updateCarrito = async (req, res) => {
  const { id } = req.params;
  const { usuario_id } = req.body;
  try {
    const carrito = await CarritoCompras.findByPk(id);
    if (!carrito) {
      return res.status(404).json({ message: 'Carrito no encontrado' });
    }
    await carrito.update({ usuario_id });
    res.json(carrito);
  } catch (error) {
    res.status(500).json({ message: 'Error al actualizar el carrito', error });
  }
};

// Eliminar un carrito
exports.deleteCarrito = async (req, res) => {
  const { id } = req.params;
  try {
    const carrito = await CarritoCompras.findByPk(id);
    if (!carrito) {
      return res.status(404).json({ message: 'Carrito no encontrado' });
    }
    await carrito.destroy();
    res.json({ message: 'Carrito eliminado' });
  } catch (error) {
    res.status(500).json({ message: 'Error al eliminar el carrito', error });
  }
};
