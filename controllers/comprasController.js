const Compras = require('../models/compras');
const Producto = require('../models/producto');

// Obtener todas las compras
exports.getAllCompras = async (req, res) => {
  try {
    const compras = await Compras.findAll();
    res.json(compras);
  } catch (error) {
    res.status(500).json({ message: 'Error al obtener las compras', error });
  }
};

// Obtener una compra por ID
exports.getCompraById = async (req, res) => {
  const { id } = req.params;
  try {
    const compra = await Compras.findByPk(id);
    if (!compra) {
      return res.status(404).json({ message: 'Compra no encontrada' });
    }
    res.json(compra);
  } catch (error) {
    res.status(500).json({ message: 'Error al obtener la compra', error });
  }
};

// Crear una nueva compra
exports.createCompra = async (req, res) => {
  const { usuario_id, total } = req.body;
  try {
    const compra = await Compras.create({ usuario_id, total });
    res.status(201).json(compra);
  } catch (error) {
    res.status(500).json({ message: 'Error al crear la compra', error });
  }
};

// Actualizar una compra
exports.updateCompra = async (req, res) => {
  const { id } = req.params;
  const { usuario_id, total } = req.body;
  try {
    const compra = await Compras.findByPk(id);
    if (!compra) {
      return res.status(404).json({ message: 'Compra no encontrada' });
    }
    await compra.update({ usuario_id, total });
    res.json(compra);
  } catch (error) {
    res.status(500).json({ message: 'Error al actualizar la compra', error });
  }
};

// Eliminar una compra
exports.deleteCompra = async (req, res) => {
  const { id } = req.params;
  try {
    const compra = await Compras.findByPk(id);
    if (!compra) {
      return res.status(404).json({ message: 'Compra no encontrada' });
    }
    await compra.destroy();
    res.json({ message: 'Compra eliminada' });
  } catch (error) {
    res.status(500).json({ message: 'Error al eliminar la compra', error });
  }
};
