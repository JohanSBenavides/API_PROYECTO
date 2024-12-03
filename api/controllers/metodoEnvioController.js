const MetodoEnvio = require('../models/metodo_envio');

// Obtener todos los métodos de envío
const getAllMetodosEnvio = async (req, res) => {
  try {
    const metodos = await MetodoEnvio.findAll();
    res.json(metodos);
  } catch (error) {
    res.status(500).json({ error: 'Error al obtener los métodos de envío.' });
  }
};

// Obtener un método de envío por ID
const getMetodoEnvioById = async (req, res) => {
  try {
    const metodo = await MetodoEnvio.findByPk(req.params.id);
    if (!metodo) {
      return res.status(404).json({ error: 'Método de envío no encontrado.' });
    }
    res.json(metodo);
  } catch (error) {
    res.status(500).json({ error: 'Error al obtener el método de envío.' });
  }
};

// Crear un nuevo método de envío
const createMetodoEnvio = async (req, res) => {
  try {
    const nuevoMetodo = await MetodoEnvio.create(req.body);
    res.status(201).json(nuevoMetodo);
  } catch (error) {
    res.status(500).json({ error: 'Error al crear el método de envío.' });
  }
};

// Actualizar un método de envío
const updateMetodoEnvio = async (req, res) => {
  try {
    const metodo = await MetodoEnvio.findByPk(req.params.id);
    if (!metodo) {
      return res.status(404).json({ error: 'Método de envío no encontrado.' });
    }
    await metodo.update(req.body);
    res.json(metodo);
  } catch (error) {
    res.status(500).json({ error: 'Error al actualizar el método de envío.' });
  }
};

// Eliminar un método de envío
const deleteMetodoEnvio = async (req, res) => {
  try {
    const metodo = await MetodoEnvio.findByPk(req.params.id);
    if (!metodo) {
      return res.status(404).json({ error: 'Método de envío no encontrado.' });
    }
    await metodo.destroy();
    res.json({ message: 'Método de envío eliminado.' });
  } catch (error) {
    res.status(500).json({ error: 'Error al eliminar el método de envío.' });
  }
};

