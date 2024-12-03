const DetalleFactura = require('../models/detalle_factura');

// Obtener todos los detalles de las facturas
const getAllDetallesFactura = async (req, res) => {
  try {
    const detalles = await DetalleFactura.findAll();
    res.json(detalles);
  } catch (error) {
    res.status(500).json({ error: 'Error al obtener los detalles de la factura.' });
  }
};

// Obtener un detalle de factura por ID
const getDetalleFacturaById = async (req, res) => {
  try {
    const detalle = await DetalleFactura.findByPk(req.params.id);
    if (!detalle) {
      return res.status(404).json({ error: 'Detalle de factura no encontrado.' });
    }
    res.json(detalle);
  } catch (error) {
    res.status(500).json({ error: 'Error al obtener el detalle de la factura.' });
  }
};

// Crear un nuevo detalle de factura
const createDetalleFactura = async (req, res) => {
  try {
    const nuevoDetalle = await DetalleFactura.create(req.body);
    res.status(201).json(nuevoDetalle);
  } catch (error) {
    res.status(500).json({ error: 'Error al crear el detalle de la factura.' });
  }
};

// Actualizar un detalle de factura
const updateDetalleFactura = async (req, res) => {
  try {
    const detalle = await DetalleFactura.findByPk(req.params.id);
    if (!detalle) {
      return res.status(404).json({ error: 'Detalle de factura no encontrado.' });
    }
    await detalle.update(req.body);
    res.json(detalle);
  } catch (error) {
    res.status(500).json({ error: 'Error al actualizar el detalle de la factura.' });
  }
};

// Eliminar un detalle de factura
const deleteDetalleFactura = async (req, res) => {
  try {
    const detalle = await DetalleFactura.findByPk(req.params.id);
    if (!detalle) {
      return res.status(404).json({ error: 'Detalle de factura no encontrado.' });
    }
    await detalle.destroy();
    res.json({ message: 'Detalle de factura eliminado.' });
  } catch (error) {
    res.status(500).json({ error: 'Error al eliminar el detalle de la factura.' });
  }
};
