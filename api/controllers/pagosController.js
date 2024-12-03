const Pagos = require('../models/pagos');

// Obtener todos los pagos
const getAllPagos = async (req, res) => {
  try {
    const pagos = await Pagos.findAll();
    res.json(pagos);
  } catch (error) {
    res.status(500).json({ error: 'Error al obtener los pagos.' });
  }
};

// Obtener un pago por ID
const getPagoById = async (req, res) => {
  try {
    const pago = await Pagos.findByPk(req.params.id);
    if (!pago) {
      return res.status(404).json({ error: 'Pago no encontrado.' });
    }
    res.json(pago);
  } catch (error) {
    res.status(500).json({ error: 'Error al obtener el pago.' });
  }
};

// Crear un nuevo pago
const createPago = async (req, res) => {
  try {
    const nuevoPago = await Pagos.create(req.body);
    res.status(201).json(nuevoPago);
  } catch (error) {
    res.status(500).json({ error: 'Error al crear el pago.' });
  }
};

// Actualizar un pago
const updatePago = async (req, res) => {
  try {
    const pago = await Pagos.findByPk(req.params.id);
    if (!pago) {
      return res.status(404).json({ error: 'Pago no encontrado.' });
    }
    await pago.update(req.body);
    res.json(pago);
  } catch (error) {
    res.status(500).json({ error: 'Error al actualizar el pago.' });
  }
};

// Eliminar un pago
const deletePago = async (req, res) => {
  try {
    const pago = await Pagos.findByPk(req.params.id);
    if (!pago) {
      return res.status(404).json({ error: 'Pago no encontrado.' });
    }
    await pago.destroy();
    res.json({ message: 'Pago eliminado.' });
  } catch (error) {
    res.status(500).json({ error: 'Error al eliminar el pago.' });
  }
};

module.exports = {
  getAllPagos,
  getPagoById,
  createPago,
  updatePago,
  deletePago,
};
