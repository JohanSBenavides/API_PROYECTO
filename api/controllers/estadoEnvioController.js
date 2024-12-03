const EstadoEnvio = require('../models/estado_envio');

// Obtener todos los estados de envío
const getAllEstadosEnvio = async (req, res) => {
  try {
    const estados = await EstadoEnvio.findAll();
    res.json(estados);
  } catch (error) {
    res.status(500).json({ error: 'Error al obtener los estados de envío.' });
  }
};

// Obtener un estado de envío por ID
const getEstadoEnvioById = async (req, res) => {
  try {
    const estado = await EstadoEnvio.findByPk(req.params.id);
    if (!estado) {
      return res.status(404).json({ error: 'Estado de envío no encontrado.' });
    }
    res.json(estado);
  } catch (error) {
    res.status(500).json({ error: 'Error al obtener el estado de envío.' });
  }
};

// Crear un nuevo estado de envío
const createEstadoEnvio = async (req, res) => {
  try {
    const nuevoEstado = await EstadoEnvio.create(req.body);
    res.status(201).json(nuevoEstado);
  } catch (error) {
    res.status(500).json({ error: 'Error al crear el estado de envío.' });
  }
};

// Actualizar un estado de envío
const updateEstadoEnvio = async (req, res) => {
  try {
    const estado = await EstadoEnvio.findByPk(req.params.id);
    if (!estado) {
      return res.status(404).json({ error: 'Estado de envío no encontrado.' });
    }
    await estado.update(req.body);
    res.json(estado);
  } catch (error) {
    res.status(500).json({ error: 'Error al actualizar el estado de envío.' });
  }
};

// Eliminar un estado de envío
const deleteEstadoEnvio = async (req, res) => {
  try {
    const estado = await EstadoEnvio.findByPk(req.params.id);
    if (!estado) {
      return res.status(404).json({ error: 'Estado de envío no encontrado.' });
    }
    await estado.destroy();
    res.json({ message: 'Estado de envío eliminado.' });
  } catch (error) {
    res.status(500).json({ error: 'Error al eliminar el estado de envío.' });
  }
};


