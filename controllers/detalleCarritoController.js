const DetalleCarrito = require('../models/detalle_carrito');

// Obtener todos los detalles de los carritos
const getAllDetallesCarrito = async (req, res) => {
  try {
    const detalles = await DetalleCarrito.findAll();
    res.json(detalles);
  } catch (error) {
    res.status(500).json({ error: 'Error al obtener los detalles del carrito.' });
  }
};

// Obtener un detalle del carrito por ID
const getDetalleCarritoById = async (req, res) => {
  try {
    const detalle = await DetalleCarrito.findByPk(req.params.id);
    if (!detalle) {
      return res.status(404).json({ error: 'Detalle del carrito no encontrado.' });
    }
    res.json(detalle);
  } catch (error) {
    res.status(500).json({ error: 'Error al obtener el detalle del carrito.' });
  }
};

// Crear un nuevo detalle en el carrito
const createDetalleCarrito = async (req, res) => {
  try {
    const nuevoDetalle = await DetalleCarrito.create(req.body);
    res.status(201).json(nuevoDetalle);
  } catch (error) {
    res.status(500).json({ error: 'Error al crear el detalle del carrito.' });
  }
};

// Actualizar un detalle del carrito
const updateDetalleCarrito = async (req, res) => {
  try {
    const detalle = await DetalleCarrito.findByPk(req.params.id);
    if (!detalle) {
      return res.status(404).json({ error: 'Detalle del carrito no encontrado.' });
    }
    await detalle.update(req.body);
    res.json(detalle);
  } catch (error) {
    res.status(500).json({ error: 'Error al actualizar el detalle del carrito.' });
  }
};

// Eliminar un detalle del carrito
const deleteDetalleCarrito = async (req, res) => {
  try {
    const detalle = await DetalleCarrito.findByPk(req.params.id);
    if (!detalle) {
      return res.status(404).json({ error: 'Detalle del carrito no encontrado.' });
    }
    await detalle.destroy();
    res.json({ message: 'Detalle del carrito eliminado.' });
  } catch (error) {
    res.status(500).json({ error: 'Error al eliminar el detalle del carrito.' });
  }
};

